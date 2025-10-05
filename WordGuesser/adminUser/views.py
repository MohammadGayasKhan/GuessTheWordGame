from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from .models import db
import re
from functools import wraps
from django.shortcuts import redirect


def login_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        username = request.session.get('username')
        if not username:
            return redirect('adminUser:login')
        return view_func(request, *args, **kwargs)
    return wrapped


@csrf_protect
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password: 
            admin = db.admins.find_one({"username": username, "password": password})
            if admin:
                request.session['username'] = username
                return redirect('adminUser:report')
            else:
                return render(request, 'adminUser/login.html', {'error_message': 'Invalid administrator credentials'})
    return render(request, 'adminUser/login.html')

@csrf_protect
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password: 
            is_valid_username, username_error = validate_username(username)
            if not is_valid_username:
                return render(request, 'adminUser/register.html', {'error_message': username_error})
 
            is_valid_password, password_error = validate_password(password)
            if not is_valid_password:
                return render(request, 'adminUser/register.html', {'error_message': password_error})

            existing_user = db.admins.find_one({"username": username})
            if existing_user:
                return render(request, 'adminUser/register.html', {'error_message': 'Username already exists'})
            
            db.admins.insert_one({
                "username": username,
                "password": password
            })
            request.session['username'] = username
            return redirect('adminUser:report')
    return render(request, 'adminUser/register.html')

def validate_username(username):
    if len(username) < 5:
        return False, "Username must be at least 5 characters long"
    if not (re.search(r'[A-Z]', username) and re.search(r'[a-z]', username)):
        return False, "Username must contain both uppercase and lowercase letters"
    return True, ""

def validate_password(password):
    if len(password) < 5:
        return False, "Password must be at least 5 characters long"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[$%*@]', password):
        return False, "Password must contain at least one special character ($, %, *, @)"
    return True, ""

def dummy(request):
    return render(request, 'adminUser/hello.html')


@login_required
def report(request):
    try:
        context = {}
        
        if request.method == 'POST':
            report_type = request.POST.get('report_type')
            
            if report_type == 'daily':
                date = request.POST.get('date')
                if date:
                    daily_logs = list(db.playerLogs.find({"date": date}))
                    unique_users = len(set(log['username'] for log in daily_logs))
                    correct_guesses = sum(1 for log in daily_logs if log['guessedword'] == log['actualword'])
                    
                    context['daily_report'] = {
                        'date': date,
                        'unique_users': unique_users,
                        'total_guesses': len(daily_logs),
                        'correct_guesses': correct_guesses
                    }
            
            elif report_type == 'user':
                username = request.POST.get('username')
                if username:
                    if username == 'all':
                        # Get all users' logs
                        all_logs = list(db.playerLogs.find({}))
                        all_user_stats = {}
                        
                        for log in all_logs:
                            username = log['username']
                            if username not in all_user_stats:
                                all_user_stats[username] = {
                                    'total_words': 0,
                                    'total_correct': 0,
                                    'dates_played': set(),
                                    'success_rate': 0
                                }
                            
                            all_user_stats[username]['total_words'] += 1
                            all_user_stats[username]['dates_played'].add(log['date'])
                            if log['guessedword'] == log['actualword']:
                                all_user_stats[username]['total_correct'] += 1
                        
                        # Calculate success rates and prepare report
                        user_report = []
                        for username, stats in all_user_stats.items():
                            user_report.append({
                                'username': username,
                                'total_words': stats['total_words'],
                                'total_correct': stats['total_correct'],
                                'days_played': len(stats['dates_played']),
                                'dates_played': sorted(list(stats['dates_played']), reverse=True)  # Sort dates in descending order
                            })
                        
                        # Sort by total words played (descending)
                        user_report.sort(key=lambda x: x['total_words'], reverse=True)
                        context['user_report'] = {
                            'username': 'all',
                            'all_users_stats': user_report
                        }
                    else:
                        # Individual user report
                        user_logs = list(db.playerLogs.find({"username": username}))
                        
                        user_stats = {}
                        for log in user_logs:
                            date = log['date']
                            if date not in user_stats:
                                user_stats[date] = {
                                    'words_tried': 0,
                                    'correct_guesses': 0
                                }
                            
                            user_stats[date]['words_tried'] += 1
                            if log['guessedword'] == log['actualword']:
                                user_stats[date]['correct_guesses'] += 1
                        
                        user_report = []
                        for date, stats in user_stats.items():
                            user_report.append({
                                'date': date,
                                'words_tried': stats['words_tried'],
                                'correct_guesses': stats['correct_guesses']
                            })
                        
                        user_report.sort(key=lambda x: x['date'], reverse=True)
                        context['user_report'] = {
                            'username': username,
                            'daily_stats': user_report
                        }
        
        all_users = sorted(list(set(u['username'] for u in db.players.find({}, {'username': 1}))))
        context['all_users'] = all_users
        
        return render(request, 'adminUser/report.html', context)
        
    except Exception as e:
        print(f"Error in admin report view: {str(e)}")
        return render(request, 'adminUser/report.html', {
            'error_message': 'An error occurred while generating the report.'
        })

@login_required
def signout(request):
    request.session.flush()
    return redirect('home')