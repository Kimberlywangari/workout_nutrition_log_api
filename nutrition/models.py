from django.db import models
from django.contrib.auth.models import User


class Food(models.Model):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100, blank=True, default='')
    calories_per_100g = models.FloatField()
    protein_g = models.FloatField()
    carbs_g = models.FloatField()
    fat_g = models.FloatField()

    class Meta:
            ordering = ['name']
            constraints = [
            models.UniqueConstraint(
                fields=['name', 'brand'], name='unique_food_name_brand'
            ),
            models.CheckConstraint(
                check=models.Q(calories_per_100g__gte=0),
                name='food_calories_nonnegative'),
            models.CheckConstraint(    
                check=models.Q(protein_g__gte=0),
                name='food_protein_nonnegative'),
            models.CheckConstraint(
                check=models.Q(carbs_g__gte=0),
                name='food_carbs_nonnegative'),
            models.CheckConstraint(
                check=models.Q(fat_g__gte=0),
                name='food_fat_nonnegative',
            ),
        ]

    def __str__(self):
            return f"{self.name} ({self.brand})" if self.brand else self.name
        

class LoggedMeal(models.Model):
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='logged_meals'
    )
    date = models.DateField()
    meal_type = models.CharField(max_length=10, choices=MEAL_TYPE_CHOICES)

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date'], name='loggedmeal_date_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'date', 'meal_type'],
                name='unique_logged_meal_slot_per_user',
            ),
        ]
    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.meal_type}"

    
    

class MealItem(models.Model):
    logged_meal = models.ForeignKey(
        LoggedMeal, on_delete=models.CASCADE, related_name='items'
    )
    food = models.ForeignKey(
        Food, on_delete=models.PROTECT, related_name='meal_items'
    )
    quantity_g = models.FloatField()

    class Meta:
                ordering = ['food__name']
                constraints = [
            models.UniqueConstraint(
                fields=['logged_meal', 'food'],
                name='unique_meal_item_per_logged_meal_and_food'
            ),
            models.CheckConstraint(
                check=models.Q(quantity_g__gt=0),
                name='meal_item_quantity_positive'
            )
        ]

    def __str__(self):
        return f"{self.logged_meal} - {self.food.name} - {self.quantity_g}g"

    

class MealPlan(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='meal_plans'
    )
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    
    class Meta:
        ordering = ['-start_date']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'], name='unique_mealplan_name_per_user'
            ),
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F('start_date')),
                name='mealplan_end_after_start',
            ),
        ]
    def __str__(self):
            return f"{self.user.username} - {self.name}"

class PlannedMeal(models.Model):
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]

    meal_plan = models.ForeignKey(
        MealPlan, on_delete=models.CASCADE, related_name='planned_meals'
    )
    food = models.ForeignKey(
        Food, on_delete=models.PROTECT, related_name='planned_meals'
    )
    planned_date = models.DateField()
    meal_type = models.CharField(max_length=10, choices=MEAL_TYPE_CHOICES)
    quantity_g = models.FloatField()

    class Meta:
        ordering = ['planned_date']
        constraints = [
            models.UniqueConstraint(
                fields=['meal_plan', 'food', 'planned_date', 'meal_type'],
                name='unique_planned_food_per_slot',
            ),
            models.CheckConstraint(
                check=models.Q(quantity_g__gt=0),
                name='plannedmeal_quantity_positive',
            ),
        ]


    def __str__(self):
        return f"{self.meal_plan.name} - {self.planned_date} - {self.meal_type} - {self.food.name}"

