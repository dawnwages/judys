from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from django.conf import settings
from wagtail.contrib.forms.models import FORM_FIELD_CHOICES, AbstractEmailForm, AbstractFormField
from wagtail.contrib.forms.panels import FormSubmissionsPanel
from wagtail.fields import RichTextField


from .forms import ContactFormBuilder

CONTACT_FIELD_CHOICES = FORM_FIELD_CHOICES + (("city", "Town / city (Google autocomplete)"),)


class ContactFormField(AbstractFormField):
    page = ParentalKey("ContactPage", on_delete=models.CASCADE, related_name="form_fields")
    field_type = models.CharField(
        verbose_name="field type", max_length=16, choices=CONTACT_FIELD_CHOICES
    )
    placeholder = models.CharField(
        max_length=100, blank=True, help_text="Example text shown inside the empty box"
    )

    panels = AbstractFormField.panels + [FieldPanel("placeholder")]


class ContactPage(AbstractEmailForm):
    """Contact / booking form. Submissions are saved in the admin and emailed."""

    form_builder = ContactFormBuilder

    intro = RichTextField(blank=True, features=["bold", "italic", "link"])
    thank_you_text = RichTextField(blank=True, features=["bold", "italic", "link"])

    content_panels = AbstractEmailForm.content_panels + [
        FormSubmissionsPanel(),
        FieldPanel("intro"),
        InlinePanel("form_fields", label="Form fields"),
        FieldPanel("thank_you_text"),
        MultiFieldPanel(
            [
                FieldRowPanel([FieldPanel("from_address"), FieldPanel("to_address")]),
                FieldPanel("subject"),
            ],
            heading="Email me new messages",
            help_text="Put your email in 'To address' to get each new message by email.",
        ),
    ]
    parent_page_types = ["home.HomePage"]
    subpage_types = []
    max_count = 1

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["google_maps_key"] = getattr(settings, "GOOGLE_MAPS_BROWSER_KEY", "")
        return context

    def send_mail(self, form):
        """Email the message to Lyndsay, with Reply going straight to the sender."""
        from django.core.mail import EmailMessage

        addresses = [a.strip() for a in self.to_address.split(",") if a.strip()]
        if not addresses:
            return
        sender = form.cleaned_data.get("email")
        message = EmailMessage(
            subject=self.subject or "New message from the website",
            body=self.render_email(form),
            from_email=self.from_address or None,
            to=addresses,
            reply_to=[sender] if sender else None,
        )
        try:
            message.send()
        except Exception:  # the message is already saved under Forms
            import logging

            logging.getLogger(__name__).exception("Couldn't email contact form message")

    def serve(self, request, *args, **kwargs):
        # The pricing page links here with ?package=<name>; prefill the subject.
        self._package = request.GET.get("package", "")[:60]
        return super().serve(request, *args, **kwargs)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        for f in self.get_form_fields():
            if f.placeholder and f.clean_name in form.fields:
                form.fields[f.clean_name].widget.attrs["placeholder"] = f.placeholder
        package = getattr(self, "_package", "")
        if package and not form.is_bound and "subject" in form.fields:
            form.fields["subject"].initial = f"Interested in the {package} package"
        return form
