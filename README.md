# Flash-Sale Reservations

Minimal backend service for temporary product reservation during flash sales.

Stack: FastAPI, PostgreSQL, Alembic, Redis, Docker Compose, pytest.

The service allows a user to hold one unit of a product for a limited time, then confirm or cancel the reservation.
Expired reservations are released automatically via a synchronization endpoint.



## Requirements

Docker, Docker Compose

No local Python installation is required when using Docker.

## Quick start
1. Clone repository:
```yaml
git clone https://github.com/ZLHRS/Flash-Sale-Reservations.git
```

2. Start services:
```yaml
docker compose up --build -d
```

Application will be available at:

http://localhost:8000/docs

## Running tests (terminal)
```yaml
docker compose run --rm test
```