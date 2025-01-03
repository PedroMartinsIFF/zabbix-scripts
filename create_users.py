#!/usr/bin/env python
from os import path
from sys import argv, exit
from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
from progressbar import ProgressBar, Percentage, ETA, ReverseBar, RotatingMarker, Timer
from logprint import LogPrint
import csv

parser = ArgumentParser(description = 'This script creates host with given template.')
parser.add_argument('--url', dest = 'url', required = True, help = 'Zabbix server address')
parser.add_argument('--user', dest = 'user', required = True, help = 'Zabbix user')
parser.add_argument('--password', dest = 'password', required = True, help = 'Zabbix password')
parser.add_argument('--no-verbose', dest = 'verbose', action = 'store_false', help = 'Don\'t show any logs on screen')
parser.add_argument('--verbose', dest = 'verbose', action = 'store_true')
parser.set_defaults(verbose=False)
parser.add_argument('--loglevel', dest = 'loglevel', default = 'ERROR', help = 'Debug level. DEBUG/INFO/WARNING/ERROR/CRITICAL')
parser.add_argument('--file', dest = 'file', required = True, help = 'CSV file to read from')
args = parser.parse_args()

TIMEOUT = 15.0
LOGFILE = "/tmp/%s.log" % path.basename(argv[0])
logger = LogPrint(echo=args.verbose, logfile=LOGFILE, loglevel=args.loglevel.upper())

if not path.isfile(args.file):
    logger.error('File not found: {}'.format(args.file))
    exit(1)

try:
    zapi = ZabbixAPI(args.url,timeout=TIMEOUT)
    zapi.login(args.user,args.password)
except Exception as e:
    logger.error("Unable to login: %s" % (e))
    exit(1)


def ug_cache():
    return zapi.usergroup.get(output=['name','usrgrpid'])

def get_usergroupid_from_cache(usergroup):
    for usergroupx in usergroup_cache:
        if usergroupx['name'] == usergroup:
            logger.debug('Usergroup cache hit: {}'.format(usergroupx['name']))
            return usergroupx['usrgrpid']
    return False

def us_cache():
    return zapi.user.get(output=['name','userid'])

def get_userid_from_cache(user):
    for user in user_cache:
        if user['name'] == user:
            logger.debug('User cache hit: {}'.format(user['name']))
            return user['userid']
    return False

def graceful_exit():
    zapi.user.logout()
    logger.info('Success!!')
    exit(0)

def manage_csv(users=None):
    for user in users:
        try:
            if len(user) < 3:
                logger.warning('Usuario aparentemente mal formado ou linha inexistente, ignorando: {}'.format(user))
                continue
            if not user.get('alias',None):
                logger.error('Line without "alias": {}'.format(user))
            if user.get('groups',None):
                user['usergroups'] = [ x.strip() for x in user['groups'].split(',') ]
                del user['groups']
            else:
                logger.error('User without usergroup: {}'.format(user['alias']))
            ## Defaults
            if not user.get('passwd',False):
                user['passwd'] = 'changeme'
            if not user.get('rows_per_page',False):
                user['rows_per_page'] = 50
            if not user.get('refresh',False):
                user['refresh'] = '5m'
            if not user.get('type',False):
                user['refresh'] = '1'
            manage_user(user=user)
        except Exception as e:
            logger.error('Unknown error[0]: {}'.format(e))

def manage_user(user):
    if get_userid_from_cache(user['alias']):
        logger.error('User already exists: {}'.format(user['alias']))
        return False
    else:
        usrgrps = []
        for group in user['usergroups']:
            groupid = get_usergroupid_from_cache(group)
            if groupid:
                usrgrps.append({'usrgrpid': groupid})
            else:
                logger.error('User group not found: {}'.format(group))
                return False
        try:
            zapi.user.create(alias=user['alias'],
                name=user['name'],
                surname=user['surname'],
                passwd=user['passwd'],
                refresh=user['refresh'],
                rows_per_page=user['rows_per_page'],
                type=user['type'],
                usrgrps=usrgrps,
                )
            logger.info('User created: {} || {}'.format(user['alias'],user['usergroups']))
        except Exception as e:
            logger.error('Error when creating user "{}": {}'.format(user['alias'],e))

    
usergroup_cache = ug_cache()
if len(usergroup_cache) > 0:
    logger.info('Usergroups cached: {}'.format(len(usergroup_cache)))

user_cache = us_cache()
if len(user_cache) > 0:
    logger.info('Users cached: {}'.format(len(user_cache)))

if args.file:
    users = list()
    with open(args.file) as csvfile:
        [ users.append(x) for x in csv.DictReader(csvfile, delimiter=',') ]
    manage_csv(users=users)

graceful_exit()
