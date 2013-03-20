# -*- coding: utf-8 -*-

from django.test import TestCase

from pompadour_wiki.apps.tagging.models import Tag

class TagTest(TestCase):
    def test_00_nothing(self):
        """ Make sure there is no objects """

        c = Tag.objects.count()

        self.assertEqual(c, 0)

    def test_01_create(self):
        """ Create a tag """

        # Create
        t = Tag()
        t.page = 'test/Test'
        t.tag = 'test'
        t.save()

        # Make sure it's here
        c = Tag.objects.count()
        self.assertEqual(c, 1)

        # Make sure it's the good one
        tags = Tag.objects.filter(page='test/Test')

        self.assertNotEqual(tags, Tag.objects.none())
        self.assertEqual(tags.count(), 1)
        self.assertEqual(tags[0].tag, 'test')
        self.assertEqual(tags[0].page, 'test/Test')

    def test_02_delete(self):
        """ Delete a tag """
        self.test_01_create()

        tag = Tag.objects.all()[0]

        tag.delete()

        c = Tag.objects.count()
        self.assertEqual(c, 0)
