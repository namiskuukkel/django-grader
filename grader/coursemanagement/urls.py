from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^add_course/$', views.add_course, name='add_course'),
    #url(r'^$')
)
