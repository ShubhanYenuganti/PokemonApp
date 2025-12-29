# Docker Deployment Guide for PokemonFinder

## Prerequisites

- Docker Desktop installed on your machine
- Docker Compose (usually comes with Docker Desktop)

## Quick Start

### 1. Build and Run with Docker Compose

From the project root directory, run:

```bash
docker-compose up --build
```

This will:
- Build the backend Django application
- Build the frontend React application
- Start both services
- Backend will be available at `http://localhost:8000`
- Frontend will be available at `http://localhost:3000`

### 2. Run in Detached Mode (Background)

```bash
docker-compose up -d --build
```

### 3. View Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### 4. Stop Services

```bash
docker-compose down
```

### 5. Stop and Remove Volumes (Clean Database)

```bash
docker-compose down -v
```

## Individual Service Commands

### Backend Only

```bash
# Build
docker build -t pokemon-backend ./backend

# Run
docker run -p 8000:8000 pokemon-backend
```

### Frontend Only

```bash
# Build
docker build -t pokemon-frontend ./frontend

# Run
docker run -p 3000:80 pokemon-frontend
```

## Running Django Management Commands

### Inside Running Container

```bash
# Access the backend container shell
docker-compose exec backend bash

# Then run any Django command
python manage.py createsuperuser
python manage.py migrate
python manage.py collectstatic
```

### One-off Command

```bash
# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Run migrations
docker-compose exec backend python manage.py migrate

# List endpoints
docker-compose exec backend python manage.py list_endpoints
```

## Production Considerations

### 1. Update Backend Settings

Before deploying to production, update [backend/pokemon_api/settings.py](backend/pokemon_api/settings.py):

- Set `DEBUG = False`
- Update `SECRET_KEY` with a secure random key
- Update `ALLOWED_HOSTS` with your domain
- Consider using PostgreSQL instead of SQLite
- Update CORS settings for your production domain

### 2. Environment Variables

Create a `.env` file:

```env
DEBUG=False
SECRET_KEY=your-very-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

Update [docker-compose.yml](docker-compose.yml) to use env file:

```yaml
services:
  backend:
    env_file:
      - .env
```

### 3. Use PostgreSQL (Recommended for Production)

Update [docker-compose.yml](docker-compose.yml):

```yaml
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: pokemondb
      POSTGRES_USER: pokemon
      POSTGRES_PASSWORD: changeme
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - pokemon-network

  backend:
    depends_on:
      - db
    environment:
      - DB_ENGINE=django.db.backends.postgresql
      - DB_NAME=pokemondb
      - DB_USER=pokemon
      - DB_PASSWORD=changeme
      - DB_HOST=db
      - DB_PORT=5432

volumes:
  postgres_data:
```

Update requirements.txt:
```
psycopg2-binary>=2.9.0
```

### 4. Redis for Channels (Production WebSockets)

Add to [docker-compose.yml](docker-compose.yml):

```yaml
services:
  redis:
    image: redis:7-alpine
    networks:
      - pokemon-network
```

Update Django settings to use Redis for channel layers.

## Troubleshooting

### Port Already in Use

If ports 8000 or 3000 are already in use, update the port mappings in [docker-compose.yml](docker-compose.yml):

```yaml
ports:
  - "8001:8000"  # Backend on 8001
  - "3001:80"    # Frontend on 3001
```

### Database Migration Issues

```bash
# Reset the database
docker-compose down -v
docker-compose up --build
```

### Frontend Can't Connect to Backend

Update [frontend/src/services/api.js](frontend/src/services/api.js) to use the correct backend URL.

For Docker development, the frontend should connect to `http://localhost:8000`.

## Health Checks

Check if services are running:

```bash
# List running containers
docker-compose ps

# Check backend health
curl http://localhost:8000/api/

# Check frontend
curl http://localhost:3000
```

## Cleaning Up

```bash
# Remove all containers and volumes
docker-compose down -v

# Remove all unused Docker resources
docker system prune -a --volumes
```
