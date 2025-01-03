from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
import csv

parser = ArgumentParser(description='Retorna lista de itens de n hosts')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')
#parser.add_argument('--file', dest='file', help='Arquivo a ser lido com nome do grupo de op. Um grupo por linha.')
args = parser.parse_args()

try:
	zapi = ZabbixAPI(args.url_api)
	zapi.login(args.user,args.password)
	print('logged')
except Exception as e:
	print(e)

f = csv.reader(open('input_format/input_switches.csv'), delimiter=',')

for line in f:
	id = zapi.host.get(output=["hostid"], search={"host" : line[0]})
	#print(id)
	for i in range(len(id)):
			try:
				trigger_id = zapi.trigger.get(output=['triggerid'],search={'description' : 'GigabitEthernet1/0/9'},hostids=id[i]['hostid'])
				print(trigger_id)
				zapi.trigger.update(triggerid=trigger_id[0]['triggerid'],status=0)
				print('Trigger Habilitada para o host', line[0] )
			except:
				print('Trigger nao encontrada no host',id[i]['hostid'])

zapi.user.logout()
