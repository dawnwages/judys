"""Load the content from the original static Judy's Daughter site into Wagtail.

Safe to run once on a fresh database:  uv run python manage.py seed_site
Use --reset to wipe and rebuild the seeded pages (images are reused).
"""

import os
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from django.db import transaction
from wagtail.images import get_image_model
from wagtail.models import Collection, GroupCollectionPermission, GroupPagePermission, Page, Site

from blog.models import BlogIndexPage, BlogPage
from contact.models import ContactFormField, ContactPage
from core.models import SiteDetails
from home.models import (
    CalendarPage,
    Collaborator,
    CollaboratorsPage,
    HomeGalleryImage,
    HomePage,
    PricingPage,
)
from testimonials.models import Testimonial, TestimonialRequestPage, TestimonialsPage

IMAGES = Path(settings.BASE_DIR) / "seed" / "images"
Image = get_image_model()

ABOUT = """
<p>I would be remiss if I didn't start by letting you know who Judy was. She was a powerhouse of a
woman: a teen mother who found herself wheelchair-bound after her second child (I am her third) due
to tumors on her spinal cord. Throughout her life I watched as she not only raised her own children
but took in and raised others, cooked for and nurtured the whole block, and became a beacon of
strength and guidance for those in need. Even now on her memorial page, I see comment after comment
of people wishing they just had her ear for a moment. That is who she was.</p>
<p>I've spent my entire life with a helper's spirit, and that comes from having a disabled mother, of
course, but mostly from watching her care for others the way she did. In this lifetime I have been a
nanny, au pair, EMT, and now doula, all of which speak to my love for raw, unfiltered humanness. I was
given the gift of showing up in the moments when we are most vulnerable and making myself right at
home in the mess, because truly that's all we ever need: someone who will witness us as we move
through life.</p>
<p>I honor my mother with every act of service I perform, knowing that her spirit guides me in all that
I do. <strong>I am Judy's daughter: doula, caretaker, healer.</strong></p>
"""

PHILOSOPHY = """
<p>My philosophy when it comes to birth, like most things in life, is a focus on
<em>intentionality</em>. I believe every birthing person should have the right to go into birth with a
clear vision of what they want. What are the enthusiastic yeses and hard nos? How can you show up as the
most authentic version of yourself during this time? Is there something in your past that needs
attention before the transition into parenthood?</p>
<p>Does this mean things will go 100% your way? We can hope, but the beauty of birth can be in its
unpredictability. Good news for you: we can be intentional about that too.</p>
"""

TESTIMONIALS = [
    dict(
        name="Nahgee Baldwin",
        headline="Mother of two, first pregnancy with a doula",
        context="Hospital birth · high risk · long distance",
        featured=True,
        sort_order=1,
        quote=(
            "My partner and I had a great experience with Lyndsay as our first time doula. We were and "
            "will forever be grateful for her. She is absolutely amazing from beginning to end; I felt "
            "completely comfortable with her. Our first sit down was all about me and what I imagined "
            "this pregnancy to be. From there she kept the ball rolling with tons of information from "
            "meal prep to breathing strategies to information on what happens during labor and after "
            "birth. Honestly she just checked all the boxes. She is the perfect person to have on your "
            "birth team, not only for you but for everyone you plan on having involved.\n\n"
            "As my doula she made sure my team was informed and aware of everything that needed to be "
            "done for me and baby to have a healthy journey. The best part about having Lyndsay was she "
            "always made sure I was comfortable throughout my whole journey. She always went over my "
            "birth plan with me when things changed with my health or when I wanted to change something "
            "just due to preference. Her main goal my entire pregnancy was the health and safety of me "
            "and baby, and she did just that."
        ),
    ),
    dict(
        name="Single parent of triplets",
        headline="Absolutely phenomenal",
        context="Postpartum & overnight care",
        featured=True,
        sort_order=2,
        quote=(
            "Lyndsay was an absolute godsend, supporting me (a single parent) of premature triplets with "
            "unwavering dedication. She handled overnight shifts like a pro, expertly caring for the "
            "babies while also managing household tasks like laundry, bottles, and organizing. Her "
            "ability to seamlessly integrate into my family and collaborate with me and other caregivers "
            "was truly impressive, constantly adjusting her care to meet our needs. Each of my children "
            "received personalized attention, and she formed unique, loving bonds with all three. Her "
            "exceptional care for three premature infants (one with special needs) was nothing short of "
            "extraordinary. I couldn't have asked for a better addition to my \"village\" during that "
            "challenging yet amazing time!"
        ),
    ),
    # The next two appeared on the old site without a name. They are kept off the
    # home page until Lyndsay confirms them.
    dict(
        name="Home birth client",
        headline="Never thought about having a doula",
        context="Home birth · meal plan · postpartum support",
        featured=False,
        sort_order=3,
        quote=(
            "Thankfully this was the easiest part of my pregnancy. Lynds was with me every step of the "
            "way. I never thought about having a doula, but I'm so glad I did. I thought doula services "
            "were going to be expensive but she was very affordable and worth every penny."
        ),
    ),
    dict(
        name="Postpartum client",
        headline="Black and queer family growing",
        context="Postpartum support",
        featured=False,
        sort_order=4,
        quote=(
            "Having a calm pregnancy was important to me. I wanted to make sure that I was able to have "
            "a home birth and have the support I needed. I'm so glad I found Lynds. She was able to "
            "provide me with the support I needed and I was able to have the birth I wanted."
        ),
    ),
]


def block_image(image):
    """ImageBlock values are images carrying their own alt text."""
    image.contextual_alt_text = image.title
    image.decorative = False
    return image


# Pricing is copied word for word from Lyndsay's "JD Packages & Payment" PDF,
# which is the source of truth. Only change it when she sends a new price sheet.
# Where contact-form messages are emailed. Kept out of the code (this repo is
# public): set CONTACT_EMAIL in the environment, or later in the admin.
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "")

# Contact form copied from the original site's form, in the same order, with the
# same wording, required fields, placeholders and field names (name, pronouns,
# phone, duedate, email, subject, message, referral). Zipcode was replaced by
# two Google-checked town/city questions: location and delivery_location.
CONTACT_INTRO = (
    "<p>Don't hesitate to reach out. Feel free to schedule your first, free appointment "
    "with me or inquire with the form below.</p>"
)
CONTACT_THANKS = "<p>Thank you for reaching out. I'll be in touch soon.</p>"
CONTACT_FIELDS = [
    # (field name, label, type, required, placeholder, help text)
    ("referral", "Were you referred?", "radio", False, "", ""),
    ("name", "Your name", "singleline", True, "Your Name", ""),
    ("pronouns", "Your pronouns", "singleline", True, "your/pronouns/here", ""),
    ("phone", "Your phone number", "singleline", True, "123-456-7890", ""),
    ("location", "Your location", "city", True, "Start typing your town or city", ""),
    ("delivery_location", "Delivery location", "city", False, "Start typing a town or city", ""),
    ("duedate", "Your due date", "date", True, "", ""),
    ("email", "Your email", "email", True, "name@yourname.com", ""),
    ("subject", "Subject", "singleline", True, "Let us know how we can help you", ""),
    ("message", "Your message", "multiline", False, "Leave a comment...", ""),
]

HEADSHOT_TITLE = "Lyndsay Cromwell smiling in a colorful headwrap"

# Collaborators (business, person, location, description, website).
# Descriptions only use facts from each collaborator's own website.
COLLABORATORS_INTRO = (
    "Birthwork takes a village. These are some of the practitioners I'm proud to "
    "work alongside."
)
COLLABORATORS = [
    ("Together Birth & Body", "Caitlin Breen", "Redwood City, CA",
     "Prenatal yoga, birth prep workshops for couples, bodywork and doula support.",
     "https://www.togetherbirthandbody.com/"),
    ("Coastal Rose Doula", "Kristin Guess", "Half Moon Bay, CA",
     "Birth doula support for families on the coast, in San Francisco and on the Peninsula.",
     "https://www.kristinguess.com/"),
    ("SageFemme Wellness", "", "",
     "Prenatal massage, plus birth and postpartum doula services.",
     "https://www.sagefemmewell.com/"),
]

# Google appointment schedule from the original site's /book page.
CALENDAR_URL = (
    "https://calendar.google.com/calendar/appointments/schedules/"
    "AcZssZ2DSChF4v8cgrIN4qF7w4twQ3brEu9IheRdWDPxL6ZZFVneNiwh9HEdJXH5adjUVjprzfzQgDlO?gv=true"
)

PRICING_TITLE = "Packages & Payment Options"
PRICING_INTRO = ""


def feat(text, detail=""):
    return {"text": text, "detail": detail}


def pkg(name, price, description, features):
    return {
        "name": name,
        "badge": "",
        "price": price,
        "price_note": "",
        "description": description,
        "features": features,
        "highlight": False,
        "button_text": "Ask about this package",
        "button_page": None,
        "button_url": "",
    }


def section(heading, nav_label="", **values):
    return {"heading": heading, "nav_label": nav_label, "show_in_links": True,
            "intro": "", "background": "auto", **values}


def pricing_sections():
    return [
        ("package_group", section(
            "", packages=[
                pkg("Foundational Support", "$3,000",
                    "For families wanting steady, grounded support through birth and early "
                    "postpartum with essential guidance and hands-on care.", [
                        feat("2 Prenatal Visits (60–90 minutes each)",
                             "In-depth birth plan, home and partner preparation, mind and body readiness"),
                        feat("4 Postpartum Visits (3 hours each)",
                             "Newborn care support, feeding guidance, emotional processing, nourishment and rest support"),
                        feat("Labor and Delivery Support (In person or virtual)",
                             "Continuous emotional, physical, and advocacy support through active labor and immediate postpartum"),
                        feat("24/7 On-Call Text and Voice Support (36 weeks–2 weeks postpartum)"),
                        feat("1 Postpartum Massage (30 minutes)",
                             "Gentle bodywork to encourage recovery and nervous system regulation"),
                    ]),
                pkg("Integrated Support", "$4,000",
                    "For families desiring deeper preparation, structured postpartum rest, and "
                    "more continuous in-home support.", [
                        feat("3 Prenatal Visits (60–90 minutes each)"),
                        feat("6 Postpartum Visits (3 hours each)", "Includes closing ceremony"),
                        feat("1 Overnight Visit (8 hours)", "Newborn care while you rest"),
                        feat("Labor and Delivery Support (In person or virtual)"),
                        feat("24/7 On-Call Text and Voice Support (36 weeks–2 weeks postpartum)"),
                        feat("1 Postpartum Massage (60 minutes)"),
                    ]),
                pkg("Full Spectrum Immersion", "$5,500",
                    "For families wanting sustained, high-touch support and structured rest.", [
                        feat("3 Prenatal Visits (60–90 minutes each)"),
                        feat("8 Postpartum Visits (3 hours each)"),
                        feat("4 Overnight Visits (8 hours each)"),
                        feat("Labor and Delivery Support (In person or virtual)"),
                        feat("24/7 On-Call Text and Voice Support (36 weeks–4 weeks postpartum)"),
                        feat("3 Postpartum Massages (60 minutes each)"),
                    ]),
            ],
            footnote="",
        )),
        ("package_group", section(
            "Postpartum Packages", packages=[
                pkg("Gentle Landing", "$900",
                    "For families wanting supportive guidance as they begin the transition "
                    "into parenthood.", [
                        feat("4 Postpartum Visits (3 hours each)"),
                        feat("Hands-on newborn care guidance"),
                        feat("Feeding support"),
                        feat("Emotional processing"),
                        feat("Practical support as your family settles into a new rhythm."),
                        feat("1 Postpartum Massage (30 minutes)",
                             "Gentle bodywork to support circulation, relaxation, and recovery"),
                    ]),
                pkg("Rooted Beginnings", "$1,350",
                    "For families wanting deeper guidance and steady support while adjusting "
                    "to life with a new baby.", [
                        feat("6 Postpartum Visits (3 hours each)"),
                        feat("Newborn care education and confidence building"),
                        feat("Feeding support and troubleshooting"),
                        feat("Maternal physical recovery support"),
                        feat("Nervous system regulation and emotional care"),
                        feat("Light meal preparation and home flow support"),
                        feat("Partner integration and family rhythm building"),
                        feat("1 Postpartum Massage (60 minutes)",
                             "Restorative massage focusing on hips, back, shoulders, and abdomen "
                             "to support postpartum recovery."),
                    ]),
                pkg("Full Circle Postpartum Care", "$1,750",
                    "For families wanting sustained, high-touch support during the transition "
                    "into parenthood.", [
                        feat("8 Postpartum Visits (3 hours each)"),
                        feat("Infant care guidance and developmental support"),
                        feat("Feeding and sleep rhythm guidance"),
                        feat("Nervous system support and integration of the birth experience"),
                        feat("Light home organization and nourishment support"),
                        feat("Partner support and family transition guidance"),
                        feat("Closing reflection or postpartum ceremony"),
                        feat("2 Postpartum Massages (60 minutes each)",
                             "Restorative bodywork spaced intentionally through recovery to "
                             "support healing and relaxation."),
                    ]),
            ],
            footnote="",
        )),
        ("price_list", section(
            "Build Your Own / À La Carte Services", "À La Carte",
            columns="one",
            footnote="",
            items=[
                {"name": name, "price": price, "note": ""} for name, price in [
                    ("Birth Doula rate", "$3,000"),
                    ("Postpartum Doula (Hourly rate)", "$75"),
                    ("Travel fee", "$50 per visit"),
                    ("Additional Perinatal Visit (60–90 minutes)", "$175"),
                    ("Extended In-Hospital Support (3 hours)", "$350"),
                    ("Overnight Support Add-On (8 hours)", "$500"),
                    ("Postpartum Massage", "60 minutes $100 / 30 minutes $70"),
                    ("Herbal Sitz and Belly Binding", "$75–$150"),
                    ("Sibling Support Visit", "$125"),
                ]
            ],
        )),
        ("payment", section(
            "Investment and Payment Details", "Payment",
            text=(
                "<p>A non-refundable retainer of 30–50% of the total package fee is required to "
                "reserve your estimated due date.</p>"
                "<p>The retainer secures your on-call window and limited monthly client capacity.</p>"
            ),
            plans_heading="Payment Plan Options",
            plans=[
                {"name": "Two Installments", "terms": "50% at signing, 50% by 36 weeks"},
                {"name": "Three Installments", "terms": "40% at signing, 30% at 28 weeks, 30% by 36 weeks"},
                {"name": "Monthly Plan", "terms": "30–40% at signing, remaining balance divided monthly and paid in full by 36 weeks"},
            ],
            footnote="",
        )),
        ("text_section", section(
            "Community Exchange and Bartering", "Community Exchange",
            # The PDF says "brith work"; corrected to "birth work".
            text=(
                "<p>Community care is an essential part of birth work, please find options below "
                "that uphold the values of this system!</p>"
                "<ul><li>Partial barter agreements may be considered on a case-by-case basis.</li>"
                "<li>Barter may cover no more than 25–40% of the total package fee and must be "
                "agreed upon in writing.</li></ul>"
                "<p><i>A monetary retainer is still required</i>.</p>"
            ),
            examples_heading="Examples may include",
            examples=[
                "massage therapy", "acupuncture", "pelvic floor physical therapy", "website design",
                "branding photography", "bookkeeping and taxes", "social media strategy",
                "meal preparation", "pet care", "garden share subscriptions", "birth photography",
                "videography", "graphic design",
            ],
            closing=(
                "Please do not let cost be a barrier to care, if you are interested and none of the "
                "options listed above work for you, reach out so we can find something that does."
            ),
        )),
    ]


class Command(BaseCommand):
    help = "Seed the site with content from the original Judy's Daughter static site."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Delete seeded pages first")
        parser.add_argument(
            "--testimonial-form",
            action="store_true",
            help="Only add the link-only testimonial form page if it's missing",
        )
        parser.add_argument(
            "--collaborators",
            action="store_true",
            help="Only add the Collaborators page if it's missing",
        )
        parser.add_argument(
            "--headshot",
            action="store_true",
            help="Only switch the home page photo to the current headshot",
        )
        parser.add_argument(
            "--site-host",
            help="Only set the site's web address (used for full links in feeds and previews)",
        )
        parser.add_argument(
            "--contact-form",
            action="store_true",
            help="Only reset the contact form's fields and text to match the original site",
        )
        parser.add_argument(
            "--calendar",
            action="store_true",
            help="Only add the link-only booking calendar page if it's missing",
        )
        parser.add_argument(
            "--demo-posts",
            action="store_true",
            help="Only add any missing demo blog posts (as unpublished drafts)",
        )
        parser.add_argument(
            "--update-pricing",
            action="store_true",
            help="Only replace the Pricing page content with the current price sheet",
        )

    def img(self, filename, title, **kw):
        existing = Image.objects.filter(title=title).first()
        if existing:
            return existing
        with open(IMAGES / filename, "rb") as fh:
            image = Image(title=title, file=ImageFile(fh, name=filename), **kw)
            image.save()
        return image

    @transaction.atomic
    def handle(self, *args, reset=False, update_pricing=False, demo_posts=False,
               calendar=False, contact_form=False, site_host=None, collaborators=False,
               headshot=False, testimonial_form=False, **opts):
        if testimonial_form:
            self.create_testimonial_form_page(HomePage.objects.get())
            return
        if collaborators:
            self.create_collaborators_page(HomePage.objects.get())
            return
        if headshot:
            home = HomePage.objects.get()
            home.hero_image = self.img("lyndsay-headshot.jpg", HEADSHOT_TITLE)
            home.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("Home page photo updated."))
            return
        if site_host is not None:
            if site_host:
                Site.objects.filter(is_default_site=True).update(hostname=site_host, port=443)
                self.stdout.write(f"Site address set to https://{site_host}")
            return
        if contact_form:
            contact = ContactPage.objects.get()
            contact.intro = CONTACT_INTRO
            contact.thank_you_text = CONTACT_THANKS
            contact.to_address = contact.to_address or CONTACT_EMAIL
            self.setup_contact_form(contact)
            self.stdout.write(self.style.SUCCESS("Contact form matches the original site."))
            return
        if calendar:
            self.create_calendar_page(HomePage.objects.get())
            return
        if demo_posts:
            self.create_demo_posts(BlogIndexPage.objects.get())
            return
        if update_pricing:
            pricing = PricingPage.objects.get()
            pricing.title = PRICING_TITLE
            pricing.eyebrow = ""
            pricing.intro = PRICING_INTRO
            pricing.sections = pricing_sections()
            pricing.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("Pricing page updated."))
            return

        root = Page.get_first_root_node()
        if HomePage.objects.exists():
            if not reset:
                self.stdout.write("Site already seeded. Use --reset to rebuild it.")
                return
            for p in HomePage.objects.all():
                p.delete()
            Testimonial.objects.all().delete()

        # Wagtail's "Welcome" placeholder page.
        for p in root.get_children().filter(content_type__model="page"):
            p.delete()

        logo = self.img("logo.png", "Judy's Daughter logo")
        portrait = self.img("lyndsay-headshot.jpg", HEADSHOT_TITLE)
        with_baby = self.img("lyndsay-with-baby.jpg", "Lyndsay holding a smiling baby")
        gallery = [
            self.img("home-visit-1.jpg", "Lyndsay supporting a client at home"),
            self.img("lyndsay-triplets.jpg", "Lyndsay resting with newborn triplets"),
            self.img("lyndsay-newborn.jpg", "Lyndsay holding a newborn"),
            self.img("lyndsay-mealtime.jpg", "Lyndsay feeding toddlers at mealtime"),
            self.img("home-visit-2.jpg", "Preparing for a home birth"),
        ]
        birth_img = self.img("stock-pregnancy.jpg", "Pregnant person outdoors")
        postpartum_img = self.img("stock-postpartum.jpg", "Parent holding a newborn")
        meals_img = self.img("stock-family.jpg", "Parent and child at home")

        home = HomePage(
            title="Home",
            slug="home",
            seo_title="Judy's Daughter: Full-spectrum doula care",
            search_description=(
                "Trauma-informed, LGBTQIA+ affirming birth and postpartum doula support, "
                "meal prep and overnight care. Now accepting Medi-Cal."
            ),
            hero_eyebrow="Full-spectrum doula care",
            hero_heading="Bringing the village back to birth and beyond.",
            hero_text=(
                "Parents and babies deserve some looking after as you move into familyhood. "
                "I'm here for the birth, the fourth trimester, and the meals in between."
            ),
            hero_image=portrait,
            hero_button_text="Book a free consult",
            values=[
                ("value", v)
                for v in [
                    "trauma-informed",
                    "pleasure-positive",
                    "body-positive",
                    "intersectional",
                    "LGBTQIA+ affirming",
                ]
            ],
            about_heading="I'm Judy's daughter.",
            about_body=ABOUT,
            about_signature="Lyndsay Cromwell",
            about_image=with_baby,
            offerings_heading="Care for every season of your growing family",
            offerings_intro=(
                "Birth and postpartum support to help you feel prepared, comfortable and "
                "cared for, from your first appointment to the weeks after baby arrives."
            ),
            offerings=[
                (
                    "offering",
                    {
                        "eyebrow": "Intentional, present birth experiences",
                        "title": "Birth",
                        "image": block_image(birth_img),
                        "summary": "",
                        "includes": [
                            "Three in-person prenatal appointments",
                            "A personalized birth plan",
                            "Unbiased support and education for your birth choices",
                            "Unlimited call, email and text support",
                            "Coaching for your partner or support person",
                        ],
                    },
                ),
                (
                    "offering",
                    {
                        "eyebrow": "Care for your body, baby and home",
                        "title": "Postpartum",
                        "image": block_image(postpartum_img),
                        "summary": "",
                        "includes": [
                            "Four, six or eight postpartum visits",
                            "Up to two hours of support right after birth",
                            "Overnight support",
                            "Massage",
                            "Referrals for lactation, chiropractic, sleep and more",
                        ],
                    },
                ),
                (
                    "offering",
                    {
                        "eyebrow": "Nourishment for a healthy household",
                        "title": "Meal planning & prep",
                        "image": block_image(meals_img),
                        "summary": "",
                        "includes": [
                            "Personalized meals to support energy and healing",
                            "Fresh food from reputable sources",
                            "Local delivery of fresh or frozen meals",
                        ],
                    },
                ),
            ],
            philosophy_heading="Birth, with intention.",
            philosophy_body=PHILOSOPHY,
            steps_heading="How we'll work together",
            steps=[
                ("step", {"title": "Free consult", "text": "We meet, talk through what you're hoping for, and see if we're a good fit."}),
                ("step", {"title": "Plan together", "text": "Prenatal visits to build your birth plan, prepare your support person and answer every question."}),
                ("step", {"title": "Birth day", "text": "I'm with you through labor and for the first hours after baby arrives."}),
                ("step", {"title": "Fourth trimester", "text": "Postpartum visits, overnights and meals so you can rest, heal and bond."}),
            ],
            testimonials_heading="Kind words from families",
            blog_heading="Notes on birth & becoming",
            contact_heading="Let's talk about your birth.",
            contact_text=(
                "Your first consultation is free. Tell me a little about you and I'll be in touch."
            ),
        )
        root.add_child(instance=home)
        home.save_revision().publish()
        for i, image in enumerate(gallery):
            HomeGalleryImage.objects.create(page=home, image=image, sort_order=i)

        site = Site.objects.filter(is_default_site=True).first() or Site(is_default_site=True)
        site.root_page = home
        site.site_name = "Judy's Daughter"
        site.hostname = site.hostname or "localhost"
        site.port = site.port or 80
        site.save()

        pricing = PricingPage(
            title=PRICING_TITLE,
            slug="pricing",
            show_in_menus=True,
            intro=PRICING_INTRO,
            sections=pricing_sections(),
        )
        home.add_child(instance=pricing)
        pricing.save_revision().publish()

        tpage = TestimonialsPage(
            title="Testimonials",
            slug="testimonials",
            show_in_menus=True,
            intro="Stories from the families I've had the honor of walking alongside.",
        )
        home.add_child(instance=tpage)
        tpage.save_revision().publish()
        for t in TESTIMONIALS:
            Testimonial.objects.create(**t)

        blog = BlogIndexPage(
            title="Journal",
            slug="journal",
            show_in_menus=True,
            intro="Notes on pregnancy, birth, postpartum and the village it takes.",
        )
        home.add_child(instance=blog)
        blog.save_revision().publish()

        self.create_demo_posts(blog)
        self.create_calendar_page(home)
        self.create_collaborators_page(home)
        self.create_testimonial_form_page(home)

        contact = ContactPage(
            title="Book a free consult",
            slug="contact",
            show_in_menus=False,
            intro=CONTACT_INTRO,
            thank_you_text=CONTACT_THANKS,
            subject="New message from the Judy's Daughter website",
            to_address=CONTACT_EMAIL,
        )
        home.add_child(instance=contact)
        self.setup_contact_form(contact)

        details = SiteDetails.for_site(site)
        details.business_name = "Judy's Daughter"
        details.tagline = "Birthwork is heart work."
        details.email = CONTACT_EMAIL or details.email
        details.logo = logo
        details.accepts_medi_cal = True
        details.save()

        self.setup_owner_group(home)
        self.stdout.write(self.style.SUCCESS("Seeded Judy's Daughter."))

    def setup_contact_form(self, contact):
        contact.form_fields.all().delete()
        for i, (name, label, ftype, required, placeholder, help_text) in enumerate(CONTACT_FIELDS):
            ContactFormField.objects.create(
                page=contact, sort_order=i, clean_name=name, label=label, field_type=ftype,
                required=required, placeholder=placeholder, help_text=help_text,
                choices="Yes\nNo" if ftype == "radio" else "",
            )
        contact.save_revision().publish()

    def create_testimonial_form_page(self, home):
        """Link-only form clients use to send a testimonial for approval."""
        if TestimonialRequestPage.objects.exists():
            self.stdout.write("Testimonial form page already exists.")
            return
        page = TestimonialRequestPage(
            title="Share your experience", slug="share-your-story", show_in_menus=False,
        )
        home.add_child(instance=page)
        page.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"Added testimonial form at {page.url}"))

    def create_collaborators_page(self, home):
        if CollaboratorsPage.objects.exists():
            self.stdout.write("Collaborators page already exists.")
            return
        page = CollaboratorsPage(
            title="Collaborators", slug="collaborators", show_in_menus=True,
            intro=COLLABORATORS_INTRO,
        )
        home.add_child(instance=page)
        for i, (business, person, location, description, url) in enumerate(COLLABORATORS):
            Collaborator.objects.create(
                page=page, sort_order=i, business=business, person=person,
                location=location, description=description, url=url,
            )
        page.save_revision().publish()
        # Put it in the menu after Testimonials.
        testimonials = home.get_children().filter(slug="testimonials").first()
        if testimonials:
            page.move(testimonials, pos="right")
        self.stdout.write(self.style.SUCCESS(f"Added collaborators page at {page.url}"))

    def create_calendar_page(self, home):
        """The booking calendar from the old /book page, shared by link only."""
        if CalendarPage.objects.exists():
            self.stdout.write("Calendar page already exists.")
            return
        page = CalendarPage(
            title="Schedule an appointment",
            slug="book",  # same address as the old site, so shared links keep working
            show_in_menus=False,
            calendar_url=CALENDAR_URL,
            calendar_height=900,
        )
        home.add_child(instance=page)
        page.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"Added calendar page at {page.url}"))

    def create_demo_posts(self, blog):
        """Example journal posts, always saved as unpublished drafts.

        They show Lyndsay what a post can hold (headings, photos, a pull quote,
        tags) and are meant to be rewritten in her own voice or deleted.
        """
        note = (
            "<p><b>Demo post.</b> This is an example to show how a journal post looks. "
            "Rewrite it in your own words, or delete it, before publishing.</p>"
        )

        def photo(title, caption="", wide=False):
            return ("image", {"image": block_image(Image.objects.get(title=title)),
                              "caption": caption, "wide": wide})

        posts = [
            dict(
                title="What does a doula actually do?",
                slug="what-does-a-doula-do",
                intro=(
                    "A doula is your continuous, non-medical support person through pregnancy, "
                    "birth and the weeks after. Here's what that looks like in practice."
                ),
                feature="Lyndsay supporting a client at home",
                tags=["doula care", "getting started"],
                body=[
                    ("paragraph", note),
                    ("heading", "Before birth"),
                    ("paragraph", "<p>Prenatal visits, a birth plan built around your yeses and nos, "
                                  "and coaching for your partner or support person.</p>"),
                    ("heading", "During birth"),
                    ("paragraph", "<p>Continuous emotional, physical, and advocacy support through "
                                  "active labor and the first hours with your baby.</p>"),
                    ("heading", "After birth"),
                    ("paragraph", "<p>Postpartum visits, newborn care, feeding guidance, and "
                                  "referrals so you can rest and heal.</p>"),
                ],
            ),
            dict(
                title="Planning for the fourth trimester",
                slug="planning-for-the-fourth-trimester",
                intro=(
                    "The weeks after birth deserve as much planning as the birth itself. "
                    "A few questions to talk through before baby arrives."
                ),
                feature="Lyndsay holding a newborn",
                tags=["postpartum", "planning"],
                body=[
                    ("paragraph", note),
                    ("paragraph", "<p>Most birth plans end the moment baby arrives. A postpartum "
                                  "plan picks up from there: who is helping, how you'll rest, and "
                                  "what you'll eat.</p>"),
                    ("heading", "Questions to talk through"),
                    ("paragraph", "<ul><li>Who can bring meals or help around the house in the "
                                  "first two weeks?</li><li>How will night feeds be shared?</li>"
                                  "<li>Who can you call when you have a feeding question?</li>"
                                  "<li>What does rest look like for you?</li></ul>"),
                    ("quote", {"quote": "The beauty of birth can be in its unpredictability, and "
                                        "we can be intentional about that too.",
                               "attribution": "Lyndsay Cromwell"}),
                    photo("Lyndsay holding a smiling baby", "Caption: a line about this photo."),
                    ("heading", "Where a postpartum doula fits"),
                    ("paragraph", "<p>In-home visits for newborn care, feeding support, emotional "
                                  "processing, and practical help as your family settles into a "
                                  "new rhythm.</p>"),
                ],
            ),
            dict(
                title="What happens during an overnight visit",
                slug="what-happens-during-an-overnight-visit",
                intro=(
                    "An overnight visit is eight hours of newborn care while you rest. "
                    "Here's how a night usually goes."
                ),
                feature="Lyndsay resting with newborn triplets",
                tags=["postpartum", "overnight support"],
                body=[
                    ("paragraph", note),
                    ("paragraph", "<p>Write about how an overnight visit starts, what you take care "
                                  "of through the night, and how you hand off in the morning.</p>"),
                    photo("Lyndsay resting with newborn triplets",
                          "Caption: a line about this photo.", wide=True),
                    ("heading", "Before you go to sleep"),
                    ("paragraph", "<p>Notes on settling in, feeding plans and anything the family "
                                  "wants to share.</p>"),
                    ("heading", "In the morning"),
                    ("paragraph", "<p>Notes on the handoff: how the night went, feeds, sleep, and "
                                  "anything to keep an eye on.</p>"),
                ],
            ),
        ]

        created = 0
        for data in posts:
            if BlogPage.objects.filter(slug=data["slug"]).exists():
                continue
            post = BlogPage(
                title=data["title"],
                slug=data["slug"],
                intro=data["intro"],
                feature_image=Image.objects.get(title=data["feature"]),
                body=data["body"],
                live=False,
            )
            blog.add_child(instance=post)
            post.tags.add(*data["tags"])
            post.save_revision()  # a draft revision only: never published
            created += 1
        self.stdout.write(self.style.SUCCESS(f"Added {created} demo post(s) as unpublished drafts."))

    def setup_owner_group(self, home):
        """A 'Site owner' group: full control of content, no access to users or code settings."""
        group, _ = Group.objects.get_or_create(name="Site owner")
        group.permissions.add(
            Permission.objects.get(codename="access_admin"),
            *Permission.objects.filter(
                content_type__app_label="testimonials", codename__in=[
                    "add_testimonial", "change_testimonial", "delete_testimonial", "view_testimonial",
                ]
            ),
            Permission.objects.get(codename="change_sitedetails"),
            *Permission.objects.filter(
                content_type__app_label="taggit", codename__in=["add_tag", "change_tag", "view_tag"]
            ),
        )
        for codename in ["add_page", "change_page", "publish_page", "lock_page", "unlock_page", "delete_page"]:
            GroupPagePermission.objects.get_or_create(
                group=group, page=home, permission=Permission.objects.get(
                    content_type__app_label="wagtailcore", codename=codename
                )
            )
        root_collection = Collection.get_first_root_node()
        for app, model in [("wagtailimages", "image"), ("wagtaildocs", "document")]:
            for action in ["add", "change", "choose", "delete"]:
                GroupCollectionPermission.objects.get_or_create(
                    group=group, collection=root_collection,
                    permission=Permission.objects.get(
                        content_type__app_label=app, codename=f"{action}_{model}"
                    ),
                )
