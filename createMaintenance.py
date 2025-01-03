#!/usr/bin/env python
import re
from argparse import ArgumentParser
from os import path
from sys import argv, exit

from logprint import LogPrint
from pyzabbix import ZabbixAPI


parser = ArgumentParser(description='This script creates maintenance for multiple hosts.')
parser.add_argument('--url', dest='url', required=True, help='Zabbix server address')
parser.add_argument('--user', dest='user', required=True, help='Zabbix user')
parser.add_argument('--password', dest='password', required=True, help='Zabbix password')
parser.add_argument('--no-verbose', dest='verbose', action='store_false', help="Don't show any logs on screen")
parser.add_argument('--verbose', dest='verbose', action='store_true')
parser.set_defaults(verbose=False)
parser.add_argument('--loglevel', dest='loglevel', default='ERROR',
                    help='Debug level. DEBUG/INFO/WARNING/ERROR/CRITICAL')
parser.add_argument('--description', dest='description', required=True, help='Description of maintenance period')
parser.add_argument('--start-date', dest='startdate', required=True, help='Start or maintenance period: yyyymmdd')
parser.add_argument('--start-time', dest='starttime', required=True, help='Time of maintenance start: 1500')
parser.add_argument('--duration', dest='duration', required=True, help='Duration in hours, up to 720')
parser.add_argument('--hosts', dest='hosts', required=True, help='List of hosts, separated by comma')
args = parser.parse_args()

TIMEOUT = 15.0
LOGFILE = "/tmp/%s.log" % path.basename(argv[0])
logger = LogPrint(echo=args.verbose, logfile=LOGFILE, loglevel=args.loglevel.upper())

if int(args.duration) > int(720):
    logger.error('Value for --duration bigger than 720: {}'.format(args.duration))
    exit(1)

try:
    zapi = ZabbixAPI(args.url, timeout=TIMEOUT)
    zapi.login(args.user, args.password)
except Exception as e:
    logger.error("Unable to login: %s" % (e))
    sentry_sdk.capture_exception(e)
    exit(1)


def graceful_exit():
    zapi.user.logout()
    logger.info('Success!!')
    exit(0)


def host_has_invalid_chars(name):
    if re.search('[^a-zA-Z0-9\s\.\-\_]', name):
        return True
    return False


def host_replace_invalid_chars(name):
    # Alphanumerics, spaces, dots, dashes and underscores are allowed
    host = re.sub('([^a-zA-Z0-9\s\.\-\_])', '_', name)
    return host, name


if len(args.hosts) > 0:
    hosts = []
    searchHosts = args.hosts.split(",")
    for host in searchHosts:
        searchHost = host.strip()
        h = zapi.host.get(output=['name'], filter={'name': searchHost})
        if len(h) == 1:
            hosts.append(searchHost)
        else:
            logger.warning('Ignoring host not found: "{}"'.format(searchHost))
    try:
        logger.info('Hosts informed: {}'.format(len(searchHosts)))
        logger.info('Hosts Found: {}'.format(len(hosts)))
        result = zapi.globo.createMaintenance(description=args.description, host=args.hosts, start_date=args.startdate, start_time=args.starttime, duration_in_hour=args.duration)
        logger.info(result)
    except Exception as e:
        logger.error('Error when creating maintenance: {}'.format(e))

graceful_exit()
