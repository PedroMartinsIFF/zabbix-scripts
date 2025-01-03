#!/usr/bin/env python

from argparse import ArgumentParser
from logprint import LogPrint
from math import ceil
from os import path
from pyzabbix import ZabbixAPI
from sys import argv, exit
from utils import ZabbixUtils

parser = ArgumentParser(description='This script creates host with given template.')
parser.add_argument('--url', dest='url', required=True, help='Zabbix server address')
parser.add_argument('--logintype', dest='logintype', required=False,
                    help='Login can be arg|env. DEFAULT: `arg`: Use --user and --password. If set to `env`, reads '
                         'environment ldap_user and ldap_pass')
parser.set_defaults(logintype='arg')
parser.add_argument('--user', dest='user', required=False, help='Zabbix user. Mandatory if --logintype=arg.')
parser.add_argument('--password', dest='password', required=False,
                    help='Zabbix password. Mandatory if --logintype=arg.')
parser.add_argument("--no-verbose", dest='verbose', action='store_false', help='Don\'t show any logs on screen')
parser.add_argument('--verbose', dest='verbose', action='store_true')
parser.set_defaults(verbose=False)
parser.add_argument('--loglevel', dest='loglevel', default='ERROR',
                    help='Debug level. DEBUG/INFO/WARNING/ERROR/CRITICAL')
parser.add_argument('--csvfile', dest='csvfile', required=False, help='CSV file with columns called "name" and "proxy"')
args = parser.parse_args()

TIMEOUT = 15.0
LOGFILE = "/tmp/%s.log" % path.basename(argv[0])
logger = LogPrint(echo=args.verbose, logfile=LOGFILE, loglevel=args.loglevel.upper())

try:
    zapi = ZabbixAPI(args.url, timeout=TIMEOUT)
    xpto = ZabbixUtils(zapi=zapi, logger=logger, args=args)
    xpto.zabbix_login()
except Exception as e:
    logger.error("Unable to login: %s" % (e))
    exit(1)

def process_hosts():
    hosts = ZabbixUtils.convert_csv_to_dict_list(file=args.csvfile, logger=logger)
    logger.info('Hosts a serem processados: {}'.format(len(hosts)))
    proxies = {}
    for host in hosts:
        if not proxies.get(host['proxy'], False):
            proxies[host['proxy']] = {}
            proxies[host['proxy']]['hosts'] = []
        hostid = xpto.get_hostid_from_cache(host.get('name', False))
        if hostid:
            proxies[host['proxy']]['hosts'].append(hostid)
        else:
            logger.warning('Host not found: {}'.format(host))
    for proxy in proxies:
        logger.info('Processing proxy {}, with {} hosts'.format(proxy, len(proxies[proxy]['hosts'])))
        maxval = int(ceil(len(proxies[proxy]['hosts']) / 100 + 1))
        i = 0
        for i in range(maxval):
            if len(proxies[proxy]['hosts']) == 0:
                break
            hosts = proxies[proxy]['hosts'][:100]
            del proxies[proxy]['hosts'][:100]
            xpto.host_massupdate_proxy(hostids=hosts, proxyname=proxy)


process_hosts()
xpto.zabbix_graceful_logout()
