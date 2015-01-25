from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
                       url(r'^add_course/$', views.add_course, name='add_course'),
                       url(r'^add_assignment/$', views.add_assignment, name='add_assignment'),
                       url(r'^authenticate/$', views.add_assignment, name='authenticate'),
                       url(r'$', views.manage, name='manage'),
                       # url(r'^$')
)
