from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
import json

parser = ArgumentParser(description='Deleta uma lista de usuários')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')
parser.add_argument('--file', dest='file', help='Lista de usuários')
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

# Tava dando errado pq no zabbix 5.4 o objeto user deixou de ter o parametro alias e passou a ter username
# Pra isso funcionar em prod é só trocar o username pra alias dnv
with open(args.file) as list:
	for line in list:
		stripped_line = line.rstrip()
		print(stripped_line)
		id = zapi.user.get(output=["userid"], filter={"username" : stripped_line})
		print(id)
		ids.append(id[0]['userid'])

print(ids)
'''
for i in range (len(ids)):
	zapi.user.delete(ids[i])
'''

