import django_filters
from .models import WorkOut, BodyMeasurement


class WorkOutFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(field_name='date')
    date_after = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_before = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    workout_type = django_filters.CharFilter(field_name='workout_type', lookup_expr='icontains')

    class Meta:
        model = WorkOut
        fields = ['date', 'workout_type']


class BodyMeasurementFilter(django_filters.FilterSet):
    date_after = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_before = django_filters.DateFilter(field_name='date', lookup_expr='lte')

    class Meta:
        model = BodyMeasurement
        fields = ['date']