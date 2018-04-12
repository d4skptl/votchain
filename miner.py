#!/usr/bin/env python3

import random, hashlib
import sys, os, time, argparse
from votchain import Votchain, VotchainCli, AddressGenerator

def parse_args():
    parser = argparse.ArgumentParser(description='VotChain Miner')
    parser.add_argument(
            '-n',
            dest='name',
            type=str,
            default=None,
            help='Name for the voting chain')
    parser.add_argument(
            '-m',
            dest='binary',
            type=str,
            default='./komodod',
            help='Location for the komodo daemon (komodod) binary')
    parser.add_argument(
            '-b',
            dest='blocks',
            type=int,
            default=100,
            help='Number of blocks before die')
    parser.add_argument(
            '-s',
            dest='supply',
            type=int,
            default=1000,
            help='Total token supply')
    parser.add_argument(
            '-a',
            dest='staking',
            action="store_true",
            help='Use proof of stake, only miners with supply generate blocks')
    parser.add_argument(
            '-i',
            dest='keysfile',
            type=str,
            default=None,
            help='File containing keys to be used (generated with -k)')
    parser.add_argument(
            '-p',
            dest='peers',
            type=str,
            default=None,
            help='Coma separated list of peers to connect with')
    parser.add_argument(
            '-d',
            dest='debug',
            action="store_true",
            help='Show debug messages')
    parser.add_argument(
            '-g',
            dest='gen',
            action="store_true",
            help='Generate blocks (mine)')
    parser.add_argument(
            '-k',
            dest='gen_keys',
            action="store_true",
            help='Generate new keys and exit')
    return parser.parse_args()

# address generator
def gen_keys():
    ag = AddressGenerator()
    keys = ag.get()
    ag.close()
    return keys

# ports are calculated from votchain name
def get_ports(name):
    m = hashlib.md5()
    m.update(name.encode('utf-8'))
    base_port = int('0x'+m.hexdigest(),16)%10000
    return base_port+20000, base_port+30000

args = parse_args()
pubkey = None
privkey = None
address = None

if args.gen_keys:
    print(gen_keys())
    sys.exit(0)

if not args.name:
    print("Please, specify a name for the chain")
    sys.exit(1)

if args.keysfile:
    with open(args.keysfile, 'r') as kf:
        raw_keys = kf.read()
    keys = eval(raw_keys)
    privkey = keys['private_key']
    pubkey = keys['public_key']
    address = keys['address']

port,rpc_port = get_ports(args.name)
if args.peers: 
    peers = args.peers.split(",")
    peers[:] = map(lambda p: p+":%d"%port, peers)
else: peers = []

v = Votchain(name=args.name, binary=args.binary, peers=peers, port=str(port),
        rpc_port=str(rpc_port), mine=args.gen, supply=args.supply,
        pubkey=pubkey, staking=args.staking)
v.debug = args.debug

print("Starting votchain [%s]" %args.name)
print(" Blocks\t%d\n Port\t%d\n RPC\t%d\n Peers\t%s\n"
        %(args.blocks,port,rpc_port,peers))
v.start()

cli = VotchainCli(rpc_port)

print("Waiting RPC to be ready")
while not cli.is_ready():
    time.sleep(1)
print("RPC ready!")

if privkey: cli.import_key(privkey)

while True:
    time.sleep(10)
    blocks = int(cli.get_blocks())
    print("[%d] blocks:%s connections:%s balance:%s difficulty:%s" 
            %(int(time.time()), blocks, cli.get_connections(),
            cli.get_balance(), cli.get_diff()))
    if blocks > args.blocks: break

print("Terminating")
v.stop()
