from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticSitemap(Sitemap):

    def items(self):
        return [
            'accounts:web_login',
            'accounts:web_signup',
            'frontend:find_services',
            'frontend:career',
            'blog:blog',
            'frontend:help_support'
        ]

    def location(self, item):
        return reverse(item)