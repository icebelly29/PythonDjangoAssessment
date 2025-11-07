# Django Assessment Project

This project contains two separate tasks demonstrating Django REST Framework API development and custom middleware implementation.

## Tasks

## [Task 1: CSV Upload API](README_TASK1.md)
Django REST Framework API endpoint that processes user data from CSV files with validation, error handling, and database integration.

**[Read Task 1 Documentation](README_TASK1.md)**

## [Task 2: Rate Limiting Middleware](README_TASK2.md)
Custom Django middleware implementing IP-based rate limiting with a rolling 5-minute window.


**[Read Task 2 Documentation](README_TASK2.md)**

## Quick Start

1. **Create and activate virtual environment (Windows):**
```bash
py -m venv .venv
.venv\Scripts\activate
```
2. **Install dependencies:**
```bash
pip install -r requirements.txt
```
3. **Apply migrations:**
```bash
python manage.py migrate
```
4. **Run testing:**
```bash
python manage.py test
``
5. **Start the server:**
```bash
python manage.py runserver
```

6. **Access the application:**
- Homepage: http://127.0.0.1:8000/
- API Endpoint: http://127.0.0.1:8000/api/upload-csv/


##  Documentation

- **Task 1**: [README_TASK1.md](README_TASK1.md) 
- **Task 2**: [README_TASK2.md](README_TASK2.md)

##  Testing

Run all tests:
```bash
python manage.py test
```

Run specific task tests:
```bash
# Task 1 tests
python manage.py test users.tests

# Task 2 tests
python manage.py test users.tests_rate_limit
```

## 📝 Notes

- Tasks are **completely separate** - each can be understood and tested independently
- The middleware (Task 2) applies globally to all requests
- Both tasks include comprehensive unit tests
- Sample files are provided in the `samples/` directory
