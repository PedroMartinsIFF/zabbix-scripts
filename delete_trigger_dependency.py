# coding: utf-8

from pyzabbix import ZabbixAPI, ZabbixAPIException
from argparse import ArgumentParser
from logprint import LogPrint

parser = ArgumentParser(description='List active hosts of a group with their registered interfaces')
parser.add_argument('--url-ro', dest='url_ro', help='Zabbix server address RO base')
parser.add_argument('--url-rw', dest='url_rw', help='Zabbix server address RW base')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')
parser.add_argument('--no-verbose', dest='verbose', action='store_false', help='Don\'t show any logs on screen')
parser.add_argument('--verbose', dest='verbose', action='store_true')
parser.add_argument('--proxy', dest='proxy', help='Proxy Name to verify')
parser.add_argument('--logfile', dest='file', help='Filename to save log')
parser.add_argument('--session-verify', dest='session_verify', help='Check ssl session. True or False')
parser.set_defaults(verbose=False, proxy='ALL')
parser.add_argument('--trigger-dependency', dest='trigger', help='Enter initials of trigger name')
parser.add_argument('--loglevel', dest='loglevel', default='ERROR',
					help='Debug level. DEBUG/INFO/WARNING/ERROR/CRITICAL')

args = parser.parse_args()

if args.file:
	logger = LogPrint(echo=args.verbose, logfile=args.file, loglevel=args.loglevel)
else:
	logger = LogPrint(echo=args.verbose, loglevel=args.loglevel)

zapi_ro = ZabbixAPI(args.url_ro, timeout=600.0)
zapi_ro.session.verify = bool(args.session_verify)

try:
	zapi_ro.login(args.user, args.password)
except Exception as e:
	logger.error("Unable to login: %s" % e)
	exit(1)

zapi_rw = ZabbixAPI(args.url_rw, timeout=600.0)
zapi_rw.session.verify = bool(args.session_verify)

try:
	zapi_rw.login(args.user, args.password)
except Exception as e:
	logger.error("Unable to login: %s" % e)
	exit(1)

try:
	if args.proxy == 'ALL':
		get_proxies = zapi_ro.host.get(output=['host'], proxy_hosts=1)
	else:
		get_proxies = zapi_ro.host.get(output=['host'], proxy_hosts=1, filter={'host': args.proxy})
except Exception as e:
	logger.error("Unable to get proxy list: %s" % e)
	exit(1)

for proxy in get_proxies:
	logger.info("Collecting data from proxy {}.".format(proxy['host']))
	
	try:
		get_hosts_from_proxies = zapi_ro.proxy.get(filter={'host': proxy['host']}, selectHosts=['hostid', 'host'])
	except Exception as e:
		logger.error("Unable to get hosts list from proxy: %s" % e)
		continue
	
	try:
		proxy_host_id = zapi_ro.host.get(filter={'host': proxy['host']}, output=['hostid'])[0]['hostid']
	except Exception as e:
		logger.error("Unable to get proxy id: %s" % e)
		continue
	
	try:
		get_trigger_id_from_proxy = zapi_ro.trigger.get(output=['triggerid', 'expression', 'description'],
														hostids=proxy_host_id, functions='nodata')
	except Exception as e:
		logger.error("Unable to get trigger id from proxy: %s" % e)
		continue
	
	for trigger_proxy in get_trigger_id_from_proxy:
		if trigger_proxy['description'].startswith(args.trigger):
			trigger_id_proxy = trigger_proxy['triggerid']
			break
	
	for host in get_hosts_from_proxies[0]['hosts']:
		if host['host'] != proxy['host']:
			try:
				get_triggers_from_hosts = zapi_ro.trigger.get(output=['triggerid', 'expression', 'description'],
															  hostids=host['hostid'], functions='nodata',
															  selectDependencies=['triggerid', 'description'])
				
				for trigger_host in get_triggers_from_hosts:
					update_dependencies = []
					update_trigger_dependencies = False
					for dependency in trigger_host['dependencies']:
						if not dependency['description'].startswith(args.trigger) and len(
								trigger_host['dependencies']) > 1:
							update_dependencies.append({'triggerid': dependency['triggerid']})
							update_trigger_dependencies = True
						elif dependency['description'].startswith(args.trigger) and len(
								trigger_host['dependencies']) == 1:
							update_trigger_dependencies = True
					if update_trigger_dependencies:
						try:
							logger.info("Updating dependencies from trigger {} to host {} [{}]".format(
								trigger_host['triggerid'], host['host'], host['hostid']))
							zapi_rw.trigger.update(triggerid=trigger_host['triggerid'],
												   dependencies=update_dependencies)
						except ZabbixAPIException:
							continue
			except Exception as e:
				logger.error("Unable to get trigger list from hosts: %s" % e)
				continue

logger.info("Process Finished.")
