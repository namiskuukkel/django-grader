from django.conf.urls import url
import views

urlpatterns = [
                       url(r'^add_course/$', views.add_course, name='add_course'),
                       url(r'^add_assignment/$', views.add_assignment, name='add_assignment'),
                       url(r'^authenticate/$', views.authenticate, name='authenticate'),
                       url(r'$', views.manage, name='manage'),
                       # url(r'^$')
]
