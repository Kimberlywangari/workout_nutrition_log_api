from rest_framework import viewsets, permissions
from .models import Food, MealPlan, PlannedMeal, LoggedMeal, MealItem, NutritionProfile
from .serializers import (
    FoodSerializer, MealPlanSerializer, NutritionProfileSerializer, PlannedMealSerializer,
    LoggedMealSerializer, MealItemSerializer,
)
from .permissions import IsMealOwner, IsPlannedMealOwner, IsMealItemOwner
from .filtering import FoodFilter, LoggedMealFilter


class NutritionProfileViewSet(viewsets.ModelViewSet):
    serializer_class = NutritionProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsMealOwner]
    http_method_names = ['get', 'patch']  

    def get_queryset(self):
        if self.request.user.is_superuser:
            return NutritionProfile.objects.all()
        return NutritionProfile.objects.filter(user=self.request.user)
class FoodViewSet(viewsets.ModelViewSet):
    """Shared reference data - not owned by any one user."""
    queryset = Food.objects.all()
    serializer_class = FoodSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = FoodFilter


class MealPlanViewSet(viewsets.ModelViewSet):
    serializer_class = MealPlanSerializer
    permission_classes = [permissions.IsAuthenticated, IsMealOwner]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return MealPlan.objects.all()
        return MealPlan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PlannedMealViewSet(viewsets.ModelViewSet):
    serializer_class = PlannedMealSerializer
    permission_classes = [permissions.IsAuthenticated, IsPlannedMealOwner]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return PlannedMeal.objects.all()
        return PlannedMeal.objects.filter(meal_plan__user=self.request.user)


class LoggedMealViewSet(viewsets.ModelViewSet):
    serializer_class = LoggedMealSerializer
    permission_classes = [permissions.IsAuthenticated, IsMealOwner]
    filterset_class = LoggedMealFilter

    def get_queryset(self):
        if self.request.user.is_superuser:
            return LoggedMeal.objects.prefetch_related('items__food').all()
        return LoggedMeal.objects.filter(user=self.request.user).prefetch_related('items__food')
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MealItemViewSet(viewsets.ModelViewSet):
    serializer_class = MealItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsMealItemOwner]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return MealItem.objects.all()
        return MealItem.objects.filter(logged_meal__user=self.request.user)