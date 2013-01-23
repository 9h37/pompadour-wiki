# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.conf import settings

from openid.consumer.consumer import SUCCESS

class GoogleBackend:
    """ Backend for Google OpenID authentication. """

    def authenticate(self, openid_response):
        if openid_response is None or openid_response.status != SUCCESS:
            return None

        google_email = openid_response.getSigned('http://openid.net/srv/ax/1.0', 'value.email')
        google_firstname = openid_response.getSigned('http://openid.net/srv/ax/1.0', 'value.firstname')
        google_lastname = openid_response.getSigned('http://openid.net/srv/ax/1.0', 'value.lastname')

        if not settings.GOOGLE_ACCEPT_ALL:
            # search domain in the list
            for domain in settings.GOOGLE_APP:
                # if found
                if google_email.endswith(domain):
                    break

            # if not found
            else:
                return None

        user, created = User.objects.get_or_create(email=google_email)
        user.username = google_email
        user.email = google_email
        user.first_name = google_firstname
        user.last_name = google_lastname
        user.save()

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


