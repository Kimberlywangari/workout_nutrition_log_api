import datetime
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from nutrition.models import Food, MealPlan, PlannedMeal, LoggedMeal, MealItem


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
]


class Command(BaseCommand):
    help = "Seed realistic sample nutrition data (idempotent - safe to rerun)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--username', default='demo_user',
            help='User to seed meal plans/logs for (created if missing).',
        )

    def handle(self, *args, **options):
        username = options['username']
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password('demo-password-123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created user '{username}'"))

        foods = {}
        for name, brand, kcal, protein, carbs, fat in FOODS:
            food, _ = Food.objects.get_or_create(
                name=name, brand=brand,
                defaults=dict(
                    calories_per_100g=kcal, protein_g=protein,
                    carbs_g=carbs, fat_g=fat,
                ),
            )
            foods[name] = food
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(foods)} Food rows"))

        today = datetime.date.today()

        plan, _ = MealPlan.objects.get_or_create(
            user=user, name="Sample training week",
            defaults=dict(start_date=today, end_date=today + datetime.timedelta(days=6)),
        )
        PlannedMeal.objects.get_or_create(
            meal_plan=plan, food=foods["Chicken breast, grilled"],
            planned_date=today, meal_type="lunch",
            defaults=dict(quantity_g=200),
        )
        PlannedMeal.objects.get_or_create(
            meal_plan=plan, food=foods["Sweet potato, boiled"],
            planned_date=today, meal_type="lunch",
            defaults=dict(quantity_g=150),
        )
        self.stdout.write(self.style.SUCCESS(f"Seeded meal plan '{plan.name}'"))

        logged_meal, _ = LoggedMeal.objects.get_or_create(
            user=user, date=today, meal_type="breakfast",
        )
        MealItem.objects.get_or_create(
            logged_meal=logged_meal, food=foods["Eggs"],
            defaults=dict(quantity_g=120),
        )
        MealItem.objects.get_or_create(
            logged_meal=logged_meal, food=foods["Chapati"],
            defaults=dict(quantity_g=80),
        )
        self.stdout.write(self.style.SUCCESS("Seeded a logged breakfast"))
        self.stdout.write(self.style.SUCCESS("Done."))