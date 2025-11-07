from django.test import override_settings
from rest_framework.test import APITestCase
from django.urls import reverse
from django.core.cache import cache


class RateLimitTests(APITestCase):
	@override_settings(RATE_LIMIT_MAX_REQUESTS=3, RATE_LIMIT_WINDOW_SECONDS=5)
	def test_rate_limit_blocks_after_threshold(self):
		cache.clear()
		# Use homepage to trigger simple GET requests
		for _ in range(3):
			resp = self.client.get("/")
			self.assertNotEqual(resp.status_code, 429)
			self.assertIn("X-RateLimit-Limit", resp)
			self.assertIn("X-RateLimit-Remaining", resp)
			self.assertIn("X-RateLimit-Reset", resp)

		blocked = self.client.get("/") 		# Fourth within window should be blocked
		self.assertEqual(blocked.status_code, 429)
		self.assertEqual(blocked["X-RateLimit-Remaining"], "0")

	@override_settings(RATE_LIMIT_MAX_REQUESTS=2, RATE_LIMIT_WINDOW_SECONDS=5)
	def test_rate_limit_counts_per_ip(self):
		cache.clear()
		# First IP (default client)
		self.client.get("/")
		self.client.get("/")
		blocked = self.client.get("/")
		self.assertEqual(blocked.status_code, 429)
		# Simulate different IP via header; should have separate counter
		other = self.client.get("/", HTTP_X_FORWARDED_FOR="203.0.113.10")
		self.assertNotEqual(other.status_code, 429)
