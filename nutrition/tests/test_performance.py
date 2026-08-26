import datetime
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from nutrition.models import Food, LoggedMeal, MealItem


class LoggedMealNPlusOneTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="perfuser", password="x")
        self.food_a = Food.objects.create(
            name="Perf Food A", brand="", calories_per_100g=100,
            protein_g=1, carbs_g=1, fat_g=1,
        )
        self.food_b = Food.objects.create(
            name="Perf Food B", brand="", calories_per_100g=100,
            protein_g=1, carbs_g=1, fat_g=1,
        )
        today = datetime.date.today()
       
        for i in range(10):
            meal = LoggedMeal.objects.create(
                user=self.user,
                date=today - datetime.timedelta(days=i),
                meal_type="breakfast" if i % 2 == 0 else "lunch",
            )
            MealItem.objects.create(logged_meal=meal, food=self.food_a, quantity_g=100)
            MealItem.objects.create(logged_meal=meal, food=self.food_b, quantity_g=100)

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_logged_meal_list_query_count_is_bounded(self):
        with self.assertNumQueries(7):
            response = self.client.get('/api/logged-meals/')
        self.assertEqual(response.status_code, 200)

    def test_query_count_does_not_grow_with_more_rows(self):
        today = datetime.date.today()
        for i in range(10, 30):
            meal = LoggedMeal.objects.create(
                user=self.user,
                date=today - datetime.timedelta(days=i),
                meal_type="dinner",
            )
            MealItem.objects.create(logged_meal=meal, food=self.food_a, quantity_g=50)

        with self.assertNumQueries(7):
            response = self.client.get('/api/logged-meals/')
        self.assertEqual(response.status_code, 200)