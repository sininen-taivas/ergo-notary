#!/usr/bin/env python3
import logging
from pprint import pprint
from urllib.error import HTTPError
from argparse import ArgumentParser, FileType
import sys
import os
import json
from datetime import datetime

from util import DEFAULT_RPC_SERVER, ErgoClient, setup_logger, get_digest

TARGET_ADDRESS = {
    'mainnet': '4MQyMKvMbnCJG3aJ',
    'testnet': 'Ms7smJmdbakqfwNo',
}


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
    # mainnet = 4MQyMKvMbnCJG3aJ
    # testnet = Ms7smJmdbakqfwNo
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--mainnet', action='store_true', help='Using main net')
    group.add_argument('--testnet', action='store_false',
                       help='Using test net')

    opts = parser.parse_args()
    return opts


def main():
    opts = parse_cli()
    setup_logger(not opts.quiet)
    api = ErgoClient(opts.server, opts.api_key)

    # скрипт считает SHA-256 хэш файла, и преобразует его в Base16-строку.
    # На Linux-платформах результат можно сверить с выходом sha256sum, он должен совпадать
    file_hash = get_digest(opts.filename)
    logging.debug('sha256 file %s: %s' % (opts.filename, file_hash))

    r4 = f'0e20{file_hash}'

    json_data = {
        "requests": [{
            "address": TARGET_ADDRESS['mainnet'] if opts.mainnet else TARGET_ADDRESS['testnet'],
            "value": 1000000,
            "assets": [],
            "registers": {
                "R4": r4
            }
        }],
        "fee": 1000000,
        "inputsRaw": []
    }
    # POST to /wallet/transaction/generate
    url_ = '/wallet/transaction/generate'
    logging.debug('Sending to %s, %s' % (url_, json_data))
    code, tx_json = api.request(url_, data=json_data)
    logging.debug(tx_json)

    # check outputs
    if not tx_json.get('outputs'):
        logging.error(f'Error response from {url_}')
        exit(1)

    # If no errors POST to /transactions
    url_ = '/transactions'
    logging.debug('Send transaction to %s' % url_)
    code, txid = api.request(url_, data=tx_json)
    logging.debug(f'txId: {txid}')

    tx_data = {}
    for box in tx_json.get('outputs', {}):
        if 'R4' in box.get('additionalRegisters', {}) and box['additionalRegisters']['R4'] == r4:
            tx_data.update(boxId=box['boxId'], transactionId=txid, updated=datetime.now().timestamp())
            break

    if not tx_data:
        logging.error('Not found needed box')
        exit(1)

    out_filename = f'{opts.filename.name}.nt.json'
    with open(out_filename, 'w+') as fw:
        logging.debug(f'Write to file {out_filename}')
        fw.write(json.dumps(tx_data))

    logging.debug('OK')

if __name__ == '__main__':
    main()
