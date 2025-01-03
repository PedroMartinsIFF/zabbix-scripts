# coding: utf-8
# !/usr/bin/python

from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
from logprint import LogPrint
import csv
import os

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
parser.add_argument('--number-of-groups', dest='n', help='Numero de hostgroups no csv')

args = parser.parse_args()

logger = LogPrint(echo=True, logfile='/tmp/my_log.log', loglevel='DEBUG')

zapi = ZabbixAPI(args.url, timeout=600.0)

try:
	zapi.login(args.user, args.password)
except Exception as e:
	logger.error("Unable to login: %s" % e)
	exit(0)

files = [open('filename%i.txt' %i, 'w') for i in range(0,int(args.n))]
f = csv.reader(open(args.file), delimiter=',')
names = []
count_line = 0
for line in f:
	if count_line == 0:
		for i in range (len(line)):
			names.append(line[i])
			files[i].write('{:10},{:10},{:10},{:10} \n'.format("Nome","Hosts Enabled","Quantidade de Erros","Hosts Disabled"))

		count_line+=1
	else:
		for i in range(len(line)):
			try:
				HGS = zapi.hostgroup.get(output=["groupid"], filter={'name': line[i]})[0]
			except:
				logger.error("Host group not found: " + line[i])
			HOSTS = zapi.host.get(output=["host", "name", "error", "snmp_error", "ipmi_error", "jmx_error"], groupids=HGS, selectInterfaces=["ip", "dns", "type"],filter={'status': 0})
			HOSTS_DISABLE = zapi.host.get(output=["host", "name"], groupids=HGS, filter={'status': 1})
		
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
			
			files[i].write('{:10},{:10},{:10},{:10} \n'.format(line[i],len(HOSTS),qtde_no_errors,len(HOSTS_DISABLE)))
			if len(HOSTS_DISABLE) > 0:
				
				files[i].write('Hosts em Disable\n')
			for x in HOSTS_DISABLE:
				files[i].write(x['name']+'\n')
for f in files:
	f.close()

for i in range (len(names)):
	os.rename('filename%i.txt'%i ,'relatorio_quinzenal/' + names[i]+ '.csv')
	#os.rename('relatorio_quinzenal/filename%i.txt'%i ,'Relatorio ' + names[i])

	
zapi.user.logout()
