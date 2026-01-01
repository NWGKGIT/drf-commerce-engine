# DRF E-Commerce Engine

A comprehensive, production-ready Django REST Framework e-commerce API with full payment integration, inventory management, and asynchronous task processing.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Running the Project](#running-the-project)
- [API Documentation](#api-documentation)
- [Testing the API](#testing-the-api)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Development Workflow](#development-workflow)
- [Troubleshooting](#troubleshooting)
- [Additional Resources](#additional-resources)

---

## 🎯 Overview

This is a full-featured e-commerce backend API built with Django REST Framework. It provides a complete solution for managing products, orders, payments, inventory, user accounts, shopping carts, wishlists, and product reviews. The system is designed with scalability in mind, using Docker for containerization and Celery for asynchronous task processing.

### Key Capabilities

- **User Management**: Email-based authentication with email verification
- **Product Catalog**: Hierarchical categories, products with images, inventory tracking
- **Shopping Cart**: Persistent cart with automatic calculations
- **Order Management**: Complete order lifecycle with status tracking
- **Payment Processing**: Integration with Chapa payment gateway
- **Inventory Management**: Real-time stock tracking with reservation system
- **Reviews & Ratings**: Product reviews with verified purchase badges
- **Wishlist**: User wishlist functionality

---

## ✨ Features

### Authentication & Authorization
- Email-based authentication (no username required)
- Email verification via django-allauth
- Session-based authentication (cookie-based)
- CSRF protection
- Secure admin initialization with token-based setup
- Email verification requirement for certain operations

### Product Management
- Hierarchical category system (parent/child categories)
- Product variants with SKU support
- Multiple product images with ordering
- Discount pricing support
- Product specifications (JSON field)
- Featured products
- Active/inactive product status

### Inventory System
- Real-time stock tracking
- Inventory reservations for pending orders
- Automatic stock updates on order completion/cancellation
- Scheduled tasks for clearing expired reservations
- Location-based inventory (optional)

### Order Processing
- Complete order lifecycle management
- Order status tracking (pending_payment, payment_failed, processing, cancelled, completed)
- Shipping address snapshots
- Order item snapshots (preserves historical data)
- Automatic order cancellation for unpaid orders

### Payment Integration
- Chapa payment gateway integration
- Payment intent creation
- Webhook handling for payment status updates
- Payment verification endpoint
- Manual payment cancellation

### Additional Features
- Shopping cart with automatic total calculations
- Wishlist functionality
- Product reviews with ratings
- Verified purchase badges for reviews
- User profiles with preferences
- Multiple shipping addresses per user
- Default address management

---

## 🛠 Tech Stack

### Backend
- **Django 5.2.8** - Web framework
- **Django REST Framework 3.16.1** - API framework
- **django-allauth 65.13.1** - Authentication & email verification
- **dj-rest-auth 7.0.1** - REST API authentication
- **drf-spectacular 0.29.0** - OpenAPI schema generation
- **Celery 5.6.0** - Asynchronous task processing
- **chapa 0.1.2** - Payment gateway integration

### Database & Caching
- **PostgreSQL 15** - Primary database
- **Redis 7** - Result backend and caching
- **RabbitMQ 3** - Message broker for Celery

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **Gunicorn** - Production WSGI server
- **WhiteNoise** - Static file serving
- **Ngrok** - Public URL tunneling (for webhooks)

### Development Tools
- **django-cors-headers** - CORS handling
- **django-environ** - Environment variable management
- **Pillow** - Image processing

---

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

1. **Docker Desktop** ([Download](https://www.docker.com/products/docker-desktop/))
   - Required for running the entire stack
   - Version 20.10 or higher recommended

2. **Git** ([Download](https://git-scm.com/downloads))
   - For cloning the repository

3. **Ngrok Account** (Optional, but required for payment webhooks)
   - Sign up at [ngrok.com](https://dashboard.ngrok.com/signup)
   - Get your auth token from [dashboard.ngrok.com/get-started/your-authtoken](https://dashboard.ngrok.com/get-started/your-authtoken)

4. **Chapa Account** (Optional, for payment testing)
   - Sign up at [chapa.co](https://chapa.co)
   - Get test API keys from your dashboard

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd drf-commerce-engine
```

### 2. Create Environment File

Create a `.env` file in the root directory:

```bash
# Copy from example if available, or create manually
touch .env
```

Add the following configuration to `.env`:

```env
# Django Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
INITIAL_ADMIN_TOKEN=your-secure-admin-setup-token-here

# Database Configuration
POSTGRES_DB=db_table
POSTGRES_USER=db_user
POSTGRES_PASSWORD=change-this-password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Celery Configuration
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Ngrok Configuration (Required for webhooks)
NGROK_AUTHTOKEN=your-ngrok-auth-token-here

# Chapa Payment Configuration (Optional for testing)
CHAPA_SECRET_KEY=your-chapa-secret-key
CHAPA_WEBHOOK_SECRET=your-webhook-secret
BACKEND_URL=https://your-ngrok-url.ngrok-free.dev

# Email Configuration (Development - uses console backend)
# For production, configure SMTP settings
```

**Important Notes:**
- Replace all placeholder values with your actual credentials
- `POSTGRES_HOST=db` is correct for Docker (refers to the service name)
- `INITIAL_ADMIN_TOKEN` is used to create the first superuser securely
- `BACKEND_URL` should be set after starting Ngrok (see step 4)

### 3. Build and Start Services

```bash
docker compose up --build
```

This command will:
- Build the Django application container
- Start PostgreSQL database
- Start Redis
- Start RabbitMQ
- Start Celery worker and beat scheduler
- Start Ngrok tunnel
- Run database migrations automatically
- Start the Django development server

**First-time setup may take 3-5 minutes** as it downloads Docker images and installs dependencies.

### 4. Verify Services are Running

Check that all services started successfully:

```bash
docker compose ps
```

You should see all services with status "Up" or "running".

### 5. Access the Application

Once all services are running, you can access:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Django API** | http://localhost:8000 | - |
| **API Schema (OpenAPI)** | http://localhost:8000/api/schema/ | - |
| **Swagger UI** | http://localhost:8000/api/schema/swagger-ui/ | - |
| **ReDoc** | http://localhost:8000/api/schema/redoc/ | - |
| **Django Admin** | http://localhost:8000/admin/ | (Create after step 6) |
| **RabbitMQ Management** | http://localhost:15672 | guest / guest |
| **Ngrok Status** | http://localhost:4040 | - |

### 6. Create Admin User

The first admin user must be created via the secure initialization endpoint:

```bash
curl -X POST http://localhost:8000/api/auth/init-admin/ \
  -H "Content-Type: application/json" \
  -d '{
    "setup_token": "your-secure-admin-setup-token-here",
    "email": "admin@example.com",
    "password": "secure-password-123",
    "password_confirm": "secure-password-123"
  }'
```

**Important:**
- Use the same `INITIAL_ADMIN_TOKEN` value from your `.env` file
- The email will be automatically verified
- This endpoint only works if no superuser exists yet

### 7. Set Up Ngrok for Webhooks (If using payments)

1. Check the Ngrok status page: http://localhost:4040
2. Copy the `https://...` URL (e.g., `https://abc123.ngrok-free.app`)
3. Update your `.env` file:
   ```env
   BACKEND_URL=https://abc123.ngrok-free.app
   ```
4. Restart the server:
   ```bash
   docker compose restart server
   ```
5. Configure the webhook URL in your Chapa dashboard:
   ```
   https://abc123.ngrok-free.app/api/payments/webhook/
   ```

---

## ⚙️ Configuration

### Environment Variables

The application uses environment variables for configuration. Key variables:

#### Required Variables

- `SECRET_KEY` - Django secret key (generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- `POSTGRES_DB` - Database name
- `POSTGRES_USER` - Database user
- `POSTGRES_PASSWORD` - Database password
- `INITIAL_ADMIN_TOKEN` - Token for creating first admin (use a strong random string)

#### Optional Variables

- `DEBUG` - Set to `False` in production
- `CHAPA_SECRET_KEY` - Required only if testing payments
- `CHAPA_WEBHOOK_SECRET` - Webhook verification secret
- `NGROK_AUTHTOKEN` - Required for webhook testing
- `BACKEND_URL` - Public URL for webhooks

### Django Settings

Key settings are in `drf_commerce_engine/settings.py`:

- **Authentication**: Email-based, no username
- **Email Verification**: Mandatory
- **CORS**: Currently allows all origins (change in production!)
- **Default Permissions**: IsAuthenticated (most endpoints require login)
- **Session Authentication**: Cookie-based

---

## 🏃 Running the Project

### Development Mode (Current Setup)

The `compose.yml` is configured for development with:
- Hot-reloading enabled (code changes reflect immediately)
- Development server (`runserver`) instead of Gunicorn
- Volume mounts for live code editing

```bash
# Start all services
docker compose up

# Start in detached mode (background)
docker compose up -d

# View logs
docker compose logs -f

# View logs for specific service
docker compose logs -f server
docker compose logs -f celery_worker
```

### Common Commands

```bash
# Run Django management commands
docker compose exec server python manage.py <command>

# Create migrations
docker compose exec server python manage.py makemigrations

# Apply migrations
docker compose exec server python manage.py migrate

# Create superuser (alternative method)
docker compose exec server python manage.py createsuperuser

# Access Django shell
docker compose exec server python manage.py shell

# Run tests
docker compose exec server python manage.py test

# Collect static files
docker compose exec server python manage.py collectstatic --noinput

# Stop all services
docker compose down

# Stop and remove volumes (⚠️ deletes database!)
docker compose down -v
```

### Production Mode

For production, modify `compose.yml` to:
- Use Gunicorn instead of `runserver`
- Remove volume mounts
- Set `DEBUG=False`
- Configure proper CORS origins
- Use production database credentials
- Set up proper email backend (SMTP)

---

## 📚 API Documentation

### Interactive Documentation

The API includes three interactive documentation interfaces:

1. **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/
   - Interactive API explorer
   - Try out endpoints directly
   - See request/response schemas

2. **ReDoc**: http://localhost:8000/api/schema/redoc/
   - Clean, readable documentation
   - Better for reading API specs

3. **OpenAPI Schema**: http://localhost:8000/api/schema/
   - Raw OpenAPI 3.0 JSON/YAML
   - Can be imported into Postman, Insomnia, etc.

### API Endpoints Overview

#### Authentication (`/api/auth/`)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/auth/login/` | POST | Login with email/password | No |
| `/api/auth/logout/` | POST | Logout current session | Yes |
| `/api/auth/registration/` | POST | Register new user | No |
| `/api/auth/registration/verify-email/` | POST | Verify email address | No |
| `/api/auth/registration/resend-email/` | POST | Resend verification email | No |
| `/api/auth/password/reset/` | POST | Request password reset | No |
| `/api/auth/password/reset/confirm/` | POST | Confirm password reset | No |
| `/api/auth/password/change/` | POST | Change password | Yes |
| `/api/auth/user/` | GET/PUT/PATCH | Get/update user details | Yes |
| `/api/auth/init-admin/` | POST | Initialize first admin | No (token required) |

#### Accounts (`/api/accounts/`)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/accounts/addresses/` | GET/POST | List/create addresses | Yes |
| `/api/accounts/addresses/{id}/` | GET/PUT/PATCH/DELETE | Address operations | Yes |
| `/api/accounts/csrf/` | GET | Get CSRF token | No |

#### Products (`/api/products/`)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/products/` | GET/POST | List/create products | Yes |
| `/api/products/{id}/` | GET/PUT/PATCH/DELETE | Product operations | Yes |
| `/api/categories/` | GET/POST | List/create categories | Yes |
| `/api/categories/{id}/` | GET/PUT/PATCH/DELETE | Category operations | Yes |

#### Cart (`/api/cart/`)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/cart/my_cart/` | GET | Get current user's cart | Yes |
| `/api/cart/items/` | GET/POST | List/create cart items | Yes |
| `/api/cart/items/{id}/` | GET/PUT/PATCH/DELETE | Cart item operations | Yes |

#### Orders (`/api/orders/`)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/orders/` | GET/POST | List/create orders | Yes |
| `/api/orders/{id}/` | GET/PATCH | Get/update order | Yes |
| `/api/orders/{id}/cancel/` | POST | Cancel an order | Yes |

#### Payments (`/api/payments/`)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/payments/initiate/` | POST | Create payment intent | Yes |
| `/api/payments/verify/` | GET | Verify payment status | Yes |
| `/api/payments/cancel/` | POST | Cancel payment | Yes |
| `/api/payments/webhook/` | POST | Chapa webhook handler | No (webhook secret) |

#### Reviews (`/api/reviews/`)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/reviews/` | GET/POST | List/create reviews | GET: No, POST: Yes |
| `/api/reviews/{id}/` | GET/PUT/PATCH/DELETE | Review operations | Yes |

#### Wishlist (`/api/wishlist/`)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/wishlist/my-wishlist/` | GET | Get current user's wishlist | Yes |
| `/api/wishlist/items/` | GET/POST | List/create wishlist items | Yes |
| `/api/wishlist/items/{id}/` | GET/PUT/PATCH/DELETE | Wishlist item operations | Yes |

### Authentication Flow

1. **Get CSRF Token** (if needed):
   ```bash
   curl http://localhost:8000/api/accounts/csrf/
   ```

2. **Register User**:
   ```bash
   curl -X POST http://localhost:8000/api/auth/registration/ \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "password1": "secure-password-123",
       "password2": "secure-password-123",
       "first_name": "John",
       "last_name": "Doe"
     }'
   ```

3. **Check Email** (in development, emails print to console):
   - Look for verification email in Docker logs: `docker compose logs server`
   - Copy the verification key

4. **Verify Email**:
   ```bash
   curl -X POST http://localhost:8000/api/auth/registration/verify-email/ \
     -H "Content-Type: application/json" \
     -d '{"key": "verification-key-from-email"}'
   ```

5. **Login**:
   ```bash
   curl -X POST http://localhost:8000/api/auth/login/ \
     -H "Content-Type: application/json" \
     -c cookies.txt \
     -d '{
       "email": "user@example.com",
       "password": "secure-password-123"
     }'
   ```

6. **Use Authenticated Endpoints**:
   ```bash
   curl http://localhost:8000/api/auth/user/ \
     -b cookies.txt
   ```

---

## 🧪 Testing the API

### Using Swagger UI

1. Navigate to http://localhost:8000/api/schema/swagger-ui/
2. Click "Authorize" button
3. Login via `/api/auth/login/` endpoint first
4. Copy the session cookie from browser DevTools
5. Use the "Try it out" feature on any endpoint

### Using cURL

```bash
# 1. Register
curl -X POST http://localhost:8000/api/auth/registration/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password1": "test123", "password2": "test123"}'

# 2. Verify email (check logs for key)
curl -X POST http://localhost:8000/api/auth/registration/verify-email/ \
  -H "Content-Type: application/json" \
  -d '{"key": "your-verification-key"}'

# 3. Login and save cookies
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"email": "test@example.com", "password": "test123"}'

# 4. Use authenticated endpoint
curl http://localhost:8000/api/products/ \
  -b cookies.txt
```

### Using Postman

1. Import the OpenAPI schema:
   - Go to http://localhost:8000/api/schema/
   - Copy the JSON/YAML
   - Import into Postman

2. Set up authentication:
   - Create a new request to `/api/auth/login/`
   - Set body to JSON with email/password
   - In Tests tab, add:
     ```javascript
     pm.environment.set("sessionid", pm.cookies.get("sessionid"));
     ```

3. Use `{{sessionid}}` in subsequent requests

### Testing Payment Flow

1. **Create an order** (via cart checkout)
2. **Initiate payment**:
   ```bash
   curl -X POST http://localhost:8000/api/payments/initiate/ \
     -H "Content-Type: application/json" \
     -b cookies.txt \
     -d '{"order": 1}'
   ```
3. **Use the payment URL** from response to complete payment in Chapa test mode
4. **Verify payment**:
   ```bash
   curl http://localhost:8000/api/payments/verify/?tx_ref=<reference> \
     -b cookies.txt
   ```

---

## 📁 Project Structure

```
drf-commerce-engine/
├── accounts/              # User management, addresses, authentication
│   ├── models.py         # User, UserProfile, Address models
│   ├── serializers.py    # User serializers
│   ├── views.py          # Address views, admin setup
│   └── urls.py           # Account routes
│
├── products/              # Product catalog
│   ├── models.py         # Category, Product, ProductImage
│   ├── serializers.py    # Product serializers
│   ├── views.py          # Product viewsets
│   └── urls.py           # Product routes
│
├── cart/                 # Shopping cart
│   ├── models.py         # Cart, CartItem
│   ├── serializers.py    # Cart serializers
│   ├── views.py          # Cart viewsets
│   └── urls.py           # Cart routes
│
├── orders/               # Order management
│   ├── models.py         # Order, OrderItem
│   ├── serializers.py    # Order serializers
│   ├── services.py      # Order business logic
│   ├── views.py          # Order viewsets
│   └── urls.py           # Order routes
│
├── payments/             # Payment processing
│   ├── models.py         # Payment model
│   ├── serializers.py    # Payment serializers
│   ├── services.py       # Chapa integration
│   ├── views.py          # Payment views, webhooks
│   └── urls.py           # Payment routes
│
├── inventory/            # Inventory management
│   ├── models.py         # InventoryItem, InventoryReservation
│   ├── services.py       # Inventory operations
│   ├── tasks.py          # Celery tasks
│   └── views.py          # Inventory views
│
├── reviews/              # Product reviews
│   ├── models.py         # Review model
│   ├── serializers.py    # Review serializers
│   └── views.py          # Review viewsets
│
├── wishlist/             # Wishlist functionality
│   ├── models.py         # Wishlist, WishlistItem
│   ├── serializers.py    # Wishlist serializers
│   └── views.py          # Wishlist viewsets
│
├── core/                 # Shared utilities
│   ├── permissions.py    # Custom permissions
│   └── views.py          # Shared views
│
├── drf_commerce_engine/  # Django project settings
│   ├── settings.py       # Main configuration
│   ├── urls.py           # Root URL configuration
│   ├── wsgi.py           # WSGI application
│   ├── asgi.py           # ASGI application
│   └── celery.py         # Celery configuration
│
├── compose.yml           # Docker Compose configuration
├── Dockerfile            # Docker image definition
├── requirements.txt      # Python dependencies
├── manage.py             # Django management script
└── README.md             # This file
```

---

## 🏗 Architecture

### System Architecture

```
┌─────────────┐
│   Client    │
│  (Browser/  │
│   Mobile)   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│      Django REST Framework      │
│  (Session Auth, API Endpoints)  │
└──────┬──────────────────────────┘
       │
       ├──► PostgreSQL (Database)
       │
       ├──► Redis (Cache/Results)
       │
       ├──► RabbitMQ (Message Queue)
       │      │
       │      ├──► Celery Worker (Async Tasks)
       │      │      ├── Inventory Updates
       │      │      ├── Order Processing
       │      │      └── Email Sending
       │      │
       │      └──► Celery Beat (Scheduled Tasks)
       │             ├── Clear Expired Reservations
       │             └── Cancel Unpaid Orders
       │
       └──► Ngrok (Public Tunnel)
              │
              └──► Chapa Webhooks
```

### Data Flow Examples

#### Order Creation Flow

1. User adds items to cart → `POST /api/cart/items/`
2. User creates order → `POST /api/orders/`
   - Cart items converted to order items
   - Inventory reserved
   - Order status: `pending_payment`
3. User initiates payment → `POST /api/payments/initiate/`
   - Payment intent created
   - Redirect URL returned
4. User completes payment on Chapa
5. Chapa sends webhook → `POST /api/payments/webhook/`
   - Payment status updated
   - Order status updated to `processing`
   - Inventory decremented
6. Admin updates order status → `PATCH /api/orders/{id}/`
   - Status: `completed`

#### Inventory Reservation System

- When order created: Inventory reserved for 10 minutes
- Celery Beat task runs every 5 minutes: Clears expired reservations
- Celery Beat task runs every 10 minutes: Cancels unpaid orders
- On order completion: Reservation removed, stock decremented
- On order cancellation: Reservation removed, stock restored

---

## 💻 Development Workflow

### Making Changes

1. **Edit code** in your local directory (mounted as volume)
2. **Changes reflect immediately** (Django auto-reloads)
3. **For model changes**:
   ```bash
   docker compose exec server python manage.py makemigrations
   docker compose exec server python manage.py migrate
   ```

### Running Tests

```bash
# Run all tests
docker compose exec server python manage.py test

# Run specific app tests
docker compose exec server python manage.py test accounts

# Run with verbosity
docker compose exec server python manage.py test --verbosity=2
```

### Database Management

```bash
# Access PostgreSQL shell
docker compose exec db psql -U db_user -d db_table

# Create database backup
docker compose exec db pg_dump -U db_user db_table > backup.sql

# Restore database backup
docker compose exec -T db psql -U db_user db_table < backup.sql

# Reset database (⚠️ deletes all data)
docker compose down -v
docker compose up -d db
docker compose exec server python manage.py migrate
```

### Adding New Dependencies

1. Add to `requirements.txt`
2. Rebuild containers:
   ```bash
   docker compose build
   docker compose up
   ```

### Code Quality

```bash
# Check for Python syntax errors
docker compose exec server python -m py_compile **/*.py

# Run Django check
docker compose exec server python manage.py check
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Services Won't Start

**Problem**: Containers fail to start or exit immediately

**Solutions**:
- Check logs: `docker compose logs`
- Verify `.env` file exists and has correct values
- Ensure Docker Desktop is running
- Check port conflicts (8000, 5432, 6379, 5672, 15672, 4040)
- Try rebuilding: `docker compose build --no-cache`

#### 2. Database Connection Errors

**Problem**: `django.db.utils.OperationalError: could not connect to server`

**Solutions**:
- Wait for database to be healthy: `docker compose ps db`
- Check `POSTGRES_HOST=db` in `.env` (not `localhost`)
- Verify database credentials match in `.env`
- Restart database: `docker compose restart db`

#### 3. Migration Errors

**Problem**: `django.db.migrations.exceptions.InconsistentMigrationHistory`

**Solutions**:
```bash
# Reset migrations (⚠️ development only)
docker compose exec server python manage.py migrate --fake-initial

# Or reset database completely
docker compose down -v
docker compose up -d db
docker compose exec server python manage.py migrate
```

#### 4. Email Verification Not Working

**Problem**: Can't receive verification emails

**Solutions**:
- In development, emails print to console: `docker compose logs server`
- Check `EMAIL_BACKEND` in settings (should be console backend)
- Verify email in logs and use the key from there

#### 5. CSRF Token Errors

**Problem**: `403 Forbidden: CSRF verification failed`

**Solutions**:
- Get CSRF token first: `GET /api/accounts/csrf/`
- Include CSRF token in headers: `X-CSRFToken: <token>`
- For cURL, use `-c cookies.txt -b cookies.txt` to maintain session

#### 6. Celery Tasks Not Running

**Problem**: Background tasks not executing

**Solutions**:
- Check Celery worker logs: `docker compose logs celery_worker`
- Verify RabbitMQ is running: `docker compose ps rabbitmq`
- Check `CELERY_BROKER_URL` in `.env`
- Restart Celery: `docker compose restart celery_worker celery_beat`

#### 7. Ngrok Not Working

**Problem**: Can't access Ngrok tunnel

**Solutions**:
- Verify `NGROK_AUTHTOKEN` in `.env`
- Check Ngrok logs: `docker compose logs ngrok`
- Access Ngrok status: http://localhost:4040
- Restart Ngrok: `docker compose restart ngrok`

#### 8. Payment Webhooks Not Received

**Problem**: Chapa webhooks not reaching the server

**Solutions**:
- Verify `BACKEND_URL` in `.env` matches Ngrok URL
- Check webhook URL in Chapa dashboard
- Ensure webhook endpoint is accessible: `GET /api/payments/webhook/`
- Check server logs for webhook requests

#### 9. Permission Denied Errors

**Problem**: `403 Forbidden: You do not have permission`

**Solutions**:
- Verify user is logged in: `GET /api/auth/user/`
- Check email is verified (required for some endpoints)
- Verify user has required permissions
- Check `IsEmailVerified` permission on endpoints

#### 10. Static Files Not Loading

**Problem**: CSS/JS not loading in admin or API docs

**Solutions**:
```bash
# Collect static files
docker compose exec server python manage.py collectstatic --noinput

# Restart server
docker compose restart server
```

### Debugging Tips

1. **View Real-time Logs**:
   ```bash
   docker compose logs -f server
   docker compose logs -f celery_worker
   ```

2. **Access Django Shell**:
   ```bash
   docker compose exec server python manage.py shell
   ```

3. **Check Service Health**:
   ```bash
   docker compose ps
   ```

4. **Inspect Container**:
   ```bash
   docker compose exec server bash
   ```

5. **Check Database**:
   ```bash
   docker compose exec db psql -U db_user -d db_table -c "SELECT * FROM accounts_user;"
   ```

---

## 📖 Additional Resources

### Documentation Links

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [Chapa API Documentation](https://developer.chapa.co/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

### API Schema

- **OpenAPI Schema**: http://localhost:8000/api/schema/
- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/
- **ReDoc**: http://localhost:8000/api/schema/redoc/

### Project Files

- **OpenAPI Spec**: `E-Commerce API (1).yaml` (can be imported into API clients)
- **Docker Guide**: `README.Docker.md` (detailed Docker setup)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

---

## 👥 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Review API documentation at `/api/schema/swagger-ui/`

---

## 🎉 Getting Started Checklist

- [ ] Docker Desktop installed and running
- [ ] Repository cloned
- [ ] `.env` file created with all required variables
- [ ] Services started with `docker compose up --build`
- [ ] All services showing as "Up" in `docker compose ps`
- [ ] Can access http://localhost:8000
- [ ] Admin user created via `/api/auth/init-admin/`
- [ ] Test user registered and email verified
- [ ] Can login and access authenticated endpoints
- [ ] Swagger UI accessible and functional
- [ ] (Optional) Ngrok configured for webhook testing
- [ ] (Optional) Chapa test keys configured


