from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
import json

parser = ArgumentParser(description='Deleta uma lista de usergroups')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')
parser.add_argument('--file', dest='file', help='Lista de grupos')
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
    for line in list:
        stripped_line = line.rstrip()
        id = zapi.usergroup.get(output=["usrgrpid"], filter={"name" : stripped_line})
        ids.append(id[0]['usrgrpid'])

for i in range (len(ids)):
    zapi.usergroup.delete(ids[i])
zapi.user.logout()
