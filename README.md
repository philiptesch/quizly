# 📘 Quiz API – README

## Project Structure

This project is organized as follows:

```
quiz_project/
├─ core/                  # Core Django settings
│  ├─ settings.py         # Django settings and configurations
│  ├─ urls.py             # Project-wide URLs
│  └─ wsgi.py / asgi.py   # WSGI/ASGI application entry points
│
├─ quiz_app/              # Main quiz functionality
│  ├─ api/                # API module for quizzes
│  │  ├─ views.py         # Quiz API views
│  │  ├─ serializers.py   # Quiz and Question serializers
│  │  ├─ urls.py          # Quiz app URLs
│  │  ├─ permissions.py   # Custom permissions (e.g., owner check)
│  │  └─ helpers.py       # Functions for YouTube download & transcription
│  └─ models.py           # Quiz and Question models
│
├─ auth_app/              # User authentication functionality
│  ├─ api/                # API module for auth
│  │  ├─ views.py         # Registration, Login, Logout, Token refresh
│  │  ├─ serializers.py   # Auth serializers
│  │  └─ urls.py          # Auth app URLs
│  └─ models.py           # Optional custom user models (if any)
│
├─ manage.py             # Django management commands
└─ requirements.txt      # Project dependencies
```

> **Note:** The `.env` file should be placed at the project root (`quiz_project/.env`). It will be automatically loaded by `python-dotenv` in `core/settings.py`.

## Overview

The **Quiz API** allows users to:

* Register and login using **cookie-based authentication** (HttpOnly cookies)
* Automatically generate quizzes from **YouTube URLs**
* Perform full **CRUD operations** on quizzes
* Restrict access so only **quiz owners** can edit or delete their quizzes

Authentication is handled with **access_token** and **refresh_token** stored as HttpOnly cookies.

---

## Authentication

| Token           | Description                       |
| --------------- | --------------------------------- |
| `access_token`  | JWT used to authenticate requests |
| `refresh_token` | Used to refresh the access token  |

---

## Requirements & Setup

### Prerequisites

* Python 3.10+
* pip (Python package manager)
* virtualenv (recommended)

### Installation

1. Clone the repository:

```bash
git clone <repository_url>
cd <repository_folder>
```

2. Create and activate a virtual environment:

**Windows (PowerShell):**

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
```

**Windows (CMD):**

```cmd
python -m venv env
env\Scripts\activate.bat
```

**macOS / Linux:**

```bash
python3 -m venv env
source env/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

4. Generate Secret Key

Run the following command in your terminal:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

You will get a key like:

```bash
django-insecure-4x9v$k2l^8p@1m!zq7e+3r#t6y%u0w
```


### 1.  🌱 Environment Variables

This project uses a **`.env` file** to store sensitive configuration values such as API keys (Gemini, Whisper, etc.).

#### 1. Create a `.env` file


create it manually:

```bash
touch .env
```

#### 2. Add your API keys and settings

Example `.env` content:

```env
GEMINI_API_KEY=your_api_key_here
WHISPER_API_KEY=your_api_key_here
DJANGO_SECRET_KEY=your_django_secret_key
```

> **Note:** Never commit your `.env` file to version control.

#### 3. Automatic loading with `python-dotenv`

All variables from `.env` are loaded automatically in Django using **`python-dotenv`**:

```python
import os
from dotenv import load_dotenv

load_dotenv()  # loads .env variables

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
```

#### 4. Run Migrations

Once your .env file is ready, run the migrations to initialize the database: 


```bash
python manage.py migrate
```
After this, your Django project is ready to run:

```bash
python manage.py runserver
```

#### 5. Create a superuser

```bash
python manage.py createsuperuser
````

---

## Key Technologies / Libraries

* **Django 5.2.8** – Web framework
* **djangorestframework 3.16.1** – REST API support
* **djangorestframework_simplejwt 5.5.1** – JWT authentication
* **django-blacklist 0.7.0** – Refresh token blacklisting
* **python-dotenv 1.2.1** – Load environment variables
* **yt-dlp 2025.12.8** – YouTube video download
* **openai-whisper 20250625** – Audio transcription
* **google-genai 1.60.0** – Gemini API client
* **django-cors-headers 4.9.0** – CORS support
* **NumPy, Torch, SymPy, NetworkX** – Data processing and AI support

---

## Running the Project

1. Apply migrations:

```bash
python manage.py migrate
```

2. Start the development server:

```bash
python manage.py runserver
```

API will be available at:
`http://127.0.0.1:8000/`

---

## Endpoints

### Auth Endpoints

#### **POST /api/register/**

Register a new user.

**Request Body:**

```json
{
  "username": "your_username",
  "password": "your_password",
  "confirmed_password": "your_confirmed_password",
  "email": "your_email@example.com"
}
```

**Status Codes:**

* 201 – User created successfully
* 400 – Invalid data
* 500 – Internal server error

---

#### **POST /api/login/**

Login a user and set auth cookies.

**Request Body:**

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Status Codes:**

* 200 – Login successful
* 401 – Invalid credentials
* 500 – Internal server error

---

#### **POST /api/logout/**

Logout a user and invalidate tokens.

**Request Body:** `{}`

**Status Codes:**

* 200 – Logout successful
* 401 – Not authenticated
* 500 – Internal server error

---

#### **POST /api/token/refresh/**

Refresh access token using refresh token.

**Request Body:** `{}`

**Status Codes:**

* 200 – Token refreshed successfully
* 401 – Refresh token invalid or missing
* 500 – Internal server error

---

### Quiz Endpoints

#### **POST /api/createQuiz/**

Create a quiz from a YouTube URL.

**Request Body:**

```json
{
  "url": "https://www.youtube.com/watch?v=example"
}
```

**Status Codes:**

* 201 – Quiz created successfully
* 400 – Invalid URL or data
* 401 – Not authenticated
* 500 – Internal server error

---

#### **GET /api/quizzes/**

Get all quizzes for the authenticated user.

**Status Codes:**

* 200 – Success
* 401 – Not authenticated
* 500 – Internal server error

---

#### **GET /api/quizzes/{id}/**

Get a specific quiz by ID.

**Status Codes:**

* 200 – Success
* 401 – Not authenticated
* 403 – Access denied
* 404 – Quiz not found
* 500 – Internal server error

---

#### **PATCH /api/quizzes/{id}/**

Update a quiz partially.

**Request Body Example:**

```json
{
  "title": "New Quiz Title"
}
```

**Status Codes:**

* 200 – Updated successfully
* 400 – Invalid data
* 401 – Not authenticated
* 403 – Access denied
* 404 – Quiz not found
* 500 – Internal server error

---

#### **DELETE /api/quizzes/{id}/**

Delete a quiz permanently.

**Status Codes:**

* 204 – Successfully deleted
* 401 – Not authenticated
* 403 – Access denied
* 404 – Quiz not found
* 500 – Internal server error

---

### Error Codes

| Code | Meaning               |
| ---- | --------------------- |
| 200  | Success               |
| 201  | Resource created      |
| 204  | Successfully deleted  |
| 400  | Invalid data          |
| 401  | Not authenticated     |
| 403  | Access denied         |
| 404  | Not found             |
| 500  | Internal server error |

---

---

## 🤝 Contributing
Contributions are welcome!  
If you'd like to improve this project, open an issue or submit a pull request.


## 🤝 Contributing
Contributions are welcome!  
If you'd like to improve this project, open an issue or submit a pull request.

---

## 📄 License
MIT License © philiptesch 

