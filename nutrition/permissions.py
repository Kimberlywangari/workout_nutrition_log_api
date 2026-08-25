from rest_framework import permissions


class IsMealOwner(permissions.BasePermission):
    """For MealPlan and LoggedMeal, which have a direct `user` field."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.user == request.user


class IsPlannedMealOwner(permissions.BasePermission):
    """PlannedMeal has no direct user field - ownership is via meal_plan.user."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.meal_plan.user == request.user


class IsMealItemOwner(permissions.BasePermission):
    """MealItem has no direct user field - ownership is via logged_meal.user."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.logged_meal.user == request.user