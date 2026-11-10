from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting


@register_setting(icon="cog")
class SiteDetails(BaseSiteSetting):
    """Business details shown in the header, footer and contact areas."""

    business_name = models.CharField(max_length=100, default="Judy's Daughter")
    tagline = models.CharField(
        max_length=120,
        default="Birthwork is heart work.",
        help_text="Short line shown under the name in the header.",
    )
    logo = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    email = models.EmailField(
        blank=True, help_text="Kept private: not shown anywhere on the website."
    )
    phone = models.CharField(max_length=40, blank=True)
    service_area = models.CharField(
        max_length=120, blank=True, help_text="e.g. 'Serving the Bay Area & Sacramento'"
    )
    booking_url = models.URLField(
        blank=True,
        help_text="Optional link to a scheduling tool (Calendly, Acuity…). "
        "Leave blank to send people to the contact page.",
    )
    instagram_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)
    accepts_medi_cal = models.BooleanField(
        default=True, help_text="Show the 'Accepting Medi-Cal' note on the home page."
    )
    footer_note = models.CharField(
        max_length=200,
        blank=True,
        default="Full-spectrum doula care, rooted in community.",
    )

    panels = [
        MultiFieldPanel(
            [FieldPanel("business_name"), FieldPanel("tagline"), FieldPanel("logo")],
            heading="Brand",
        ),
        MultiFieldPanel(
            [
                FieldPanel("email"),
                FieldPanel("phone"),
                FieldPanel("service_area"),
                FieldPanel("booking_url"),
                FieldPanel("accepts_medi_cal"),
            ],
            heading="Contact",
        ),
        MultiFieldPanel(
            [FieldPanel("instagram_url"), FieldPanel("facebook_url"), FieldPanel("tiktok_url")],
            heading="Social",
        ),
        FieldPanel("footer_note"),
    ]

    class Meta:
        verbose_name = "Business details"
