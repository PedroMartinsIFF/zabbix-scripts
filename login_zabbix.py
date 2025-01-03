from zabbix_utils import ZabbixAPI
from argparse import ArgumentParser
from datetime import datetime
import csv

parser = ArgumentParser(description='Retorna lista de itens de n hosts')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API')
#parser.add_argument('--user', dest='user', help='Zabbix user')
#parser.add_argument('--password', dest='password', help='Zabbix password')
args = parser.parse_args()


if args.url_api:
	zapi = ZabbixAPI(args.url_api, timeout=600.0)
	try:
		zapi.login(user="", password="")
		print("Logged")
	except Exception:
		print("Unable to login: %s")
		exit(1)
else:
	print("Erro ao logar na API.")
	exit(0)


zapi.logout()

