from django.contrib.sitemaps import Sitemap
from .models import NewsArticle

class NewsArticleSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return NewsArticle.objects.all()

    def lastmod(self, obj):
        return obj.published_at

    def location(self, obj):
        return f"/news/{obj.id}/"  # Adjust the URL pattern as needed