from django.conf.urls import patterns, url

urlpatterns = patterns('',
       url(r'^launch_lti/$', 'LTI.views.launch_lti', name="launch_lti"),
)
