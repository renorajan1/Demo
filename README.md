## Library Management System API

This repository contains the code for a Django REST Framework API for managing a library's books, authors, and borrowing records.

### Installation

1. Create a virtual environment: `python -m venv env`
2. Activate the environment: `source env/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `python manage.py makemigrations` and `python manage.py migrate`

### Running the API

1. Start the development server: `python manage.py runserver`
2. Start the Celery worker: `celery -A your_project_name worker -l info`

### API Documentation

#