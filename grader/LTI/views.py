#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from ims_lti_py.tool_provider import DjangoToolProvider
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from django.conf import settings 
from utils import *
from django.contrib.auth.models import User
from django.contrib.auth import login
import logging

logging.basicConfig(filename='Logs/lti.log' ,level=logging.DEBUG)

@csrf_exempt
def launch_lti(request):
    """ Receives a request from the lti consumer and creates/authenticates user in django """

    """ See post items in log by setting LTI_DEBUG=True in settings """    
    if settings.LTI_DEBUG:
        for item in request.POST:
            print ('%s: %s \r' % (item, request.POST[item]))

    if 'oauth_consumer_key' not in request.POST:
        logging.error('oauth_consumer_key missing from request')
        raise PermissionDenied()  
    
    """ key/secret from settings """
    consumer_key = settings.CONSUMER_KEY 
    secret = settings.LTI_SECRET    
    tool_provider = DjangoToolProvider(consumer_key, secret, request.POST)

    """ Decode parameters - UOC LTI uses a custom param to indicate the encoding: utf-8, iso-latin, base64 """
    encoding = None
    utf8 = get_lti_value('custom_lti_message_encoded_utf8', tool_provider)         
    iso = get_lti_value('custom_lti_message_encoded_iso', tool_provider)       
    b64 = get_lti_value('custom_lti_message_encoded_base64', tool_provider)  

    if iso and int(iso) == 1: encoding = 'iso'
    if utf8 and int(utf8) == 1: encoding = 'utf8'
    if b64 and int(b64) == 1: encoding = 'base64'
    
    try: # attempt to validate request, if fails raises 403 Forbidden
        tool_provider.valid_request(request)
    except:
        logging.error('Invalid LTI request')
        print "LTI Exception:  Not a valid request."
        raise PermissionDenied() 

    email = get_lti_value(settings.LTI_EMAIL, tool_provider, encoding=encoding)
    roles = get_lti_value(settings.LTI_ROLES, tool_provider, encoding=encoding)
    user_id = get_lti_value('user_id', tool_provider, encoding=encoding)
    course_id= get_lti_value('context_id', tool_provider, encoding=encoding)
    course_name = get_lti_value('context_title', tool_provider, encoding=encoding)
    assignment = get_lti_value('resource_link_title', tool_provider, encoding=encoding)
    outcome_url = get_lti_value(settings.LTI_OUTCOME, tool_provider, encoding=encoding)

    if not email or not user_id:
        if settings.LTI_DEBUG: print "Email and/or user_id wasn't found in post"
        raise PermissionDenied()
    
    """ GET OR CREATE NEW USER AND LTI_PROFILE """
    lti_username = '%s;user_%s' % (email, user_id) #create username with email and user_id
    try:
        """ Check if user already exists using email, if not create new """    
        user = User.objects.get(email=email)
        if user.username != lti_username:
            """ If the username is not in the format user_id, change it and save.  This could happen
            if there was a previously populated User table. """
            user.username = lti_username
            user.save()
    except User.DoesNotExist:
        """ first time entry, create new user """
        user = User.objects.create_user(lti_username, email)
        user.set_unusable_password()
        user.save()
    except User.MultipleObjectsReturned:
        """ If the application is not requiring unique emails, multiple users may be returned if there was an existing
        User table before implementing this app with multiple users for the same email address.  Could add code to merge them, but for now we return 404 if 
        the user with the lti_username does not exist """    
        user = get_object_or_404(User, username=lti_username)

    #If person has an instructor role, let's make he/she an admin
    if 'Instructor' in roles and user.is_superuser == False:
        user.is_superuser = True
        user.is_staff = True
        user.save()
    
    """ Log in user and redirect to LOGIN_REDIRECT_URL defined in settings (default: accounts/profile) """
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
    request.session['course_id'] = course_id
    request.session['course_name'] = course_name
    request.session['assignment_name'] = assignment
    request.session['outcome'] = outcome_url

    return HttpResponseRedirect('/')
    