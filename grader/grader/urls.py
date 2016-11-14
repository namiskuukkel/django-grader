from django.conf.urls import include, url
from django.contrib import admin
from grade.views import error, index
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    url(r'^lti/', include('LTI.urls')),
    url(r'^manage/', include('course_management.urls')),
    url(r'^grader/', include('grade.urls')),
    url(r'error', error, name='error'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'$', index, name='index'),
]

    # Examples:
    # url(r'^$', 'grader.views.home', name='home'),
    # url(r'^grader/', include('grader.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
