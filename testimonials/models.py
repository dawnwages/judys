from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.models import Page
from wagtail.search import index


class TestimonialQuerySet(models.QuerySet):
    def shown(self):
        """Testimonials approved to appear on the website."""
        return self.filter(approved=True)


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
    approved = models.BooleanField(
        "Show on website",
        default=True,
        help_text="Testimonials sent through the share link start unticked until you approve them.",
    )
    featured = models.BooleanField(default=True, help_text="Show on the home page (up to 3)")
    sort_order = models.PositiveIntegerField(default=0, help_text="Lower numbers show first")
    created = models.DateTimeField(auto_now_add=True)
    from_share_link = models.BooleanField(default=False, editable=False)
    email = models.EmailField(
        blank=True, help_text="Private: never shown on the website. Filled in by the share form."
    )

    objects = TestimonialQuerySet.as_manager()

    panels = [
        MultiFieldPanel(
            [FieldPanel("name"), FieldPanel("headline"), FieldPanel("context")], heading="Who"
        ),
        FieldPanel("quote"),
        FieldPanel("photo"),
        MultiFieldPanel(
            [FieldPanel("approved"), FieldPanel("featured"), FieldPanel("sort_order")],
            heading="Display",
        ),
        FieldPanel("email"),
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
        context["testimonials"] = Testimonial.objects.shown()
        context["contact_page"] = ContactPage.objects.live().first()
        return context


class TestimonialRequestPage(Page):
    """A form clients use to send a testimonial, shared by link only.

    Never shown in menus, left out of the sitemap and marked noindex.
    Submissions are saved as testimonials waiting for Lyndsay's approval.
    """

    eyebrow = models.CharField(max_length=40, blank=True, default="Kind words")
    intro = models.TextField(
        blank=True,
        max_length=500,
        default="Thank you for letting me be part of your story. If you'd like to share "
        "your experience, I'd be honored to hear it.",
    )
    permission_text = models.CharField(
        max_length=200,
        default="I give permission for Judy's Daughter to share my words on its website.",
        help_text="The box people must tick before sending",
    )
    thank_you_heading = models.CharField(max_length=80, default="Thank you.")
    thank_you_text = models.TextField(
        max_length=400, default="Your words mean so much. I'll read them soon."
    )
    notify_email = models.EmailField(
        blank=True,
        help_text="Where to send a heads-up when a testimonial arrives. Leave blank to use "
        "the contact page's 'To address'.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("eyebrow"),
        FieldPanel("intro"),
        FieldPanel("permission_text"),
        MultiFieldPanel(
            [FieldPanel("thank_you_heading"), FieldPanel("thank_you_text")],
            heading="After sending",
        ),
        FieldPanel("notify_email"),
    ]
    promote_panels = [
        MultiFieldPanel([FieldPanel("slug"), FieldPanel("seo_title")], "Link"),
    ]
    parent_page_types = ["home.HomePage"]
    subpage_types = []
    max_count = 1

    class Meta:
        verbose_name = "Testimonial form (shared by link only)"

    def clean(self):
        super().clean()
        self.show_in_menus = False  # this page is never listed

    def get_sitemap_urls(self, request=None):
        return []

    def serve(self, request, *args, **kwargs):
        from django.template.response import TemplateResponse

        from .forms import ShareTestimonialForm

        if request.method == "POST":
            form = ShareTestimonialForm(request.POST, permission_text=self.permission_text)
            if form.is_valid():
                data = form.cleaned_data
                if not data["website"]:  # the hidden box is empty for real people
                    testimonial = Testimonial.objects.create(
                        name=data["name"],
                        headline=data["headline"],
                        context=data["context"],
                        quote=data["quote"],
                        email=data["email"],
                        approved=False,
                        featured=False,
                        sort_order=100,
                        from_share_link=True,
                    )
                    self.notify(request, testimonial)
                context = self.get_context(request)
                context["sent"] = True
                return TemplateResponse(request, self.get_template(request), context)
        else:
            form = ShareTestimonialForm(permission_text=self.permission_text)
        context = self.get_context(request)
        context["form"] = form
        return TemplateResponse(request, self.get_template(request), context)

    def notify(self, request, testimonial):
        """Email Lyndsay that a testimonial is waiting. Never blocks the visitor."""
        import logging

        from django.conf import settings
        from django.core.mail import EmailMessage
        from django.urls import reverse

        from contact.models import ContactPage

        to = self.notify_email
        if not to:
            contact = ContactPage.objects.first()
            to = contact.to_address if contact else ""
        addresses = [a.strip() for a in (to or "").split(",") if a.strip()]
        if not addresses:
            return
        admin_url = getattr(settings, "WAGTAILADMIN_BASE_URL", "").rstrip("/") + reverse(
            "wagtailsnippets_testimonials_testimonial:edit", args=[testimonial.pk]
        )
        body = (
            f"{testimonial.name} sent a testimonial through your share link.\n\n"
            f"\"{testimonial.quote}\"\n\n"
            "It isn't on the website yet. To review it and tick \"Show on website\":\n"
            f"{admin_url}\n"
        )
        try:
            EmailMessage(
                subject=f"New testimonial from {testimonial.name}",
                body=body,
                to=addresses,
                reply_to=[testimonial.email] if testimonial.email else None,
            ).send()
        except Exception:
            logging.getLogger(__name__).exception("Couldn't email testimonial notice")
