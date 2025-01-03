# coding: utf-8
# !/usr/bin/python

from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
from logprint import LogPrint
import csv

parser = ArgumentParser(description='List active hosts of a group with their registered interfaces')
parser.add_argument('--url', dest='url', help='Zabbix server address')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')
parser.add_argument('--no-verbose', dest='verbose', action='store_false', help='Don\'t show any logs on screen')
parser.add_argument('--verbose', dest='verbose', action='store_true')
parser.set_defaults(verbose=False)
parser.add_argument('--file', dest='file', help='Arquivo a ser lido com nome do grupo de operação. Um grupo por linha.')
parser.add_argument('--loglevel', dest='loglevel', default='ERROR',
					help='Debug level. DEBUG/INFO/WARNING/ERROR/CRITICAL')

args = parser.parse_args()

logger = LogPrint(echo=True, logfile='/tmp/my_log.log', loglevel='DEBUG')

zapi = ZabbixAPI(args.url, timeout=600.0)

try:
	zapi.login(args.user, args.password)
except Exception as e:
	logger.error("Unable to login: %s" % e)
	exit(0)

f = csv.reader(open(args.file))

for hg in f:
	try:
		HGS = zapi.hostgroup.get(output=["groupid"], filter={'name': hg[0]})[0]
	except:
		logger.error("Host group not found: " + hg[0])
		exit(0)
	
	HOSTS = zapi.host.get(output=["host", "error", "snmp_error", "ipmi_error", "jmx_error"], groupids=HGS, selectInterfaces=["ip", "dns", "type"],
						  filter={'status': 0})
	
	HOSTS_DISABLE = zapi.host.get(output=["host"], groupids=HGS, filter={'status': 1})
	
	qtde_no_errors = 0
	
	for HOST in HOSTS:
		for INTERFACE in HOST['interfaces']:
			if INTERFACE['type'] == '1':
				interfaceType = "Agent"
				errorInterface = HOST['error'] or "No Error"
			elif INTERFACE['type'] == '2':
				interfaceType = "SNMP"
				errorInterface = HOST['snmp_error'] or "No Error"
			elif INTERFACE['type'] == '3':
				interfaceType = "IPMI"
				errorInterface = HOST['ipmi_error'] or "No Error"
			else:
				interfaceType = "JMX"
				errorInterface = HOST['jmx_error'] or "No Error"
			# Esse print só serve se quiser ler o erro dos agentes.
			#print(HOST['host'], "- ", INTERFACE['ip'], "- ", INTERFACE['dns'], "- ", interfaceType, "- ", errorInterface)
			if errorInterface != "No Error":
				qtde_no_errors += 1
	
	print(f'{hg[0]},{len(HOSTS)},{qtde_no_errors},{len(HOSTS_DISABLE)}')

zapi.user.logout()
