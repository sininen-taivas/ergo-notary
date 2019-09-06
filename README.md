# Ergo Natary
## Installation
Just install python of 3rd version.

## Notarize Script
### Usage
```bash
python3 notarize.py filename --api-key API_KEY
```

### Command Line Options
- `-h`, `--help`- show this help message and exit
- `-s SERVER`, `--server SERVER` - Address of RPC server in format SERVER:PORT
- `-q`, `--quiet` - Do not show debug output
- `--api-key API_KEY` - API key to pass RPC node authentication
- `--duration DURATION` - Time period to store data on the blockchain (in years)
- `--mainnet` - Using main net, default server localhost:9053
- `--testnet` - Using test net, default server localhost:9052

### How it works
- receives `filename`, `api-key` as required params
- calculate SHA-256 file hash then convert to Base16-string.
  - on Linux could compare with sha256sum out must be equal
- generate arbitrary transactions
- send an Ergo transaction
- save result into `{filename}.nt.json` 

## Check Script
### Usage
```bash
python3 check.py testfile.txt.nt.json --testnet
```

### Command Line Options
- `-h`, `--help` - show this help message and exit
- `-s SERVER`, `--server SERVER` Address of RPC server in format SERVER:PORT
- `-q`, `--quiet` - Do not show debug output
- `--api-key API_KEY` - API key to pass RPC node authentication
- `--mainnet` - Using main net, default server localhost:9053
- `--testnet` - Using test net, default server localhost:9052

### How it works
- receives `{filename}.nt.json`, `api-key` as required params
- script get `boxId` and sending request to `/utxo/boxById/$boxId`
- if result status 404 then delete field `confirmed` from file
- if result status OK and `confirmed` not in file then field `confirmed=timestamp` add into file 
