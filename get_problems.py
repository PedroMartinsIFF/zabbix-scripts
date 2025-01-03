from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
import json
import time
import datetime

parser = ArgumentParser(description='Script generico que retorna o relatório de um erro especifico de um hostgroup')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')
parser.add_argument('--start', dest='start', help='Data de início do relatório : dd/mm/yyyy')
parser.add_argument('--end', dest='end', help='Data de fim do relatório : dd/mm/yyyy')
parser.add_argument('--group', dest='group', help='Host Group')
parser.add_argument('--alarm', dest='alarm', help='Nome do alarme')
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

start = args.start
end = args.end

start_convertido = time.mktime(datetime.datetime.strptime(start, "%d/%m/%Y").timetuple())
end_convertido = time.mktime(datetime.datetime.strptime(end, "%d/%m/%Y").timetuple())

id = zapi.hostgroup.get(output=["groupid"], filter={"name" : args.group})

teste = zapi.event.get(output=['name'],groupids=id[0]['groupid'],time_from=start_convertido,time_till=end_convertido,value=1)
error = 0

for i in range(len(teste)):
    
    if args.alarm in teste[i]['name']:
        error = error + 1
        print(teste[i]['name'])

print('View:',args.group)
print('Period:',start,'until',end)
print('Total errors:', len(teste))
print('Error :',args.alarm,'| Number of occurrences:',error)
