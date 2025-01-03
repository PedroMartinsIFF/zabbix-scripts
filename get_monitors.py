from os import path
from sys import argv, exit
from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
import json

parser = ArgumentParser(description = 'Print info for multiple hosts')
parser.add_argument('--url', required = True, dest = 'url', help = 'Zabbix server address')
parser.add_argument('--user', required = True, dest = 'user', help = 'Zabbix user')
parser.add_argument('--password', required = True, dest = 'password', help = 'Zabbix password')
parser.add_argument('--hosts', required = True, dest = 'hosts', nargs='+', help = 'Exact `visible name` for hosts')
args = parser.parse_args()
TIMEOUT = 10.0
try:
    zapi = ZabbixAPI(args.url,timeout=TIMEOUT)
    zapi.login(args.user,args.password)
except Exception as e:
    print("ERROR: Unable to login: %s" % (e))
    exit(1)
for host in args.hosts:
	h = zapi.host.get(output=['name','hostid'],selectMacros=['macro','value'],selectGroups=['name'],selectParentTemplates=['name'],filter={'name': host})
	print(json.dumps(h, sort_keys=True, indent=4, separators=(',', ': ')))
