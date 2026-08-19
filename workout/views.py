from rest_framework import viewsets, permissions, mixins
from .models import WorkOut, BodyMeasurement, Profile
from .serializers import WorkOutSerializer, BodyMeasurementSerializer, ProfileSerializer
from .permissions import IsOwner
from .filtering import WorkOutFilter, BodyMeasurementFilter


class WorkOutViewSet(viewsets.ModelViewSet):
    serializer_class = WorkOutSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    filterset_class = WorkOutFilter

    def get_queryset(self):
        return WorkOut.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BodyMeasurementViewSet(viewsets.ModelViewSet):
    serializer_class = BodyMeasurementSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    filterset_class = BodyMeasurementFilter

    def get_queryset(self):
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
        return Profile.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        instance.user.delete()