from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
import json

parser = ArgumentParser(description='Retorna lista de itens de n hosts')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')
parser.add_argument('--name', dest='name', help='Nome do discovery')
parser.add_argument('--key', dest='key', help='Chave do discovery')
parser.add_argument('--template', dest='template', help='Nome do template')
parser.add_argument('--file', dest='file', help='File')
parser.add_argument('--macro', dest='macro', help='File')

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


create_template = zapi.template.create(groups=[{"groupid":1},{"groupid":1977},{"groupid":3613},{"groupid":3614}],host=args.template)

id = zapi.template.get(output=["templateid"], filter={"name" : args.template})

create_discovery = zapi.discoveryrule.create(name=args.name,key_=args.key,hostid=id[0]['templateid'],type=2,delay="1d")

get_discovery_id = zapi.discoveryrule.get(output=["itemid"], filter={"name" : args.name})


count = 0
conditions = "{'macro': '{#SNMPVALUE}', 'value' : '"
string = ""

f = open(args.file)
row_count = sum(1 for row in f)

with open(args.file) as itens:
	for line in itens:
		count = count + 1
		stripped_line = line.rstrip()
		if count != row_count:
			string = string + conditions + stripped_line + "'}, "
		else:
			string = string + conditions + stripped_line + "'} " 


string2 = "{'evaltype' : 1, 'conditions' : [" + string + "]}"
y = eval(string2)
teste = zapi.discoveryrule.update(itemid=get_discovery_id[0]['itemid'],filter=y)
