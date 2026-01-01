# Docker Setup Guide

This project is fully containerized with Docker. It uses a multi-container architecture to handle the web server, database, task queue, and external tunneling.

## System Architecture

* **Django (Server):** The core Python application.
* **PostgreSQL (DB):** Persistent relational database.
* **Redis:** Result backend and caching.
* **RabbitMQ:** Message broker for asynchronous tasks.
* **Celery Worker/Beat:** Handles background processing and scheduled tasks.
* **Ngrok:** Tunnels your local server to a public URL (essential for Chapa Webhooks).

---

## Getting Started (Development)

The development environment is optimized for **speed** and **debugging** with hot-reloading enabled.

### 1. Prerequisites

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed.
* An [Ngrok Auth Token](https://dashboard.ngrok.com/get-started/your-authtoken).
* Chapa API Keys (Test mode).

### 2. Configuration

Copy the example environment file and fill in your keys:

```bash
cp .env.example .env

```

> **Note:** Ensure `POSTGRES_HOST=db`, `REDIS_URL=redis://redis:6379/0`, and `CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//` are set correctly in your `.env`.

### 3. Launch the Stack

Run the following command to build and start all services:

```bash
docker compose up --build

```

### 4. Useful Local URLs

| Service | URL | Port |
| --- | --- | --- |
| **Django App** | [http://localhost:8000](http://localhost:8000) | 8000 |
| **RabbitMQ UI** | [http://localhost:15672](http://localhost:15672) | 15672 (guest/guest) |
| **Ngrok Status** | [http://localhost:4040](http://localhost:4040) | 4040 |

---

## Setting Up Chapa Webhooks

Since this project uses Chapa for payments, you need a public URL for webhooks to reach your local machine.

1. Start the containers.
2. Open the **Ngrok Status** page at `http://localhost:4040`.
3. Copy the `https://...` URL provided.
4. Update your `.env` file: `BACKEND_URL=https://your-unique-id.ngrok-free.dev`.
5. Restart the server: `docker compose restart server`.

---

## Commands Table

| Task | Command |
| --- | --- |
| **View Logs** | `docker compose logs -f` |
| **Create Migrations** | `docker compose exec server python manage.py makemigrations` |
| **Apply Migrations** | `docker compose exec server python manage.py migrate` |
| **Create Superuser** | `docker compose exec server python manage.py createsuperuser` |
| **Stop & Remove All** | `docker compose down -v` (The `-v` deletes the DB data!) |

