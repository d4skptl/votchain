# Votchain

This program is a proof-of-concept and still in development, not all features has been yet implemented.

## Introduction

This program simplifies the komodo asset chain creation following the **Vocdoni** principles and design.

Written in *python* it's a wrapper for the komodo daemon and komodo client, unified in a uniq script.

## Usage

#### Get komodo daemon

First of all the komodo daemon must exist in the filesystem, you can either download it from a komodo official source or use the one compiled by Vocdoni.
It is recommended to use the Vocdoni one since it has been tested and has enabled all required features.

`wget https://raw.githubusercontent.com/vocdoni/komodo/master/komodod`

You must place the komodod file to the votchain directory or rather specify the binary location when executing *miner.py* using *-m* parameter.

Check https://github.com/vocdoni/komodo/blob/master/README.md for more information regarding the komodo daemon.

#### Generate keys

Fist of all lets generate the keys.

`python3 miner.py -k > mykey`

This file can be used several times, also on several votingchains.

#### Launch miners

At least two miners are required (more are recommended). So let's assume first miner with IP1 and a second miner with IP2.

On both machines the same command must be launched (only IPs are different).

**Miner 1**
`python3 miner.py -n test -g -a -i mykey -p IP2`

**Miner 2**
`python3 miner.py -n test -g -a -i mykey -p IP1`

The name *test* identifies to voting chain. Listen ports are calculated from name, so it's no need to specify any specific port and several chains can be executed in paralel.

Listen port must be open (no firewall or NAT blocking). By default the listen connection port will be random between 20000 and 29999.

At this point, the voting chain should be working, then a user can connect to the blockchain (avoiding mine). In this case no listening ports are required since the TCP connection is one-way and opened by the user.

**Voter user**
`python3 miner.py -n test -a -i mykey -p IP1,IP2`


## Help

```
usage: miner.py [-h] [-n NAME] [-m BINARY] [-b BLOCKS] [-s SUPPLY] [-a]
                [-i KEYSFILE] [-p PEERS] [-d] [-g] [-k]

VotChain Miner

optional arguments:
  -h, --help   show this help message and exit
  -n NAME      Name for the voting chain
  -m BINARY    Location for the komodo daemon (komodod) binary
  -b BLOCKS    Number of blocks before die
  -s SUPPLY    Total token supply
  -a           Use proof of stake, only miners with supply generate blocks
  -i KEYSFILE  File containing keys to be used (generated with -k)
  -p PEERS     Coma separated list of peers to connect with
  -d           Show debug messages
  -g           Generate blocks (mine)
  -k           Generate new keys and exit
```
