from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
import json

parser = ArgumentParser(description='Retorna lista de itens de n hosts')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')
parser.add_argument('--host_file', dest='file', help='Adicionar o ID dos hosts')
parser.add_argument('--output-file', dest='saida', help='Adicionar o path para o arquivo de saida')

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

with open(args.file) as hosts:
    for line in hosts:
        stripped_line = line.rstrip()
        id = zapi.host.get(output=["hostid"], filter={"host" : stripped_line})
        ids.append(id[0]['hostid'])



with open(args.saida, 'w') as arquivo:
    for i in range (len(ids)):
        itens = zapi.item.get(hostids=ids[i],output=['item_id','name','hostid'])     
        name = zapi.host.get(hostids=ids[i], output=['host'])
        print(name)
        print(name, file=arquivo)
        for item in itens:
            # Essa linha adiciona um filtro para os itens, para pegar todos os itens basta remover
            if(item["name"].find("State of service") != -1):
                print(item["name"], file=arquivo)
