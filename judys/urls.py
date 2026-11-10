from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps import Sitemap
from wagtail.documents import urls as wagtaildocs_urls

from blog.feeds import BlogFeed

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("blog/feed/", BlogFeed(), name="blog_feed"),
    path("sitemap.xml", sitemap, {"sitemaps": {"pages": Sitemap}}),
]

if settings.DEBUG or getattr(settings, "SERVE_MEDIA", False):
    # static() only works with DEBUG on, so wire the view up directly.
    from django.urls import re_path
    from django.views.static import serve

    urlpatterns += [
        re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT})
    ]

urlpatterns += [path("", include(wagtail_urls))]
