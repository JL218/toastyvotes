# ToastyVotes

A beautiful white and orange themed voting application built with Django.

## Features

- User registration and authentication
- Admin-controlled voting sessions
- Vote for speakers, evaluators, and table topics masters
- Temporary voting links that last 24 hours
- Secure vote counting and result display
- Mobile-friendly responsive design

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Configure environment variables (see .env.example)
5. Run migrations:
   ```
   python manage.py migrate
   ```
6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```
7. Run the development server:
   ```
   python manage.py runserver
   ```

## Deployment

This project is configured for deployment on Hostwinds.

## License

[MIT](LICENSE)
