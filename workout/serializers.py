from rest_framework import serializers
from .models import WorkOut, BodyMeasurement, Profile


class WorkOutSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = WorkOut
        fields = [
            'id',
            'user',
            'workout_type',
            'duration',
            'date',
            'location',
            'calories_burnt',
        ]

    def validate_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError("Duration must be greater than zero.")
        return value

    def validate_calories_burnt(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Calories burnt cannot be negative.")
        return value


class BodyMeasurementSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = BodyMeasurement
        fields = [
            'id',
            'user',
            'weight',
            'height',
            'body_fat_percentage',
            'date',
        ]

    def validate_weight(self, value):
        if value <= 0:
            raise serializers.ValidationError("Weight must be greater than zero.")
        return value

    def validate_height(self, value):
        if value <= 0:
            raise serializers.ValidationError("Height must be greater than zero.")
        return value

    def validate_body_fat_percentage(self, value):
        if value is not None and not (0 <= value <= 100):
            raise serializers.ValidationError("Body fat percentage must be between 0 and 100.")
        return value


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Profile
        fields = [
            'id',
            'user',
            'age',
            'gender',
        ]

    def validate_age(self, value):
        if value <= 0:
            raise serializers.ValidationError("Age must be greater than zero.")
        return value