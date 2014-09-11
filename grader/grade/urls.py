from django.conf.urls import patterns, include, url
import views

urlpatterns = patterns('',
    # ex: /polls/
    url(r'^$', views.grade, name='grade'),
)
