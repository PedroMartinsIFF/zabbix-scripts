from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
import csv
from datetime import datetime, timedelta

parser = ArgumentParser(description='Retorna lista de itens de n hosts')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')
parser.add_argument('--group', dest='group', help='Arquivo a ser lido com nome do grupo de op. Um grupo por linha.')
parser.add_argument('--path', dest='path', help='Arquivo a ser lido com nome do grupo de op. Um grupo por linha.')

args = parser.parse_args()

try:
	zapi = ZabbixAPI(args.url_api)
	zapi.login(args.user,args.password)
	print('logged')
except Exception as e:
	print(e)

# HOST | GROUP | PROBLEM | DURATION 
with open(args.path, 'w') as arquivo:
	dt = datetime.now()
	problems = zapi.problem.get(output=['objectid','clock','name'],groupids=args.group,search = {'name': 'close to expire'})
	triggers = []
	for problem in problems:
		triggers.append(problem['objectid']) 

	triggers_info = zapi.trigger.get(triggerids=triggers,selectHosts=['host'],selectGroups=['name'])

	for i in range(len(problems)):
		HOST = triggers_info[i]['hosts'][0]['host']
		PROBLEM = problems[i]['name']
		TIME = datetime.fromtimestamp(int(problems[i]['clock']))
		DURATION = dt - TIME

		print(str(TIME)+','+HOST+','+PROBLEM+','+str(DURATION),file=arquivo)


zapi.user.logout()

