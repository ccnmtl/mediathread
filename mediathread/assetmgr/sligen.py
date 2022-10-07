from django.conf import settings
from django.core.cache import cache
import hashlib
import requests
from panopto.session import PanoptoSessionManager
import time


def sligen_streaming_processor(url, label=None, request=None):  # noqa: C901
    # JUST flv_pseudo, video_pseudo, and NOT 'video' or 'flv'
    # because the javascript won't activate streaming unless there's _pseudo
    if label == 'image_fpxid':
        # ARTStor
        fpx_id = url
        fpx_url = cache.get(fpx_id)
        if fpx_url is not None:
            return fpx_url

        # ARTStor is still using SHA-1 certs, which requests does not like
        # Turn off verification until they get their act together
        try:
            session = requests.Session()
            artstor_login_url = getattr(settings, 'ARTSTOR_LOGIN_URL', None)
            artstor_credentials = getattr(
                settings, 'ARTSTOR_CREDENTIALS', None)
            response = session.post(
                artstor_login_url, data=artstor_credentials, verify=False)
            response.raise_for_status()

            # retrieve & cache a new image url via artstor's json api
            base_url = 'https://library.artstor.org/api/secure/imagefpx'
            url = '%s/%s/103/5' % (base_url, fpx_id)

            response = session.get(url, verify=False)
            response.raise_for_status()

            data = response.json()[0]
            fpx_url = '%s%s' % (data['imageServer'], data['imageUrl'])
            cache.set(fpx_id, fpx_url, 3600)
        except (requests.exceptions.HTTPError, ValueError):
            fpx_url = url

        return fpx_url
    elif label == 'mp4_panopto':
        panopto_id = url
        panopto_url = cache.get(panopto_id)
        if panopto_url:
            return panopto_url

        session_mgr = PanoptoSessionManager(
            getattr(settings, 'PANOPTO_SERVER', None),
            getattr(settings, 'PANOPTO_API_USER', None),
            instance_name=getattr(settings, 'PANOPTO_INSTANCE_NAME', None),
            password=getattr(settings, 'PANOPTO_API_PASSWORD', None),
            cache_dir=getattr(settings, 'ZEEP_CACHE_DIR', None))
        panopto_url = session_mgr.get_session_url(url)

        if panopto_url:
            # cache forever
            cache.set(panopto_id, panopto_url, timeout=None)

        return panopto_url
    elif url.startswith('https://cdn.jwplayer.com/'):
        jw_url = cache.get(url)
        if jw_url is not None:
            return jw_url

        response = requests.get(url)
        data = response.json()
        manifest_url = data['playlist'][0]['sources'][0]['file']
        response = requests.get(manifest_url)
        lines = response.content.decode('utf-8').split('\n')
        jw_url = lines[2]
        cache.set(url, jw_url, 10800)
        return jw_url

    ccnmtlstream_testprefix = getattr(
        settings, 'CCNMTLSTREAM_TESTPREFIX', None)
    if ccnmtlstream_testprefix and url.startswith(ccnmtlstream_testprefix):
        url_slashed = url.split('?')[0].split('/')
        filename = '/%s' % url_slashed[5]
        secret = getattr(settings, 'CCNMTLSTREAM_SECRET', None)
        prefix = getattr(settings, 'CCNMTLSTREAM_PREFIX', None)
        t_hex = '%08x' % round(time.time())
        m = hashlib.md5(
            (secret + filename + t_hex).encode('utf-8')).hexdigest()
        return '%s/%s/%s/%s' % (prefix, m, t_hex, filename)

    flvstream_prefix = getattr(settings, 'FLVSTREAM_PREFIX', None)
    if flvstream_prefix and (
            label in ('flv_pseudo', 'video_pseudo') and
            url.startswith(flvstream_prefix)):
        # remove any query string, because that's not part of the file
        url_slashed = url.split('?')[0].split('/')
        filename = '/'.join(url_slashed[7:])
        dechex = hex(int(round(time.time(), -3)))[2:]
        address = getattr(settings, 'FLVSTREAM_ADDRESS', None)
        SECRET = getattr(settings, 'FLVSTREAM_SECRET', None)

        address = request.META.get('HTTP_X_FORWARDED_FOR',
                                   request.META['REMOTE_ADDR'])

        url_slashed[5] = hashlib.sha1(
            '{}{}{}{}'.format(
                filename, dechex, address, SECRET).encode('utf-8')
        ).hexdigest()
        return '%s?pos=${start}' % '/'.join(url_slashed)

    return url
