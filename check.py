#!/usr/bin/env python3
import logging
from pprint import pprint
from argparse import ArgumentParser, FileType
import json
from datetime import datetime

from util import DEFAULT_RPC_SERVER, ErgoClient, setup_logger, get_digest


def parse_cli():
    parser = ArgumentParser()
    # parser.add_argument('filename')
    parser.add_argument('filename', type=FileType('rb'), help='file name')
    parser.add_argument(
        '-s', '--server',
        default=DEFAULT_RPC_SERVER,
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

    opts = parser.parse_args()
    return opts

def main():
    opts = parse_cli()
    setup_logger(not opts.quiet)
    api = ErgoClient(opts.server, opts.api_key)

    tx_data = json.loads(opts.filename.read())
    logging.debug(f'Read file {opts.filename.name} {tx_data}')

    box_id = tx_data.get('boxId')
    code, res = api.request(f'/utxo/byId/{box_id}')
    logging.debug(f'Box: {res}')
    if code == 404:
        tx_data.pop('confirmed', None)
    elif 'confirmed' not in tx_data:
        tx_data.update(confirmed=datetime.now().timestamp())
    tx_data.update(updated=datetime.now().timestamp())
    logging.debug(f'Result json {tx_data}')

    out_filename = f'{opts.filename.name}'
    with open(out_filename, 'w+') as fw:
        logging.debug(f'Write to file {out_filename}')
        fw.write(json.dumps(tx_data))

    logging.debug('OK')


if __name__ == '__main__':
    main()
