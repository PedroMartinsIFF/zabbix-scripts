# coding: utf-8

from pyzabbix import ZabbixAPI
import csv
from argparse import ArgumentParser

parser = ArgumentParser(description='Adiciona usuários locais no Zabbix em lote')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')
parser.add_argument('--file', dest='file', help='Arquivo a ser lido. Usar padrão: Nome;alias')
parser.add_argument('--padrao', dest='padrao', help='Senha Padrao')
args = parser.parse_args()

if args.url_api:
	zapi = ZabbixAPI(args.url_api, timeout=600.0)
	try:
		zapi.login(args.user, args.password)
	except Exception:
		print("Unable to login: %s")
		exit(1)
else:
	print("Execute add_users.py -h para obter ajuda.")
	exit(0)
	
f = csv.reader(open(args.file), delimiter=',')

list_users = []
for user in f:
	try:
		group = zapi.usergroup.get(output=['usrgrpid'], filter={'name' : user[1]})
		id=group[0]['usrgrpid']
		users = zapi.user.create(alias=user[0], name=user[0], passwd=args.padrao, usrgrps=[{'usrgrpid': id }])
		print("Criando usuário: ", user[0] + " - " + user[0])
	except:
		print("Error usuario não cadastrado")

zapi.user.logout()
