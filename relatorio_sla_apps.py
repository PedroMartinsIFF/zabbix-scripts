from zabbix_utils import ZabbixAPI
from argparse import ArgumentParser
from datetime import datetime, time ,timedelta, date

parser = ArgumentParser(description='Gera um relatório do service MPLS')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API - ex.: https://monitor.zabbix.staging.globoi.com',
                    required=True)
parser.add_argument('--user', dest='user', help='Usuário Zabbix', required=True)
parser.add_argument('--password', dest='password', help='Senha Zabbix', required=True)
args = parser.parse_args()

 
if args.url_api:
	zapi = ZabbixAPI(args.url_api, timeout=600.0)
	try:
		zapi.login(user=args.user, password=args.password)
		print("Logged")
	except Exception:
		print("Unable to login: %s")
		exit(1)
else:
	print("Erro ao logar na API.")
	exit(0)



month = datetime.now().month
year = datetime.now().year

first_day_of_current_month = datetime(year, month, 1)
first_day_of_next_month = datetime(year, month - 1, 1)


first_day_of_next_month_timestamp = first_day_of_current_month.timestamp()
first_day_of_current_month_timestamp = first_day_of_next_month.timestamp()

'''
def get_leaf(leaf_id,f):
    children = leaf_id[0]['children']
    for i in range(len(children)):
        slaid = zapi.sla.get(serviceids=children[i]['serviceid'])
        for sla in slaid:
            sli = zapi.sla.getsli(slaid=sla['slaid'], serviceids=children[i]['serviceid'], period_from=int(first_day_of_current_month_timestamp))
            print(f"{children[i]['name']},{sli['sli'][0][0]['sli']}",file=f)
'''

def get_children_info(node_id,f):

    children = node_id[0]['children']
    for i in range(len(children)):
        slaid = zapi.sla.get(serviceids=children[i]['serviceid'])
        for sla in slaid:
            sli = zapi.sla.getsli(slaid=sla['slaid'], serviceids=children[i]['serviceid'], period_from=int(first_day_of_current_month_timestamp))
            print(f"{children[i]['name']},{sli['sli'][1][0]['sli']}",file=f)
            service_leaf = zapi.service.get(serviceids=children[i]['serviceid'], selectChildren= ['serviceid', 'name'])
            #get_leaf(service_leaf,f)
       

def get_consolidado(f):
    data_services = zapi.service.get(serviceids="2997", selectChildren= ['serviceid', 'name'])

    for i in range(len(data_services[0]['children'])):
        servicesid = (data_services[0]['children'][i]['serviceid'])
        slaid = zapi.sla.get(serviceids=servicesid)
        sli = zapi.sla.getsli(slaid=slaid[0]['slaid'], serviceids=servicesid, period_from=int(first_day_of_current_month_timestamp))
        print(f"{data_services[0]['children'][i]['name']},{sli['sli'][1][0]['sli']},{sli['sli'][1][0]['uptime']},{sli['sli'][1][0]['downtime']}",file=f)
        get_children = zapi.service.get(serviceids=servicesid, selectChildren= ['serviceid', 'name'])
        get_children_info(get_children,f)



with open('input_format/consolidado.csv', 'w') as f:
    get_consolidado(f)
