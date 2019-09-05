from pprint import pprint
import json
import logging
import sys
from urllib.parse import urljoin
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import hashlib

LOG_FORMAT = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
DEFAULT_RPC_SERVER = 'localhost:9053'


def setup_logger(stdout=True, file_name=None):  # type: () -> logging.Logger
    _logger = logging.getLogger()
    _logger.setLevel(logging.DEBUG)
    if file_name is not None:
        _handler = logging.handlers.RotatingFileHandler(file_name, maxBytes=1024 * 1024, backupCount=3)
        _handler.setFormatter(LOG_FORMAT)
        _logger.addHandler(_handler)
    if stdout:
        _console = logging.StreamHandler()
        _console.setLevel(logging.DEBUG)
        _console.setFormatter(LOG_FORMAT)
        logging.getLogger('').addHandler(_console)
    return _logger



class ErgoClient:
    def __init__(self, server, api_key=None):
        self.server, self.api_key = server, api_key
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        if api_key is not None:
            self.headers['api_key'] = api_key

    def log(self, message, level=logging.DEBUG):
        logging.log(level, 'ErgoClient:%s' % message)

    def request(self, path, data=None):  # type: (str) -> (int, dict)
        url = urljoin('http://%s' % self.server, path)
        self.log('request %s' % url)
        if not isinstance(data, bytes):
            data = bytes(json.dumps(data), encoding='utf-8')
        req = Request(url=url, headers=self.headers, data=data)
        try:
            res = urlopen(req)  # type: http.client.HTTPResponse
            return res.code, json.loads(res.read())
        except (ConnectionResetError, TimeoutError) as e:
            self.log('Ergo API server not responding (%s)' % str(e), level=logging.ERROR)
            exit(1)
        except HTTPError as eres:
            self.log(json.loads(eres.read()), level=logging.ERROR)
            exit(1)


def get_digest(fo):
    sha256 = hashlib.sha256()  # type: _hashlib.HASH
    for buf in iter(lambda: fo.read(4096), b''):
        sha256.update(buf)
    return sha256.hexdigest()
