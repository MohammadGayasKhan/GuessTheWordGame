from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from functools import wraps
import re
from datetime import datetime
from .models import db
import uuid

def login_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        username = request.session.get('username')
        if not username:
            return redirect('playerUser:login')
        return view_func(request, *args, **kwargs)
    return wrapped


# Create your views here.

words = ["APPLE", "BREAD", "CHAIR", "TABLE", "WATER", "HOUSE", "PLANT", "MUSIC", "LIGHT", "TRAIN", "SMILE", "CLOUD", "RIVER", "STONE", "BRAIN", "HEART", "SUGAR", "DREAM", "GRASS", "PAPER"]


rules = [
        'When the game starts, submit a <span class="text-uppercase fw-bold">5-letter word</span> (uppercase only). You have <span class="fw-bold">5 guesses</span> maximum.',
        '<span class="badge bg-success">Green</span> = Letter is correct and in the right position.<br><span class="badge" style="background-color: #e36110; color: white;">Orange</span> = Letter is correct but in the wrong position.<br><span class="badge bg-secondary">Grey</span> = Letter is not in the word.',
        'If you guess the word correctly, <span class="text-success fw-bold">you win!</span> A congratulatory message will appear. Click OK to stop the game.',
        'If you use all 5 guesses and don\'t guess the word, <span class="text-danger fw-bold">better luck next time!</span> Click OK to stop the game.',
        'If your guess is incorrect, you can try again. Previous guesses are shown in order.'
    ]

@login_required
def home(request):
    return render(request, 'playerUser/home.html',{'rules':rules})

@csrf_protect
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password: 
            player = db.players.find_one({"username": username, "password": password})
            if player:
                request.session['username'] = username
                return redirect('playerUser:home')
            else:
                return render(request, 'playerUser/login.html', {'error_message': 'Invalid username or password'})
    return render(request, 'playerUser/login.html')

@csrf_protect
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password: 
            is_valid_username, username_error = validate_username(username)
            if not is_valid_username:
                return render(request, 'playerUser/register.html', {'error_message': username_error})
 
            is_valid_password, password_error = validate_password(password)
            if not is_valid_password:
                return render(request, 'playerUser/register.html', {'error_message': password_error})

            existing_user = db.players.find_one({"username": username})
            if existing_user:
                return render(request, 'playerUser/register.html', {'error_message': 'Username already exists'})
            
            
            db.players.insert_one({
                "username": username,
                "password": password
            })
            request.session['username'] = username
            return redirect('playerUser:home')
    return render(request, 'playerUser/register.html')

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
@csrf_protect
def game(request):
    if 'game_id' not in request.session:
        request.session['game_id'] = str(uuid.uuid4().hex)
    if 'attemptsLeft' not in request.session:
        request.session['attemptsLeft'] = 5
        request.session['guesses'] = []
        request.session['lost'] = False
        request.session['won'] = False
    if 'target' not in request.session:
        request.session['target'] = next(db.words.aggregate([{ "$sample": { "size": 1 } }]))['word']
        print("Target word is:", request.session['target'])
    if request.session['attemptsLeft'] <= 0:
        request.session['lost'] = True

    grid = []
    guesses = request.session.get('guesses', [])
    for guess in guesses:
        row = []
        for i, char in enumerate(guess):
            if char == request.session['target'][i]:
                status = 'correct'
            elif char in request.session['target']:
                status = 'wrong_position'
            else:
                status = 'incorrect'
            row.append({'char': char, 'status': status})
        grid.append(row)
    
    choices_left = 5 - len(guesses)   

    if request.method == 'POST' and not request.session['lost']:
        guess = request.POST.get('guessInput', '').upper()
        if guess and len(guess) == 5:
            if guess not in request.session['guesses']:   
                current_time = datetime.now()
                
                db.playerLogs.insert_one({
                    "username": request.session['username'],
                    "date": current_time.strftime("%Y-%m-%d"),
                    "datetime": current_time,
                    "guessedword": guess,
                    "actualword": request.session['target'],
                    "gameid": request.session['game_id'],
                })
                
                request.session['guesses'].append(guess)
                request.session['attemptsLeft'] -= 1
                
                if request.session['attemptsLeft'] <= 0:
                    request.session['lost'] = True
                
                request.session.modified = True  

                row = []
                for i, char in enumerate(guess):
                    if char == request.session['target'][i]:
                        status = 'correct'
                    elif char in request.session['target']:
                        status = 'wrong_position'
                    else:
                        status = 'incorrect'
                    row.append({'char': char, 'status': status})
                grid.append(row)
            
            if guess == request.session['target']:
                request.session['won'] = True

    context = {
        'grid': grid,
        'attemptsLeft': request.session['attemptsLeft'],
        'won': request.session.get('won', False),
        'lost': request.session.get('lost', False),
        'error_message': request.session.get('error_message', None),
        'guesses': request.session.get('guesses', []),
        'choicesLeft': range(choices_left),
        'choicesLeft': '1'*request.session['attemptsLeft']
    }
    
    return render(request, 'playerUser/game.html', context)
    
@login_required
def restart(request):
    current_date = datetime.now().strftime("%Y-%m-%d")
    username = request.session.get('username')
    
    games = db.playerLogs.distinct(
        "gameid",
        {"username": username, "date": current_date}
    )
    game_count = len(games)
    print("Game count for user", username, "on", current_date, "is", game_count)
    
    if game_count >= 3:
        request.session['error_message'] = "You have reached the maximum of 3 games for today. Please try again tomorrow."
        return redirect('playerUser:game')

    game_vars = ['attemptsLeft', 'guesses', 'lost', 'won', 'target', 'gameid']
    for var in game_vars:
        if var in request.session:
            del request.session[var]
    request.session.modified = True
    request.session['game_id'] = str(uuid.uuid4().hex)
    return redirect('playerUser:game')

@login_required
def signout(request):
    request.session.flush()
    return redirect('home')