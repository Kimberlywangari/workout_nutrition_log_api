from rest_framework import permissions
from .models import LoggedMeal


def _is_their_trainer(request_user, owner_user):
    profile = getattr(request_user, 'profile', None)
    owner_profile = getattr(owner_user, 'profile', None)
    return bool(
        profile and profile.role == 'trainer'
        and owner_profile and owner_profile.trainer_id == request_user.id
    )


class IsMealOwner(permissions.BasePermission):
    """For MealPlan and LoggedMeal, which have a direct `user` field."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if obj.user == request.user:
            return True
        if not _is_their_trainer(request.user, obj.user):
            return False
        if isinstance(obj, LoggedMeal):
            return request.method in permissions.SAFE_METHODS  # progress viewing only
        return True  # MealPlan - the trainer assigned it


class IsPlannedMealOwner(permissions.BasePermission):
    """PlannedMeal has no direct user field - ownership is via meal_plan.user."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if obj.meal_plan.user == request.user:
            return True
        return _is_their_trainer(request.user, obj.meal_plan.user)


class IsMealItemOwner(permissions.BasePermission):
    """MealItem has no direct user field - ownership is via logged_meal.user."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.logged_meal.user == request.user