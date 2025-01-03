#!/usr/bin/python
from os import path
from sys import argv, exit
from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
from progressbar import ProgressBar, Percentage, ETA, ReverseBar, RotatingMarker, Timer
from logprint import LogPrint

parser=ArgumentParser(description='Change proxy of monitored.')
parser.add_argument('--url',dest='url',help='Zabbix server address')
parser.add_argument('--user',dest='user',help='Zabbix user')
parser.add_argument('--password',dest='password',help='Zabbix password')
parser.add_argument('--no-verbose',dest='verbose',action='store_false',help='Dont show any logs on screen')
parser.add_argument('--verbose',dest='verbose',action='store_true')
parser.set_defaults(verbose=False)
parser.add_argument('--loglevel',dest='loglevel',default='ERROR',help='Debug level. DEBUG/INFO/WARNING/ERROR/CRITICAL')
parser.add_argument('--no-run',dest='run',action='store_false',help='Work')
parser.add_argument('--run',dest='run',action='store_true',help='Dont perform any operation')
parser.set_defaults(run=False)
parser.add_argument('--hostname',dest='hostname',required=True,help='Zabbix host visible name')
parser.add_argument('--region',dest='region',required=True,help='Region to change to. Possible values: AS-SP/CM-RJ/CT-RJ/DC-RJ')
parser.add_argument('--env',dest='env',required=True,help='Environments. Possible values: BE/BORDA_DMZ/BORDA_DSR/DB/FE/OOB')

args = parser.parse_args()

TIMEOUT = 10.0
LOGFILE = '/tmp/%s.log' % path.basename(argv[0])
logger = LogPrint(echo=args.verbose, logfile=LOGFILE, loglevel=args.loglevel.upper())
control = {}
control['region'] = ['AS-SP','CM-RJ','CT-RJ','DC-RJ']
control['env'] = ['BE','BORDA_DMZ','BORDA_DSR','DB','FE','OOB']


if str(args.region).upper() not in control['region']:
	logger.error('--region should be: {0}'.format(control['region']))
	exit(0)
if str(args.env).upper() not in control['env']:
	logger.error('--env should be: {0}'.format(control['env']))
	exit(0)

try:
	zapi = ZabbixAPI(args.url,timeout=TIMEOUT)
	zapi.login(args.user,args.password)
except:
	logger.error('Unable to login. Check your credentials.')
	exit(1)

def main():
	proxy = get_proxy(region=str(args.region).upper(),env=str(args.env).upper())
	if proxy:
		print(proxy)
		host = get_host(hostname=args.hostname)
		if host:
			out = zapi.host.update(hostid=host['hostid'],proxy_hostid=proxy['proxyid'])
			if out:
				logger.info('Host \'{0}\'migrated to {1}'.format(host['name'],proxy['host']))
				zapi.user.logout()
				exit(0)
			else:
				logger.error('Failed to update: {0}'.format(out))
		else:
			logger.error('Failed to find exact match for host \'{0}\''.format(args.hostname))
	else:
		logger.error('Failed to find matching proxy: region {0} + env {1}'.format(args.region,args.env))
	zapi.user.logout()
	exit(1)
			

def get_proxy(region=None,env=None):
	proxies = zapi.proxy.get(output=['host','proxyid'],search={'host': region})
	for proxy in proxies:
		if env in proxy['host']:
			return { 'proxyid': proxy['proxyid'], 'host': proxy['host'] }
	logger.error('No proxy found matching your request:\n{0}'.format(proxies))
	return None

def get_host(hostname=None):
	host = zapi.host.get(output=['hostid','name'],filter={'name': hostname})
	if host.__len__() == 1:
		return host[0]
	logger.error('No exact matches found.')
	return None
	

main()
exit(2)
