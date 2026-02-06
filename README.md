# DRF Commerce Engine

A robust, scalable E-Commerce backend API built with Python, Django, and Django REST Framework. This project provides a complete solution for managing an online store, including product management, shopping carts, orders, payments, user authentication, and inventory control.

## 🚀 Features

-   **User Authentication & Accounts**:
    -   Secure registration and login using JWT (JSON Web Tokens).
    -   Email verification and password reset flows.
    -   Custom user model supporting extended profiles.
-   **Product Catalog**:
    -   Comprehensive product management with categories and details.
    -   Efficient filtering, searching, and sorting.
-   **Shopping Cart**:
    -   Persistent cart functionality for authenticated users.
    -   Add, update, and remove items dynamically.
-   **Order Management**:
    -   Order placement and tracking.
    -   Order status updates and history.
-   **Inventory Management**:
    -   Real-time stock tracking.
    -   Reservation system to prevent overselling during checkout.
    -   Background tasks to clear expired reservations.
-   **Payments**:
    -   Integration with Chapa payment gateway.
    -   Secure payment processing and verification.
-   **Reviews & Wishlists**:
    -   Product reviews and ratings.
    -   User wishlists for saving favorite items.
-   **API Documentation**:
    -   Auto-generated Interactive API docs via Swagger UI and ReDoc.

## 🛠 Tech Stack

-   **Backend Framework**: [Django](https://www.djangoproject.com/) & [Django REST Framework](https://www.django-rest-framework.org/)
-   **Database**: PostgreSQL
-   **Caching & Broker**: Redis
-   **Async Tasks**: Celery & Celery Beat
-   **Documentation**: drf-spectacular (OpenAPI 3.0)
-   **Deployment**: Ready for Render (includes `build.sh` and `render.yaml`)

## ⚙️ Prerequisites

Ensure you have the following installed locally:

-   [Python 3.10+](https://www.python.org/)
-   [PostgreSQL](https://www.postgresql.org/)
-   [Redis](https://redis.io/) (for caching and background tasks)

## 📥 Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd drf-commerce-engine
    ```

2.  **Create and activate a virtual environment**:
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Linux/MacOS
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration**:
    Create a `.env` file in the root directory (based on `.env.example` if available) and configure your secrets:
    ```env
    # Security
    SECRET_KEY=your-super-secret-key-here
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1

    # Database
    POSTGRES_DB=commerce_db
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=yourpassword
    POSTGRES_HOST=localhost
    POSTGRES_PORT=5432

    # Redis
    CELERY_BROKER_URL=redis://localhost:6379/1
    CELERY_RESULT_BACKEND=redis://localhost:6379/1
    REDIS_URL=redis://localhost:6379/2
    
    # Payments (Chapa)
    CHAPA_SECRET_KEY=your-chapa-secret-key
    CHAPA_WEBHOOK_SECRET=your-webhook-secret
    ```

5.  **Apply Database Migrations**:
    ```bash
    python manage.py migrate
    ```

6.  **Create a Superuser**:
    ```bash
    python manage.py createsuperuser
    ```

7.  **Run the Development Server**:
    ```bash
    python manage.py runserver
    ```

## 🏃‍♂️ Background Tasks

This project uses Celery for background tasks (e.g., clearing expired inventory reservations).

To run the Celery worker and beat scheduler locally:

**Worker:**
```bash
celery -A config worker -l info --pool=solo
```
*(Note: `--pool=solo` is often required on Windows)*

**Beat Scheduler:**
```bash
celery -A config beat -l info
```

## 📖 API Documentation

The API comes with built-in interactive documentation. Once the server is running, visit:

-   **Swagger UI**: [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/)
-   **ReDoc**: [http://localhost:8000/api/schema/redoc/](http://localhost:8000/api/schema/redoc/)

## 🚀 Deployment

This project is configured for easy deployment on [Render](https://render.com/).

1.  Push your code to a generic Git repository.
2.  Connect your repository to Render.
3.  Use the `render.yaml` Blueprint or manually configure a **Web Service**.
4.  Set the required environment variables in the Render dashboard.
5.  Render will automatically build and start the application using `build.sh`.

See `walkthrough.md` for a more detailed deployment guide.
