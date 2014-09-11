""" 
This file contains the default settings, the project 
settings file will override them 
""" 

from django.conf import settings


def setconf(name, default_value):
    """set default value to django.conf.settings"""
    value = getattr(settings, name, default_value)
    setattr(settings, name, value)

setconf('LTI_DEBUG', False)
setconf('CONSUMER_URL', 'consumer url')
setconf('CONSUMER_KEY', 'the consumer key')
setconf('LTI_SECRET', 'the secret key')
setconf('LTI_FIRST_NAME','lis_person_name_given')
setconf('LTI_LAST_NAME','lis_person_name_family')
setconf('LTI_EMAIL','lis_person_contact_email_primary')
setconf('LTI_ROLES', 'roles')
setconf('LTI_OUTCOME', 'lis_outcome_service_url')


