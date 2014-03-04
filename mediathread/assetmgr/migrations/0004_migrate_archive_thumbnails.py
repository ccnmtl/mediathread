# flake8: noqa
# encoding: utf-8
from south.v2 import DataMigration
from mediathread.assetmgr.models import SupportedSource, Asset, Source


class Migration(DataMigration):

    url_map = {
        'http://archive.org/images/911.jpg': '/media/img/thumbs/911archive.png',
        'http://library.artstor.org/library/g-artstor-logo.gif': '/media/img/thumbs/artstor.png',
        'http://www.ancientgreece.co.uk/share_im/bm_logo.gif': '/media/img/thumbs/thebritishmuseum.png',
        'http://www.democracynow.org/images/nav/dn_logo.png': '/media/img/thumbs/democracynow.png',
        'http://digitaltibet.ccnmtl.columbia.edu/sites/digitaltibet.ccnmtl.columbia.edu/themes/tibetan/ccnmtl_images/portfolio_image.jpg': '/media/img/thumbs/digitaltibet.png',
        '/site_media/img/flickr_logo.png': '/media/img/thumbs/flickr.png',
        'http://www.hathitrust.org/sites/www.hathitrust.org/themes/hathitrust_zen/images/hathi/HathiTrust.gif': '/media/img/thumbs/hathitrust.png',
        'http://cdn.loc.gov/images/img-head/logo-loc.png': '/media/img/thumbs/libraryofcongress.png',
        'http://www.college.columbia.edu/core/sites/core/themes/core/images/header.gif': '/media/img/thumbs/literaturehumanities.png',
        'https://encrypted-tbn2.google.com/images?q=tbn:ANd9GcQ8DZNNxSIIIkb7msQI_Nu3nYMOaLi4toRab1jaIFkF1iCW2HYw7w': '/media/img/thumbs/naxos.png',
        'http://www.columbia.edu/cu/lweb/img/assets/10015/digcoll_nyre.gif': '/media/img/thumbs/realestatebrochures.png',
        'http://2.bp.blogspot.com/_4HiFPL4xVfo/SERAy4HkdsI/AAAAAAAABm8/ZksKXNP_Onc/s200/nypl-logo-01.png': '/media/img/thumbs/nypl.png',
        'https://encrypted-tbn2.google.com/images?q=tbn:ANd9GcQhNbvfYflf8db58I5Np8XnjhJ2OFtTp-cm7QKLSkibQVeVhYp6': '/media/img/thumbs/openuniversity.png',
        'http://passets-cdn.pinterest.com/images/LogoRed.png': '/media/img/thumbs/pinterest.png',
        'https://causes-prod.s3.amazonaws.com/photos/bf/Ez/W4/Br/tN/GQ/0o/vzH.jpg': '/media/img/thumbs/projectrebirth.png',
        'http://web.mit.edu/shakspere/sia/wmv_images/wmv_images_sm/mac_tian.jpg': '/media/img/thumbs/shakespeareasia.png',
        'http://genizah.bodleian.ox.ac.uk/images/BODLEIAN-LIBRARIES-logo-without-strapline.png': '/media/img/thumbs/cairogenizah.png',
        'http://www.metmuseum.org/content/img/presentation/icons/header-logo-icon.gif': '/media/img/thumbs/met.png',
        'http://thlib.org/places/monasteries/meru-nyingpa/murals/preview/mnmural01.jpg': '/media/img/thumbs/tibetanlibrary.png',
        'http://www.columbia.edu/~mlp55/visuals/vanderbilttv.jpg': '/media/img/thumbs/televisionarchive.png',
        '/site_media/img/vimeo_logo.png': '/media/img/thumbs/vimeo.png',
        'http://www.wgbh.org/images/defaultMediumPlayer_WGBH.jpg': '/media/img/thumbs/openvault.png',
        'http://www.blakearchive.org/blake/public/urizen.G.P5.detail.jpg': '/media/img/thumbs/williamblake.png',
        '/site_media/img/youtube_logo.jpg': '/media/img/thumbs/youtube.png',
        'http://mediathread.ccnmtl.columbia.edu/site_media/img/youtube_logo.jpg': '/media/img/thumbs/youtube.png',
        'http://ccnmtl.columbia.edu/images/portfolio/thumbs/287.jpg': '/media/img/thumbs/southsidechicago.png',
        'http://classpop.ccnmtl.columbia.edu/sites/default/themes/mythemes/acq_classpop/images/logo_classpop.png': '/media/img/thumbs/classpop.png',
        'http://techtv.mit.edu/images/logo.jpg': '/media/img/thumbs/mittechtv.png'
    }

    def forwards(self, orm):
        sources = SupportedSource.objects.all()
        for s in sources:
            if s.thumb_url in self.url_map:
                s.thumb_url = self.url_map[s.thumb_url]
                s.save()

        archives = Asset.objects.archives()
        for a in archives:
            try:
                thumb = Source.objects.get(asset=a, label='thumb')
                if thumb.url in self.url_map:
                    thumb.url = self.url_map[thumb.url]
                    thumb.save()
            except Source.DoesNotExist:
                pass # this is ok, ignore

    def backwards(self, orm):
        "Write your backwards methods here."


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'main.usersetting': {
            'Meta': {'object_name': 'UserSetting'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['main']
