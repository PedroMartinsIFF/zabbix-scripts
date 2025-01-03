#!/usr/bin/env python

from argparse import ArgumentParser
from logprint import LogPrint
from os import path
from progressbar import ProgressBar, Percentage, ETA, ReverseBar, RotatingMarker, Timer
from pyzabbix import ZabbixAPI
from sys import argv, exit

parser = ArgumentParser(description = 'Adds a list of NEW macro(s) or context macros to a list of host(s)')
parser.add_argument('--url', dest = 'url', required = True, help = 'Zabbix server address')
parser.add_argument('--user', dest = 'user', required = True, help = 'Zabbix user')
parser.add_argument('--password', dest = 'password', required = True, help = 'Zabbix password')
parser.add_argument('--no-verbose', dest = 'verbose', action = 'store_false', help = 'Dont show any logs on screen')
parser.add_argument('--verbose', dest = 'verbose', action = 'store_true')
parser.set_defaults(verbose=False)
parser.add_argument('--loglevel', dest = 'loglevel', required = True, default = 'WARNING', help = 'Debug level. DEBUG/INFO/WARNING/ERROR/CRITICAL')
parser.add_argument('--no-run', dest = 'run', action = 'store_false', help = 'Default. Don\'t perform WRITE inside zabbix')
parser.add_argument('--run', dest = 'run', action = 'store_true')
parser.set_defaults(run=False)
parser.add_argument('--hosts', dest = 'hosts', required = True, nargs = '+', help = 'Hosts to be used. Exact name required. Separeated by spaces. Format: --hosts \'host a\' hostb')
parser.add_argument('--macros', dest = 'macros', required = False, nargs = '+', help = 'Plain macro\'s to be added. No {$NAME} required. Use just NAME:VALUE. Format: --macros NAME1:VALUE1 NAME2:VALUE2')
parser.add_argument('--context', dest = 'context', required = False, nargs = '+', help = 'Macro\'s to be added in context mode. No {$NAME:"context"} required. Use just NAME:CONTEXT:VALUE. Format: --macros NAME1:CONTEXT1:VALUE1 NAME2:CONTEXT:VALUE2')
args = parser.parse_args()

TIMEOUT = 20.0
LOGFILE = '/tmp/%s.log' % path.basename(argv[0])
logger = LogPrint(echo=args.verbose, logfile=LOGFILE, loglevel=args.loglevel.upper())
macros = []
i = 0

if not args.context and not args.macros:
	logger.error('At least one of the following HAS to be declared: --macros or --context')

try:
	zapi = ZabbixAPI(args.url,timeout=TIMEOUT)
	zapi.login(args.user,args.password)
except:
	logger.error('Unable to login. Check your credentials.')
	exit(1)

if args.macros:
	for macro in args.macros:
		(k,v) = macro.split(':')
		macros.append({'macro': '{$%s}' % k, 'value': v})

if args.context:
	for macro in args.context:
		(k,c,v) = macro.split(':')
		macros.append({'macro': '{$%s:"%s"}' % (k,c), 'value': v})

logger.debug('Macros:')
logger.print_json(macros)

'''
TODO:
Macros que jah existem falharao miseravelmente. Podemos tratar isso antes de enviar o host.massadd.
'''

if args.run:
	bar = ProgressBar(maxval=args.hosts.__len__(),widgets=[Percentage(), ReverseBar(), ETA(), RotatingMarker(), Timer()]).start()
for host in args.hosts:
	h = zapi.host.get(output=['hostid','host'],selectMacros=['macro','value'],filter={'host': host})
	if h.__len__() == 1:
		if args.run:
			o = zapi.host.massadd(hosts=[{'hostid': h[0]['hostid']}],macros=macros)
			i += 1
			bar.update(i)
		else:
			logger.warning('Host {} hostid {}'.format(host,h[0]['hostid']))
	else:
		logger.error('Host {} not found'.format(host))
if args.run:
	bar.finish()

zapi.user.logout()
