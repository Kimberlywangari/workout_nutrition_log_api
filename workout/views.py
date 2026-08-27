from rest_framework import viewsets, permissions, mixins, generics, status
from .models import WorkOut, BodyMeasurement, Profile
from .serializers import (
    WorkOutSerializer, BodyMeasurementSerializer, ProfileSerializer,
    RegisterSerializer, TrainerSerializer,
)
from .permissions import IsOwner
from .filtering import WorkOutFilter, BodyMeasurementFilter

from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TrainerListView(generics.ListAPIView):
    """Public list of trainers, for the registration form's trainer picker."""
    queryset = User.objects.filter(profile__role='trainer').order_by('username')
    serializer_class = TrainerSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None  # this list needs to be complete, not page-1-only


class MyTraineesView(generics.ListAPIView):
    """A trainer's own linked trainees, for the meal-plan assignment picker."""
    serializer_class = TrainerSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return User.objects.filter(profile__trainer=self.request.user).order_by('username')


class WorkOutViewSet(viewsets.ModelViewSet):
    serializer_class = WorkOutSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    filterset_class = WorkOutFilter

    def get_queryset(self):
        if self.request.user.is_superuser:
            return WorkOut.objects.all()
        return WorkOut.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BodyMeasurementViewSet(viewsets.ModelViewSet):
    serializer_class = BodyMeasurementSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    filterset_class = BodyMeasurementFilter

    def get_queryset(self):
        if self.request.user.is_superuser:
            return BodyMeasurement.objects.all()
        return BodyMeasurement.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProfileViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Profile.objects.all()
        return Profile.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        instance.user.delete()