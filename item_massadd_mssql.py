from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
import json
import csv

parser = ArgumentParser(description='Adicionar itens a um template em lote - Funcionando para template Database Monitor')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')
parser.add_argument('--file', dest='file', help='Lista de ids')
parser.add_argument('--template', dest='template', help='Nome do Template para adicionar os hosts')
parser.add_argument('--application', dest='application', help='ID da application')


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

id = zapi.template.get(output=["templateid"], filter={"name" : args.template})
template_id=id[0]['templateid']

application = zapi.application.get(output=["applicationid"],templateids=template_id, filter={"name" : args.application})
application_id = application[0]['applicationid']
with open(args.file) as f:
	f_csv = csv.reader(f)
	headers = next(f_csv)
	
	for row in f_csv:
		try:
			zapi.item.create(name=row[0],
				key_='db.odbc.select[' + str(row[8]) + ',,"Driver={$MSSQL.DRIVER};Server={HOST.CONN};Trusted_Connection={$MSSQL.KERBEROS}"]',
				hostid=template_id,
				type=11,
				value_type=row[11],
				delay="0;"+row[9],
				params=row[6],
				history="1w",
				trends="456d",
				description=row[3],
				password="{$ODBC_PASSWORD}",
				username="{$ODBC_USER}")
			new_item=zapi.item.get(output=["itemid"],templateids=template_id, filter=[{"name":row[0]}])
		except Exception as e:
			print(e)

for i in range(len(new_item)):
	zapi.application.massadd(applications=[{"applicationid":application_id}],items=[{"itemid": new_item[i]['itemid']}])
