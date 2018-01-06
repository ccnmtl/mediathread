import hashlib

from django.conf import settings
from zeep import Client
from zeep.exceptions import Fault
from zeep.helpers import serialize_object


class PanoptoApi(object):
    def __init__(self):
        self.api = {
            'sessions': self._api('SessionManagement')
        }

    @classmethod
    def _api(cls, name):
        url = 'https://{}/Panopto/PublicAPI/4.6/{}.svc?wsdl'.format(
            settings.PANOPTO_SERVER, name)
        return Client(url)

    def _user_key(self, username):
        return '%s\\%s' % (settings.PANOPTO_API_APP_ID, username)

    def _auth_code(self, user_key):
        payload = user_key + '@' + settings.PANOPTO_SERVER
        signed_payload = payload + '|' + settings.PANOPTO_API_TOKEN
        return hashlib.sha1(signed_payload).hexdigest().upper()

    def _auth_info(self, username):
        user_key = self._user_key(username)
        return {
            'AuthCode': self._auth_code(user_key),
            'UserKey': user_key
        }

    def get_session_url(self, username, session_id):
        try:
            response = self.api['sessions'].service.GetSessionsById(
                auth=self._auth_info(username), sessionIds=[session_id])

            if response is None or len(response) < 1:
                return ''

            obj = serialize_object(response)
            return obj[0]['MP4Url']
        except Fault:
            return ''
