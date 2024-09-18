# Backend Setup for Voters Management System

This guide outlines the steps to set up and run the backend server for the Voters Management System. The backend is built using Python and Django, with PostgreSQL as the database.

## Prerequisites

Before you begin, ensure you have the following installed:

- [Python 3.12](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/)

## Setting Up PostgreSQL

1. **Install PostgreSQL**:
   - Follow the official instructions for your operating system to install PostgreSQL.
2. **Open PostgreSQL Terminal**:
   Open a terminal and access PostgreSQL by running:

   ```bash
   psql postgres
   ```

3. **Create a PostgreSQL User**:
   In the PostgreSQL terminal, create a user `root` with the following command:

   ```sql
   CREATE USER root WITH PASSWORD 'password';
   ```

4. **Create a PostgreSQL Database**:
   Create a new database named `voters`:

   ```sql
   CREATE DATABASE voters;
   ```

5. **Grant Privileges**:
   Grant all privileges on the `voters` database to the `root` user:

   ```sql
   GRANT ALL PRIVILEGES ON DATABASE voters TO root;
   ```

## Setting Up the Django Backend

1. **Clone the Repository**:
   Clone this repository to your local machine:

   ```bash
   git clone https://github.com/oyerohabib/backend-test.git
   cd backend-test
   ```

2. **Create and Activate a Virtual Environment**:
   Set up a Python virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Database**:
   Open the `settings.py` file and configure your database settings as follows:

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'voters',
           'USER': 'root',
           'PASSWORD': 'password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

5. **Run Migrations**:
   Apply the database migrations:

   ```bash
   python manage.py migrate
   ```

6. **Run the Setup Script**:
   This script will perform any necessary initial setup for your application:

   ```bash
   python manage.py app_setup
   ```

7. **Start the Server**:
   Run the Django development server:

   ```bash
   python manage.py runserver
   ```

## API Endpoints

Below are some key API endpoints developed for this system:

- **POST** `/api/v1/auth/login/`: Login with email and password.
- **POST** `/api/v1/auth/token/refresh/`: Refresh JSON web token.
- **POST** `/api/v1/auth/token/verify/`: Verify the validity of a token.
- **POST** `/api/v1/auth/users/upload-users/`: Upload and process user data from a CSV file.
