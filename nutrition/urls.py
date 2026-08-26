from rest_framework.routers import DefaultRouter
from .views import (
    FoodViewSet, MealPlanViewSet, NutritionProfileViewSet, PlannedMealViewSet,
    LoggedMealViewSet, MealItemViewSet,
)

router = DefaultRouter()
router.register(r'foods', FoodViewSet, basename='food')
router.register(r'meal-plans', MealPlanViewSet, basename='mealplan')
router.register(r'planned-meals', PlannedMealViewSet, basename='plannedmeal')
router.register(r'logged-meals', LoggedMealViewSet, basename='loggedmeal')
router.register(r'meal-items', MealItemViewSet, basename='mealitem')
router.register(r'nutrition-profile', NutritionProfileViewSet, basename='nutritionprofile')

urlpatterns = router.urls