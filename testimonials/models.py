from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.models import Page
from wagtail.search import index


class Testimonial(index.Indexed, models.Model):
    name = models.CharField(max_length=100, help_text="How the client wants to be credited")
    headline = models.CharField(
        max_length=120, blank=True, help_text="e.g. 'Mother of two, first time with a doula'"
    )
    context = models.CharField(
        max_length=120, blank=True, help_text="e.g. 'Hospital birth · postpartum support'"
    )
    quote = models.TextField()
    photo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Optional. Only use a photo the client has said you can share.",
    )
    featured = models.BooleanField(default=True, help_text="Show on the home page (up to 3)")
    sort_order = models.PositiveIntegerField(default=0, help_text="Lower numbers show first")
    created = models.DateTimeField(auto_now_add=True)

    panels = [
        MultiFieldPanel(
            [FieldPanel("name"), FieldPanel("headline"), FieldPanel("context")], heading="Who"
        ),
        FieldPanel("quote"),
        FieldPanel("photo"),
        MultiFieldPanel([FieldPanel("featured"), FieldPanel("sort_order")], heading="Display"),
    ]
    search_fields = [index.SearchField("name"), index.SearchField("quote")]

    class Meta:
        ordering = ["sort_order", "-created"]

    def __str__(self):
        return f"{self.name}: {self.headline or self.quote[:40]}"


class TestimonialsPage(Page):
    intro = models.TextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("intro")]
    parent_page_types = ["home.HomePage"]
    subpage_types = []
    max_count = 1

    def get_context(self, request, *args, **kwargs):
        from contact.models import ContactPage

        context = super().get_context(request, *args, **kwargs)
        context["testimonials"] = Testimonial.objects.all()
        context["contact_page"] = ContactPage.objects.live().first()
        return context
