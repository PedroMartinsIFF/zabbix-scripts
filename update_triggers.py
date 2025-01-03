#!/usr/bin/python
from os import path
from sys import argv, exit
from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
from progressbar import ProgressBar, Percentage, ETA, ReverseBar, RotatingMarker, Timer
from logprint import LogPrint
import csv

parser = ArgumentParser(description = 'Change status of multiple triggers in multiple Zabbix Hosts.')
parser.add_argument('--url', dest = 'url', help = 'Zabbix server address')
parser.add_argument('--user', dest = 'user', help = 'Zabbix user')
parser.add_argument('--password', dest = 'password', help = 'Zabbix password')
parser.add_argument('--no-verbose', dest = 'verbose', action = 'store_false', help = 'Dont show any logs on screen')
parser.add_argument('--verbose', dest = 'verbose', action = 'store_true')
parser.set_defaults(verbose=False)
parser.add_argument('--no-run', dest = 'run', action = 'store_false', help = 'Dont perform any operation')
parser.add_argument('--run', dest = 'run', action = 'store_true')
parser.set_defaults(run=False)
parser.add_argument('--file', nargs = '+', dest = 'file', help = 'List of hosts and triggers csv')
parser.add_argument('--status', dest = 'status', type = int, required = True, help = 'Status to change trigger to. [0=enable|1=disable]')
parser.add_argument('--loglevel', dest = 'loglevel', default = 'ERROR', help = 'Debug level. DEBUG/INFO/WARNING/ERROR/CRITICAL')
args = parser.parse_args()

TIMEOUT = 20.0
LOGFILE = '/tmp/%s.log' % path.basename(argv[0])
logger = LogPrint(echo=args.verbose, logfile=LOGFILE, loglevel=args.loglevel.upper())

if args.status != 0 and args.status != 1:
	logger.error('--status should be either 0 or 1')
	exit(1)

if args.url:
	zapi = ZabbixAPI(args.url, timeout=600.0)
	try:
		zapi.login(args.user, args.password)
	except Exception:
		print("Não foi possível fazer login: %s")
		exit(1)
else:
	print("Execute get_events.py -h para obter ajuda.")
	exit(0)

lista = []

with open(args.file[0], mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter=';')
    [ lista.append(row) for row in csv_reader ]



triggers_ids = []

for item in lista:
	h = zapi.host.get(output=['hostid','name'],search={'name': item['host']})
	if h.__len__() == 0:
		logger.warning('Host {0} not found!'.format(item['host']))
		continue
	all_triggers = zapi.trigger.get(output=['description','triggerid'],hostids=[h[0]['hostid']])

	triggers = []
	for i in range(len(all_triggers)):
		if item['trigger'] in all_triggers[i]['description']:
			triggers.append(all_triggers[i])

	logger.info('Found {0} triggers for host {1}'.format(triggers.__len__(),item['host']))
	logger.print_json(triggers)
	for t in triggers:
		triggers_ids.append(t['triggerid'])

i = 0
logger.info('Found {0} triggers'.format(triggers_ids.__len__()))
bar = ProgressBar(maxval=triggers_ids.__len__(),widgets=[Percentage(), ReverseBar(), ETA(), RotatingMarker(), Timer()]).start()
for t in triggers_ids:
	if args.run == True:
		out = zapi.trigger.update(triggerid=t,status=args.status)
		i += 1
		bar.update(i)
	else:
		logger.warning('Should change triggerid {0} to status {1}'.format(t,args.status))
bar.finish()

zapi.user.logout()
logger.info('Done!!')

