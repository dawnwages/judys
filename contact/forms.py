from django import forms
from django.core.exceptions import ValidationError
from wagtail.contrib.forms.forms import BaseForm, FormBuilder

from .places import NotACity, server_key, verify_city

PICK_FROM_LIST = "Please choose your town or city from the suggestions as you type."


class CityField(forms.CharField):
    """A town/city box that Google autocompletes in the browser."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 255)
        super().__init__(*args, **kwargs)
        self.widget.attrs.update({"data-city-autocomplete": "", "autocomplete": "off"})


class ContactForm(BaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Keep the picked suggestion if the form is shown again with errors.
        for name, field in self.city_fields():
            field.widget.attrs["data-place-id"] = self.data.get(f"{name}__place_id", "")

    def city_fields(self):
        return [(n, f) for n, f in self.fields.items() if isinstance(f, CityField)]

    def clean(self):
        cleaned = super().clean()
        if not server_key():
            return cleaned  # Google not set up yet: accept what was typed
        for name, _ in self.city_fields():
            if not cleaned.get(name):
                continue
            try:
                checked = verify_city(self.data.get(f"{name}__place_id", "").strip())
            except NotACity:
                self.add_error(name, ValidationError(PICK_FROM_LIST))
                continue
            if checked:
                cleaned[name] = checked
        return cleaned


class ContactFormBuilder(FormBuilder):
    def create_city_field(self, field, options):
        return CityField(**options)

    def get_form_class(self):
        return type("ContactWagtailForm", (ContactForm,), self.formfields)
