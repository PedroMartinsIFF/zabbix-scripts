import enum
from re import template
from tokenize import group
from turtle import goto
from numpy import outer
from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
import csv


parser = ArgumentParser(description='Retorna lista de itens de n hosts')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')
args = parser.parse_args()

if args.url_api:
	zapi = ZabbixAPI(args.url_api, timeout=600.0)
	try:
		zapi.login(args.user, args.password)
		print("Logged")
	except Exception as e:
		print(e)
		exit(1)
else:
	print("Erro ao logar na API.")
	exit(0)

listHostGroupName = []
listHostGroupError = []
hostGroup = zapi.host.get(output=['host', 'jmx_error'], groupids = '61836')

for index, item in enumerate(hostGroup):
	listHostGroupName.append(item['host'])
	listHostGroupError.append(item['jmx_error'])

with open('./teste.csv', 'w') as csvfile:
	csv.writer(csvfile, delimiter='\n').writerow(['Nome Hosts:'])
	csv.writer(csvfile, delimiter='\n').writerow(listHostGroupName)
