# Setup Guide for PokemonApp

## Quick Start (First Time Setup)

### Step 1: Clone Your Fork

If you haven't already, clone your forked repository:

```bash
git clone <your-forked-repo-url>
cd PokemonApp
```

### Step 2: Create Environment Variables File

Create a `.env` file in the project root directory (same directory as `docker-compose.yml`) with the following content:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,backend
# Get your free API key from: https://openweathermap.org/api
OPENWEATHER_API_KEY=your-openweather-api-key-here
```

### Step 3: Start the Application

From the project root directory (where `docker-compose.yml` is located), run:

```bash
docker-compose up --build
```

### Step 4: Access the Application

Once the containers are running, you should see logs indicating the services are ready. Open your browser:

- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000](http://localhost:8000)

The frontend should automatically connect to the backend API.

### Step 5: Initialize the Database (First Run Only)

On the first run, you need to set up the database. In a new terminal window, run:

```bash
docker-compose exec backend python manage.py migrate
```

This creates the database tables needed for the application.

### Step 6: Create a Superuser (Optional)

To access the Django admin panel, you can create a superuser account:

```bash
docker-compose exec backend python manage.py createsuperuser
```

Follow the prompts to enter a username, email (optional), and password. Once created, you can access the admin panel at [http://localhost:8000/admin](http://localhost:8000/admin).
