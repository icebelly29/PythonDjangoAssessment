import time
import logging
from typing import List
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

logger=logging.getLogger(__name__)

RATE_LIMIT_CACHE_PREFIX =getattr(settings, "RATE_LIMIT_CACHE_PREFIX", "rlip:")


def _get_client_ip(request) -> str:
	xff =request.META.get("HTTP_X_FORWARDED_FOR")
	if xff:
		return xff.split(",")[0].strip()
	return request.META.get("REMOTE_ADDR", "0.0.0.0")


class RateLimitMiddleware(MiddlewareMixin):
	def process_request(self, request):
		# Read settings dynamically to honor override_settings in tests
		max_requests = getattr(settings, "RATE_LIMIT_MAX_REQUESTS", 100)
		window_seconds = getattr(settings, "RATE_LIMIT_WINDOW_SECONDS", 300)
		ip = _get_client_ip(request)
		now = int(time.time())
		key = f"{RATE_LIMIT_CACHE_PREFIX}{ip}"
		timestamps: List[int] = cache.get(key) or []
		window_start = now - window_seconds
		timestamps = [t for t in timestamps if t > window_start]

		current_count = len(timestamps)
		if current_count >= max_requests:
			reset_in = max(1, (timestamps[0] + window_seconds) - now) if timestamps else window_seconds
			headers = {
				"Retry-After": str(reset_in),
				"X-RateLimit-Limit": str(max_requests),
				"X-RateLimit-Remaining": "0",
				"X-RateLimit-Reset": str(reset_in),
			}
			logger.info("Rate limit exceeded for IP %s", ip)
			return JsonResponse({"detail": "Too Many Requests"}, status=429, headers=headers)

		timestamps.append(now)
		cache.set(key, timestamps, window_seconds)

		request._rate_limit = {
			"limit": max_requests,
			"remaining": max(0, max_requests - len(timestamps)),
			"reset": max(0, (timestamps[0] + window_seconds) - now) if timestamps else window_seconds,
		}

		return None
	
	def process_response(self, request, response):
		info = getattr(request, "_rate_limit", None)
		if info:
			response["X-RateLimit-Limit"] = str(info["limit"])
			response["X-RateLimit-Remaining"] = str(info["remaining"])
			response["X-RateLimit-Reset"] = str(info["reset"])
		return response

