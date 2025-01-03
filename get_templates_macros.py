from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
import json
import csv

parser = ArgumentParser(description='Retorna uma lista de macros associadas a todos os templates')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API - ex.: https://api.zabbix.dev.globoi.com')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')

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

get_templates_ids = zapi.template.get(output='templateid')
with open('lista_macro_template_debug.txt', 'w') as arquivo:
	for template in range (len(get_templates_ids)):
		template=get_templates_ids[template]['templateid']
		macros=zapi.template.get(output=['hostmacroid'],selectMacros='extend',templateids=template)
		lista_macros = macros[0]['macros']
		for i in range (len(lista_macros)):
			if (lista_macros != []) and (lista_macros[i]['macro'][:5] == '{$DOC'):
				template_name = zapi.template.get(output=['name'], templateids=template)
				print(template+";"+template_name[0]['name']+";"+lista_macros[i]['hostmacroid']+";"+lista_macros[i]['macro']+";"+lista_macros[i]['value'], file=arquivo)

zapi.user.logout()
