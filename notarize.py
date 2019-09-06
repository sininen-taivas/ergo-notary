#!/usr/bin/env python3
import json
import logging
from argparse import ArgumentParser, FileType, ArgumentTypeError
from time import time

from util import TARGET_ADDRESS, TARGET_SERVER, ErgoClient, setup_logger, get_digest


def valid_duration(d):
    try:
        val = int(d)
        if val % 4 != 0:
            raise ValueError
        return val
    except ValueError:
        raise ArgumentTypeError(f'Not a valid duration: {d}')


def parse_cli():
    parser = ArgumentParser()
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
        required=True,
        help='API key to pass RPC node authentication',
    )
    parser.add_argument(
        '--duration',
        type=valid_duration, default=4,
        help='Time period to store data on the blockchain (in years)'
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--mainnet', action='store_true',
                       help='Using main net, default server localhost:9053')
    group.add_argument('--testnet', action='store_true',
                       help='Using test net, default server localhost:9052')

    opts = parser.parse_args()
    return opts


def main():
    opts = parse_cli()
    setup_logger(not opts.quiet)

    target_ = 'mainnet'
    if opts.testnet:
        target_ = 'testnet'

    server_ = opts.server or TARGET_SERVER[target_]
    api = ErgoClient(server_, opts.api_key)

    # Script calculate SHA-256 file hash then convert to Base16-string.
    # On Linux could compare with sha256sum out must be equal
    file_hash = get_digest(opts.filename)
    logging.debug('sha256 file %s: %s' % (opts.filename, file_hash))

    r4 = f'0e20{file_hash}'

    json_data = {
        "requests": [{
            "address": TARGET_ADDRESS[target_],
            "value": opts.duration / 4 * 1000000,
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
    # logging.debug(tx_json)

    if code != 200:
        logging.error(tx_json)
        exit(1)

    logging.debug(tx_json)

    # check outputs
    if not tx_json.get('outputs'):
        logging.error(f'Error response from {url_}')
        exit(1)

    # If no errors POST to /transactions
    url_ = '/transactions'
    logging.debug('Send transaction to %s' % url_)
    code, txid = api.request(url_, data=tx_json)
    if code != 200:
        logging.error(txid)
        exit(1)

    logging.debug(f'txId: {txid}')

    tx_data = {}
    for box in tx_json.get('outputs', {}):
        if 'R4' in box.get('additionalRegisters', {}) and box['additionalRegisters']['R4'] == r4:
            tx_data.update(
                boxId=box['boxId'], transactionId=txid, updated=int(time()))
            break

    if not tx_data:
        logging.error('Not found needed box')
        exit(1)

    out_filename = f'{opts.filename.name}.nt.json'

    try:
        with open(out_filename, 'w+') as fw:
            logging.debug(f'Write to file {out_filename}')
            fw.write(json.dumps(tx_data))
    except IOError as er:
        logging.debug(f'Write file error: {er}')
        exit(1)

    logging.debug('OK')


if __name__ == '__main__':
    main()
