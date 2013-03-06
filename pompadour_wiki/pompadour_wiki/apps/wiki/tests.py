# -*- coding: utf-8 -*-

from django.test import TestCase
from django.test.client import Client

from django.template.defaultfilters import slugify

from django.contrib.auth.models import User
from pompadour_wiki.apps.wiki.models import Wiki

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

class WikiTest(TestCase):
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

    def test_01_home(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)

    def test_02_create_wiki(self):
        self.assertEqual(Wiki.objects.count(), 1)

    def test_03_view_page(self):
        response = self.client.get('/wiki/wiki-test-hehe/Home')

        self.assertEqual(response.status_code, 200)

    def test_04_edit_page(self):
        # Verify the page doesn't exist
        response = self.client.get('/wiki/wiki-test-hehe/Page')

        self.assertEqual(response.status_code, 302) # if the page is not found, the wiki redirect the user to an edit page

        # Check GET on edit page
        response = self.client.get('/wiki/wiki-test-hehe/Page/edit')

        self.assertEqual(response.status_code, 200)

        # Now send data
        response = self.client.post('/wiki/wiki-test-hehe/Page/edit', {
            'path': 'Page',
            'content': u'Test héhé',
            'comment': u'Commentaire de test héhé',
        })

        self.assertEqual(response.status_code, 302) # after an edit, the wiki redirect the user to the page

        # And now, check that the new page exists
        response = self.client.get('/wiki/wiki-test-hehe/Page')

        self.assertEqual(response.status_code, 200)

    def test_05_remove_page(self):
        self.test_04_edit_page()

        # Remove page

        response = self.client.get('/wiki/wiki-test-hehe/Page/remove')

        self.assertEqual(response.status_code, 302) # On delete, the user is redirected to wiki's home

        # Verify the page doesn't exist anymore
        
        response = self.client.get('/wiki/wiki-test-hehe/Page')

        self.assertEqual(response.status_code, 302) # if the page is not found, the wiki redirect the user to an edit page

