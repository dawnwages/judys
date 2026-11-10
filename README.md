# Judy's Daughter

Website for Judy's Daughter, Lyndsay Cromwell's full-spectrum doula practice.
Built with Django + [Wagtail](https://wagtail.org) so Lyndsay can log in and
change photos, text, pricing, blog posts and testimonials herself.

This replaces the static HTML site in `dawnwages/judys`, live at https://judysdaughter.support. The original copy,
photos, pricing and testimonials were carried over by `manage.py seed_site`.

## Developer path

- Python is installed and managed by [`uv`](https://docs.astral.sh/uv/). The
  version is pinned in `.python-version` (3.14). Don't use the macOS system
  `python3` or Homebrew Python.
- One virtual environment per project, named `.venv`, created with `uv venv`.
- Install packages with `uv pip install` (uv environments have no `pip`, so
  "No module named pip" is expected). Dependencies are pinned in
  `pyproject.toml`; `requirements.txt` is generated from it for Docker:
  `uv pip compile pyproject.toml -o requirements.txt --python-version 3.14`.
- Run commands with `uv run ...` or after `source .venv/bin/activate`.

## Run it locally

```bash
uv venv
uv pip install -r pyproject.toml
uv run python manage.py migrate
uv run python manage.py seed_site          # loads the original site's content
uv run python manage.py add_editor lyndsay <her email> --first-name Lyndsay
uv run python manage.py runserver
```

Then open http://localhost:8000 for the site and http://localhost:8000/admin/
to log in. You can also create a full admin for yourself with
`uv run python manage.py createsuperuser`.

## What Lyndsay can edit (after logging in at `/admin/`)

| She wants to… | Where |
| --- | --- |
| Change a photo or any text on the home page | **Pages → Home → Edit**. Sections are grouped: top of page, about, offerings, philosophy & photos, how it works. |
| Upload or replace photos | **Images** (drag in several at once), or pick/upload straight from any image field. |
| Write a blog post | **Pages → Journal → Add child page**. Save a draft, preview, then Publish. |
| Add or reorder testimonials | **Testimonials** in the left menu. "Featured" ones (up to 3) show on the home page. |
| Change packages, prices, payment plans or bartering terms | **Pages → Packages & Pricing → Edit**. See "Editing the pricing page" below. |
| Read contact form messages | **Forms → Book a free consult**. Can export to CSV. |
| Change the contact form questions or get messages by email | **Pages → Book a free consult → Edit**. Put her email in "To address". |
| Change email, phone, logo, socials, booking link, Medi-Cal note | **Settings → Business details**. |
| Share her booking calendar with a client | Send them **/book/** (e.g. https://judysdaughter.support/book/). The page isn't linked anywhere on the site and is hidden from search engines. To change the calendar, edit **Pages → Schedule an appointment** and paste a new Google Calendar, Calendly, Acuity or Cal.com link. |
| Ask a client for a testimonial | Send them **/share-your-story/** (e.g. https://judysdaughter.support/share-your-story/). Like /book/, it isn't linked anywhere and is hidden from search engines. What they send arrives under **Testimonials** with "Show on website" unticked, and she gets an email with a link to it. Tick the box to publish it. The form's wording is under **Pages → Share your experience**. |
| Add, edit or reorder collaborators | **Pages → Collaborators → Edit**. Each has a business name, person, website, optional photo or logo (initials show without one), location, short description, tag and group heading. |
| Add another page (FAQ, resources…) | **Pages → Home → Add child page → Standard page**. Tick "Show in menus" under the Promote tab to add it to the nav. |

### Editing the pricing page

Everything on the pricing page is editable. The page is a stack of sections she
can add (+), reorder (arrows), duplicate or delete:

- **Package cards**: up to 4 cards per group. Each card has a name, price, optional
  note above the price ("starting at"), optional badge ("Most popular"), a "who it's
  for" line, what's included (each item can have a smaller explanation), a highlight
  option, and a button (contact form by default, or any page or web link).
- **Price list**: menu-style rows with dotted leaders, optional note per row,
  one or two columns.
- **Payment details**: policy text plus up to 4 numbered plan cards.
- **Text section**: paragraphs, rounded tags and a highlighted note (used for bartering).
- **Questions (FAQ)**: questions that open to show the answer.
- **Callout**: a short highlighted notice between sections, e.g. "Now accepting Medi-Cal".

Every section also has a short name for the links bar, a show/hide-in-links option,
an intro and a background choice. The title area and the closing box at the bottom
are editable too. Character limits and preset colors keep the layout legible
whatever she types.

While logged in, every page on the live site shows a small Wagtail button in
the corner with an **Edit this page** shortcut.

Her account is in the **Site owner** group (created by `seed_site`): full
control of content, images, testimonials and business details, but no access
to user accounts.

## Content to confirm with Lyndsay

- **Testimonials**: two short testimonials from the old site had no name and
  read like placeholder copy. They're imported but not featured on the home
  page. Confirm or delete them.
- **Starter blog post** "What does a doula actually do?" is a draft outline for
  her to rewrite in her own voice. It isn't published.
- **Email**: Lyndsay's Gmail is the default for now, set with the `CONTACT_EMAIL`
  environment variable rather than in code, because this repo is public (it
  receives contact-form messages, and is the production "from" address). It is
  never shown on the website. Switch to a
  judysdaughter.support address later in Business details, the contact page's
  "To address", and the `DEFAULT_FROM_EMAIL` setting.
- **Booking calendar**: the Google appointment schedule carried over from the old
  /book page belongs to a different Google account than Lyndsay's, so bookings go to that calendar. Swap
  in Lyndsay's own scheduling link when ready.
- **Business details**: service area and social links were not on the old site, so
  they're blank.
- **Stock photos**: the Birth, Postpartum and Meals offering cards use Unsplash
  photos from the old site. Swap in her own when she has them.

- **Pricing** follows Lyndsay's "JD Packages & Payment" PDF. To reload it from
  the seed after editing `seed_site.py`: `uv run python manage.py seed_site --update-pricing`
  (this overwrites any pricing edits made in the admin).

## Deploying

The live site (judysdaughter.support) is served by Netlify, which can't run Django.
Its contact form uses Netlify Forms: export any past submissions from the Netlify
dashboard before moving the domain, since they won't carry over. The new form uses
the same fields and field names, saves messages under **Forms** in the admin, and
emails them to Lyndsay with Reply set to the sender.

### Staging on Render

This code lives on the `wagtail` branch of `dawnwages/judys`. Netlify keeps deploying
`main`, so the live site is unaffected. `render.yaml` sets up staging:

1. In Render: **New → Blueprint**, connect `dawnwages/judys`, branch `wagtail`.
2. Fill in the values it asks for: `CONTACT_EMAIL` (Lyndsay's email), your admin
   login (`DJANGO_SUPERUSER_USERNAME`, `_EMAIL`, `_PASSWORD`), and optionally the
   two Google keys (below). Leave Google blank to start; town/city boxes then
   accept typed text.
3. Deploy. The first start loads all content and creates your admin login. The
   site appears at `https://judys-daughter-staging.onrender.com` (or similar),
   with a "Staging preview" banner, hidden from search engines.
4. Log in at `/admin/`, then **Settings → Users → Add a user** for Lyndsay and put
   her in the **Site owner** group.

Every push to `wagtail` redeploys staging. Content and photos stay (database and
disk persist). Email isn't sent until `EMAIL_HOST` etc. are set; messages are still
saved under **Forms**.

### Google town/city autocomplete

The contact form's "Your location" and "Delivery location" boxes suggest US towns
and cities as you type, and the server double-checks the choice with Google.
In Google Cloud: enable **Places API (New)** and **Maps JavaScript API**, then make
two API keys:

- `GOOGLE_MAPS_BROWSER_KEY`: restrict to websites (your staging and live addresses)
  and to those two APIs.
- `GOOGLE_PLACES_SERVER_KEY`: restrict to Places API (New) only.

Lyndsay can add more town/city questions in the admin with the field type
"Town / city (Google autocomplete)".

### Going live later

Point judysdaughter.support (DNS is managed in Netlify) at the Render service,
add the domain in Render, and set `ALLOWED_HOSTS`, `WAGTAILADMIN_BASE_URL` and
`STAGING=false`. A `Dockerfile` is also included for other hosts.

## Project layout

```
judys/        settings, urls, templates, static (site.css, site.js)
core/         Business details setting, shared content blocks, seed_site + add_editor commands
home/         Home, Pricing and Standard pages
blog/         Journal index + posts (tags, RSS at /blog/feed/)
testimonials/ Testimonial snippets + the Testimonials page
contact/      Contact form page (submissions stored in the admin)
seed/images/  Photos carried over from the original site
```
