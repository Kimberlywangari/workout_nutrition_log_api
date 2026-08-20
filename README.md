# Workout Log API
 
A REST API for tracking workouts, body measurements, and user profiles, built with Django REST Framework. Built as Gate 3 of 21 (Track A: Python & Django Core) — a learning project focused on CRUD, validation, authentication, and object-level permissions.
 
## Features
 
- Token-based authentication
- Full CRUD on `Workout` and `BodyMeasurement` resources
- Restricted CRUD on `Profile` (no create — profiles are auto-created via signal; delete removes the entire account)
- Object-level permissions — users can only view/edit/delete their own data
- Pagination and query-string filtering
- Split settings (`base` / `dev` / `prod`)
- 55 automated integration tests covering success, validation failure, unauthorized, not-found, and non-owner scenarios
## Requirements
 
- Python 3.10+
- pip
## Setup
 
1. **Clone the repository**
```bash
   git clone <repo-url>
   cd workout_log_api
```
 
2. **Create and activate a virtual environment**
```bash
   python -m venv .venv
   source .venv/bin/activate   # macOS/Linux
   .venv\Scripts\activate      # Windows
```
 
3. **Install dependencies**
```bash
   pip install -e ".[dev]"
```
 
4. **Set up environment variables**
   Copy the example file and fill in real values:
```bash
   cp .env.example .env
```
   At minimum, set a `SECRET_KEY`. Generate one with:
```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
 
5. **Run migrations**
```bash
   python manage.py migrate
```
 
6. **Create a superuser** (for Django admin access)
```bash
   python manage.py createsuperuser
```
 
7. **Run the server**
```bash
   python manage.py runserver
```
 
   API available at `http://127.0.0.1:8000/`.
 
## Running Tests
 
```bash
python manage.py test workout
```
 
Expect `Ran 55 tests ... OK`.
 
## Authentication
 
Obtain a token:
```
POST /api/login/
Content-Type: application/json
 
{"username": "yourusername", "password": "yourpassword"}
```
 
Response:
```json
{"token": "your-token-here"}
```
 
Attach it to every subsequent request:
```
Authorization: Token your-token-here
```
 
## Endpoints
 
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/workouts/` | List your workouts (paginated, filterable) |
| `POST` | `/api/workouts/` | Create a workout |
| `GET` | `/api/workouts/{id}/` | Retrieve one workout |
| `PATCH` | `/api/workouts/{id}/` | Partially update a workout |
| `PUT` | `/api/workouts/{id}/` | Fully replace a workout |
| `DELETE` | `/api/workouts/{id}/` | Delete a workout |
| `GET` | `/api/bodymeasurements/` | List your body measurements |
| `POST` | `/api/bodymeasurements/` | Create a body measurement |
| `GET` / `PATCH` / `DELETE` | `/api/bodymeasurements/{id}/` | Retrieve / update / delete one |
| `GET` | `/api/profile/` | List your profile |
| `GET` / `PATCH` | `/api/profile/{id}/` | Retrieve / update your profile |
| `DELETE` | `/api/profile/{id}/` | **Deletes your entire account** (cascades to all your data) |
| `POST` | `/api/login/` | Obtain an auth token |
 
Note: `Profile` does not support `POST` (create) — a profile is automatically created when a user account is created.
 
### Filtering
 
- `?date=YYYY-MM-DD` — exact date match
- `?date_after=YYYY-MM-DD` — on or after
- `?date_before=YYYY-MM-DD` — on or before
- `?workout_type=running` — case-insensitive partial match (workouts only)
### Pagination
 
- `?page=2` — page number
- `?page_size=5` — override default page size (capped at `max_page_size`)
## Project Structure
 
```
workout_log_api/
├── manage.py
├── pyproject.toml
├── .env.example
├── config/
│   └── settings/
│       ├── base.py
│       ├── dev.py
│       └── prod.py
└── workout/
    ├── models.py
    ├── serializers.py
    ├── permissions.py
    ├── views.py
    ├── urls.py
    ├── filtering.py
    ├── pagination.py
    └── tests/
        ├── test_workout_crud.py
        ├── test_bodymeasurement_crud.py
        ├── test_profile_crud.py
        └── test_permissions.py
```
 
## Notes
 
- Deleting a `Profile` deletes the associated `User` account and, via cascade, every `WorkOut` and `BodyMeasurement` belonging to that user. This is intentional — it functions as an "account deletion" endpoint.
- The `dev.py` and `prod.py` settings files should diverge before any real deployment (`DEBUG`, `ALLOWED_HOSTS`, and secret sourcing all need production-appropriate values).
 