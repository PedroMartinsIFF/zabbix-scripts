#!/usr/bin/python

import os, sys
from pyzabbix import ZabbixAPI
from argparse import ArgumentParser

parser = ArgumentParser(description = 'Example script to connect to Zabbix API')
parser.add_argument('--url', dest = 'url', help = 'Zabbix server address')
parser.add_argument('--user', dest = 'user', help = 'Zabbix user')
parser.add_argument('--password', dest = 'password', help = 'Zabbix password')
parser.add_argument('--no-verbose', dest = 'verbose', action = 'store_false', help = 'Don\'t show any logs on screen')
parser.add_argument('--verbose', dest = 'verbose', action = 'store_true')
parser.set_defaults(verbose=False)
args = parser.parse_args()

# Zabbix API 
# https://api.zabbix.staging.globoi.com
# https://api.zabbix.globoi.com

TIMEOUT = 300.0

try:
	zapi = ZabbixAPI(args.url,timeout=TIMEOUT)
	#zapi.session.verify = False
	zapi.login(args.user,args.password)
except Exception:
    print("Unable to login")
    sys.exit(1)

web = [ 				
		{ "hostname": "Example-hostname", "hostip":  "myIP", "hostgroups": "Projeto/Claranet/DCCM"},
		
]
for x in web:
	query = {

        "hostgroups": x['hostgroups'], 
        # Organizar de acordo com a planilha entre os grupos
        # 'Projeto/Claranet/ION', 'Projeto/Claranet/CJB' e 'Projeto/Claranet/DCCM'
        "host": x['hostname'],
        "ip": x['hostip'],
		"alarm": "yes",
		"locality": "CM-RJ",
		# 'CM-RJ' para DCCM e Ion, 'TVG-LQ' para CJB
		"environment": "BE",
		# 'BE' para DCCM e CJB, 'GSAT-BE' para Ion
		"protocol": "agent",
		}
	#logger.print_json(zapi.globo.createNewWeb(**query))
	zapi.globo.createLinuxMonitors(**query)
zapi.user.logout()
