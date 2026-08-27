# Workout & Nutrition Log API

A Django REST Framework API for logging meals, planning meal plans, tracking
workouts and body measurements, and supporting a trainer/trainee relationship
between users.

## Stack

- Django 5.2, Django REST Framework
- PostgreSQL (via `psycopg`), configured through `DATABASE_URL`
- Token authentication (`rest_framework.authtoken`)
- `django-filter` for query-param filtering
- `django-cors-headers` for the React frontend

## Project layout

```
config/       settings (base/dev/prod), root urls.py
workout/      WorkOut, BodyMeasurement, Profile models + trainer/trainee views
nutrition/    Food, LoggedMeal, MealItem, MealPlan, PlannedMeal, NutritionProfile
```

Settings are split: `config/settings/base.py` holds shared config,
`config/settings/dev.py` is used by default (see `manage.py`), and
`config/settings/prod.py` is for deployment.

## Setup

1. Create a `.env` file in the project root (see `.env.example`) with at least:
   ```
   SECRET_KEY=your_secret_key_here
   DEBUG=True
   DATABASE_URL=postgres://user:password@localhost:5432/dbname
   ```
2. Install dependencies (a `pyproject.toml` is provided):
   ```
   pip install -e .
   ```
3. Run migrations:
   ```
   python manage.py migrate
   ```
4. Start the server:
   ```
   python manage.py runserver
   ```
   Defaults to `http://localhost:8000`, with `config.settings.dev` as the
   settings module.

Every new `User` automatically gets a `Profile` (role: trainee by default)
and a `NutritionProfile` via post_save signals — you don't need to create
these manually. A **trainee account can't fully register without an existing
trainer to select**, so create at least one trainer account first.

## Authentication

Token-based. Obtain a token via `POST /api/login/` with `username` and
`password`, then send it on every subsequent request as:
```
Authorization: Token <token>
```

## Endpoints

All routes are prefixed with `/api/`.

| Endpoint | Notes |
|---|---|
| `POST /login/` | Returns `{ "token": "..." }` |
| `POST /register/` | Creates a user; `role: "trainee"` requires `trainer_id` |
| `POST /logout/` | Invalidates the current token |
| `GET /profile/` | The logged-in user's profile |
| `GET /trainers/` | List of trainer accounts (no pagination) |
| `GET /my-trainees/` | A trainer's assigned trainees (no pagination) |
| `/workouts/`, `/bodymeasurements/` | Standard DRF viewsets |
| `/foods/`, `/logged-meals/`, `/meal-items/`, `/meal-plans/`, `/planned-meals/`, `/nutrition-profile/` | Standard DRF viewsets |

List endpoints (except `/trainers/` and `/my-trainees/`) are paginated —
`?page=` and `?page_size=` (max page size: 6). `/logged-meals/` supports
`?date=` and `?meal_type=` filters; `/meal-plans/` supports `?name=`
(case-insensitive contains).

## Data model highlights

- **Constraints live at the database level** (`CheckConstraint`,
  `UniqueConstraint`), not just in serializers — e.g. a `LoggedMeal` can't
  have two entries for the same user/date/meal_type, quantities must be
  positive, a `MealPlan`'s `end_date` can't be before its `start_date`.
- `Food` records are protected (`on_delete=PROTECT`) from deletion while
  referenced by a `MealItem` or `PlannedMeal`.
- `Profile.trainer` is nullable and set to `NULL` if the trainer account is
  deleted (`on_delete=SET_NULL`), rather than cascading.

## CORS

`django-cors-headers` is configured to allow `http://localhost:5173` (Vite's
default dev port). If the frontend runs on a different port, update
`CORS_ALLOWED_ORIGINS` in `config/settings/base.py`.

## Tests

```
python manage.py test
```
Covers model-level constraint tests (uniqueness, check constraints) and
API-level behavior.