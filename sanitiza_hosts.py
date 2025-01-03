#Verificar hosts fora de view operacional
#Verificar hosts com alarmes desativados
#Verificar hosts com falha de comunicação SNMP/AGENT

#Critérios para deleção:
# 1 - Alarmes desativados e falha nas interfaces
# 2 - Fora de View Operacional /  Projeto e sem notificação

from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
import csv
from datetime import datetime, timedelta

parser = ArgumentParser(description='Retorna lista de itens de n hosts')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')
#parser.add_argument('--group', dest='group', help='Arquivo a ser lido com nome do grupo de op. Um grupo por linha.')
args = parser.parse_args()

try:
	zapi = ZabbixAPI(args.url_api)
	zapi.login(args.user,args.password)
	print('logged')
except Exception as e:
	print(e)

#Verifica se a interface do agent OU a interface SNMP esta com status failed
def check_availability(host):
	if((host['available'] or host['snmp_available'])  ==  '2'):
		return 1
	else:
		return 0

#Verifica se pelo menos um alarme está enableds	
def  check_alarms(host):
	trigger_on = 0
	triggers = zapi.trigger.get(hostids=host['hostid'])
	for status in triggers:
		if status['status'] == '0':
			trigger_on = 1
			break
		else:
			continue
	if trigger_on == 1:
		return 0
	else:
		return 1

#Verifica se o host possui algum grupo de Projeto/Notificação/Operação			
def check_hostgroups(host):
	group_on = 0
	for group in host['groups']:
		if (('Projeto' in str(group['name']) ) or ('Operacao'  in str(group['name'])) or ('Notificacao' in str(group['name']))):
			group_on = 1
			print('Encontrado')
			break
		else:
			print('Nao Encontrado')
			continue
	if group_on == 1:
		return 0
	else:
		return 1
		
def get_all_hosts():
	hosts_interfaces_status_get= zapi.host.get(output=['name','status','available','snmp_available'],selectGroups=['name'],filter={'status': 0})
	with open('results/relatorio_hosts_inativos_prod.csv', 'w') as arquivo:
		for host in hosts_interfaces_status_get:
			print('Host is enabled, checking conditions on ', host['name'])
			print('Checking Interface Status on ', host['name'])
			interfaces_check = check_availability(host)
			print(interfaces_check)
			print('Checking Triggers on ', host['name'])
			alarms_check =check_alarms(host)
			print(alarms_check)
			print('Checking Groups on ', host['name'])
			groups=check_hostgroups(host)
			print(groups)
			if((groups and interfaces_check and alarms_check) == 1 ):
				print('Host deve ser deletado')
				print(str(host['name'])+','+str(interfaces_check)+','+str(alarms_check)+','+str(groups)+',Host deve ser deletado',file=arquivo)
			else:
				print('Host não deve ser deletado')
				print(str(host['name'])+','+str(interfaces_check)+','+str(alarms_check)+','+str(groups)+',Host não deve ser deletado',file=arquivo)

get_all_hosts()

zapi.user.logout()

