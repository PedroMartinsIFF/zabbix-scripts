from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
import json
import csv

parser = ArgumentParser(description='Deleta uma lista de usergroups')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')
parser.add_argument('--file', dest='file', help='Lista de grupos')
parser.add_argument('--output', dest='output', help='Saida em arquivo')

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

ids = []

with open(args.file) as list:
	with open(args.output, 'w') as arquivo:
		print(f'{"Ids"},{"Username"}', file=arquivo)
	for line in list:
		stripped_line = line.rstrip()
		id = zapi.usergroup.get(output=["usrgrpid","name","userids","gui_access"], filter={"name" : stripped_line})
		ids.append(id[0]['usrgrpid'])
		for i in range(len(ids)):
#			users = zapi.user.get(output=["name","userids","username","roleid"], usrgrpids=ids[i])
			users = zapi.user.get(output=["name","userids","alias","type"], usrgrpids=ids[i])

		for j in range(len(users)):
			with open(args.output, 'a+') as arquivo:
#				print(f'{users[j]["userid"]},{users[j]["username"]},{users[j]["roleid"]}', file=arquivo)
				print(f'{users[j]["userid"]},{users[j]["alias"]},{users[j]["type"]}', file=arquivo)

zapi.user.logout()
