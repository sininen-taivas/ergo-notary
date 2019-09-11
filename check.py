#!/usr/bin/env python3
import json
import logging
from argparse import ArgumentParser, FileType
from time import time

from utils.util import TARGET_SERVER, ErgoClient, setup_logger


def parse_cli():
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
        required=True,
        help='API key to pass RPC node authentication',
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

    tx_data = json.loads(opts.filename.read())
    logging.debug(f'Read file {opts.filename.name} {tx_data}')

    box_id = tx_data.get('boxId')
    code, res = api.request(f'/utxo/byId/{box_id}')
    logging.debug(f'Box: {res}')
    if code == 404:
        tx_data.pop('confirmed', None)
    elif 'confirmed' not in tx_data:
        tx_data.update(confirmed=int(time()))
    tx_data.update(updated=int(time()))
    logging.debug(f'Result json {tx_data}')

    out_filename = f'{opts.filename.name}'

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
