from django.contrib.auth.models import update_last_login
from django.contrib.auth.signals import user_logged_in

from buildingofs.ofsapi import rpc

from .models import Staff


class PlatformBackend(object):

    def authenticate(self, username=None, password=None):
        if not all([username, password]):
            return None

        result = rpc.staff.auth_staff_member(
            identifier=username,
            password=password
        )

        if result['success']:
            user_logged_in.disconnect(update_last_login)
            return Staff(result['data'])

        return None

    def get_user(self, user_id):
        try:
            return Staff.objects.get_cached(id=user_id)
        except Staff.DoesNotExist:
            return None
