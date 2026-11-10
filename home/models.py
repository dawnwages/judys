from django.db import models
from modelcluster.fields import ParentalKey
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page
from wagtail.search import index

from core.blocks import BodyBlock, OfferingBlock, PricingStreamBlock, StepBlock


class HomePage(Page):
    # Hero
    hero_eyebrow = models.CharField(max_length=120, blank=True, default="Full-spectrum doula care")
    hero_heading = models.CharField(
        max_length=200, default="Bringing the village back to birth and beyond."
    )
    hero_text = models.TextField(blank=True)
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="A portrait works best. A photo with the background removed looks great here.",
    )
    hero_button_text = models.CharField(max_length=60, default="Book a free consult")
    values = StreamField(
        [("value", blocks.CharBlock(label="Value"))],
        blank=True,
        help_text="Short words that describe your care, e.g. trauma-informed.",
    )

    # About
    about_heading = models.CharField(max_length=120, default="Who was Judy?")
    about_body = RichTextField(blank=True, features=["bold", "italic", "link"])
    about_signature = models.CharField(max_length=120, blank=True)
    about_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    # Offerings
    offerings_heading = models.CharField(max_length=120, default="Offerings")
    offerings_intro = models.TextField(blank=True)
    offerings = StreamField([("offering", OfferingBlock())], blank=True)

    # Philosophy
    philosophy_heading = models.CharField(max_length=120, default="Philosophy")
    philosophy_body = RichTextField(blank=True, features=["bold", "italic", "link"])

    # How it works
    steps_heading = models.CharField(max_length=120, default="How we'll work together")
    steps = StreamField([("step", StepBlock())], blank=True)

    # Testimonials / blog / contact
    testimonials_heading = models.CharField(max_length=120, default="Kind words")
    blog_heading = models.CharField(max_length=120, default="From the journal")
    contact_heading = models.CharField(max_length=120, default="Let's talk")
    contact_text = models.TextField(blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("hero_eyebrow"),
                FieldPanel("hero_heading"),
                FieldPanel("hero_text"),
                FieldPanel("hero_image"),
                FieldPanel("hero_button_text"),
                FieldPanel("values"),
            ],
            heading="Top of page",
        ),
        MultiFieldPanel(
            [
                FieldPanel("about_heading"),
                FieldPanel("about_body"),
                FieldPanel("about_signature"),
                FieldPanel("about_image"),
            ],
            heading="About",
        ),
        MultiFieldPanel(
            [FieldPanel("offerings_heading"), FieldPanel("offerings_intro"), FieldPanel("offerings")],
            heading="Offerings",
        ),
        MultiFieldPanel(
            [
                FieldPanel("philosophy_heading"),
                FieldPanel("philosophy_body"),
                InlinePanel("gallery_images", label="Photo", heading="Photo gallery"),
            ],
            heading="Philosophy & photos",
        ),
        MultiFieldPanel([FieldPanel("steps_heading"), FieldPanel("steps")], heading="How it works"),
        MultiFieldPanel(
            [
                FieldPanel("testimonials_heading"),
                FieldPanel("blog_heading"),
                FieldPanel("contact_heading"),
                FieldPanel("contact_text"),
            ],
            heading="Other section headings",
            help_text="Testimonials and blog posts are managed in their own areas of the menu.",
        ),
    ]

    max_count = 1
    subpage_types = [
        "home.StandardPage",
        "home.PricingPage",
        "blog.BlogIndexPage",
        "testimonials.TestimonialsPage",
        "contact.ContactPage",
        "home.CalendarPage",
        "home.CollaboratorsPage",
    ]

    def get_context(self, request, *args, **kwargs):
        from blog.models import BlogPage
        from contact.models import ContactPage
        from testimonials.models import Testimonial, TestimonialsPage

        context = super().get_context(request, *args, **kwargs)
        context["testimonials"] = Testimonial.objects.filter(featured=True)[:3]
        context["posts"] = (
            BlogPage.objects.live().public().descendant_of(self).order_by("-date")[:3]
        )
        context["contact_page"] = ContactPage.objects.live().first()
        context["pricing_page"] = PricingPage.objects.live().first()
        context["testimonials_page"] = TestimonialsPage.objects.live().first()
        return context


class HomeGalleryImage(Orderable):
    page = ParentalKey(HomePage, on_delete=models.CASCADE, related_name="gallery_images")
    image = models.ForeignKey("wagtailimages.Image", on_delete=models.CASCADE, related_name="+")
    caption = models.CharField(max_length=200, blank=True)

    panels = [FieldPanel("image"), FieldPanel("caption")]


class PricingPage(Page):
    eyebrow = models.CharField(
        max_length=40, blank=True,
        help_text="Small capitals line above the page title",
    )
    intro = models.TextField(blank=True, max_length=300)
    show_section_links = models.BooleanField(
        default=True,
        help_text="Show a bar of links to each section under the title",
    )
    sections = StreamField(
        PricingStreamBlock(),
        blank=True,
        help_text="Build the page from sections. Use the + buttons to add one and "
        "the arrows to reorder.",
    )

    show_cta = models.BooleanField("Show closing box", default=True)
    cta_heading = models.CharField(max_length=70, default="Not sure which fits?")
    cta_text = models.TextField(
        max_length=240,
        blank=True,
        default="Your first consultation is free. We'll talk through what you need and "
        "find the right support together.",
    )
    cta_button_text = models.CharField(max_length=30, default="Book a free consult")
    cta_link = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Leave blank to use the booking link from Business details, "
        "or the contact page.",
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [FieldPanel("eyebrow"), FieldPanel("intro"), FieldPanel("show_section_links")],
            heading="Top of page",
        ),
        FieldPanel("sections"),
        MultiFieldPanel(
            [
                FieldPanel("show_cta"),
                FieldPanel("cta_heading"),
                FieldPanel("cta_text"),
                FieldPanel("cta_button_text"),
                FieldPanel("cta_link"),
            ],
            heading="Closing box",
            classname="collapsed",
        ),
    ]
    parent_page_types = ["home.HomePage"]
    subpage_types = []

    def get_context(self, request, *args, **kwargs):
        from django.utils.text import slugify

        from contact.models import ContactPage
        from core.models import SiteDetails

        context = super().get_context(request, *args, **kwargs)
        contact_page = ContactPage.objects.live().first()
        context["contact_page"] = contact_page

        # Work out each section's anchor, links-bar label and background so
        # the template stays simple. "auto" alternates cream and sand.
        sections, links, used, alternate = [], [], set(), False
        for block in self.sections:
            v = block.value
            if block.block_type == "callout":
                sections.append({"block": block, "anchor": "", "bg": ""})
                continue
            label = v.get("nav_label") or v.get("heading") or ""
            base = slugify(label) or "section"
            anchor, n = base, 2
            while anchor in used:
                anchor, n = f"{base}-{n}", n + 1
            used.add(anchor)
            bg = v.get("background") or "auto"
            if bg == "auto":
                bg = "soft" if alternate else "plain"
            alternate = bg == "plain"
            sections.append({"block": block, "anchor": anchor, "bg": bg})
            if label and v.get("show_in_links", True):
                links.append((anchor, label))
        context["sections"] = sections
        context["section_links"] = links if self.show_section_links and len(links) > 1 else []

        if self.cta_link_id:
            context["cta_url"] = self.cta_link.specific.url
        else:
            details = SiteDetails.for_request(request)
            context["cta_url"] = details.booking_url or (contact_page.url if contact_page else "")
        return context


class StandardPage(Page):
    """A general page for anything else: FAQ, resources, policies."""

    intro = models.TextField(blank=True)
    header_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    body = StreamField(BodyBlock(), blank=True)

    search_fields = Page.search_fields + [index.SearchField("intro"), index.SearchField("body")]
    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("header_image"),
        FieldPanel("body"),
    ]


# Scheduling services whose booking pages may be embedded on a calendar page.
CALENDAR_HOSTS = (
    "calendar.google.com",
    "calendly.com",
    "acuityscheduling.com",
    "app.squarespacescheduling.com",
    "cal.com",
)


class CalendarPage(Page):
    """A booking calendar shared by link only.

    Never shown in menus, left out of the sitemap and marked noindex, so only
    people Lyndsay sends the link to will find it.
    """

    eyebrow = models.CharField(max_length=40, blank=True)
    intro = models.TextField(blank=True, max_length=400)
    calendar_url = models.URLField(
        max_length=500,
        help_text="The booking page link from Google Calendar (Appointment schedule → "
        "Share → Website embed, copy the address inside src=\"…\"), or from Calendly, "
        "Acuity or Cal.com.",
    )
    calendar_height = models.PositiveIntegerField(
        default=900, help_text="Height of the calendar in pixels (600–1600)."
    )
    note = models.TextField(
        blank=True, max_length=400, help_text="Optional text shown under the calendar"
    )

    content_panels = Page.content_panels + [
        FieldPanel("eyebrow"),
        FieldPanel("intro"),
        FieldPanel("calendar_url"),
        FieldPanel("calendar_height"),
        FieldPanel("note"),
    ]
    promote_panels = [
        MultiFieldPanel([FieldPanel("slug"), FieldPanel("seo_title")], "Link"),
    ]
    parent_page_types = ["home.HomePage"]
    subpage_types = []

    class Meta:
        verbose_name = "Calendar page (shared by link only)"

    def clean(self):
        from urllib.parse import urlparse

        from django.core.exceptions import ValidationError

        super().clean()
        self.show_in_menus = False  # this page is never listed
        errors = {}
        url = urlparse(self.calendar_url or "")
        host = (url.hostname or "").lower()
        if url.scheme != "https" or not any(
            host == h or host.endswith("." + h) for h in CALENDAR_HOSTS
        ):
            errors["calendar_url"] = (
                "Use an https link from Google Calendar, Calendly, Acuity or Cal.com."
            )
        if not 600 <= (self.calendar_height or 0) <= 1600:
            errors["calendar_height"] = "Choose a height between 600 and 1600."
        if errors:
            raise ValidationError(errors)

    def get_sitemap_urls(self, request=None):
        return []


class CollaboratorsPage(Page):
    """Practitioners Lyndsay works alongside, each linking to their own site."""

    eyebrow = models.CharField(max_length=40, blank=True, default="Community")
    intro = models.TextField(blank=True, max_length=400)
    closing = models.TextField(
        blank=True, max_length=300, help_text="Optional note at the bottom of the page"
    )

    content_panels = Page.content_panels + [
        FieldPanel("eyebrow"),
        FieldPanel("intro"),
        InlinePanel("collaborators", label="Collaborator", heading="Collaborators"),
        FieldPanel("closing"),
    ]
    parent_page_types = ["home.HomePage"]
    subpage_types = []
    max_count = 1

    class Meta:
        verbose_name = "Collaborators page"


class Collaborator(Orderable):
    page = ParentalKey(CollaboratorsPage, on_delete=models.CASCADE, related_name="collaborators")
    business = models.CharField(max_length=80, help_text="e.g. Coastal Rose Doula")
    person = models.CharField(max_length=80, blank=True, help_text="e.g. Kristin Guess")
    group = models.CharField(
        max_length=40,
        blank=True,
        help_text="Optional heading to group people under, e.g. 'Birth Doulas'. "
        "Collaborators in a row with the same group share one heading.",
    )
    label = models.CharField(
        max_length=40, blank=True, help_text="Optional small tag, e.g. 'Prenatal education'"
    )
    location = models.CharField(max_length=60, blank=True, help_text="e.g. Half Moon Bay, CA")
    description = models.TextField(blank=True, max_length=240, help_text="One or two sentences")
    photo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Headshot or logo. Without one, their initials are shown.",
    )
    url = models.URLField("Website")

    panels = [
        FieldPanel("business"),
        FieldPanel("person"),
        FieldPanel("url"),
        FieldPanel("photo"),
        FieldPanel("location"),
        FieldPanel("description"),
        FieldPanel("label"),
        FieldPanel("group"),
    ]

    @property
    def initials(self):
        words = [w for w in (self.person or self.business).replace("&", " ").split() if w[0].isalpha()]
        return "".join(w[0] for w in words[:2]).upper()
