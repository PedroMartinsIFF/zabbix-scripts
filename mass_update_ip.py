import os
from argparse import ArgumentParser
from pyzabbix import ZabbixAPI
import csv
import requests
from datetime import datetime, time ,timedelta, date
import time
import json


parser = ArgumentParser(description='Relatorio de hosts adicionados e removidos do zabbix no dia')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')
parser.add_argument('--file', dest='file', help='Arquivo')

args = parser.parse_args()

if args.url_api:
	zapi = ZabbixAPI(args.url_api, timeout=600.0)
	try:
		zapi.login(args.user, args.password)
		print("Logged")
	except Exception:
		print("Unable to login: %s")
		exit(1)
else:
	print("Erro ao logar na API.")
	exit(0)

f = csv.reader(open(args.file), delimiter=';')
for line in f:
    host_id = zapi.host.get(output=["hostid"], filter={"host" : line[0]})
    #print(host_id)
    teste = zapi.hostinterface.get(hostids=host_id[0]['hostid'])
    for i in range(len(teste)):
        #print(teste[i]['ip'], line[1])
        zapi.hostinterface.update(interfaceid=teste[i]['interfaceid'], ip=line[1])
