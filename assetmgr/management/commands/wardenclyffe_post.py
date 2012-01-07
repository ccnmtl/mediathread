from restclient import POST

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):

    def handle(self, *app_labels, **options):
        mediathread_base = "http://localhost:8000" 
        
        params = {
          'set_course' : 'tlc.cunix.local:columbia.edu',
          'as' : 'sld2131',
          'secret' : 'mediathread_secret',
          'title' : "A Test Video",
          "metadata-wardenclyffe-id" : str(4321),
          "metadata-tag": "upload",
          'mp4': "http://h.i.j/kl",
          "mp4-metadata": "200%200%200",
          "thumb": "http://ccnmtl.columbia.edu/broadcast/posters/vidthumb_480x360.jpg"
        }
        
        resp,content = POST(mediathread_base + "/save/", params=params,async=False,resp=True)
