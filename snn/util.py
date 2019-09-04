from pprint import pprint
import json
import logging
import sys
try:
    from urllib.parse import urljoin
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import Request, urlopen
    from urlparse import urljoin
import hashlib

DEFAULT_RPC_SERVER = 'localhost:9053'
network_logger = logging.getLogger('network')


def setup_logging(quiet, show_network_log):
    # Setup logging
    if quiet:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.DEBUG)
    for hdl in logging.getLogger().handlers:
        hdl.setFormatter(logging.Formatter('%(message)s'))
    if not quiet and show_network_log:
        network_logger.setLevel(logging.DEBUG)
    else:
        network_logger.setLevel(logging.INFO)


class ErgoNodeApi(object):
    def __init__(self, server=None):
        self.server = (
            server if server else DEFAULT_RPC_SERVER
        )

    def request(self, path, data=None, api_key=None):
        if sys.version_info[0] == 2 and isinstance(data, unicode):
            data = data.encode()
        if sys.version_info[0] == 3 and isinstance(data, str):
            data = data.encode()
        #if sys.version_info[0] == 2 and isinstance(api_key, unicode):
        #    api_key = api_key.encode()
        #if sys.version_info[0] == 3 and isinstance(api_key, str):
        #    api_key = api_key.encode()
        url = urljoin('http://%s' % self.server, path)
        network_logger.debug('GET %s', url)
        headers = {
            'Accept': 'application/json',
        }
        if data:
            headers['Content-Type'] = 'application/json'
        if api_key:
            headers['api_key'] = api_key
        req = Request(url=url, headers=headers, data=data)
        res = urlopen(req)
        res_data = res.read().decode('utf-8')
        res_data_json = json.loads(res_data)
        return res_data_json


def get_digest(fo):
    sha256 = hashlib.sha256()  # type: _hashlib.HASH
    for buf in iter(lambda: fo.read(4096), b''):
        sha256.update(buf)
    return sha256.hexdigest()
