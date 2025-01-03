from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
import json

parser = ArgumentParser(description='Adiciona usuários locais no Zabbix em lote')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')
parser.add_argument('--group-id', dest='group_id', help='Adicionar o ID do Host Group')
parser.add_argument('--item-key', dest='item_key', help='Chave do item no zabbix')

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

hosts = zapi.host.get(groupids=args.group_id,output=['hostid'])
itens = zapi.item.get(groupids=args.group_id,output=['item_id','hostid'],filter={'key_': '' + args.item_key})

with open('file.txt', 'w') as arquivo:
    for i in range (len(itens)):
            info = zapi.history.get(hostids=itens[i]['hostid'],itemids=itens[i]['itemid'],history=1,output=['value'],limit=1)
            name = zapi.host.get(hostids=itens[i]['hostid'], output=['host'])
            print(name, info, file=arquivo)

zapi.user.logout()
