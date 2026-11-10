from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import Testimonial


class TestimonialViewSet(SnippetViewSet):
    model = Testimonial
    icon = "openquote"
    menu_label = "Testimonials"
    menu_order = 200
    add_to_admin_menu = True
    list_display = ["name", "headline", "approved", "featured", "created"]
    list_filter = ["approved", "featured", "from_share_link"]
    search_fields = ["name", "quote"]


register_snippet(TestimonialViewSet)
