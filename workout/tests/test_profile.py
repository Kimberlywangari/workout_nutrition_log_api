from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from workout.models import Profile


class ProfileCRUDTests(APITestCase):

    def setUp(self):
        # Creating the User automatically creates a Profile, via the post_save signal.
        self.user = User.objects.create_user(username="fauna", password="pass123")
        self.token = Token.objects.create(user=self.user)
        self.profile = Profile.objects.get(user=self.user)

    def authenticate(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    # ---------- LIST ----------

    def test_list_profile_success(self):
        self.authenticate()
        response = self.client.get("/api/profile/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_list_profile_unauthorized(self):
        response = self.client.get("/api/profile/")
        self.assertEqual(response.status_code, 401)

    # ---------- CREATE NOT ALLOWED ----------

    def test_create_profile_not_allowed(self):
        self.authenticate()
        response = self.client.post("/api/profile/", {"age": 30, "gender": "F"})
        self.assertEqual(response.status_code, 405)

    # ---------- RETRIEVE ----------

    def test_retrieve_profile_success(self):
        self.authenticate()
        response = self.client.get(f"/api/profile/{self.profile.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user"], "fauna")

    def test_retrieve_profile_not_found(self):
        self.authenticate()
        response = self.client.get("/api/profile/9999/")
        self.assertEqual(response.status_code, 404)

    def test_retrieve_profile_unauthorized(self):
        response = self.client.get(f"/api/profile/{self.profile.id}/")
        self.assertEqual(response.status_code, 401)

    # ---------- UPDATE ----------

    def test_update_profile_success(self):
        self.authenticate()
        response = self.client.patch(f"/api/profile/{self.profile.id}/", {
            "age": 29,
            "gender": "F",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["age"], 29)

    def test_update_profile_invalid_age(self):
        self.authenticate()
        response = self.client.patch(f"/api/profile/{self.profile.id}/", {
            "age": -5,
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("age", response.data)

    def test_update_profile_not_found(self):
        self.authenticate()
        response = self.client.patch("/api/profile/9999/", {"age": 29})
        self.assertEqual(response.status_code, 404)

    def test_update_profile_unauthorized(self):
        response = self.client.patch(f"/api/profile/{self.profile.id}/", {"age": 29})
        self.assertEqual(response.status_code, 401)

    # ---------- DELETE (wipes the whole account) ----------

    def test_delete_profile_deletes_user_too(self):
        self.authenticate()
        user_id = self.user.id
        response = self.client.delete(f"/api/profile/{self.profile.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(User.objects.filter(id=user_id).exists())
        self.assertFalse(Profile.objects.filter(id=self.profile.id).exists())

    def test_delete_profile_not_found(self):
        self.authenticate()
        response = self.client.delete("/api/profile/9999/")
        self.assertEqual(response.status_code, 404)

    def test_delete_profile_unauthorized(self):
        response = self.client.delete(f"/api/profile/{self.profile.id}/")
        self.assertEqual(response.status_code, 401)