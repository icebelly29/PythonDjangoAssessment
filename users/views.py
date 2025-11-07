import csv
from typing import Any, Dict, List
from django.db import transaction
from django.utils.text import get_valid_filename
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.renderers import JSONRenderer

from .models import User
from .serializers import UserSerializer


@method_decorator(csrf_exempt, name="dispatch")
class UploadCSVView(APIView):
	parser_classes = [MultiPartParser]
	renderer_classes = [JSONRenderer]

	def post(self, request, *args, **kwargs):
		uploaded_file = request.FILES.get("file")
		if not uploaded_file:
			return Response({"detail": "No file uploaded. Use 'file' field."}, status=status.HTTP_400_BAD_REQUEST)

		filename = get_valid_filename(uploaded_file.name)
		if not filename.lower().endswith(".csv"):
			return Response({"detail": "Only .csv files are accepted."}, status=status.HTTP_400_BAD_REQUEST)

		try:
			decoded = uploaded_file.read().decode("utf-8")
		except UnicodeDecodeError:
			return Response({"detail": "File must be UTF-8 encoded."}, status=status.HTTP_400_BAD_REQUEST)

		reader = csv.DictReader(decoded.splitlines())
		required_columns = {"name", "email", "age"}
		missing = required_columns.difference(set(reader.fieldnames or []))
		if missing:
			return Response({"detail": f"Missing columns: {', '.join(sorted(missing))}"}, status=status.HTTP_400_BAD_REQUEST)

		success_count = 0
		rejected_count = 0
		errors: List[Dict[str, Any]] = []
		existing_emails = set(User.objects.values_list("email", flat=True)) 	# Preload existing emails to minimize DB hits on large CSVs
		new_users_to_create: List[User] = []

		for row_index, row in enumerate(reader, start=2):  # start=2 accounts for header row as line 1
			raw_name = (row.get("name") or "").strip()
			raw_email = (row.get("email") or "").strip()
			raw_age = (row.get("age") or "").strip()
			try:
				age_value = int(raw_age)
			except (TypeError, ValueError):
				age_value = None  

			serializer = UserSerializer(data={"name": raw_name, "email": raw_email, "age": age_value})
			if not serializer.is_valid():
				rejected_count += 1
				errors.append({
					"row": row_index,
					"errors": serializer.errors,
				})
				continue

			if raw_email in existing_emails:
				# treat as skipped but not an error; don't increment rejected
				continue

			validated = serializer.validated_data
			new_users_to_create.append(User(**validated))
			existing_emails.add(raw_email)
			success_count += 1

		# Bulk create for performance
		if new_users_to_create:
			with transaction.atomic():
				User.objects.bulk_create(new_users_to_create, ignore_conflicts=True)

		return Response(
			{
				"saved": success_count,
				"rejected": rejected_count,
				"errors": errors,
			},
			status=status.HTTP_200_OK,
		)
