import datetime
import random
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from nutrition.models import Food, MealPlan, PlannedMeal, LoggedMeal, MealItem, NutritionProfile

FOODS = [
    # name, brand, calories_per_100g, protein_g, carbs_g, fat_g
    ("Ugali", "", 122, 2.5, 27.0, 0.5),
    ("Sukuma wiki", "", 32, 2.9, 5.6, 0.4),
    ("Nyama choma (beef)", "", 250, 26.0, 0.0, 17.0),
    ("Chapati", "", 297, 6.0, 45.0, 10.0),
    ("Githeri", "", 130, 6.5, 22.0, 2.0),
    ("Brown rice, cooked", "", 111, 2.6, 23.0, 0.9),
    ("Chicken breast, grilled", "", 165, 31.0, 0.0, 3.6),
    ("Avocado", "", 160, 2.0, 8.5, 14.7),
    ("Banana", "", 89, 1.1, 22.8, 0.3),
    ("Whole milk", "Brookside", 61, 3.2, 4.8, 3.3),
    ("Eggs", "", 155, 13.0, 1.1, 11.0),
    ("Sweet potato, boiled", "", 86, 1.6, 20.1, 0.1),
    ("Beans, boiled", "", 127, 8.7, 22.8, 0.5),
    ("Mandazi", "", 297, 6.5, 43.0, 11.0),
    ("Tilapia, grilled", "", 128, 26.0, 0.0, 2.7),
    ("Spinach, cooked", "", 23, 2.9, 3.6, 0.3),
    ("Mango", "", 60, 0.8, 15.0, 0.4),
    ("Pilau rice", "", 175, 4.0, 30.0, 4.5),
    ("Yoghurt, plain", "Brookside", 61, 3.5, 4.7, 3.3),
    ("Groundnuts, roasted", "", 567, 25.8, 16.1, 49.2),
    ("White bread", "Supa Loaf", 265, 9.0, 49.0, 3.2),
    ("Peanut butter", "", 588, 25.0, 20.0, 50.0),
    ("Orange", "", 47, 0.9, 11.8, 0.1),
    ("Cabbage, cooked", "", 25, 1.3, 5.8, 0.1),
    ("Irish potatoes, boiled", "", 87, 1.9, 20.1, 0.1),
    ("Fish stew (omena)", "", 200, 18.0, 5.0, 12.0),
    ("Black tea with milk", "", 40, 1.2, 6.0, 1.0),
    ("Mursik", "", 98, 3.4, 5.2, 7.0),
    ("Watermelon", "", 30, 0.6, 7.6, 0.2),
    ("Samosa (beef)", "", 260, 8.0, 22.0, 16.0),
]


class Command(BaseCommand):
    help = "Seed a full nutrition dataset for a given user (default: kimberly)."

    def add_arguments(self, parser):
        parser.add_argument('--username', default='kimberly')
        parser.add_argument('--password', default='kimani123')

    def handle(self, *args, **options):
        username = options['username']
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password(options['password'])
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created user '{username}'"))

        foods = {}
        for name, brand, kcal, protein, carbs, fat in FOODS:
            food, _ = Food.objects.get_or_create(
                name=name, brand=brand,
                defaults=dict(calories_per_100g=kcal, protein_g=protein, carbs_g=carbs, fat_g=fat),
            )
            foods[name] = food
        food_list = list(foods.values())
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(food_list)} Food rows"))

        NutritionProfile.objects.update_or_create(
            user=user, defaults=dict(daily_calorie_target=2200, dietary_preference="omnivore"),
        )
        self.stdout.write(self.style.SUCCESS("Set nutrition profile"))

        today = datetime.date.today()
        meal_types = ["breakfast", "lunch", "dinner", "snack"]

        # Logged meals for the past 10 days - never today+ in the future.
        for d in range(10):
            log_date = today - datetime.timedelta(days=d)
            for meal_type in random.sample(meal_types, k=random.randint(2, 4)):
                meal, _ = LoggedMeal.objects.get_or_create(
                    user=user, date=log_date, meal_type=meal_type
                )
                for food in random.sample(food_list, k=random.randint(1, 3)):
                    MealItem.objects.get_or_create(
                        logged_meal=meal, food=food,
                        defaults=dict(quantity_g=random.randint(50, 300)),
                    )
        self.stdout.write(self.style.SUCCESS("Seeded 10 days of logged meals"))

        # A meal plan for the upcoming week, with planned meals inside its range.
        plan, _ = MealPlan.objects.get_or_create(
            user=user, name="This week",
            defaults=dict(start_date=today, end_date=today + datetime.timedelta(days=6)),
        )
        for d in range(7):
            plan_date = today + datetime.timedelta(days=d)
            for meal_type in random.sample(meal_types, k=2):
                for food in random.sample(food_list, k=random.randint(1, 2)):
                    PlannedMeal.objects.get_or_create(
                        meal_plan=plan, food=food, planned_date=plan_date, meal_type=meal_type,
                        defaults=dict(quantity_g=random.randint(50, 300)),
                    )
        self.stdout.write(self.style.SUCCESS(f"Seeded meal plan '{plan.name}'"))
        self.stdout.write(self.style.SUCCESS("Done."))