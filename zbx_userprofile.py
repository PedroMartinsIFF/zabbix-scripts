#!/usr/bin/python
from getpass import getpass
from os import path
from sys import argv, exit
from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
from logprint import LogPrint

parser = ArgumentParser(description = 'Change password across multiple Zabbix Servers')
parser.add_argument('--url', dest = 'url', help = 'Zabbix server address')
parser.add_argument('--user', dest = 'user', help = 'Zabbix user')
parser.add_argument('--password', dest = 'password', help = 'Zabbix password')
parser.add_argument('--no-verbose', dest = 'verbose', action = 'store_false', help = 'Don\'t show any logs on screen')
parser.add_argument('--verbose', dest = 'verbose', action = 'store_true')
parser.set_defaults(verbose=False)
parser.add_argument('--loglevel', dest = 'loglevel', default = 'ERROR', help = 'Debug level. DEBUG/INFO/WARNING/ERROR/CRITICAL')

parser.add_argument('--new-password',required = False, dest = 'newpassword', help = 'New Zabbix password')
args = parser.parse_args()

TIMEOUT = 3.0
LOGFILE = "/tmp/%s.log" % path.basename(argv[0])
logger = LogPrint(echo=args.verbose, logfile=LOGFILE, loglevel=args.loglevel.upper())


newpassword = args.newpassword
if ( not args.newpassword ):
	print("Enter new password: ")
	newpassword = getpass()

envs = [
	'http://zabbix.dev.globoi.com',
	'http://zabbix.qa01.globoi.com',
	'http://zabbix.staging.globoi.com',
	'http://zabbix.tsuru.globoi.com',
	'http://zabbix.globoi.com',
]
for url in envs:
	try:
		zapi = ZabbixAPI(url,timeout=TIMEOUT)
		zapi.login(args.user,args.password)
	except Exception as e:
		logger.error("Unable to login: %s" % (e))
	logger.debug("Changing %s password in %s" % (args.user,url))
	logger.print_json(zapi.user.updateprofile(alias=args.user,passwd=newpassword))
zapi.user.logout()
