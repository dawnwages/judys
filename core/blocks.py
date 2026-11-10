from wagtail import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageBlock


class OfferingBlock(blocks.StructBlock):
    eyebrow = blocks.CharBlock(required=False, help_text="Small line above the title")
    title = blocks.CharBlock()
    image = ImageBlock(required=False)
    summary = blocks.TextBlock(required=False)
    includes = blocks.ListBlock(blocks.CharBlock(label="Item"), label="What's included")

    class Meta:
        icon = "pick"
        template = "blocks/offering.html"


class StepBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    text = blocks.TextBlock()

    class Meta:
        icon = "list-ol"


# ---------------------------------------------------------------------------
# Pricing page
#
# Everything on the pricing page is built from these blocks. Character limits
# and a fixed set of style choices keep the page tidy however it's edited.
# ---------------------------------------------------------------------------

BACKGROUND_CHOICES = [
    ("auto", "Automatic (alternates)"),
    ("plain", "Cream"),
    ("soft", "Warm sand"),
    ("sage", "Soft sage"),
]


class SectionBlock(blocks.StructBlock):
    """Shared settings for every pricing section."""

    heading = blocks.CharBlock(
        required=False, max_length=70,
        help_text="Leave blank for no heading (the section is then left out of the links bar "
        "unless it has a short link name).",
    )
    nav_label = blocks.CharBlock(
        required=False,
        max_length=28,
        label="Short link name",
        help_text="Shorter name for the links bar at the top, e.g. 'Postpartum'. "
        "Leaves the heading as-is if blank.",
    )
    show_in_links = blocks.BooleanBlock(
        required=False, default=True, label="Show in links bar"
    )
    intro = blocks.TextBlock(required=False, max_length=280, help_text="One or two sentences")
    background = blocks.ChoiceBlock(choices=BACKGROUND_CHOICES, default="auto")


class PackageFeature(blocks.StructBlock):
    text = blocks.CharBlock(max_length=90, help_text="e.g. 4 Postpartum Visits (3 hours each)")
    detail = blocks.CharBlock(
        required=False, max_length=160, help_text="Optional explanation shown under the item"
    )


class PackageBlock(blocks.StructBlock):
    name = blocks.CharBlock(max_length=50, help_text="e.g. Foundational Support")
    badge = blocks.CharBlock(
        required=False, max_length=24, help_text="Optional tag on the card, e.g. 'Most popular'"
    )
    price = blocks.CharBlock(max_length=18, help_text="e.g. $3,000")
    price_note = blocks.CharBlock(
        required=False, max_length=40, help_text="Optional, e.g. 'starting at' or 'per hour'"
    )
    description = blocks.TextBlock(
        required=False, max_length=220, help_text="Who this package is for"
    )
    features = blocks.ListBlock(
        PackageFeature(), min_num=1, max_num=14, label="What's included"
    )
    highlight = blocks.BooleanBlock(
        required=False, help_text="Give this card a highlighted border and filled button"
    )
    button_text = blocks.CharBlock(max_length=30, default="Ask about this package")
    button_page = blocks.PageChooserBlock(
        required=False,
        help_text="Where the button goes. Leave blank for the contact form "
        "(the package name is filled in for them).",
    )
    button_url = blocks.URLBlock(
        required=False, help_text="Or a web address, e.g. a booking or payment link"
    )

    class Meta:
        icon = "tag"


class PackageGroupBlock(SectionBlock):
    packages = blocks.ListBlock(PackageBlock(), min_num=1, max_num=4, collapsed=True)
    footnote = blocks.CharBlock(
        required=False, max_length=200, help_text="Small print under the cards"
    )

    class Meta:
        icon = "folder-open-inverse"
        label = "Package cards"
        description = "A group of up to 4 package cards with prices and what's included"


class PriceItem(blocks.StructBlock):
    name = blocks.CharBlock(max_length=80)
    price = blocks.CharBlock(max_length=40, help_text="e.g. $75, $75–$150")
    note = blocks.CharBlock(required=False, max_length=140, help_text="Optional small line underneath")


class PriceListBlock(SectionBlock):
    items = blocks.ListBlock(PriceItem(), min_num=1)
    columns = blocks.ChoiceBlock(
        choices=[("one", "One column"), ("two", "Two columns on wide screens")], default="one"
    )
    footnote = blocks.CharBlock(required=False, max_length=200)

    class Meta:
        icon = "list-ul"
        label = "Price list"
        description = "A menu-style list of services and prices, like à la carte add-ons"


class PaymentPlan(blocks.StructBlock):
    name = blocks.CharBlock(max_length=40, help_text="e.g. Two Installments")
    terms = blocks.CharBlock(max_length=160, help_text="e.g. 50% at signing, 50% by 36 weeks")


class PaymentBlock(SectionBlock):
    text = blocks.RichTextBlock(features=["bold", "italic", "link"], required=False)
    plans_heading = blocks.CharBlock(default="Payment plan options", required=False, max_length=50)
    plans = blocks.ListBlock(PaymentPlan(), required=False, max_num=4)
    footnote = blocks.CharBlock(required=False, max_length=200)

    class Meta:
        icon = "doc-full"
        label = "Payment details"
        description = "Retainer or policy text plus numbered payment plan cards"


class TextSectionBlock(SectionBlock):
    text = blocks.RichTextBlock(features=["bold", "italic", "link", "ul", "ol"])
    examples_heading = blocks.CharBlock(
        required=False, max_length=50, help_text="Optional, e.g. 'Examples may include'"
    )
    examples = blocks.ListBlock(
        blocks.CharBlock(label="Tag", max_length=40), required=False,
        help_text="Short words or phrases shown as rounded tags",
    )
    closing = blocks.TextBlock(
        required=False, max_length=300, help_text="Optional note shown in a highlighted box"
    )

    class Meta:
        icon = "pilcrow"
        label = "Text section"
        description = "Paragraphs, optional tags and a highlighted note (e.g. bartering)"


class FAQItem(blocks.StructBlock):
    question = blocks.CharBlock(max_length=140)
    answer = blocks.RichTextBlock(features=["bold", "italic", "link", "ul"])


class FAQBlock(SectionBlock):
    questions = blocks.ListBlock(FAQItem(), min_num=1)

    class Meta:
        icon = "help"
        label = "Questions (FAQ)"
        description = "Questions that open to show the answer"


class CalloutBlock(blocks.StructBlock):
    """A short highlighted notice between sections. Not shown in the links bar."""

    heading = blocks.CharBlock(required=False, max_length=70)
    text = blocks.TextBlock(max_length=300)
    style = blocks.ChoiceBlock(
        choices=[("sage", "Soft sage"), ("blush", "Soft peach"), ("forest", "Deep green")],
        default="sage",
    )
    button_text = blocks.CharBlock(required=False, max_length=30)
    button_page = blocks.PageChooserBlock(required=False)
    button_url = blocks.URLBlock(required=False)

    class Meta:
        icon = "warning"
        label = "Callout"
        description = "A short highlighted notice, e.g. 'Now accepting Medi-Cal'"


class PricingStreamBlock(blocks.StreamBlock):
    package_group = PackageGroupBlock()
    price_list = PriceListBlock()
    payment = PaymentBlock()
    text_section = TextSectionBlock()
    faq = FAQBlock()
    callout = CalloutBlock()

    class Meta:
        collapsed = True  # start as a tidy outline in the editor


class QuoteBlock(blocks.StructBlock):
    quote = blocks.TextBlock()
    attribution = blocks.CharBlock(required=False)

    class Meta:
        icon = "openquote"
        template = "blocks/quote.html"


class ImageWithCaption(blocks.StructBlock):
    image = ImageBlock()
    caption = blocks.CharBlock(required=False)
    wide = blocks.BooleanBlock(required=False, help_text="Let the image go wider than the text")

    class Meta:
        icon = "image"
        template = "blocks/image.html"


class BodyBlock(blocks.StreamBlock):
    heading = blocks.CharBlock(form_classname="title", icon="title", template="blocks/heading.html")
    paragraph = blocks.RichTextBlock(
        features=["bold", "italic", "link", "ol", "ul", "h3", "h4", "hr"]
    )
    image = ImageWithCaption()
    quote = QuoteBlock()
    video = EmbedBlock(help_text="Paste a YouTube, Vimeo or Instagram link", icon="media")
