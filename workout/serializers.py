from rest_framework import serializers
from .models import WorkOut, BodyMeasurement, Profile
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class TrainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    role = serializers.ChoiceField(choices=Profile.ROLE_CHOICES, write_only=True)
    trainer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(profile__role='trainer'),
        source='trainer', write_only=True, required=False, allow_null=True,
    )

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'role', 'trainer_id']

    def validate(self, data):
        role = data.get('role')
        trainer = data.get('trainer')
        if role == 'trainee' and not trainer:
            raise serializers.ValidationError("Trainees must select a trainer.")
        if role == 'trainer' and trainer:
            raise serializers.ValidationError("Trainers cannot select a trainer.")
        return data

    def create(self, validated_data):
        role = validated_data.pop('role')
        trainer = validated_data.pop('trainer', None)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )
        # Profile already exists (post_save signal) - fill in role/trainer here.
        user.profile.role = role
        user.profile.trainer = trainer
        user.profile.save()
        return user


class WorkOutSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = WorkOut
        fields = ['id', 'user', 'workout_type', 'duration', 'date', 'location', 'calories_burnt']

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
        fields = ['id', 'user', 'weight', 'height', 'body_fat_percentage', 'date']

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
    trainer = serializers.ReadOnlyField(source='trainer.username', default=None)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'age', 'gender', 'role', 'trainer']
        read_only_fields = ['role', 'trainer']

    def validate_age(self, value):
        if value <= 0:
            raise serializers.ValidationError("Age must be greater than zero.")
        return value