from django.http import HttpResponse


class HealthCheckMiddleware:
    """Answer Render's health check before Django checks the request's host.

    Render's internal health check may use an address that isn't in
    ALLOWED_HOSTS (an internal IP, or the custom domain with a port), which
    would otherwise get "400 Bad Request" and fail the deploy.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/healthz":
            return HttpResponse("ok", content_type="text/plain")
        return self.get_response(request)
