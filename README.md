# Votchain

This program is a proof-of-concept and still in development, not all features have been yet implemented.

## Introduction

This program simplifies the komodo asset chain creation following the **Vocdoni** principles and design.

Written in *python* it's a wrapper for the komodo daemon and komodo client.

A voting chain (**votchain**) is a temporary blockchain including mainly the following characteristics:

- Anonymous by using z-snarks, tokens might be sent from/to a transparent address *t* or from/to a anonymous address *z*
- Limited amount of life time specified by numer of blocks (during the election process)
- All supply is controlled by a trusted party, no mining reward. Thus only those identified users will receive vote tokens
- Mining is protected by a Proof-of-Stake that performs similar to a Proof-of-Authority (only nodes with tokens are able to generate new blocks)

## Usage

#### Get komodo daemon

First of all the komodo daemon must exist in the filesystem, you can either download it from a komodo official source or use the one compiled by Vocdoni.
It is recommended to use the Vocdoni one since it has been tested and has  all required features enabled.

`wget https://raw.githubusercontent.com/vocdoni/komodo/master/komodod.gz -O- | gunzip -c > komodod`

You must place the komodod file to the votchain directory or rather specify the binary location when executing *vcd* using *-m* parameter. Also the komodod should be converted to executable.

`chmod a+x komodod`

Check https://github.com/vocdoni/komodo/blob/master/README.md for more information regarding the komodo daemon.

#### Download ZkSnark params

Download zkSNARK parameters using Komodo's official script

`wget https://raw.githubusercontent.com/KomodoPlatform/komodo/master/zcutil/fetch-params.sh -O- | bash`

#### Generate keys

Fist of all lets generate the keys.

`./vcd -k > mykey`

The keys file *mykey* can be used several times, also on different voting chains.

#### Launch miners

At least two miners are required (more are recommended). So let's assume first miner with IP1 and a second miner with IP2.

On both machines the same command must be launched (only IPs are different).

**Miner 1**
`./vcd -n test -g -a -i mykey -p IP2`

**Miner 2**
`./vcd -n test -g -a -i mykey -p IP1`

The name *test* identifies to voting chain. Listen ports are calculated from name, so it's no need to specify any specific port and several chains can be executed in paralel.

Listen port must be open (no firewall or NAT blocking). By default the listen connection port will be random between 20000 and 29999.

At this point, the voting chain should be working, then a user can connect to the blockchain (avoiding mine). In this case no listening ports are required since the TCP connection is one-way and opened by the user.

**Voter user**
`./vcd -n test -a -i mykey -p IP1,IP2`

#### Send tokens and vote

The client tool *vcc* can be used to check some wallet and network information and to send funds to another wallet.

`./vcc -n test -s destination_addr:amount`

## Help

```
usage: vcd [-h] [-n NAME] [-m BINARY] [-b BLOCKS] [-s SUPPLY] [-a]
                [-i KEYSFILE] [-p PEERS] [-d] [-g] [-k]

VotChain Miner

optional arguments:
  -h, --help   show this help message and exit
  -n NAME      Name for the voting chain
  -m BINARY    Location for the komodo daemon (komodod) binary
  -b BLOCKS    Number of blocks before die
  -s SUPPLY    Initial token supply (first mined block get it)
  -a           Enable proof of stake
  -r REWARD    Enable reward per block (in satoshis)
  -i KEYSFILE  File containing keys to be used (generated with -k)
  -p PEERS     Coma separated list of peers to connect with
  -d           Show debug messages
  -g           Generate blocks (mine)
  -k           Generate new keys and exit
```

```
usage: vcc [-h] [-n NAME] [-i KEYSFILE] [-b] [-w] [-tt SENDTO] [-tz TZ_SENDTO]
           [-zz ZZ_SENDTO] [--shield] [--showzops] [--fee SET_FEE]
           [-c RAWCALL]

VotChain Miner

optional arguments:
  -h, --help     show this help message and exit
  -n NAME        Name for the voting chain
  -i KEYSFILE    File containing keys to be used
  -b             Show current tokens balance
  -w             Show wallet info (address and public key)
  -tt SENDTO     Send tokens from T to T address. Syntax <addr>:<amount>
  -tz TZ_SENDTO  Send tokens from T address to Z. Syntax <addr>:<amount>
  -zz ZZ_SENDTO  Send tokens from Z address to T or Z. Syntax <addr>:<amount>
  --shield       Shield coinbase tokens to an own Z address
  --showzops     Show Z operations status
  --fee SET_FEE  Set fee for tx operation (float)
  -c RAWCALL     Make raw RPC calls to daemon like: -c "getblock 1"
```
