from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from workout.models import BodyMeasurement


class BodyMeasurementCRUDTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="fauna", password="pass123")
        self.token = Token.objects.create(user=self.user)
        self.measurement = BodyMeasurement.objects.create(
            user=self.user,
            weight=68.5,
            height=165,
            date="2026-08-17",
        )

    def authenticate(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    # ---------- LIST ----------

    def test_list_measurements_success(self):
        self.authenticate()
        response = self.client.get("/api/bodymeasurements/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_list_measurements_unauthorized(self):
        response = self.client.get("/api/bodymeasurements/")
        self.assertEqual(response.status_code, 401)

    # ---------- CREATE ----------

    def test_create_measurement_success(self):
        self.authenticate()
        response = self.client.post("/api/bodymeasurements/", {
            "weight": 70,
            "height": 165,
            "date": "2026-08-18",
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["user"], "fauna")

    def test_create_measurement_invalid_weight(self):
        self.authenticate()
        response = self.client.post("/api/bodymeasurements/", {
            "weight": -5,
            "height": 165,
            "date": "2026-08-18",
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("weight", response.data)

    def test_create_measurement_invalid_body_fat_percentage(self):
        self.authenticate()
        response = self.client.post("/api/bodymeasurements/", {
            "weight": 70,
            "height": 165,
            "body_fat_percentage": 150,
            "date": "2026-08-18",
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("body_fat_percentage", response.data)

    def test_create_measurement_unauthorized(self):
        response = self.client.post("/api/bodymeasurements/", {
            "weight": 70,
            "height": 165,
            "date": "2026-08-18",
        })
        self.assertEqual(response.status_code, 401)

    # ---------- RETRIEVE ----------

    def test_retrieve_measurement_success(self):
        self.authenticate()
        response = self.client.get(f"/api/bodymeasurements/{self.measurement.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["weight"], 68.5)

    def test_retrieve_measurement_not_found(self):
        self.authenticate()
        response = self.client.get("/api/bodymeasurements/9999/")
        self.assertEqual(response.status_code, 404)

    def test_retrieve_measurement_unauthorized(self):
        response = self.client.get(f"/api/bodymeasurements/{self.measurement.id}/")
        self.assertEqual(response.status_code, 401)

    # ---------- UPDATE ----------

    def test_update_measurement_success(self):
        self.authenticate()
        response = self.client.patch(f"/api/bodymeasurements/{self.measurement.id}/", {
            "weight": 69,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["weight"], 69)

    def test_update_measurement_invalid_height(self):
        self.authenticate()
        response = self.client.patch(f"/api/bodymeasurements/{self.measurement.id}/", {
            "height": -10,
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("height", response.data)

    def test_update_measurement_not_found(self):
        self.authenticate()
        response = self.client.patch("/api/bodymeasurements/9999/", {"weight": 69})
        self.assertEqual(response.status_code, 404)

    def test_update_measurement_unauthorized(self):
        response = self.client.patch(f"/api/bodymeasurements/{self.measurement.id}/", {"weight": 69})
        self.assertEqual(response.status_code, 401)

    # ---------- DELETE ----------

    def test_delete_measurement_success(self):
        self.authenticate()
        response = self.client.delete(f"/api/bodymeasurements/{self.measurement.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(BodyMeasurement.objects.filter(id=self.measurement.id).exists())

    def test_delete_measurement_not_found(self):
        self.authenticate()
        response = self.client.delete("/api/bodymeasurements/9999/")
        self.assertEqual(response.status_code, 404)

    def test_delete_measurement_unauthorized(self):
        response = self.client.delete(f"/api/bodymeasurements/{self.measurement.id}/")
        self.assertEqual(response.status_code, 401)