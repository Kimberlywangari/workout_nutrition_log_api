from rest_framework import serializers
from .models import Food, MealPlan, PlannedMeal, LoggedMeal, MealItem


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
        fields = ['id', 'food', 'food_id', 'quantity_g']

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


class MealPlanSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    planned_meals = PlannedMealSerializer(many=True, read_only=True)

    class Meta:
        model = MealPlan
        fields = ['id', 'user', 'name', 'start_date', 'end_date', 'planned_meals']

    def validate(self, data):
        start = data.get('start_date', getattr(self.instance, 'start_date', None))
        end = data.get('end_date', getattr(self.instance, 'end_date', None))
        if start and end and end < start:
            raise serializers.ValidationError("end_date cannot be before start_date.")
        return data