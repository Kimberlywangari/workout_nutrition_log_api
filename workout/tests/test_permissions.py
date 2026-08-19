from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from workout.models import WorkOut, BodyMeasurement, Profile


class NonOwnerPermissionTests(APITestCase):
    """
    Proves that a logged-in user cannot view, edit, or delete
    another user's objects, across all three resources.
    """

    def setUp(self):
        self.owner = User.objects.create_user(username="fauna", password="pass123")
        self.intruder = User.objects.create_user(username="kimberly", password="pass456")

        self.owner_token = Token.objects.create(user=self.owner)
        self.intruder_token = Token.objects.create(user=self.intruder)

        self.workout = WorkOut.objects.create(
            user=self.owner, workout_type="Running", duration=45,
            date="2026-08-17", location="Eldoret",
        )
        self.measurement = BodyMeasurement.objects.create(
            user=self.owner, weight=68.5, height=165, date="2026-08-17",
        )
        self.owner_profile = Profile.objects.get(user=self.owner)

    def authenticate_as_intruder(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.intruder_token.key}")

    def authenticate_as_owner(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.owner_token.key}")

    # ---------- WorkOut ----------

    def test_non_owner_cannot_view_workout(self):
        self.authenticate_as_intruder()
        response = self.client.get(f"/api/workouts/{self.workout.id}/")
        self.assertEqual(response.status_code, 404)

    def test_non_owner_cannot_update_workout(self):
        self.authenticate_as_intruder()
        response = self.client.patch(f"/api/workouts/{self.workout.id}/", {"duration": 999})
        self.assertEqual(response.status_code, 404)

    def test_non_owner_cannot_delete_workout(self):
        self.authenticate_as_intruder()
        response = self.client.delete(f"/api/workouts/{self.workout.id}/")
        self.assertEqual(response.status_code, 404)
        self.assertTrue(WorkOut.objects.filter(id=self.workout.id).exists())

    def test_non_owner_workout_list_excludes_others_data(self):
        self.authenticate_as_intruder()
        response = self.client.get("/api/workouts/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)

    # ---------- BodyMeasurement ----------

    def test_non_owner_cannot_view_measurement(self):
        self.authenticate_as_intruder()
        response = self.client.get(f"/api/bodymeasurements/{self.measurement.id}/")
        self.assertEqual(response.status_code, 404)

    def test_non_owner_cannot_update_measurement(self):
        self.authenticate_as_intruder()
        response = self.client.patch(f"/api/bodymeasurements/{self.measurement.id}/", {"weight": 999})
        self.assertEqual(response.status_code, 404)

    def test_non_owner_cannot_delete_measurement(self):
        self.authenticate_as_intruder()
        response = self.client.delete(f"/api/bodymeasurements/{self.measurement.id}/")
        self.assertEqual(response.status_code, 404)
        self.assertTrue(BodyMeasurement.objects.filter(id=self.measurement.id).exists())

    # ---------- Profile ----------

    def test_non_owner_cannot_view_profile(self):
        self.authenticate_as_intruder()
        response = self.client.get(f"/api/profile/{self.owner_profile.id}/")
        self.assertEqual(response.status_code, 404)

    def test_non_owner_cannot_update_profile(self):
        self.authenticate_as_intruder()
        response = self.client.patch(f"/api/profile/{self.owner_profile.id}/", {"age": 99})
        self.assertEqual(response.status_code, 404)

    def test_non_owner_cannot_delete_profile(self):
        self.authenticate_as_intruder()
        response = self.client.delete(f"/api/profile/{self.owner_profile.id}/")
        self.assertEqual(response.status_code, 404)
        self.assertTrue(User.objects.filter(id=self.owner.id).exists())

    # ---------- Confirms the owner is unaffected throughout ----------

    def test_owner_can_still_access_their_own_workout(self):
        self.authenticate_as_owner()
        response = self.client.get(f"/api/workouts/{self.workout.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["workout_type"], "Running")