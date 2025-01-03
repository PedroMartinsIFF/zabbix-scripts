#!/usr/bin/python

from os import path
from sys import argv, exit
from logprint import LogPrint
from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
import csv
from progressbar import ProgressBar, Percentage, ETA, ReverseBar, RotatingMarker, Timer

parser = ArgumentParser(description = 'Mass Create Hostgroups')
parser.add_argument('--url', required = True, dest = 'url', help = 'Zabbix server address')
parser.add_argument('--user', required = True, dest = 'user', help = 'Zabbix user')
parser.add_argument('--password', required = True, dest = 'password', help = 'Zabbix password')
parser.add_argument('--no-verbose', dest = 'verbose', action = 'store_false', help = 'Don\'t show any logs on screen')
parser.add_argument('--verbose', dest = 'verbose', action = 'store_true')
parser.set_defaults(verbose=False)
parser.add_argument('--loglevel', dest = 'loglevel', default = 'ERROR', help = 'Debug level. DEBUG/INFO/WARNING/ERROR/CRITICAL')
parser.add_argument('--file', required = True, dest = 'file', help = 'List os hostgroup names')

args = parser.parse_args()


TIMEOUT = 10.0
LOGFILE = "/tmp/%s.log" % path.basename(argv[0])
logger = LogPrint(echo=args.verbose, logfile=LOGFILE, loglevel=args.loglevel.upper())

try:
    zapi = ZabbixAPI(args.url,timeout=TIMEOUT)
    zapi.login(args.user,args.password)
except Exception as e:
    logger.error("Unable to login: %s" % (e))
    exit(1)

f = csv.reader(open(args.file), delimiter=';')

list_groups = []

for group in f:
    zapi.hostgroup.create(name=group[0])

zapi.user.logout()
