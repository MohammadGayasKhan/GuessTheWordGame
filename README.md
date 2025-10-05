# Word Guesser Game

A modern web-based word guessing game built with Django, featuring separate interfaces for players and administrators.

## Features

### Player Features
- Interactive word guessing gameplay
- User registration and authentication

### Admin Features 
- Game statistics and reports
- Number of user played on any date
- Number of times a player had guessed the words
- Number of correct words guessed by the user

## Technology Stack

- **Backend**: Django 4.x
- **Frontend**: HTML5, Bootstrap 5.3.8
- **Database**: MongoDB
- **Icons**: Bootstrap Icons 1.11.1

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/MohammadGayasKhan/GuessTheWordGame.git
cd GuessTheWordGame
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Unix/macOS
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply database migrations:
```bash
cd WordGuesser
python manage.py migrate
```

5. Create a superuser (admin):
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Access the application:
- Main game: http://localhost:8000
- Admin interface: http://localhost:8000/admin

## Key Structure of Project

```
WordGuesser/
├── adminUser/           # Admin interface app
│   ├── templates/      # Admin-specific templates
│   └── views.py        # Admin view logic
├── playerUser/         # Player interface app
│   ├── static/        # Static files (images, etc.)
│   ├── templates/     # Player-specific templates
│   └── views.py       # Player view logic
└── WordGuesser/       # Main project settings
    ├── settings.py    # Project settings
    └── urls.py        # Main URL configuration
```

## Playing the Game

1. Register a new account or login
2. Start a new game from the home page
3. Try to guess the word by entering letters
4. Get feedback on your guesses with color-coded responses:
   - Green: Correct letter in correct position
   - Yellow: Correct letter in wrong position
   - Gray: Letter not in word


## Author
Mohammad Gayas Khan
