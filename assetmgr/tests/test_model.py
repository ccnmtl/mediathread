from assetmgr.models import Asset
from courseaffils.models import Course
from django.contrib.auth.models import User
from django.test import TestCase
from djangosherd.models import SherdNote
import simplejson


class AssetTest(TestCase):
    fixtures = ['unittest_sample_course.json']

    def test_video(self):
        # youtube -- asset #1
        asset = Asset.objects.get(id=1)
        self.assertEquals(asset.media_type(), 'video')
        self.assertFalse(asset.primary.is_image())
        self.assertFalse(asset.primary.is_archive())
        self.assertFalse(asset.primary.is_audio())

    def test_image(self):
        # image -- asset #2
        asset = Asset.objects.get(id=2)

        self.assertEquals(asset.media_type(), 'image')
        self.assertTrue(asset.primary.is_image())
        self.assertFalse(asset.primary.is_archive())
        self.assertFalse(asset.primary.is_audio())

    asset_set = [{"author": {"full_name": "Instructor One",
                             "id": 2,
                             "resource_uri": ""},
                  "id": 1,
                  "primary_type":"youtube",
                  "thumb_url":"http://i.ytimg.com/vi/7KjzRG8zYYo/default.jpg",
                  "title": "Mediathread: Introduction",
                  "sherdnote_set": [{
                      "id": 2,
                      "asset_id": "1",
                      "author": {"full_name": "Instructor One",
                                 "id": 2,
                                 "resource_uri": ""},
                      "is_global_annotation": "False",
                      "resource_uri": "/_main/api/v1/sherdnote/2/",
                      "title": "Manage Sources"},
                      {"asset_id": "1",
                       "author": {"full_name": "test_instructor_two",
                                  "id": 10,
                                  "resource_uri": ""},
                       "id": 19,
                       "is_global_annotation": "False",
                       "resource_uri": "/_main/api/v1/sherdnote/19/",
                       "title": "Video Selection Is Time-based"},
                      {"asset_id": "1",
                       "author": {"full_name": "test_instructor_two",
                                  "id": 10,
                                  "resource_uri": ""},
                       "id": 20,
                       "is_global_annotation": "True",
                       "resource_uri": "/_main/api/v1/sherdnote/20/",
                       "title": None,
                       "tags": ",ccnmtl,foo",
                       "body": "test instructor two notes"}]},
                 {"author": {"full_name": "Instructor One",
                             "id": 2,
                             "resource_uri": ""},
                  "id": 1,
                  "primary_type":"youtube",
                  "thumb_url":"http://i.ytimg.com/vi/7KjzRG8zYYo/default.jpg",
                  "title": "Wrong"},
                 {"author": {"full_name": "Instructor One",
                             "id": 2,
                             "resource_uri": ""},
                  "id": 2,
                  "primary_type": "image",
                  "thumb_url": "http://i.ytimg.com/vi/7KjzRG8zYYo/default.jpg",
                  "title": "MAAP Award Reception"}]

    def test_migrate_many(self):
        course = Course.objects.get(id=2)
        self.assertEquals(course.title, "Alternate Course")
        self.assertEquals(len(course.asset_set.all()), 1)

        user = User.objects.get(username='test_instructor_two')

        asset_json = simplejson.dumps(self.asset_set)
        assets = simplejson.loads(asset_json)

        object_map = {'assets': {}, 'notes': {}}
        object_map = Asset.objects.migrate(assets,
                                           course, user, object_map)

        self.assertEquals(len(course.asset_set.all()), 3)
        asset = object_map['assets'][1]
        self.assertNotEquals(asset.id, 1)
        self.assertEquals(asset.title, "Mediathread: Introduction")
        self.assertEquals(asset.course, course)
        self.assertEquals(asset.author, user)
        self.assertEquals(len(asset.sherdnote_set.all()), 3)

        asset = object_map['assets'][2]
        self.assertNotEquals(asset.id, 2)
        self.assertEquals(asset.title, "MAAP Award Reception")
        self.assertEquals(asset.course, course)
        self.assertEquals(asset.author, user)
        self.assertEquals(len(asset.sherdnote_set.all()), 1)

    def test_migrate_one(self):
        asset = Asset.objects.get(id=1)
        self.assertEquals(asset.title, "Mediathread: Introduction")

        new_course = Course.objects.get(id=2)
        self.assertEquals(new_course.title, "Alternate Course")

        new_user = User.objects.get(username='test_instructor_alt')

        new_asset = Asset.objects.migrate_one(asset, new_course, new_user)
        self.assertEquals(new_asset.author, new_user)
        self.assertEquals(new_asset.course, new_course)

        self.assertEquals(new_asset.media_type(), 'video')
        self.assertFalse(new_asset.primary.is_image())
        self.assertFalse(new_asset.primary.is_archive())
        self.assertFalse(new_asset.primary.is_audio())

        # migrate a global annotation
        global_annotation = SherdNote.objects.get(id=1)
        global_note = SherdNote.objects.migrate_one(global_annotation,
                                                    new_asset,
                                                    new_user)
        self.assertTrue(global_note.is_global_annotation())
        self.assertEquals(global_note.author, new_user)
        self.assertEquals(global_note.title, None)
        self.assertEquals(global_note.tags, '')
        self.assertEquals(global_note.body, None)

        # try to migrate another global annotation as well
        # the global annotation that was already created will come back
        another_global_annotation = SherdNote.objects.get(id=20)
        another_note = SherdNote.objects.migrate_one(another_global_annotation,
                                                     new_asset,
                                                     new_user)
        self.assertEquals(another_note, global_note)

        selected_annotation = SherdNote.objects.get(id=2)
        new_note = SherdNote.objects.migrate_one(selected_annotation,
                                                 new_asset,
                                                 new_user)
        self.assertFalse(new_note.is_global_annotation())
        self.assertEquals(new_note.author, new_user)
        self.assertEquals(new_note.title, 'Manage Sources')
        self.assertEquals(new_note.tags, ',video')
        self.assertEquals(new_note.body, None)

    def test_update_reference_in_string(self):
        text = ('<p><a href="/asset/2/annotations/10/">Nice Tie</a>'
                '</p><p><a href="/asset/2/annotations/10/">Nice Tie</a>'
                '</p><p><a href="/asset/2/annotations/8/">Nice Tie</a>'
                '</p><a href="/asset/2/">Whole Item</a></p>')

        old_asset = Asset.objects.get(id=2)
        new_asset = Asset.objects.get(id=1)

        new_text = new_asset.update_references_in_string(text, old_asset)

        citations = SherdNote.objects.references_in_string(new_text,
                                                           new_asset.author)
        self.assertEquals(len(citations), 4)
        self.assertEquals(citations[0].id, 10)
        self.assertEquals(citations[0].asset.id, 2)

        self.assertEquals(citations[1].id, 10)
        self.assertEquals(citations[1].asset.id, 2)

        self.assertEquals(citations[2].id, 8)
        self.assertEquals(citations[2].asset.id, 2)

        self.assertEquals(citations[3].id, 1)
        self.assertEquals(citations[3].asset.id, 1)
