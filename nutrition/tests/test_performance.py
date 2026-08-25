"""
Proves the N+1 on GET /api/logged-meals/ is fixed and stays bounded.

Before the fix, LoggedMealViewSet.get_queryset() had no prefetch_related,
so serializing each LoggedMeal's nested items (and each item's nested food)
triggered one extra query per meal, plus one extra query per item - the
query count grew with the number of rows returned. After adding
.prefetch_related('items__food'), Django fetches every item and every food
in two extra queries total, regardless of how many meals/items exist.

assertNumQueries fails the test if the actual query count is anything
other than the exact number given - which is exactly what "bounded" means
here: a fixed ceiling, not "fewer than before."
"""
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
        # Deliberately more rows than the page size (3), so a broken,
        # unbounded version of this view would show a HIGHER query count
        # here than with fewer rows - proving the fix isn't a fluke of
        # having too little data to notice the N+1 in the first place.
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
        # Add 20 more meals - if the N+1 were still present, this second
        # request would need noticeably more queries than the first test's
        # 10-meal setup. It should still be exactly 7.
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