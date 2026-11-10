from django.conf import settings


def site_flags(request):
    return {"STAGING": getattr(settings, "STAGING", False)}
