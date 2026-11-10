from django.contrib.syndication.views import Feed

from .models import BlogIndexPage, BlogPage


class BlogFeed(Feed):
    title = "Judy's Daughter journal"
    description = "Notes on birth, postpartum and family life."

    def link(self):
        index = BlogIndexPage.objects.live().first()
        return index.url if index else "/"

    def items(self):
        return BlogPage.objects.live().public().order_by("-date")[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.intro

    def item_link(self, item):
        return item.full_url
