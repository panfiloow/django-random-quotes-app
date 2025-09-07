# Random Quotes Django Application

A web application that displays random quotes from movies and books with interactive features like liking and disliking quotes.

## ✨ Features

- **🎲 Random Quote Generator**: Get a random weighted quote on each page load
- **❤️ Like/Dislike System**: Users can rate quotes (stored in session)
- **➕ Add New Quotes**: Form to add new quotes with sources
- **📊 Popular Quotes**: Top 10 most liked quotes page
- **⚖️ Weight System**: Quotes with higher weight appear more frequently
- **🎯 Source Limits**: Maximum 3 quotes per source
- **🔄 Next Quote Button**: AJAX-powered button to get new quotes without page reload
  
## 🛠️ Technologies Used

- **Backend**: Django 5.2.6
- **Database**: SQLite3
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Session-based (no login required)


## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- pip package manager

### 1. Clone the Repository
```bash
git clone https://github.com/panfiloow/django-random-quotes-app.git
cd django-random-quotes-app
  ```
### 2. Create Virtual Environment
  ```
  python -m venv venv
  ```
### 3. Activate Virtual Environment
   
  Windows:
  ```
  venv\Scripts\activate
  ```
  Mac/Linux:
  ```
  source venv/bin/activate
  ```

### 4. Install Dependencies
  ``` 
  pip install -r requirements.txt
  ```  

### 6. Set Up Environment Variables

  Create a .env file in the project root:
  
  Copy the example environment file
  ```
  cp .env.example .env
  ```

  Edit .env with your settings:
  ```
  SECRET_KEY=your-super-secret-key-here

  DEBUG=True
  ```
### 6. Apply Migrations

  ```
  python manage.py migrate
  ```
### 8. Create Superuser (Optional)
  ``` 
  python manage.py createsuperuser
  ```

### 10. Run Development Server
  ```  
  python manage.py runserver
  ```

  Visit http://127.0.0.1:8000/ in your browser.

# Project Structure

jango-random-quotes-app/

quote_project/ - Project settings

settings.py - Configuration

urls.py - Main URLs

wsgi.py - WSGI config

asgi.py - ASGI config

__init__.py

quotes/ - Main application

models.py - Database models

views.py - Application logic

urls.py - App URLs

forms.py - Django forms

admin.py - Admin configuration

apps.py - App config

tests.py - Tests

__init__.py

migrations/ - Database migrations

__init__.py

*.py (migration files)

templates/quotes/ - HTML templates

random_quote.html

add_quote.html

popular_quotes.html

Root files

manage.py - Django management script

requirements.txt - Python dependencies

.gitignore - Git ignore rules

.env.example - Environment variables template

README.md - Documentation


# Environment Configuration

For production deployment, make sure to:

### 1. Set a proper SECRET_KEY:

python

Generate a new secret key: 
  ```
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
### 2. Set DEBUG=False in production

### 3. Use environment variables:
   ```  
import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-key-for-development-only')

DEBUG = os.environ.get('DEBUG', 'False') == 'True'
  ```

# Usage

View Random Quote: Visit the homepage to see a random quote

Like/Dislike: Click thumbs up/down to rate quotes (once per quote)

Add Quote: Use "Add Quote" link to submit new quotes

View Popular: See top liked quotes on the popular page

# API Endpoints

GET / - Random quote page

GET /next/ - Get next random quote (AJAX)

POST /like/<id>/ - Like a quote

POST /dislike/<id>/ - Dislike a quote

GET /add/ - Add quote form

GET /popular/ - Popular quotes page

# Contributing

Fork the repository

Create a feature branch: git checkout -b feature-name

Commit changes: git commit -am 'Add feature'

Push to branch: git push origin feature-name

Submit a pull request

# License

This project is open source and available under the MIT License.

# Deployment

For production deployment, consider:

Using PostgreSQL instead of SQLite

Setting up a proper WSGI server (Gunicorn + Nginx)

Using environment variables for configuration

Setting up proper static file serving

Implementing proper security headers

