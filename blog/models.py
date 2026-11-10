from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.utils import timezone
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.search import index

from core.blocks import BodyBlock


class BlogIndexPage(Page):
    intro = models.TextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("intro")]
    parent_page_types = ["home.HomePage"]
    subpage_types = ["blog.BlogPage"]
    max_count = 1

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        posts = BlogPage.objects.live().public().child_of(self).order_by("-date")
        tag = request.GET.get("tag")
        if tag:
            posts = posts.filter(tags__slug=tag)
        paginator = Paginator(posts, 9)
        try:
            page_obj = paginator.page(request.GET.get("page"))
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        context.update(posts=page_obj, tag=tag)
        return context


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey("blog.BlogPage", on_delete=models.CASCADE, related_name="tagged_items")


class BlogPage(Page):
    date = models.DateField("Post date", default=timezone.localdate)
    intro = models.TextField(
        max_length=300, help_text="One or two sentences shown on the blog list and in link previews."
    )
    feature_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    body = StreamField(BodyBlock())
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)

    search_fields = Page.search_fields + [index.SearchField("intro"), index.SearchField("body")]
    content_panels = Page.content_panels + [
        MultiFieldPanel([FieldPanel("date"), FieldPanel("tags")], heading="Post details"),
        FieldPanel("intro"),
        FieldPanel("feature_image"),
        FieldPanel("body"),
    ]
    parent_page_types = ["blog.BlogIndexPage"]
    subpage_types = []

    @property
    def reading_minutes(self):
        words = len(str(self.body).split())
        return max(1, round(words / 220))

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["more_posts"] = (
            BlogPage.objects.live().public().sibling_of(self, inclusive=False).order_by("-date")[:2]
        )
        return context
