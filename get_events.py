# coding: utf-8
from pyzabbix import ZabbixAPI
import calendar
import datetime
from argparse import ArgumentParser

parser = ArgumentParser(description='Recupera número de eventos dos grupos DBOps, Enterprise, NetOps e SysOps em determinado período.')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API - ex.: https://ro.api.zabbix.globoi.com')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')
parser.add_argument('--inicio', dest='inicio', help='Informe a data de início no formato yyyymmdd')
parser.add_argument('--fim', dest='fim', help='Informe a data de fim no formato yyyymmdd')
parser.add_argument('--hostgroup-name', required = True, dest = 'hostgroup', nargs='+', help = 'Exact `name of the hostgroup')
args = parser.parse_args()

if args.url_api:
	zapi = ZabbixAPI(args.url_api, timeout=600.0)
	try:
		zapi.login(args.user, args.password)
	except Exception:
		print("Não foi possível fazer login: %s")
		exit(1)
else:
	print("Execute get_events.py -h para obter ajuda.")
	exit(0)

hora_inicial = "000000"
hora_final   = "235959"

data_inicial = args.inicio
data_final   = args.fim

data_inicial_convertida = calendar.timegm(datetime.datetime.strptime(str(int(data_inicial + hora_inicial)), "%Y%m%d%H%M%S").timetuple())
data_final_convertida = calendar.timegm(datetime.datetime.strptime(str(int(data_final + hora_final)), "%Y%m%d%H%M%S").timetuple())

hostgroup_id = zapi.hostgroup.get(
	output = 'groupid',
	filter = {
		'name': args.hostgroup
	}
)

get_events_for_hostgroup = zapi.event.get(
	countOutput =True,
	output = 'extend',
	filter = {'value': '1'},
	groupids = hostgroup_id[0]['groupid'],
	time_from = data_inicial_convertida,
	time_till = data_final_convertida)

print(args.hostgroup)
print('Eventos: ',get_events_for_hostgroup)

zapi.user.logout()
