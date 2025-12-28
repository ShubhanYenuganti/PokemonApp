# Pokemon Finder Backend

Django REST Framework backend with WebSocket support for the Pokemon Finder application.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Initial Setup

### 1. Navigate to the backend directory

```bash
cd backend
```

### 2. Create a virtual environment (recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run database migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a superuser (optional, for admin access)

```bash
python manage.py createsuperuser
```

Follow the prompts to set up your admin account.

### 6. Collect static files (if needed)

```bash
python manage.py collectstatic --noinput
```

## Running the Development Server

### Option 1: Using Django's development server (HTTP only)

For basic REST API testing without WebSocket support:

```bash
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`

### Option 2: Using Daphne (Recommended - supports WebSockets)

Since this project uses Django Channels for WebSocket support, use Daphne for full functionality:

```bash
daphne -b 127.0.0.1 -p 8000 pokemon_api.asgi:application
```

Or simply:

```bash
daphne pokemon_api.asgi:application
```

This will start the server at `http://127.0.0.1:8000/` with both HTTP and WebSocket support.

## API Endpoints

Once the server is running, you can access:

- **Admin Panel**: `http://127.0.0.1:8000/admin/`
- **API Root**: `http://127.0.0.1:8000/api/`
- **Pokemon API**: `http://127.0.0.1:8000/api/pokemon/`
- **Users API**: `http://127.0.0.1:8000/api/users/`
- **Authentication**: `http://127.0.0.1:8000/api/auth/`

Note: The API requires authentication by default (Token or Session authentication).

## Testing

### Running Tests

Django's test framework can discover and run tests automatically. To run all tests:

```bash
python manage.py test
```

To run tests for a specific app:

```bash
# Test Pokemon app
python manage.py test apps.pokemon

# Test Users app
python manage.py test apps.users
```

To run a specific test class or test method:

```bash
# Run specific test class
python manage.py test apps.pokemon.tests.TestClassName

# Run specific test method
python manage.py test apps.pokemon.tests.TestClassName.test_method_name
```

### Creating Tests

To create tests for your application, create a `tests.py` file in the respective app directory (e.g., `apps/pokemon/tests.py`). Example test structure:

```python
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from apps.pokemon.models import Pokemon

class PokemonTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_create_pokemon(self):
        """Test creating a Pokemon"""
        data = {
            'name': 'Pikachu',
            'latitude': 37.7749,
            'longitude': -122.4194,
            'type_primary': 'Electric',
            'sprite': 'https://example.com/pikachu.png',
            'source': 'API'
        }
        response = self.client.post('/api/pokemon/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
```

### Running Tests with Verbosity

For more detailed output:

```bash
python manage.py test --verbosity=2
```

### Test Coverage (Optional)

To check test coverage, install coverage.py:

```bash
pip install coverage
```

Then run:

```bash
coverage run --source='.' manage.py test
coverage report
coverage html  # Generates HTML report
```

## Environment Variables

You can customize the following environment variables:

- `SECRET_KEY`: Django secret key (defaults to development key if not set)
- `DEBUG`: Set to `'True'` or `'False'` (defaults to `'True'`)

Example:

```bash
export SECRET_KEY='your-secret-key-here'
export DEBUG='False'
python manage.py runserver
```

## Database

By default, the project uses SQLite (`db.sqlite3` in the backend directory). The database file will be created automatically when you run migrations.

To reset the database:

```bash
rm db.sqlite3
python manage.py migrate
```

## Troubleshooting

### Import Errors

If you encounter import errors, make sure:
1. Your virtual environment is activated
2. All dependencies are installed (`pip install -r requirements.txt`)
3. You're in the backend directory when running commands

### Port Already in Use

If port 8000 is already in use, specify a different port:

```bash
python manage.py runserver 8001
# or
daphne -b 127.0.0.1 -p 8001 pokemon_api.asgi:application
```

### Migration Issues

If you have migration conflicts:

```bash
# Show migration status
python manage.py showmigrations

# Create migrations for all apps
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

