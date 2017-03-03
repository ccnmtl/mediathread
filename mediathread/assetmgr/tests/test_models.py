# pylint: disable-msg=R0904
from django.core.cache import cache
from django.test import TestCase

from mediathread.assetmgr.models import Asset, Source, METADATA_ORIGINAL_OWNER
from mediathread.djangosherd.models import SherdNote
from mediathread.factories import (
    MediathreadTestMixin, AssetFactory,
    UserFactory, SherdNoteFactory, ProjectFactory,
    SuggestedExternalCollectionFactory, SourceFactory,
    ExternalCollectionFactory,
)


class AssetTest(MediathreadTestMixin, TestCase):
    def setUp(self):
        self.setup_sample_course()
        self.setup_alternate_course()

        # instructor that sees both Sample Course & Alternate Course
        self.instructor_three = UserFactory(username='instructor_three')
        self.add_as_faculty(self.sample_course, self.instructor_three)
        self.add_as_faculty(self.alt_course, self.instructor_three)

        # Sample Course Image Asset
        self.asset1 = AssetFactory.create(course=self.sample_course,
                                          primary_source='image',
                                          author=self.instructor_one)

        self.student_note = SherdNoteFactory(
            asset=self.asset1, author=self.student_one,
            tags=',student_one_selection',
            body='student one selection note', range1=0, range2=1)
        self.student_ga = SherdNoteFactory(
            asset=self.asset1, author=self.student_one,
            tags=',student_one_item',
            body='student one item note',
            title=None, range1=None, range2=None)
        self.instructor_note = SherdNoteFactory(
            asset=self.asset1, author=self.instructor_one,
            tags=',image, instructor_one_selection,',
            body='instructor one selection note', range1=0, range2=1)
        self.instructor_ga = SherdNoteFactory(
            asset=self.asset1, author=self.instructor_one,
            tags=',image, instructor_one_item,',
            body='instructor one item note',
            title=None, range1=None, range2=None)

    def tearDown(self):
        cache.clear()

    def test_unicode(self):
        asset1 = AssetFactory.create(course=self.sample_course,
                                     primary_source='image',
                                     author=self.instructor_one,
                                     title="Item Title")
        self.assertEquals(asset1.__unicode__(),
                          'Item Title <%s> (Sample Course)' % asset1.id)

    def test_get_by_args(self):
        success, asset = Asset.objects.get_by_args(
            {'foo': 'bar'}, asset__course=self.sample_course)
        self.assertFalse(success)
        self.assertIsNone(asset)

        data = {'title': 'Z',
                'url': 'https://www.google.com/search=X',
                'metadata-image': '',
                'image': 'data:image/jpeg;base64,/9j/'}
        success, asset = Asset.objects.get_by_args(
            data, asset__course=self.sample_course)
        self.assertTrue(success)
        self.assertIsNone(asset)

        asset1 = AssetFactory.create(course=self.sample_course,
                                     primary_source='mp4_pseudo',
                                     author=self.instructor_one)

        data = {'title': asset1.title,
                'mp4_pseudo': asset1.primary.url}

        success, asset = Asset.objects.get_by_args(
            data, asset__course=self.sample_course)
        self.assertTrue(success)
        self.assertEquals(asset1, asset)

    def test_metadata(self):
        asset1 = AssetFactory.create(
            course=self.sample_course, primary_source='image',
            author=self.instructor_one,
            metadata_blob='{"category": ["Education"], "author": ["CCNMTL"]}',
            title="Item Title")

        ctx = asset1.metadata()
        self.assertEquals(ctx['author'], [u'CCNMTL'])
        self.assertEquals(ctx['category'], [u'Education'])

        asset2 = AssetFactory.create(course=self.sample_course)
        self.assertEquals(asset2.metadata(), {})

        asset3 = AssetFactory.create(
            course=self.sample_course, primary_source='image',
            author=self.instructor_one,
            metadata_blob='#$%^&*()_',
            title="Item Title")
        self.assertEquals(asset3.metadata(), {})

    def test_video(self):
        asset = AssetFactory.create(
            course=self.sample_course, primary_source='youtube')

        # youtube -- asset #1
        self.assertEquals(asset.media_type(), 'video')
        self.assertFalse(asset.primary.is_image())
        self.assertFalse(asset.primary.is_audio())

    def test_image(self):
        asset = AssetFactory.create(
            course=self.sample_course, primary_source='image')

        self.assertEquals(asset.media_type(), 'image')
        self.assertTrue(asset.primary.is_image())
        self.assertFalse(asset.primary.is_audio())

    def test_migrate_many(self):
        from_course = self.sample_course
        faculty = [user.id for user in from_course.faculty.all()]

        to_course = self.alt_course
        self.assertEquals(to_course.asset_set.count(), 0)

        assets = Asset.objects.filter(course=self.sample_course)

        object_map = {'assets': {}, 'notes': {}}
        object_map = Asset.objects.migrate(
            assets, to_course, self.instructor_three, faculty, object_map,
            True, True)

        self.assertEquals(to_course.asset_set.count(), 1)
        asset = object_map['assets'][self.asset1.id]
        self.assertEquals(asset.title, self.asset1.title)
        self.assertEquals(asset.course, to_course)
        self.assertEquals(asset.author, self.instructor_three)
        self.assertEquals(len(asset.sherdnote_set.all()), 2)

        # instructor note exists with tags
        note = asset.sherdnote_set.get(title=self.instructor_note.title)
        self.assertEquals(note.tags, ',image, instructor_one_selection,')
        self.assertEquals(note.body, 'instructor one selection note')

        gann = asset.global_annotation(self.instructor_three, False)
        self.assertTrue(gann is not None)
        self.assertEquals(gann.tags, ',image, instructor_one_item,')
        self.assertEquals(gann.body, 'instructor one item note')

    def test_migrate_one(self):
        new_course = self.alt_course
        new_user = self.alt_instructor

        asset = Asset.objects.migrate_one(
            self.asset1, new_course, new_user)
        self.assertEquals(asset.author, new_user)
        self.assertEquals(asset.course, new_course)

        self.assertEquals(asset.sherdnote_set.count(), 1)

        gann = asset.sherdnote_set.all()[0]
        self.assertTrue(gann.is_global_annotation())
        self.assertEquals(gann.tags, '')
        self.assertEquals(gann.body, None)

        self.assertEquals(
            asset.metadata()[METADATA_ORIGINAL_OWNER], 'Instructor One')

        asset2 = Asset.objects.migrate_one(
            asset, self.sample_course, self.instructor_two)
        self.assertEquals(asset2.author, self.instructor_two)
        self.assertEquals(asset2.course, self.sample_course)
        self.assertEquals(
            asset2.metadata()[METADATA_ORIGINAL_OWNER], 'Instructor One')

    def test_migrate_note_global_annotations(self):
        alt_asset = AssetFactory.create(course=self.alt_course,
                                        primary_source='image')

        # migrate a global annotation
        global_note = SherdNote.objects.migrate_one(
            self.instructor_ga, alt_asset, self.instructor_three, True, True)
        self.assertTrue(global_note.is_global_annotation())
        self.assertEquals(global_note.author, self.instructor_three)
        self.assertEquals(global_note.title, None)
        self.assertEquals(global_note.tags, self.instructor_ga.tags)
        self.assertEquals(global_note.body, self.instructor_ga.body)

        # try to migrate another global annotation as well
        # the global annotation that was already created will come back
        another_note = SherdNote.objects.migrate_one(
            self.student_ga, alt_asset, self.instructor_three, True, True)
        self.assertEquals(another_note, global_note)

    def test_migrate_note_regular_annotations(self):
        alt_asset = AssetFactory.create(course=self.alt_course,
                                        primary_source='image')

        # migrate a regular annotation
        new_note = SherdNote.objects.migrate_one(
            self.instructor_note, alt_asset, self.instructor_three, True, True)
        self.assertFalse(new_note.is_global_annotation())
        self.assertEquals(new_note.author, self.instructor_three)
        self.assertEquals(new_note.title, self.instructor_note.title)
        self.assertEquals(new_note.tags, self.instructor_note.tags)
        self.assertEquals(new_note.body, self.instructor_note.body)

    def test_migrate_one_duplicates(self):
        new_asset = Asset.objects.migrate_one(
            self.asset1, self.alt_course, self.alt_instructor)
        self.assertEquals(new_asset.author, self.alt_instructor)
        self.assertEquals(new_asset.course, self.alt_course)
        self.assertEquals(new_asset.get_metadata(
            METADATA_ORIGINAL_OWNER), 'Instructor One')

        duplicate_asset = Asset.objects.migrate_one(
            self.asset1, self.alt_course, self.alt_instructor)
        self.assertEquals(new_asset, duplicate_asset)
        self.assertEquals(duplicate_asset.get_metadata(
            METADATA_ORIGINAL_OWNER), 'Instructor One')

        new_note = SherdNote.objects.migrate_one(
            self.instructor_note, new_asset, self.alt_instructor, True, True)
        self.assertFalse(new_note.is_global_annotation())
        self.assertEquals(new_note.author, self.alt_instructor)
        self.assertEquals(new_note.title, self.instructor_note.title)

        duplicate_note = SherdNote.objects.migrate_one(
            self.instructor_note, new_asset, self.alt_instructor, True, True)
        self.assertEquals(new_note, duplicate_note)

    def test_update_reference_in_string(self):
        extra_asset = AssetFactory.create(course=self.sample_course,
                                          primary_source='image')
        extra_note = SherdNoteFactory(
            asset=extra_asset, author=self.student_one)

        new_asset = AssetFactory.create(course=self.sample_course,
                                        primary_source='image')

        project = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='PrivateEditorsAreOwners')
        self.add_citation(project, self.instructor_note)
        self.add_citation(project, extra_note)

        # old-style whole-item annotation
        project.body = '%s <a class="materialCitation" \
            href="/asset/%s/">Whole Item</a></p>' % \
            (project.body, self.asset1.id)

        new_text = new_asset.update_references_in_string(project.body,
                                                         self.asset1)

        new_asset_href = "/asset/%s/" % (new_asset.id)
        self.assertTrue(new_text.find(new_asset_href) > 0)

        old_asset_href = "/asset/%s/" % self.asset1.id
        self.assertTrue(new_text.find(old_asset_href) > 0)

        citations = SherdNote.objects.references_in_string(new_text,
                                                           new_asset.author)
        self.assertEquals(len(citations), 3)
        self.assertEquals(citations[0].id, self.instructor_note.id)
        self.assertEquals(citations[0].asset.id, self.asset1.id)

        self.assertEquals(citations[1].id, extra_note.id)
        self.assertEquals(citations[1].asset.id, extra_asset.id)

        gann = new_asset.global_annotation(new_asset.author, False)
        self.assertEquals(citations[2].id, gann.id)
        self.assertEquals(citations[2].asset.id, new_asset.id)

    def test_user_analysis_count(self):
        SherdNoteFactory(
            asset=self.asset1, author=self.student_two,
            tags=',student_two_item',
            title=None, range1=None, range2=None)

        # global notes y/n + global tag count + annotation count
        self.assertEquals(0,
                          self.asset1.user_analysis_count(self.instructor_two))
        self.assertEquals(1,
                          self.asset1.user_analysis_count(self.student_two))
        self.assertEquals(4,
                          self.asset1.user_analysis_count(self.instructor_one))

    def test_assets_by_course(self):
        assets = Asset.objects.by_course(course=self.sample_course)
        self.assertEquals(assets.count(), 1)

        self.assertEquals(self.asset1, assets[0])

    def test_assets_by_course_and_user(self):
        # tweak an asset to have a non-primary archive label
        asset2 = AssetFactory.create(course=self.sample_course,
                                     author=self.instructor_one,
                                     primary_source='image')
        metadata = Source.objects.create(asset=asset2, label='archive',
                                         primary=False,
                                         url="http://ccnmtl.columbia.edu")
        asset2.source_set.add(metadata)

        assets = Asset.objects.by_course_and_user(self.sample_course,
                                                  self.instructor_one)
        self.assertEquals(assets.count(), 1)
        self.assertIsNotNone(assets[0], asset2)

        assets = Asset.objects.by_course_and_user(self.sample_course,
                                                  self.student_one)
        self.assertEquals(assets.count(), 1)
        self.assertIsNotNone(assets[0], asset2)

        assets = Asset.objects.by_course_and_user(self.sample_course,
                                                  self.student_two)
        self.assertEquals(assets.count(), 0)

    def test_source_unicode(self):
        desc = self.asset1.primary.__unicode__()
        self.assertTrue('[image]' in desc)
        self.assertTrue('Sample Course' in desc)

    def test_external_collection_unicode(self):
        collection = ExternalCollectionFactory()
        self.assertEquals(collection.__unicode__(), 'collection')

    def test_suggested_external_collection_unicode(self):
        collection = SuggestedExternalCollectionFactory()
        self.assertEquals(collection.__unicode__(), 'collection')

    def test_html_source(self):
        with self.assertRaises(Source.DoesNotExist):
            self.asset1.html_source

        src = SourceFactory(label='url', asset=self.asset1,
                            url="http://ccnmtl.columbia.edu")
        self.assertEquals(src, self.asset1.html_source)

    def test_xmeml_source(self):
        self.assertIsNone(self.asset1.xmeml_source())
        src = SourceFactory(label='xmeml', asset=self.asset1,
                            url="http://ccnmtl.columbia.edu")
        self.assertEquals(src, self.asset1.xmeml_source())

    def test_sources(self):
        self.assertTrue('image' in self.asset1.sources)

        image_src = Source.objects.get(label='image', asset=self.asset1)
        self.assertEquals(self.asset1.sources['image'], image_src)

    def test_thumb_url_empty(self):
        self.assertIsNone(self.asset1.thumb_url)

    def test_thumb_url_valid(self):
        SourceFactory(label='thumb', asset=self.asset1,
                      url="http://ccnmtl.columbia.edu")
        self.assertEquals(self.asset1.thumb_url, "http://ccnmtl.columbia.edu")
        self.assertEquals(self.asset1.thumb_url, "http://ccnmtl.columbia.edu")

    def test_tags(self):
        tags = self.asset1.tags()
        self.assertEquals(len(tags), 5)
        self.assertEquals(tags[0].name, 'image')
        self.assertEquals(tags[1].name, 'instructor_one_item')
        self.assertEquals(tags[2].name, 'instructor_one_selection')
        self.assertEquals(tags[3].name, 'student_one_item')
        self.assertEquals(tags[4].name, 'student_one_selection')

    def test_filter_tags_by_users(self):
        tags = self.asset1.filter_tags_by_users([self.student_one])
        self.assertEquals(len(tags), 2)
        self.assertEquals(tags[0].name, 'student_one_item')
        self.assertEquals(tags[1].name, 'student_one_selection')

    def test_update_primary(self):
        s = self.asset1.primary
        self.assertEquals(s.label, 'image')

        # update
        self.asset1.update_primary('mp4_pseudo', 'something new')
        s = self.asset1.primary

        # verify the new value is returned
        self.assertEquals(s.label, 'mp4_pseudo')
        self.assertEquals(s.url, 'something new')


class SourceTest(TestCase):
    def setUp(self):
        self.source = SourceFactory()

    def test_is_valid_from_factory(self):
        self.source.full_clean()
