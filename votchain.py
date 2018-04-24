import subprocess, threading
import random, hashlib
import os, time, requests, json, shutil

class Votchain(object):
    '''Votchain generator. Starts a new Komodo asset chain for voting'''
    debug = False
    def __init__(self, binary="./komodod", name=None, supply=1000, port=1714,
            rpc_port=None, pubkey=None, peers=[], mine=True,
            basedir='/tmp', staking=False, reward=None, whitelistpeers=True):
        self.t = None
        self.proc = None
        self.rpc_port = rpc_port or str((int(100000*random.random())%60000)+5000)
        datadir = '%s/%s'%(basedir,name)
        self.args = [binary]
        self.args.append('-ac_name=' + str(name or int(1000000*random.random())))
        self.args.append('-ac_supply='+str(supply))
        if reward: self.args.append('-ac_reward='+str(reward))
        else: self.args.append('-ac_end=1') # no reward after first block
        if staking: self.args.append('-ac_staking=100')
        self.args.append('-port='+str(port))
        self.args.append('-rpcport='+self.rpc_port)
        self.args.append('-rpcbind=127.0.0.1')
        self.args.append('-rpcuser=vocdoni')
        self.args.append('-rpcpassword=vocdoni')
        self.args.append('-server')
        self.args.append('-listen')
        if pubkey: self.args.append('-pubkey='+pubkey)
        self.args.append('-datadir='+datadir)
        self.args.append('-txexpirydelta=100')
#       self.args.append('-keypool=16000')
        if mine:
            self.args.append('-gen')
            self.args.append('-genproclimit=-1')
        for p in peers: 
            self.args.append('-addnode='+p)
            self.args.append('-connect='+p)
            if whitelistpeers: self.args.append('-whitelist=%s'%(p.split(':')[0]))

        if not os.path.exists(datadir):
            os.makedirs(datadir)
            # write basic parameters to config file
            with open(datadir+"/%s.conf"%name,'w') as cf:
                cf.write("rpcuser=vocdoni\n")
                cf.write("rpcpassword=vocdoni\n")
                cf.write("rpcport=%s\n"%str(port))
                cf.write("txindex=1\n")
                cf.write("server=1\n")
                if mine: cf.write("gen=1\n")
                cf.write("rpcallowip=127.0.0.1\n")

    def output(self, proc):
        if self.debug:
            for line in iter(proc.stdout.readline, b''):
                print('got line: {0}'.format(line.decode('utf-8')), end='')

    def start(self):
        self.proc = subprocess.Popen(self.args,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        self.t = threading.Thread(target=self.output, args=(self.proc,))
        self.t.start()

    def stop(self):
        self.proc.terminate()
        try:
            self.proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self.proc.kill()
        self.t.join()

    def get_rpc(self):
        return self.rpc_port


class AddressGenerator(object):
    '''Starts a temporary komodo daemon and returns the wallet addresses generated'''

    def __init__(self, binary="./komodod", basedir='/tmp'):
        rpc_port = int(random.random()*1000)+17000 
        self.datadir = '%s/addrgen_%d'%(basedir,rpc_port)
        self.args = [binary]
        self.args.append('-rpcport='+str(rpc_port))
        self.args.append('-rpcbind=127.0.0.1')
        self.args.append('-rpcuser=vocdoni')
        self.args.append('-rpcpassword=vocdoni')
        self.args.append('-connect=127.0.0.1')
        self.args.append('-server')
        self.args.append('-datadir='+self.datadir)
        if not os.path.exists(self.datadir):
            os.makedirs(self.datadir)
        with open(self.datadir+'/komodo.conf','w') as c:
            c.write("")
        self.proc = subprocess.Popen(self.args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT)
        self.rpc = RPCHost('http://%s:%s@%s:%s'%('vocdoni','vocdoni','127.0.0.1',str(rpc_port)))

    def get(self):
        ready = False
        while not ready:
            time.sleep(1)
            try:
                self.rpc.call('help')
                ready = True
            except: pass

        addr = self.rpc.call('getaccountaddress','')
        priv_key = self.rpc.call('dumpprivkey', addr)
        pub_key = self.rpc.call('validateaddress', addr)['pubkey']
        return {"address":addr, "private_key": priv_key, "public_key": pub_key}

    def close(self):
        self.proc.kill()
        shutil.rmtree(self.datadir, ignore_errors=True)


class VotchainCli(object):
    '''Votchain client to communicate with komodo daemon via RPC'''
    def __init__(self, port, host='127.0.0.1', user='vocdoni', passw='vocdoni'):
        self.rpc = RPCHost('http://%s:%s@%s:%s'%(user,passw,host,str(port)))

    def call(self, rpcMethod, *params):
        try:
            out = self.rpc.call(rpcMethod, *params)
        except Exception:
            print("RPC not responding")
            out = False
        return out

    def is_ready(self):
        try:
            ready = True
            self.rpc.call('help')
        except:
            ready = False
        return ready

    def get_blocks(self):
        return self.call('getblockcount') or 0
        
    def get_diff(self):
        return self.call('getdifficulty')

    def get_balance(self):
        out = self.call('getinfo')
        if out: return out['balance']

    def get_connections(self):
        out = self.call('getinfo')
        if out: return out['connections']

    def get_addresses(self, account=""):
        return self.call("getaddressesbyaccount", account)
    
    def get_pubkey(self, addr=None):
        if not addr:
            addr = self.get_addresses()[0]
        return self.call("validateaddress", addr)['pubkey']

    def import_key(self, key):
        return self.call("importprivkey", key)

    def send(self, dst_addr, amount, account=""):
        return self.call("sendfrom",account, dst_addr, amount)


class RPCHost(object):
    '''Simple class to comunicate with bitcoin based RPC'''
    debug = False
    def __init__(self, url):
        self._session = requests.Session()
        self._url = url
        self._headers = {'content-type': 'application/json'}

    def call(self, rpcMethod, *params):
        payload = json.dumps({"method": rpcMethod, "params": list(params), "jsonrpc": "2.0"})
        if self.debug:
            print("CALL",self._url, payload)
        try:
            response = self._session.post(self._url, headers=self._headers, data=payload)
        except requests.exceptions.ConnectionError:
            raise Exception('Failed to connect for remote procedure call.')
 
        if not response.status_code in (200, 500):
            raise Exception('RPC connection failure: ' + str(response.status_code) + ' ' + response.reason)
        
        responseJSON = response.json()
        
        if 'error' in responseJSON and responseJSON['error'] != None:
            raise Exception('Error in RPC call: ' + str(responseJSON['error']))
        if self.debug: print(responseJSON['result'])
        return responseJSON['result']

