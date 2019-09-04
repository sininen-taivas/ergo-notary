#!/usr/bin/python3

import logging
import logging.handlers
import os
from urllib.request import urlopen, Request
from urllib.parse import urljoin
import urllib
import json
import argparse
import hashlib

if False:  # for type check
    import http.client
    import _hashlib

LOG_FORMAT = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')
DEFAULT_ERGO_SERVER = 'localhost:9053'  # localhost:9053

_MY_DIR = os.path.dirname(os.path.abspath(__file__))


# log_file = os.path.join(_MY_DIR, 'log', 'notarize.log')

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

    def log(self, message, level=logging.INFO):
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
        except urllib.error.HTTPError as eres:
            self.log(json.loads(eres.read()), level=logging.ERROR)
            exit(1)


def parce_args():  # type: () -> Namespace
    a_parcer = argparse.ArgumentParser()
    a_parcer.add_argument('filename', type=argparse.FileType('rb'), help='file name')
    a_parcer.add_argument('--api-key', type=str, help='Ergo API auth key')
    return a_parcer.parse_args()


def get_digest(fo):
    sha256 = hashlib.sha256()  # type: _hashlib.HASH
    for buf in iter(lambda: fo.read(4096), b''):
        sha256.update(buf)
    return sha256.hexdigest()


def test1():
    setup_logger()
    logging.debug('test1')
    ergo = ErgoClient('localhost:9052')
    code, info = ergo.request('/info')
    logging.debug('Return code: %i' % code)
    logging.debug('info: %s' % info)


def main():
    setup_logger()
    args = parce_args()
    ergo = ErgoClient('localhost:9052', api_key=args.api_key)
    digest = get_digest(args.filename)
    logging.info('sha256 hash: %s' % digest)
    code, trns = ergo.request('/wallet/transaction/generate', {
        'requests': [{
            'address': '4MQyMKvMbnCJG3aJ',
            'value': 1000000,
            'registers': {
                'R4': '0e03%s' % digest
            }
        }],
        'fee': 1000000,
        'inputsRaw': []
    })
    logging.debug('Return code: %i' % code)
    logging.debug('info: %s' % trns)


if __name__ == '__main__':
    main()
    # test1()
