from django.conf.urls import url
from views import launch_lti, login_info
urlpatterns = [
       url(r'^launch_lti/$', launch_lti, name="launch_lti"),
       url(r'^login_info/$', login_info, name="login_info"),
]
