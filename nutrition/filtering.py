import django_filters
from .models import Food, LoggedMeal


class FoodFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Food
        fields = ['name', 'brand']


class LoggedMealFilter(django_filters.FilterSet):
    date_after = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_before = django_filters.DateFilter(field_name='date', lookup_expr='lte')

    class Meta:
        model = LoggedMeal
        fields = ['date', 'meal_type']