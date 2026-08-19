from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from workout.models import WorkOut


class WorkOutCRUDTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="fauna", password="pass123")
        self.token = Token.objects.create(user=self.user)
        self.workout = WorkOut.objects.create(
            user=self.user,
            workout_type="Running",
            duration=45,
            date="2026-08-17",
            location="Eldoret",
        )

    def authenticate(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    # ---------- LIST ----------

    def test_list_workouts_success(self):
        self.authenticate()
        response = self.client.get("/api/workouts/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_list_workouts_unauthorized(self):
        response = self.client.get("/api/workouts/")
        self.assertEqual(response.status_code, 401)

    # ---------- CREATE ----------

    def test_create_workout_success(self):
        self.authenticate()
        response = self.client.post("/api/workouts/", {
            "workout_type": "Weights",
            "duration": 30,
            "date": "2026-08-18",
            "location": "Eldoret",
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["workout_type"], "Weights")
        self.assertEqual(response.data["user"], "fauna")

    def test_create_workout_invalid_duration(self):
        self.authenticate()
        response = self.client.post("/api/workouts/", {
            "workout_type": "Weights",
            "duration": -10,
            "date": "2026-08-18",
            "location": "Eldoret",
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("duration", response.data)

    def test_create_workout_unauthorized(self):
        response = self.client.post("/api/workouts/", {
            "workout_type": "Weights",
            "duration": 30,
            "date": "2026-08-18",
            "location": "Eldoret",
        })
        self.assertEqual(response.status_code, 401)

    # ---------- RETRIEVE ----------

    def test_retrieve_workout_success(self):
        self.authenticate()
        response = self.client.get(f"/api/workouts/{self.workout.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["workout_type"], "Running")

    def test_retrieve_workout_not_found(self):
        self.authenticate()
        response = self.client.get("/api/workouts/9999/")
        self.assertEqual(response.status_code, 404)

    def test_retrieve_workout_unauthorized(self):
        response = self.client.get(f"/api/workouts/{self.workout.id}/")
        self.assertEqual(response.status_code, 401)

    # ---------- UPDATE ----------

    def test_update_workout_success(self):
        self.authenticate()
        response = self.client.patch(f"/api/workouts/{self.workout.id}/", {
            "duration": 60,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["duration"], 60)

    def test_update_workout_invalid_duration(self):
        self.authenticate()
        response = self.client.patch(f"/api/workouts/{self.workout.id}/", {
            "duration": -5,
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("duration", response.data)

    def test_update_workout_not_found(self):
        self.authenticate()
        response = self.client.patch("/api/workouts/9999/", {"duration": 60})
        self.assertEqual(response.status_code, 404)

    def test_update_workout_unauthorized(self):
        response = self.client.patch(f"/api/workouts/{self.workout.id}/", {"duration": 60})
        self.assertEqual(response.status_code, 401)

    # ---------- DELETE ----------

    def test_delete_workout_success(self):
        self.authenticate()
        response = self.client.delete(f"/api/workouts/{self.workout.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(WorkOut.objects.filter(id=self.workout.id).exists())

    def test_delete_workout_not_found(self):
        self.authenticate()
        response = self.client.delete("/api/workouts/9999/")
        self.assertEqual(response.status_code, 404)

    def test_delete_workout_unauthorized(self):
        response = self.client.delete(f"/api/workouts/{self.workout.id}/")
        self.assertEqual(response.status_code, 401)