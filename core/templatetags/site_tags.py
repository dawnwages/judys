from django import template
from wagtail.models import Page, Site

register = template.Library()


@register.simple_tag(takes_context=True)
def nav_pages(context):
    """Top-level pages marked 'Show in menus', in page-tree order."""
    request = context.get("request")
    site = Site.find_for_request(request) if request else None
    if not site:
        return Page.objects.none()
    return site.root_page.get_children().live().in_menu().specific()


@register.simple_tag
def nav_contact():
    from contact.models import ContactPage

    return ContactPage.objects.live().first()


@register.filter
def in_section(item, page):
    """True when `page` is `item` or lives underneath it."""
    if not page or not hasattr(page, "path"):
        return False
    return page.pk == item.pk or page.path.startswith(item.path)
