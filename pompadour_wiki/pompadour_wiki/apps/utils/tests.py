# -*- coding: utf-8 -*-

from django.test import TestCase

from django.core.cache import cache

from git_db import Repository
import subprocess

class RepositoryTest(TestCase):
    """
    Test Repository API
    """

    def test_repository(self):
        # Create repo
        repo = Repository.new('/tmp/test-repo')

        # Check if creation were OK
        self.assertTrue(repo.exists('Home.md'))

        # Check if commit were OK
        repo.set_content('test', 'test content', 'test message')
        self.assertTrue(repo.exists('test'))

        # Check if getting file were OK
        self.assertEqual(repo.get_content('test'), ('test content', 'test', 'text/plain'))

        # Check if modifying a file were OK
        repo.set_content('test', 'content', 'test message')

        self.assertTrue(repo.exists('test'))
        self.assertEqual(repo.get_content('test'), ('content', 'test', 'text/plain'))

        # Check if removing a file were OK
        repo.rm_content('test')
        self.assertFalse(repo.exists('test'))

        # Remove repo
        subprocess.call(['rm', '-rf', '/tmp/test-repo'])


class CacheTest(TestCase):
    """
    Test cache system
    """

    def test_cache(self):
        import random

        i = random.randint(0, 100)

        self.assertFalse(cache.has_key('test_key'))

        cache.set('test_key', i)

        self.assertTrue(cache.has_key('test_key'))
        self.assertEqual(cache.get('test_key'), i)

        cache.delete('test_key')

        self.assertFalse(cache.has_key('test_key'))