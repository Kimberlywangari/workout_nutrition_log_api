from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Food, MealPlan, PlannedMeal, LoggedMeal, MealItem, NutritionProfile


class NutritionProfileSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = NutritionProfile
        fields = ['id', 'user', 'daily_calorie_target', 'dietary_preference']


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ['id', 'name', 'brand', 'calories_per_100g', 'protein_g', 'carbs_g', 'fat_g']

    def validate_calories_per_100g(self, value):
        if value < 0:
            raise serializers.ValidationError("Calories cannot be negative.")
        return value


class MealItemSerializer(serializers.ModelSerializer):
    food = FoodSerializer(read_only=True)
    food_id = serializers.PrimaryKeyRelatedField(
        queryset=Food.objects.all(), source='food', write_only=True
    )

    class Meta:
        model = MealItem
        fields = ['id', 'logged_meal', 'food', 'food_id', 'quantity_g']

    def validate_quantity_g(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value


class LoggedMealSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    items = MealItemSerializer(many=True, read_only=True)

    class Meta:
        model = LoggedMeal
        fields = ['id', 'user', 'date', 'meal_type', 'items']

    def validate_date(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError("Logged meal date cannot be in the future.")
        return value

    def validate(self, data):
        # 'user' is read-only, so the auto-generated UniqueTogetherValidator
        # from Meta.constraints can't be trusted to fire correctly on create -
        # check it explicitly instead, and give a message people understand.
        request = self.context.get('request')
        date = data.get('date', getattr(self.instance, 'date', None))
        meal_type = data.get('meal_type', getattr(self.instance, 'meal_type', None))
        if request and date and meal_type:
            qs = LoggedMeal.objects.filter(user=request.user, date=date, meal_type=meal_type)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    f"You already have a {meal_type} logged for {date}."
                )
        return data


class PlannedMealSerializer(serializers.ModelSerializer):
    food = FoodSerializer(read_only=True)
    food_id = serializers.PrimaryKeyRelatedField(
        queryset=Food.objects.all(), source='food', write_only=True
    )

    class Meta:
        model = PlannedMeal
        fields = ['id', 'meal_plan', 'food', 'food_id', 'planned_date', 'meal_type', 'quantity_g']

    def validate_quantity_g(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value

    def validate(self, data):
        meal_plan = data.get('meal_plan', getattr(self.instance, 'meal_plan', None))
        planned_date = data.get('planned_date', getattr(self.instance, 'planned_date', None))
        food = data.get('food', getattr(self.instance, 'food', None))
        meal_type = data.get('meal_type', getattr(self.instance, 'meal_type', None))

        if meal_plan and planned_date:
            if not (meal_plan.start_date <= planned_date <= meal_plan.end_date):
                raise serializers.ValidationError(
                    f"planned_date must fall between {meal_plan.start_date} "
                    f"and {meal_plan.end_date} for this meal plan."
                )

        if meal_plan and food and planned_date and meal_type:
            qs = PlannedMeal.objects.filter(
                meal_plan=meal_plan, food=food, planned_date=planned_date, meal_type=meal_type
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    f"You've already added {food.name} to {meal_type} on {planned_date}."
                )
        return data


class MealPlanSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    planned_meals = PlannedMealSerializer(many=True, read_only=True)
    trainee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True, required=False,
    )

    class Meta:
        model = MealPlan
        fields = ['id', 'user', 'name', 'start_date', 'end_date', 'planned_meals', 'trainee_id']

    def validate(self, data):
        start = data.get('start_date', getattr(self.instance, 'start_date', None))
        end = data.get('end_date', getattr(self.instance, 'end_date', None))
        if start and end and end < start:
            raise serializers.ValidationError("end_date cannot be before start_date.")

        request = self.context.get('request')
        trainee = data.get('user')  # only present if trainee_id was supplied
        if trainee and request:
            profile = getattr(request.user, 'profile', None)
            if not profile or profile.role != 'trainer':
                raise serializers.ValidationError("Only trainers can assign a plan to someone else.")
            trainee_profile = getattr(trainee, 'profile', None)
            if not trainee_profile or trainee_profile.trainer_id != request.user.id:
                raise serializers.ValidationError("You can only assign plans to your own trainees.")
        return data