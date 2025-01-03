#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from os import path, environ
from sys import argv, exit
from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
from logprint import LogPrint
from datetime import datetime, time
import pytz

parser = ArgumentParser(description = 'Enable/Disable hosts by policy')
parser.add_argument('--url', required = True, dest = 'url', help = 'API URL')
parser.add_argument('--user', required = True, dest = 'user', help = 'Username for API login')
parser.add_argument('--api-token', required = True, dest = 'api_token', help = 'API Token for API login')
parser.add_argument('--hostgroup-name', dest='hostgroup_name', default='false', help='Name of hostgroup for search ("_Policy/")')
parser.add_argument('--no-verbose', dest='verbose', action='store_false', help='Dont show any logs on screen')
parser.add_argument('--verbose', dest='verbose', action='store_true')
parser.add_argument('--loglevel', dest='loglevel', default='ERROR', help='Debug level. DEBUG/INFO/WARNING/ERROR/CRITICAL')
args = parser.parse_args()

TIMEOUT = 10
LOGFILE = "/tmp/%s.log" % path.basename(argv[0])
logger = LogPrint(echo=args.verbose, logfile=LOGFILE, loglevel=args.loglevel.upper())

def zapi_login(url, user, api_token):
    try:
        zapi = ZabbixAPI(url)
        logger.debug(f"Logging on {url} as {user} using API token")
        zapi.session.verify = True
        zapi.timeout = 10
        zapi.login(api_token=api_token)
        logger.info(f"Logged on {url} as {user} using API token")
        
        return zapi
    
    except Exception as e:
        logger.error(f"Unable to login on {url} as {user} using API token: {e}")
        exit(1)

#ENABLE HOSTS WITH MASSUPDATE
def enable_hosts(host_ids, obj):
    try:
        result = obj.host.massupdate(hosts=[{'hostid': host['hostid']} for host in host_ids], status=0)
        if 'hostids' in result:
            logger.info(f'Enabled {len(host_ids)} hosts: {host_ids}')

        else:
            logger.error(f'Failed to enable hosts')
    
    except Exception as e:
        logger.error(f'{e}')

#DISABLE HOSTS WITH MASSUPDATE
def disable_hosts(host_ids, obj):
    try:
        result = obj.host.massupdate(hosts=[{'hostid': host['hostid']} for host in host_ids], status=1)
        if 'hostids' in result:
            logger.info(f'Disabled {len(host_ids)} hosts: {host_ids}')

        else:
            logger.error(f'Failed to disable hosts')
    
    except Exception as e:
        logger.error(f'{e}')

#GET HOST FOR HOSTGROUP
def get_hosts_for_hostgroup(group_id, option, obj):
    try:
        host_ids = obj.host.get(output=["hostid"], groupids=group_id)

        if option == 0:
            enable_hosts(host_ids, obj)
        elif option == 1:
            disable_hosts(host_ids, obj)
        else:
            logger.error(f'Invalid option: {option}')

    except Exception as e:
        logger.error(f'Failed to get hosts for hostgroup "{group_id}": {e}')

#LOG INFOS ABOUT HOSTGROUP
def log_info(group_name, policy, day_of_week, time):
    logger.info(f'group_name: {group_name}')
    logger.info(f'policy: {policy}')
    logger.info(f'day_of_week: {day_of_week}')
    logger.info(f'time: {time}')

#DATE INFO
def get_date_info():
    date = datetime.now(pytz.timezone('America/Sao_Paulo'))
    day_of_week = date.isoweekday()
    hour = date.strftime('%H')     #16
    minute = date.strftime('%M')   #30
    time = hour + ':' + minute     #16:30

    return day_of_week, time

#GET HOSTGROUPS INFOS
def get_hostgroups_info(hostgroup_name, obj):
    try:
        for hostgroup in obj.hostgroup.get(output=["groupid", "name"], search={"name" : hostgroup_name}, with_hosts = True):
            group_name = hostgroup['name']
            group_id = hostgroup['groupid']
            group_name_split = group_name.split('-')
            stop = group_name_split[1]      #20:00 / 19:00
            start = group_name_split[3]     #08:00 / 10:00
            policy = group_name_split[-1]   #DAILY / WEEKEND

            try:
                day_of_week, time = get_date_info()

                time = '08:00'

                if policy == 'DAILY' and day_of_week in [1, 2, 3, 4, 5] and time == stop:
                    log_info(group_name, policy, day_of_week, time)
                    option = 1 #disable
                    logger.info(f'Calling get_hosts_for_hostgroup with option = {option}')
                    get_hosts_for_hostgroup(group_id, option, obj)

                elif policy == 'DAILY' and day_of_week in [1, 2, 3, 4, 5] and time == start:
                    log_info(group_name, policy, day_of_week, time)
                    option = 0 #enable
                    logger.info(f'Calling get_hosts_for_hostgroup with option = {option}')
                    get_hosts_for_hostgroup(group_id, option, obj)

                elif policy == 'WEEKEND' and day_of_week in [1, 2, 3, 4, 5, 6, 7] and time == stop:
                    log_info(group_name, policy, day_of_week, time)
                    option = 1 #disable
                    logger.info(f'Calling get_hosts_for_hostgroup with option = {option}')
                    get_hosts_for_hostgroup(group_id, option, obj)

                elif policy == 'WEEKEND' and day_of_week in [1, 2, 3, 4, 5, 6, 7] and time == start:
                    log_info(group_name, policy, day_of_week, time)
                    option = 0 #enable
                    logger.info(f'Calling get_hosts_for_hostgroup with option = {option}')
                    get_hosts_for_hostgroup(group_id, option, obj)
                
                else:
                    logger.info(f'{group_name} do not match any condition at this moment: {time}')
                
            except Exception as e:
                logger.error(f'Failed to check conditions for hostgroup: "{group_name}": {e}')

    except Exception as e:
        logger.error(f'No hostgroup found with name: "{hostgroup_name}"')

#MAIN
def main():
    exit_code = 0
    url = args.url
    user = args.user
    api_token = args.api_token
    hostgroup_name = args.hostgroup_name

    try:
        instance = zapi_login(url, user, api_token)
        get_hostgroups_info(hostgroup_name, obj=instance)

    except Exception as e:
        logger.error(f'ERROR: {e}')
        exit_code = 1

main()
