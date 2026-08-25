import random
import datetime
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from nutrition.models import Food, LoggedMeal, MealItem

MEAL_TYPES = ['breakfast', 'lunch', 'dinner', 'snack']


class Command(BaseCommand):
    help = "Bulk-seed thousands of LoggedMeal/MealItem rows for the N+1/indexing gate."

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=50)
        parser.add_argument('--days', type=int, default=60)

    def handle(self, *args, **options):
        num_users = options['users']
        num_days = options['days']

        foods = list(Food.objects.all())
        if not foods:
            self.stderr.write(self.style.ERROR(
                "No Food rows found - run 'python manage.py seed_nutrition' first."
            ))
            return

        base_date = datetime.date.today() - datetime.timedelta(days=num_days)
        end_date = base_date + datetime.timedelta(days=num_days)

        for u in range(num_users):
            username = f"bulk_user_{u}"
            user, _ = User.objects.get_or_create(username=username)

            meals_to_create = []
            for d in range(num_days):
                meal_date = base_date + datetime.timedelta(days=d)
                for meal_type in MEAL_TYPES:
                    meals_to_create.append(
                        LoggedMeal(user=user, date=meal_date, meal_type=meal_type)
                    )
            LoggedMeal.objects.bulk_create(meals_to_create, ignore_conflicts=True)

            # Re-fetch from the database rather than relying on bulk_create's
            # returned objects, since their .pk is not reliably populated
            # when ignore_conflicts=True on every backend.
            user_meals = list(LoggedMeal.objects.filter(
                user=user, date__gte=base_date, date__lt=end_date
            ))

            items_to_create = []
            for meal in user_meals:
                sample_foods = random.sample(foods, k=min(2, len(foods)))
                for food in sample_foods:
                    items_to_create.append(
                        MealItem(
                            logged_meal=meal, food=food,
                            quantity_g=random.randint(50, 300),
                        )
                    )
            MealItem.objects.bulk_create(items_to_create, ignore_conflicts=True)

            self.stdout.write(self.style.SUCCESS(
                f"Seeded {username}: {len(user_meals)} meals"
            ))

        self.stdout.write(self.style.SUCCESS("Bulk seed complete."))