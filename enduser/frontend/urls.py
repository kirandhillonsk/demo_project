'''
/**
 *@copyright : ToXSL Technologies Pvt. Ltd. < www.toxsl.com >
 *@author     : Shiv Charan  spaceeta < shiv@toxsl.com >
 *
 * All Rights Reserved.
 * Proprietary and confidential :  All information contained herein is, and remains
 * the property of ToXSL Technologies Pvt. Ltd. and its partners.
 * Unauthorized copying of this file, via any medium is strictly prohibited.
 *
 *
 */
 '''
 
from django.conf.urls import url
from django.contrib import admin
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from .sitemaps import  StaticSitemap
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

admin.autodiscover()

app_name = 'frontend'

sitemaps = {
 'pages': StaticSitemap,
}


urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^sitemap.xml$', sitemap, {'sitemaps': sitemaps}),
    url(r'^robots.txt$', robot, name='robots'),
    url(r'^robots/$', robot, name='robots'),
    url(r'contact-us/$', ContactUs, name='contact'),
    url(r'find-services/$', FindServices, name='find_services'),
    url(r'career/$', Career, name='career'),
    url(r'rvt-main-profile/$', ProfileView, name='user_profile'),
    url(r'help-support/$', HelpSupport, name='help_support'),
    url(r'promotional-video-/$', HelpSupport, name='romotional_video_stream'),
    url(r'service-list/$', ServiceList, name='service_list'),
    url(r'search-service/$', SearchService, name='search_service'),
    url(r'user-check-rvt/$', UserCheckRvt, name='user_check_rvt'),
    url(r'terms-and-conditions/$', TermPage, name='terms'),
    url(r'privacy-policy/$', PrivacyPage, name='privacy_policy'),
    url(r'cookie-policy/$', CookiePolicyPage, name='cookie_policy'),
    url(r'about-us/$', AboutPage, name='about'),
    url(r'join-us/$', join_us, name='join_us'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
