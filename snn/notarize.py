#!/usr/bin/env python
import logging
from pprint import pprint
try:
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import HTTPError
from argparse import ArgumentParser, FileType
import sys
import os
import json

from util import ErgoNodeApi, setup_logging, get_digest


def parse_cli():
    """
    base useage: `notarize.py filename --api-key 7yaASMijGEGTbttYHg1MrXnWB8EbzjJnFLSWvmNoHrXV`
    server (опциональный, по умолчанию значение 127.0.0.1:9053)
    и duration (опциональный, если нет, значение по умолчанию равно 4)
    """
    parser = ArgumentParser()
    # parser.add_argument('filename')
    parser.add_argument('filename', type=FileType('rb'), help='file name')
    parser.add_argument(
        '-s', '--server',
        help='Address of RPC server in format SERVER:PORT'
    )
    parser.add_argument(
        '-n', '--network-log', action='store_true', default=False,
        help='Show network logs'
    )
    parser.add_argument(
        '-q', '--quiet', action='store_true', default=False,
        help='Do not show debug output'
    )
    parser.add_argument(
        '--api-key',
        help='API key to pass RPC node authentication',
    )
    parser.add_argument(
        '--duration',
        type=int, default=4,
        help='I need help'
    )
    opts = parser.parse_args()

    return opts


def main():
    opts = parse_cli()
    setup_logging(opts.quiet, opts.network_log)
    api = ErgoNodeApi(opts.server)

    # скрипт считает SHA-256 хэш файла, и преобразует его в Base16-строку.
    # На Linux-платформах результат можно сверить с выходом sha256sum, он должен совпадать
    file_hash = get_digest(opts.filename)
    logging.debug('sha256 file %s: %s' % (opts.filename, file_hash))

    json_data = {
        "requests": [{
            "address": "4MQyMKvMbnCJG3aJ",
            "value": 1000000,
            "registers": {
                "R4": "0e03%s" % file_hash
            }
        }],
        "fee": 1000000,
        "inputsRaw": []
    }
    json_dump = json.dumps(json_data)

    # POST to /wallet/transaction/generate
    try:
        url_ = '/wallet/transaction/generate'
        logging.debug('Sending to %s' % url_)
        tx_json = api.request(url_, data=json_dump, api_key=opts.api_key)
    except HTTPError as ex:
        logging.error(
            '[RPC ERROR] method=%s, http-status=%d\n%s' % (
                url_, ex.code, ex.read().decode()
            )
        )
        sys.exit(1)
    else:
        logging.debug(tx_json)

    # If no errors POST to /transactions
    try:
        url_ = '/transactions'
        logging.debug('Send transaction to %s' % url_)
        res = api.request(url_, data=tx_json, api_key=opts.api_key)
    except expression as identifier:
        logging.error('[RPC ERROR] method=%s, http-status=%d\n%s' % (
            url_, ex.code, ex.read().decode()
        ))
    else:
        logging.debug(res)


if __name__ == '__main__':
    main()
