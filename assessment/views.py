from django.http import HttpResponse
from django.urls import reverse


def home(request):
	upload_url = "/api/upload-csv/"
	return HttpResponse(
		f"""
		<!doctype html>
		<html>
		<head>
			<meta charset=\"utf-8\" />
			<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
			<title>CSV Upload API</title>
			<style>
				body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; padding: 2rem; line-height: 1.5; }}
				.code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; background: #f5f5f5; padding: 0.2rem 0.4rem; border-radius: 4px; }}
				.container {{ max-width: 780px; margin: 0 auto; }}
				.card {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 1.25rem; }}
				.btn {{ display: inline-block; padding: 0.5rem 0.9rem; background: #2563eb; color: #fff; text-decoration: none; border-radius: 6px; }}
				.btn:hover {{ background: #1e40af; }}
				.form-row {{ margin: 0.75rem 0; }}
			</style>
		</head>
		<body>
			<div class=\"container\">
				<h1>CSV Upload API</h1>
				<p>Use the POST endpoint below to upload a <span class=\"code\">.csv</span> file with columns <span class=\"code\">name,email,age</span>.</p>
				<div class=\"card\">
					<p><strong>Endpoint:</strong> <span class=\"code\">POST {upload_url}</span></p>
					<p><strong>Upload from browser:</strong></p>
					<form method=\"post\" action=\"{upload_url}\" enctype=\"multipart/form-data\">
						<div class=\"form-row\">
							<input type=\"file\" name=\"file\" accept=\".csv,text/csv\" required />
						</div>
						<div class=\"form-row\">
							<button type=\"submit\" class=\"btn\">Upload CSV</button>
						</div>
					</form>
					<p style=\"margin-top: 1rem;\"><strong>Or try with curl:</strong></p>
					<pre class=\"code\">curl -X POST -F \"file=@samples/users.csv\" http://127.0.0.1:8000{upload_url}</pre>
				</div>
			</div>
		</body>
		</html>
		"""
	)
