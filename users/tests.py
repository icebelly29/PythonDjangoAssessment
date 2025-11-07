from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import User


class UploadCSVTests(APITestCase):
	def _post_csv(self, content: str):
		csv_file = SimpleUploadedFile("users.csv", content.encode("utf-8"), content_type="text/csv")
		return self.client.post(reverse("upload-csv"), {"file": csv_file}, format="multipart")

	def test_upload_valid_csv(self):
		content = "name,email,age\nJohn Doe,john@example.com,30\nJane Roe,jane@example.com,25\n"
		resp = self._post_csv(content)
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		self.assertEqual(resp.data["saved"], 2)
		self.assertEqual(resp.data["rejected"], 0)
		self.assertEqual(User.objects.count(), 2)

	def test_upload_invalid_rows(self):
		content = "name,email,age\n,invalid,130\nOk,ok@example.com,40\n"
		resp = self._post_csv(content)
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		self.assertEqual(resp.data["saved"], 1)
		self.assertEqual(resp.data["rejected"], 1)
		self.assertTrue(len(resp.data["errors"]) >= 1)

	def test_duplicate_emails_skipped(self):
		User.objects.create(name="X", email="dup@example.com", age=50)
		content = "name,email,age\nNew Name,dup@example.com,20\nFresh,fresh@example.com,22\n"
		resp = self._post_csv(content)
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		self.assertEqual(resp.data["saved"], 1)
		self.assertEqual(resp.data["rejected"], 0)
		self.assertEqual(User.objects.count(), 2)

	def test_non_csv_extension_rejected(self):
		file = SimpleUploadedFile("users.txt", b"name,email,age\nA,a@a.com,10\n", content_type="text/plain")
		resp = self.client.post(reverse("upload-csv"), {"file": file}, format="multipart")
		self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
