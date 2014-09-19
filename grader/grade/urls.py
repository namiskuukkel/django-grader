from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'(?P<course_name>.+)/(?P<assignment_name>.+)/$', views.grade, name='grade'),
    #url(r'^$')
)
