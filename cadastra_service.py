from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
import csv
from datetime import datetime, timedelta
import re

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

def create_service_sla(OPERATOR,HOST_1_PAR_1,HOST_2_PAR_1,LINK_1_PAR_1,LINK_2_PAR_1,HOST_1_PAR_2,HOST_2_PAR_2,LINK_1_PAR_2,LINK_2_PAR_2):
	MAIN_SERVICE = '2040'
	print('Criando Service SLA')
	print(f'CONSOLIDADO {OPERATOR} {HOST_1_PAR_1}/{HOST_2_PAR_1}')
	CONSOLIDADO = 'CONSOLIDADO '+OPERATOR+' '+ HOST_1_PAR_1+'/'+HOST_2_PAR_1
	father_id = zapi.service.create(parents=[{'serviceid':MAIN_SERVICE}],name=CONSOLIDADO,algorithm=1,sortorder=1)

	print(f'{HOST_1_PAR_1}-{HOST_2_PAR_1}')
	LINK_P = HOST_1_PAR_1+'-'+HOST_2_PAR_1
	father_id_p = zapi.service.create(parents=[{'serviceid':father_id['serviceids'][0]}],name=LINK_P,sortorder=1,algorithm=1)

	print(f'{HOST_1_PAR_1}')

	ID_1_PAR_1 = zapi.host.get(output=['hostid'],filter={'name':HOST_1_PAR_1})
	zapi.service.create(parents=[{'serviceid':father_id_p['serviceids'][0]}],name=HOST_1_PAR_1,sortorder=1,algorithm=1,tags=[{'tag': 'SLA', 'value': 'MPLS'}],problem_tags=[{'tag':'neighbor','operator':'0','value':str(LINK_1_PAR_1)},{'tag':'host_id','operator':'0','value':str(ID_1_PAR_1[0]['hostid'])}])

	print(f'{HOST_2_PAR_1}')
	ID_2_PAR_1 = zapi.host.get(output=['hostid'],filter={'name':HOST_2_PAR_1})
	zapi.service.create(parents=[{'serviceid':father_id_p['serviceids'][0]}],name=HOST_2_PAR_1,sortorder=1,algorithm=1,tags=[{'tag': 'SLA', 'value': 'MPLS'}],problem_tags=[{'tag':'neighbor','operator':'0','value':str(LINK_2_PAR_1)},{'tag':'host_id','operator':'0','value':str(ID_2_PAR_1[0]['hostid'])}])

	print(f'{HOST_1_PAR_2}-{HOST_2_PAR_2}')
	LINK_S = HOST_1_PAR_2+'-'+HOST_2_PAR_2
	father_id_s = zapi.service.create(parents=[{'serviceid':father_id['serviceids'][0]}],name=LINK_S,algorithm=2,sortorder=1)

	print(f'{HOST_1_PAR_2}')
	ID_1_PAR_2 = zapi.host.get(output=['hostid'],filter={'name':HOST_1_PAR_2})
	zapi.service.create(parents=[{'serviceid':father_id_s['serviceids'][0]}],name=HOST_1_PAR_2,sortorder=1,algorithm=1,tags=[{'tag': 'SLA', 'value': 'MPLS'}],problem_tags=[{'tag':'neighbor','operator':'0','value':str(LINK_1_PAR_2)},{'tag':'host_id','operator':'0','value':str(ID_1_PAR_2[0]['hostid'])}])

	print(f'{HOST_2_PAR_2}')
	ID_2_PAR_2 = zapi.host.get(output=['hostid'],filter={'name':HOST_2_PAR_2})
	zapi.service.create(parents=[{'serviceid':father_id_s['serviceids'][0]}],name=HOST_2_PAR_2,sortorder=1,algorithm=1,tags=[{'tag': 'SLA', 'value': 'MPLS'}],problem_tags=[{'tag':'neighbor','operator':'0','value':str(LINK_2_PAR_2)},{'tag':'host_id','operator':'0','value':str(ID_2_PAR_2[0]['hostid'])}])
'''
OPERATOR = 'EMBRATEL'
HOST_1_PAR_1 = 'mpls-ion-01.globoi.com'
HOST_2_PAR_1 = 'mpls-mg-01.globoi.com'
LINK_1_PAR_1 = '10008.10.255.128.199'
LINK_2_PAR_1 = '10008.10.255.128.198'

HOST_1_PAR_2 = 'mpls-ion-02.globoi.com'
HOST_2_PAR_2 = 'mpls-mg-02.globoi.com'
LINK_1_PAR_2 = '10008.10.255.128.201'
LINK_2_PAR_2 = '100025.10.255.128.182'

OPERATOR,HOST_1_PAR_1,HOST_2_PAR_1,LINK_1_PAR_1,LINK_2_PAR_1,LINK_1_PAR_2,LINK_2_PAR_2
'''
with open('input_format/services.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter=',')
    for row in csv_reader:
    	create_service_sla(row['OPERATOR'],row['HOST_1_PAR_1'],row['HOST_2_PAR_1'],row['LINK_1_PAR_1'],row['LINK_2_PAR_1'],row['HOST_1_PAR_2'],row['HOST_2_PAR_2'],row['LINK_1_PAR_2'],row['LINK_2_PAR_2'])


#service = zapi.service.get(selectParents=['serviceid'],serviceids='1746')
#print(service)





zapi.user.logout()

