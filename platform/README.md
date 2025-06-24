# Platform Infrastructure

This directory contains Docker Compose configuration for running the GAP Quote Service infrastructure.

## Quick Start

1. Start PostgreSQL database:
```bash
cd platform
docker-compose up -d postgres
```

2. Start with pgAdmin (optional):
```bash
docker-compose up -d
```

3. Set environment variable for your application:
```bash
export DATABASE_URL="postgresql+asyncpg://gap_user:gap_password@localhost:5432/gap_quotes"
```

4. Run your application from the project root:
```bash
cd ..
python run.py
```

## Services

### PostgreSQL Database
- **Container:** `gap_quotes_db`
- **Port:** `5432`
- **Database:** `gap_quotes`
- **User:** `gap_user`
- **Password:** `gap_password`
- **Data Volume:** `postgres_data` (persistent)

### pgAdmin (Optional)
- **Container:** `gap_quotes_pgadmin`
- **Port:** `8080`
- **URL:** http://localhost:8080
- **Email:** `admin@example.com`
- **Password:** `admin`

## Commands

### Start all services:
```bash
docker-compose up -d
```

### Start only PostgreSQL:
```bash
docker-compose up -d postgres
```

### Stop all services:
```bash
docker-compose down
```

### Stop and remove volumes (⚠️ deletes data):
```bash
docker-compose down -v
```

### View logs:
```bash
docker-compose logs postgres
docker-compose logs pgadmin
```

### Access PostgreSQL directly:
```bash
docker-compose exec postgres psql -U gap_user -d gap_quotes
```

## Configuration

### Environment Variables
Copy `.env.example` to `.env` and modify as needed:
```bash
cp .env.example .env
```

### Database Connection
The application should use this connection string:
```
postgresql+asyncpg://gap_user:gap_password@localhost:5432/gap_quotes
```

## Data Persistence

PostgreSQL data is stored in a Docker volume `postgres_data` which persists between container restarts. To completely reset the database, run:
```bash
docker-compose down -v
docker-compose up -d
```

## Connecting from pgAdmin

If using pgAdmin, add a new server with these settings:
- **Host:** `postgres` (container name)
- **Port:** `5432`
- **Database:** `gap_quotes`
- **Username:** `gap_user`
- **Password:** `gap_password`