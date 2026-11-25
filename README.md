# E-commerce API

A RESTful e-commerce backend built with FastAPI, PostgreSQL and SQLAlchemy. It provides 33 API endpoints covering user authentication, profiles, addresses, product management, shopping carts, orders and billing.

## Tech Stack

- Python
- FastAPI and Uvicorn
- PostgreSQL
- SQLAlchemy ORM
- Pydantic
- JWT (python-jose) and bcrypt
- SMTP for order confirmation emails

## Features

- User registration, login and JWT-based authentication
- Profile management and password updates
- User-specific addresses, carts, orders and bills
- Category and product management
- Product search, filtering, pagination and price sorting
- Stock validation and soft deletion of products
- Shopping cart management with automatic subtotal calculation
- Transactional order placement and stock updates
- Order cancellation with stock restoration
- Automatic bill generation and cash-on-delivery checkout
- Background email notifications for successful orders
- Interactive API documentation with Swagger UI

## Project Structure

```text
ecommerce-api/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── dependencies.py
│   ├── security.py
│   ├── email_service.py
│   ├── models/
│   ├── schemas/
│   └── routes/
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Getting Started

### 1. Clone the repository

Clone this repository using the URL under GitHub's **Code** menu, then enter the `ecommerce-api` directory.

### 2. Install dependencies

Python 3.13 and a running PostgreSQL instance are recommended for reproducing the development environment.

```bash
python3 -m pip install -r requirements.txt
```

### 3. Create the database

Run the following in PostgreSQL:

```sql
CREATE DATABASE ecommerce;
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Update `.env` with your database credentials and JWT secret.

```env
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/ecommerce
JWT_SECRET_KEY=replace_with_a_secure_random_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DELIVERY_FEE=50.00
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM=orders@example.com
SMTP_USE_TLS=false
```

Use the PostgreSQL driver installed by `requirements.txt` in the database URL. Never commit `.env` or real credentials.

### 5. Run the application

```bash
python3 -m uvicorn app.main:app --reload
```

In the original development setup, SQLAlchemy creates missing tables at startup. If the project has been switched to Alembic migrations, run `python3 -m alembic upgrade head` before starting the server instead.

## API Documentation

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

Register a user, log in, copy the access token and use the **Authorize** button in Swagger UI to access protected endpoints.

All endpoints use the `/api/v1` prefix. Category and product browsing are public; other operations require authentication, except registration and login.

## API Endpoints

### Authentication

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/auth/register` | Register a user |
| POST | `/auth/login` | Log in and obtain an access token |

### User Profile

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/users/me` | Get current user profile |
| PATCH | `/users/me` | Update profile |
| PATCH | `/users/me/password` | Change password |

### Addresses

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/addresses` | Create address |
| GET | `/addresses` | List user addresses |
| GET | `/addresses/{id}` | Get address |
| PATCH | `/addresses/{id}` | Update address |
| DELETE | `/addresses/{id}` | Delete address |

### Categories

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/categories` | Create category |
| GET | `/categories` | List categories |
| GET | `/categories/{id}` | Get category |
| PATCH | `/categories/{id}` | Update category |
| DELETE | `/categories/{id}` | Delete empty category |

### Products

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/products` | Create product |
| GET | `/products` | List, search and filter products |
| GET | `/products/{id}` | Get product |
| PATCH | `/products/{id}` | Update product |
| PATCH | `/products/{id}/stock` | Update stock |
| DELETE | `/products/{id}` | Soft delete product |
| GET | `/categories/{id}/products` | List products by category |

### Cart

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/cart` | Get shopping cart |
| POST | `/cart/items` | Add item to cart |
| PATCH | `/cart/items/{id}` | Update item quantity |
| DELETE | `/cart/items/{id}` | Remove item |
| DELETE | `/cart` | Clear cart |

### Orders

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/orders` | Place order |
| GET | `/orders` | List user orders |
| GET | `/orders/{id}` | Get order details |
| POST | `/orders/{id}/cancel` | Cancel order |

### Bills

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/orders/{id}/bill` | Get order bill |
| GET | `/bills` | List user bills |

## Authentication and Security

Passwords are hashed using bcrypt before being stored. On successful login, the API issues a signed JWT access token containing the user ID and expiration time.

Protected endpoints use `HTTPBearer` and the `get_current_user` dependency to validate the token and retrieve the authenticated user. Private resources are filtered by the authenticated user's ID to enforce data ownership.

## Order Processing

Order placement validates the shipping address, cart contents and available stock. Product prices are retrieved from the database, and totals are calculated using `Decimal`.

Order creation, order items, stock reduction, bill generation and cart clearance are handled within a single database transaction. PostgreSQL row-level locks help prevent concurrent overselling. Failed transactions are rolled back.

Product details and shipping addresses are stored as snapshots to preserve order history. Cancelling a pending order restores its stock.

## Email Notifications

Order confirmation emails are scheduled using FastAPI `BackgroundTasks` after a successful database commit. SMTP failures are logged without rolling back the order.

For local email testing, start a development SMTP server in a separate terminal:

```bash
python3 -m aiosmtpd -n -l localhost:1025
```

Messages are printed locally rather than delivered to real inboxes. To use Gmail SMTP, configure `smtp.gmail.com`, port `587`, TLS, your sender address and a Google App Password in `.env`.

