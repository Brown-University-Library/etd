'''Backport a useful change in the test Client from django 1.9.
Of course, this will be unnecessary when our version of django gets upgraded.'''
from importlib import import_module
from django.conf import settings
from django.http import HttpRequest
from django.test import Client


class ETDTestClient(Client):

    def login(self, **credentials):
        from django.contrib.auth import authenticate
        user = authenticate(**credentials)
        if (user and user.is_active and apps.is_installed('django.contrib.sessions')):
            self._login(user)
            return True
        else:
            return False

    def force_login(self, user, backend=None):
        if backend is None:
            backend = settings.AUTHENTICATION_BACKENDS[0]
        user.backend = backend
        self._login(user)

    def _login(self, user):
        from django.contrib.auth import login
        engine = import_module(settings.SESSION_ENGINE)

        # Create a fake request to store login details.
        request = HttpRequest()
        if self.session:
            request.session = self.session
        else:
            request.session = engine.SessionStore()
        login(request, user)

        # Save the session values.
        request.session.save()

        # Set the cookie to represent the session.
        session_cookie = settings.SESSION_COOKIE_NAME
        self.cookies[session_cookie] = request.session.session_key
        cookie_data = {
            'max-age': None,
            'path': '/',
            'domain': settings.SESSION_COOKIE_DOMAIN,
            'secure': settings.SESSION_COOKIE_SECURE or None,
            'expires': None,
        }
        self.cookies[session_cookie].update(cookie_data)
