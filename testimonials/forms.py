from django import forms


class ShareTestimonialForm(forms.Form):
    name = forms.CharField(
        label="Your name, as you'd like it shown",
        max_length=100,
        help_text="First name and last initial is fine.",
        widget=forms.TextInput(attrs={"placeholder": "e.g. Jordan M.", "autocomplete": "name"}),
    )
    headline = forms.CharField(
        label="A few words about you",
        max_length=120,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "e.g. First-time parent"}),
    )
    context = forms.CharField(
        label="What support did you have?",
        max_length=120,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "e.g. Home birth, postpartum visits"}),
    )
    quote = forms.CharField(
        label="Your experience",
        max_length=3000,
        widget=forms.Textarea(attrs={"rows": 8}),
    )
    email = forms.EmailField(
        label="Your email",
        required=False,
        help_text="Optional and private, in case Lyndsay has a question. Never shown.",
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    permission = forms.BooleanField(label="")  # label comes from the page
    # Hidden from people; bots tend to fill it in.
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={
        "tabindex": "-1", "autocomplete": "off",
    }))

    def __init__(self, *args, permission_text="", **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["permission"].label = permission_text
