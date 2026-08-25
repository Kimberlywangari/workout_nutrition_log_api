
import datetime
from django.contrib.auth.models import User
from django.db import IntegrityError, connection, transaction
from django.db.models import ProtectedError
from django.test import TestCase, TransactionTestCase

from nutrition.models import Food, MealPlan, PlannedMeal, LoggedMeal, MealItem


class FoodConstraintTests(TestCase):
    def setUp(self):
        self.food = Food.objects.create(
            name="Ugali", brand="", calories_per_100g=122,
            protein_g=2.5, carbs_g=27.0, fat_g=0.5,
        )

    def test_duplicate_name_brand_rejected(self):
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Food.objects.create(
                    name="Ugali", brand="", calories_per_100g=130,
                    protein_g=3.0, carbs_g=28.0, fat_g=0.6,
                )

    def test_negative_calories_rejected(self):
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Food.objects.create(
                    name="Broken food", brand="", calories_per_100g=-5,
                    protein_g=1.0, carbs_g=1.0, fat_g=1.0,
                )

    def test_null_calories_rejected(self):
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Food.objects.create(
                    name="No calories", brand="", calories_per_100g=None,
                    protein_g=1.0, carbs_g=1.0, fat_g=1.0,
                )


class MealPlanConstraintTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="fauna", password="x")
        self.today = datetime.date.today()

    def test_duplicate_plan_name_per_user_rejected(self):
        MealPlan.objects.create(
            user=self.user, name="Race week",
            start_date=self.today, end_date=self.today,
        )
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                MealPlan.objects.create(
                    user=self.user, name="Race week",
                    start_date=self.today, end_date=self.today,
                )

    def test_end_before_start_rejected(self):
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                MealPlan.objects.create(
                    user=self.user, name="Backwards plan",
                    start_date=self.today,
                    end_date=self.today - datetime.timedelta(days=1),
                )


class PlannedMealConstraintTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="fauna", password="x")
        self.today = datetime.date.today()
        self.plan = MealPlan.objects.create(
            user=self.user, name="Race week",
            start_date=self.today, end_date=self.today,
        )
        self.food = Food.objects.create(
            name="Chicken breast", brand="", calories_per_100g=165,
            protein_g=31, carbs_g=0, fat_g=3.6,
        )

    def test_duplicate_slot_rejected(self):
        PlannedMeal.objects.create(
            meal_plan=self.plan, food=self.food,
            planned_date=self.today, meal_type="lunch", quantity_g=200,
        )
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                PlannedMeal.objects.create(
                    meal_plan=self.plan, food=self.food,
                    planned_date=self.today, meal_type="lunch", quantity_g=150,
                )

    def test_zero_quantity_rejected(self):
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                PlannedMeal.objects.create(
                    meal_plan=self.plan, food=self.food,
                    planned_date=self.today, meal_type="dinner", quantity_g=0,
                )

    def test_deleting_referenced_food_is_blocked(self):
        PlannedMeal.objects.create(
            meal_plan=self.plan, food=self.food,
            planned_date=self.today, meal_type="lunch", quantity_g=200,
        )
        with self.assertRaises(ProtectedError):
            self.food.delete()


class OrphanedForeignKeyTests(TransactionTestCase):
    """
    Uses TransactionTestCase, not TestCase, on purpose: TestCase wraps each
    test in one big transaction, and Django defers SQLite's foreign-key
    checking inside that wrapper. TransactionTestCase runs each test
    without that wrapping, so the constraint is checked immediately -
    matching what PostgreSQL does per-statement regardless of backend.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="fauna", password="x")
        self.today = datetime.date.today()
        self.plan = MealPlan.objects.create(
            user=self.user, name="Race week",
            start_date=self.today, end_date=self.today,
        )
        self.food = Food.objects.create(
            name="Chicken breast", brand="", calories_per_100g=165,
            protein_g=31, carbs_g=0, fat_g=3.6,
        )

    def test_orphaned_food_fk_rejected_at_db_level(self):
        nonexistent_food_id = self.food.id + 9999
        with self.assertRaises(IntegrityError):
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO nutrition_plannedmeal
                        (meal_plan_id, food_id, planned_date, meal_type, quantity_g)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    [self.plan.id, nonexistent_food_id, self.today, "snack", 50],
                )


class LoggedMealConstraintTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="fauna", password="x")
        self.today = datetime.date.today()
        self.food = Food.objects.create(
            name="Eggs", brand="", calories_per_100g=155,
            protein_g=13, carbs_g=1.1, fat_g=11,
        )

    def test_duplicate_meal_slot_per_user_rejected(self):
        LoggedMeal.objects.create(user=self.user, date=self.today, meal_type="breakfast")
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                LoggedMeal.objects.create(
                    user=self.user, date=self.today, meal_type="breakfast"
                )

    def test_duplicate_food_within_meal_rejected(self):
        meal = LoggedMeal.objects.create(
            user=self.user, date=self.today, meal_type="breakfast"
        )
        MealItem.objects.create(logged_meal=meal, food=self.food, quantity_g=100)
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                MealItem.objects.create(
                    logged_meal=meal, food=self.food, quantity_g=50
                )

    def test_negative_quantity_rejected(self):
        meal = LoggedMeal.objects.create(
            user=self.user, date=self.today, meal_type="lunch"
        )
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                MealItem.objects.create(
                    logged_meal=meal, food=self.food, quantity_g=-10
                )