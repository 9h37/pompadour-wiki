# -*- coding: utf-8 -*-

from django.test import TestCase
from django.test.client import Client

from django.template.defaultfilters import slugify

from django.contrib.auth.models import User

from pompadour_wiki.apps.wiki.models import Wiki

import json

class UserTest(User):
    """
    Just create or get a user
    """

    @classmethod
    def get_or_create(cls, username, password, first_name, last_name, email):
        try:
            new_user = User.objects.create_user(username, email, password)

        except User.IntegrityError:
            return User.objects.get(username=username, email=email)

        else:
            new_user.first_name = first_name
            new_user.last_name = last_name
            new_user.save()

        return new_user


class FileManagerTest(TestCase):
    """
    Test Wiki views
    """

    def setUp(self):
        # Create User
        self.user = UserTest.get_or_create('gerard@example.com', 'gerard', u'Gérard', u'Test', 'gerard@example.com')

        # Authenticate user
        self.client = Client()
        self.client.login(username=self.user.username, password='gerard')

        # Create Wiki
        self.wiki = Wiki()
        self.wiki.name = u'Wiki Test Héhé'
        self.wiki.slug = slugify(self.wiki.name)
        self.wiki.description = u'Wiki de test héhé'
        self.wiki.gitdir = '/tmp/test-wiki/'

        self.wiki.create_repo()

        self.wiki.save()

    def tearDown(self):
        import subprocess
        subprocess.call(['rm', '-rf', self.wiki.gitdir])

    def test_01_index(self):
        response = self.client.get('/files/wiki-test-hehe/tree/')

        self.assertEqual(response.status_code, 200)

    def test_02_upload(self):
        # Upload that script
        import inspect

        with open(inspect.getfile(inspect.currentframe())) as fp:
            response = self.client.post('/files/wiki-test-hehe/upload', {
                'format': 'json',
                'path': '/',
                'doc': fp
            })

        # Make sure the file was uploaded
        self.assertEqual(response.status_code, 200)

        # Make sure that it returns the correct URL
        data = json.loads(response.content)
        self.assertEqual(data['url'], 'tests.py')

        # And make sure the file is accessible
        response = self.client.get('/files/wiki-test-hehe/view/tests.py')
        self.assertEqual(response.status_code, 200)