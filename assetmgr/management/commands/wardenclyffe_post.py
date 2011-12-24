from restclient import POST

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):

    def handle(self, *app_labels, **options):
        mediathread_base = "http://localhost:8000" 
        
        params = {
          'set_course' : 'tlc.cunix.local:columbia.edu',
          'as' : 'sld2131',
          'secret' : 'mediathread_secret',
          'title' : "foo",
          "metadata-wardenclyffe-id" : str(4321),
          "metadata-tag": "upload",
          'mp4': "http://e.f.g/id",
          "mp4-metadata": "200%200%200"
        }
        
        resp,content = POST(mediathread_base + "/save/", params=params,async=False,resp=True)
