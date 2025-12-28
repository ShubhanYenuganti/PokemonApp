# Pokemon Finder Frontend

React frontend for the Pokemon Finder application.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The frontend will run at http://localhost:3000

## Features

- User Registration
- User Login
- User Logout
- Protected Landing Page

## Backend Integration

Make sure the Django backend is running at http://localhost:8000 before starting the frontend.

To start the backend:
```bash
cd ../backend
python manage.py runserver
# or
daphne pokemon_api.asgi:application
```
