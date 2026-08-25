# Workout & Nutrition Log API
 
A REST API for tracking workouts, body measurements, meal plans, and logged meals, built with Django REST Framework and PostgreSQL.
 
Started as Gate 3 (Track A: Python & Django Core — CRUD, validation, authentication, object-level permissions). Extended through:
- **Gate 4** (Track B: PostgreSQL & Data — normalized schema, database-level constraints, Postgres migration)
- **Gate 5** (Track B: PostgreSQL & Data — query performance, N+1 elimination, indexing)
## Features
 
- Token-based authentication
- Full CRUD on `Workout`, `BodyMeasurement`, `Food`, `MealPlan`, `PlannedMeal`, `LoggedMeal`, `MealItem`
- Restricted CRUD on `Profile` (no create — auto-created via signal; delete removes the entire account)
- Object-level permissions — users can only view/edit/delete their own data
- Pagination and query-string filtering
- Split settings (`base` / `dev` / `prod`)
- PostgreSQL database with foreign keys, unique constraints, and check constraints enforced at the database level — not just in application code
- Query optimization: `prefetch_related` eliminates N+1 queries on the meal-listing endpoint; a database index speeds up date-based filtering, verified with `EXPLAIN ANALYZE`
- 69 automated tests: CRUD, validation, permissions, constraint rejection, and query-count regression
## Requirements
 
- Python 3.10+
- PostgreSQL 15+
- pip
## Setup
 
1. **Clone the repository**
```bash
git clone <repo-url>
cd workout_nutrition_log_api
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
 
4. **Create the PostgreSQL database and user**
```bash
psql -U postgres -h localhost
```
```sql
CREATE DATABASE nutrition_log;
CREATE USER workout_user WITH PASSWORD 'devpass';
GRANT ALL PRIVILEGES ON DATABASE nutrition_log TO workout_user;
ALTER USER workout_user CREATEDB;
\c nutrition_log
GRANT ALL ON SCHEMA public TO workout_user;
GRANT CREATE ON SCHEMA public TO workout_user;
ALTER DATABASE nutrition_log OWNER TO workout_user;
\q
```
`CREATEDB` is required so Django's test runner can create its own temporary test database.
 
5. **Set up environment variables**
```bash
cp .env.example .env
```
At minimum, set `SECRET_KEY` and `DATABASE_URL`:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
```
DATABASE_URL=postgres://workout_user:devpass@localhost:5432/nutrition_log
```
 
6. **Run migrations**
```bash
python manage.py migrate
```
 
7. **Seed sample data**
```bash
python manage.py seed_nutrition
```
 
8. **Create a superuser** (for Django admin access)
```bash
python manage.py createsuperuser
```
 
9. **Run the server**
```bash
python manage.py runserver
```
API available at `http://127.0.0.1:8000/`.
 
## Running Tests
 
```bash
python manage.py test workout
python manage.py test nutrition
```
Expect `Ran 55 tests ... OK` and `Ran 14 tests ... OK` respectively.
 
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
 
### Workout
 
| Method | Endpoint | Description |
|---|---|---|
| `GET` / `POST` | `/api/workouts/` | List / create your workouts (paginated, filterable) |
| `GET` / `PATCH` / `PUT` / `DELETE` | `/api/workouts/{id}/` | Retrieve / update / delete one |
| `GET` / `POST` | `/api/bodymeasurements/` | List / create your body measurements |
| `GET` / `PATCH` / `DELETE` | `/api/bodymeasurements/{id}/` | Retrieve / update / delete one |
| `GET` | `/api/profile/` | List your profile |
| `GET` / `PATCH` | `/api/profile/{id}/` | Retrieve / update your profile |
| `DELETE` | `/api/profile/{id}/` | **Deletes your entire account** (cascades to all your data) |
 
### Nutrition
 
| Method | Endpoint | Description |
|---|---|---|
| `GET` / `POST` | `/api/foods/` | List / create foods (shared reference data, not user-owned) |
| `GET` / `PATCH` / `DELETE` | `/api/foods/{id}/` | Retrieve / update / delete one |
| `GET` / `POST` | `/api/meal-plans/` | List / create your meal plans |
| `GET` / `PATCH` / `DELETE` | `/api/meal-plans/{id}/` | Retrieve / update / delete one |
| `GET` / `POST` | `/api/planned-meals/` | List / create planned meals within your plans |
| `GET` / `POST` | `/api/logged-meals/` | List / create logged meals (filterable by date) |
| `GET` / `POST` | `/api/meal-items/` | List / create items within your logged meals |
 
### Auth
 
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/login/` | Obtain an auth token |
 
### Filtering
 
- `?date=YYYY-MM-DD` — exact date match
- `?date_after=YYYY-MM-DD` — on or after
- `?date_before=YYYY-MM-DD` — on or before
- `?workout_type=running` — case-insensitive partial match (workouts only)
- `?meal_type=breakfast` — exact match (logged meals)
- `?name=egg` — case-insensitive partial match (foods)
### Pagination
 
- `?page=2` — page number
- `?page_size=5` — override default page size (capped at `max_page_size`)
## Database Schema
 
Five `nutrition` models, normalized with foreign keys and enforced at the database level:
 
```
Food ──< MealItem >── LoggedMeal   (user's actual eating history)
Food ──< PlannedMeal >── MealPlan  (user's forward-looking plan)
```
 
- **`Food`** — shared reference data (name, brand, calories/protein/carbs/fat per 100g)
- **`LoggedMeal`** — one meal slot (user, date, meal_type) actually eaten
- **`MealItem`** — one food + quantity within a `LoggedMeal`
- **`MealPlan`** — a named, dated plan (e.g. "Race week")
- **`PlannedMeal`** — one food + quantity within a `MealPlan`, for a specific day/slot
**Deletion behavior is deliberate per relationship:** `MealItem.food` and `PlannedMeal.food` use `on_delete=PROTECT` (a `Food` referenced by history can't be deleted); every other foreign key uses `CASCADE` (child rows are meaningless without their parent).
 
**Constraints enforced by PostgreSQL itself** (verifiable via `psql`'s `\d <table>`, not just present in Django code):
 
| Table | Constraint | Rule |
|---|---|---|
| `nutrition_food` | `unique_food_name_brand` | No duplicate (name, brand) |
| `nutrition_food` | `food_*_nonnegative` (×4) | Calories/protein/carbs/fat ≥ 0 |
| `nutrition_loggedmeal` | `unique_logged_meal_slot_per_user` | One meal per (user, date, meal_type) |
| `nutrition_mealitem` | `unique_food_per_logged_meal` | No duplicate food within one logged meal |
| `nutrition_mealitem` | `meal_item_quantity_positive` | quantity_g > 0 |
| `nutrition_mealplan` | `unique_mealplan_name_per_user` | No duplicate plan name per user |
| `nutrition_mealplan` | `mealplan_end_after_start` | end_date ≥ start_date |
| `nutrition_plannedmeal` | `unique_planned_food_per_slot` | No duplicate food in one plan slot |
| `nutrition_plannedmeal` | `plannedmeal_quantity_positive` | quantity_g > 0 |
| `nutrition_loggedmeal` | `loggedmeal_date_idx` (index, not constraint) | Speeds up date filtering/sorting |
 
`workout` app constraints follow the same pattern (`workout_duration_positive`, `unique_bodymeasurement_per_user_per_day`, `bodymeasurement_bodyfat_in_range`, `profile_age_nonnegative`, etc.).
 
## Seed Data
 
Two separate commands, run in order:
 
```bash
python manage.py seed_nutrition
```
Creates a small, realistic demo dataset: 12 real foods, one demo user, one meal plan, one logged breakfast. Safe to rerun (uses `get_or_create` throughout).
 
```bash
python manage.py seed_bulk --users 50 --days 60
```
Generates bulk volume (~12,000 `LoggedMeal` rows, ~24,000 `MealItem` rows) across many users and dates — needed to make query-performance differences (N+1 query counts, index speedup) actually measurable. Requires `seed_nutrition` to have run first (needs existing `Food` rows). Uses `bulk_create` for speed and `ignore_conflicts=True` for safe reruns.
 
## Query Performance
 
**N+1 fix:** `LoggedMealViewSet.get_queryset()` uses `.prefetch_related('items__food')` so listing meals fetches all items and foods in a fixed number of extra queries, instead of one query per meal plus one per item. Measured directly: 14 queries → 7 queries for the same request, and the count stays at 7 regardless of how many rows exist (`nutrition/tests/test_performance.py`).
 
**Index:** `LoggedMeal` has a database index on `date` (`loggedmeal_date_idx`), since it's filtered and sorted on constantly. Verified with `EXPLAIN ANALYZE` against bulk-seeded data — before the index, Postgres does a `Seq Scan` (reads every row); after, an `Index Scan` (jumps straight to matches), with a measurably lower `actual time`.
 
To reproduce the before/after comparison:
```bash
psql -U workout_user -h localhost -d nutrition_log -c "DROP INDEX IF EXISTS loggedmeal_date_idx;"
psql -U workout_user -h localhost -d nutrition_log -c "EXPLAIN ANALYZE SELECT * FROM nutrition_loggedmeal WHERE date = '2026-06-15';"
python manage.py migrate
psql -U workout_user -h localhost -d nutrition_log -c "EXPLAIN ANALYZE SELECT * FROM nutrition_loggedmeal WHERE date = '2026-06-15';"
```
 
## Project Structure
 
```
workout_nutrition_log_api/
├── manage.py
├── pyproject.toml
├── .env.example
├── config/
│   ├── urls.py
│   └── settings/
│       ├── base.py
│       ├── dev.py       # PostgreSQL via DATABASE_URL
│       └── prod.py
├── workout/
│   ├── models.py         # WorkOut, BodyMeasurement, Profile + constraints
│   ├── serializers.py
│   ├── permissions.py
│   ├── views.py
│   ├── urls.py
│   ├── filtering.py
│   ├── pagination.py
│   └── tests/
└── nutrition/
    ├── models.py          # Food, LoggedMeal, MealItem, MealPlan, PlannedMeal + constraints + index
    ├── serializers.py
    ├── permissions.py
    ├── views.py            # prefetch_related fix on LoggedMealViewSet
    ├── urls.py
    ├── filtering.py
    ├── migrations/
    │   ├── 0001_initial.py
    │   └── 0002_loggedmeal_loggedmeal_date_idx.py
    ├── management/commands/
    │   ├── seed_nutrition.py   # small realistic dataset
    │   └── seed_bulk.py        # bulk volume for performance testing
    └── tests/
        ├── test_constraints.py    # 12 tests - DB-level constraint rejection
        └── test_performance.py    # 2 tests - assertNumQueries, N+1 regression
```
 








