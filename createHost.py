#!/usr/bin/env python3
from os import path
from sys import argv, exit
from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
from logprint import LogPrint
import csv
import re
parser = ArgumentParser(description = 'This script creates host with given template.')
parser.add_argument('--url', dest = 'url', required = True, help = 'Zabbix server address')
parser.add_argument('--user', dest = 'user', required = True, help = 'Zabbix user')
parser.add_argument('--password', dest = 'password', required = True, help = 'Zabbix password')
parser.add_argument('--no-verbose', dest = 'verbose', action = 'store_false', help = 'Don\'t show any logs on screen')
parser.add_argument('--verbose', dest = 'verbose', action = 'store_true')
parser.set_defaults(verbose=False)
parser.add_argument('--recreate', dest = 'recreate', action = 'store_true', help = 'Force host recreation if already exists (delete+create)')
parser.set_defaults(recreate=False)
parser.add_argument('--update', dest = 'update', action = 'store_true', help = 'Force host update')
parser.set_defaults(update=False)
parser.add_argument('--loglevel', dest = 'loglevel', default = 'ERROR', help = 'Debug level. DEBUG/INFO/WARNING/ERROR/CRITICAL')
parser.add_argument('--file', dest = 'file', required = True, help = 'File to read from')
parser.add_argument('--filetype', dest = 'filetype', default = 'json', required = False, help = 'File type, json(default) or csv')
parser.add_argument('--filedelimiter', dest = 'filedelimiter', default = ';', required = False, help = 'File type delimiter, comma (",") or semi-colon (";")')
args = parser.parse_args()

TIMEOUT = 15.0
LOGFILE = "/tmp/%s.log" % path.basename(argv[0])
logger = LogPrint(echo=args.verbose, logfile=LOGFILE, loglevel=args.loglevel.upper())

if args.recreate and args.update:
    logger.error('--recreate and --update are mutually exclusive')
    exit(1)

if not path.isfile(args.file):
    logger.error('File not found: {}'.format(args.file))
    exit(1)

try:
    zapi = ZabbixAPI(args.url,timeout=TIMEOUT)
    zapi.login(args.user,args.password)
except Exception as e:
    logger.error("Unable to login: %s" % (e))
    exit(1)

# Cache de hosts
def host_cache():
    return zapi.host.get(output=['name','host'])

def get_hostid_from_cache(host_field,fields=['host'],cache=None):
    try:
        len(cache['hosts'])
    except Exception:
        cache['hosts'] = host_cache()
    for field in fields:
        if field != 'host' and field != 'name':
            logger.error('field can be only "host" or "name". You used "{}"'.format(field))
            exit(1)
        for hostx in cache['hosts']:
            if hostx[field] == host_field:
                logger.debug('Host cache hit: {}'.format(hostx[field]))
                return hostx['hostid']
    return False

# Cache de hostgroups
def hg_cache():
    return zapi.hostgroup.get(output=['name', 'groupid'])

def get_hostgroupid_from_cache(name,cache=None):
    try:
        len(cache['hostgroups'])
    except Exception:
        cache['hostgroups'] = hg_cache()
    for hgx in cache['hostgroups']:
        if ( hgx['name'] == name ):
            logger.debug('Hostgroup cache hit: {}'.format(name))
            return hgx['groupid']
    return False

# Cache de templates
def tpl_cache():
    return zapi.template.get(output=['name', 'templateid'])

def get_templateid_from_cache(name,cache=None):
    try:
        len(cache['templates'])
    except Exception:
        cache['templates'] = tpl_cache()
    for tplx in cache['templates']:
        if ( tplx['name'] == name ):
            logger.debug('Template cache hit: {}'.format(name))
            return tplx['templateid']
    return False

# Cache de proxies
def prx_cache():
    return zapi.proxy.get(output=['proxyid','host'])

def get_proxyid_from_cache(name,cache=None):
    try:
        len(cache['proxies'])
    except Exception:
        cache['proxies'] = prx_cache()
    try:
        int(name[-1])
        # Se ainda estamos aqui, entao eh um proxy especifico
        for prx in cache['proxies']:
            if ( prx['host'] == name ):
                logger.debug('Proxy cache hit: {}'.format(name))
                return prx['proxyid']
        return False
    except Exception as e:
        # Se estamos aqui, entao eh um grupo de proxy, onde eu sorteio um dos possiveis
        found = [ prx for prx in cache['proxies'] if name in prx['host'] ]
        if len(found) > 0:
            import random
            prx = found[random.randint(0,(len(found)-1))]
            logger.debug('Random proxy hit: {}'.format(prx['host']))
            return prx['proxyid']
        else:
            logger.error('Proxy "{}"" not found'.format(name))
            return False

def manage_csv(cache=None,hosts=None):
    for host in hosts:
        print(host['macros'])
        try:
            if len(host) < 3:
                logger.warning('Host aparentemente mal formado ou linha inexistente, ignorando: {}'.format(host))
                continue
            host['groups'] = [ x.strip() for x in host['groups'].split(',') ]

            if host.get('templates', False):
                host['templates'] = [ x.strip() for x in host['templates'].split(',') ]
            else:
                if host.get('template', False):
                    host['templates'] = [host['template']] # compatibilidade (por enquanto)
                    del host['template']
                else:
                    logger.error('Nenhum template informado para host "{}"'.format(host))
                    continue
            if host.get('macros', False):
                host['macros'] = eval(host['macros'])
            manage_host(cache=cache,host=host)
        except Exception as e:
            logger.error('Unknown error[0]: {}'.format(e))

def manage_json(cache=None,hosts=None):
    """
    Criar host
    """
    for host in hosts:
        try:
            if host.startswith('#') or len(host) < 10:
                continue
            host = eval(host)
            manage_host(cache=cache,host=host)
        except Exception as e:
            logger.error('Malformed line: {0}'.format(e))
            continue

def graceful_exit():
    zapi.user.logout()
    logger.info('Success!!')
    exit(0)

def host_has_invalid_chars(name):
    if re.search('[^a-zA-Z0-9\s\.\-\_]',name):
        return True
    return False

def host_replace_invalid_chars(name):
    #Alphanumerics, spaces, dots, dashes and underscores are allowed
    host = re.sub('([^a-zA-Z0-9\s\.\-\_])','_',name)
    return host,name

def manage_host(cache=None,host=None):
    tmp_name = host.get('name', host.get('host', False))
    # Verifico se host ja existe, apenas se nao for para substituir
    if not args.recreate and not args.update:
        if get_hostid_from_cache(cache=cache,host_field=tmp_name,fields=['host','name']):
            logger.warning('Host ja existe, ignorando: {}'.format(tmp_name))
            return False

    # Traduzo template para templateid
    templates = []
    t_error = False
    for t in host['templates']:
        templateid = get_templateid_from_cache(cache=cache,name=t)
        if not templateid:
            logger.error('Template not found: "{}"'.format(t))
            t_error = True
        else:
            templates.append({'templateid': templateid})
    if t_error:
        return False

    # Traduzo group para groupid
    groups = []
    g_error = False
    for g in host['groups']:
        groupid = get_hostgroupid_from_cache(cache=cache,name=g)
        if not groupid:
            logger.error('Hostgroup not found: "{}"'.format(g))
            g_error = True
        else:
            groups.append({'groupid': groupid})
    if g_error:
        return False

    # Traduzo proxy
    proxyid = get_proxyid_from_cache(cache=cache,name=host['proxy'])
    if not proxyid:
        logger.error('Proxy "{}" not found'.format(host['proxy']))
        return False

    params = {
        'templates': templates,
        'groups': groups,
        'proxy_hostid': proxyid,
    }
    params['status'] = host.get('status', 0) # Status = o que for especificado, ou ativo (default)
    if host.get('ip', False):
        if host.get('host', False):
            params['host'] = host['host'].strip()
        else:
            params['host'] = host['ip']
        params['interfaces'] = [ {'type': '1', 'useip': '1', 'ip': host['ip'], 'main': '1', 'dns': '', 'port': '10050'}, {'type': '2', 'useip': '1', 'ip': host['ip'], 'main': '1', 'dns': '','details' : {'version' : 2, 'bulk' : 1,'community' : '{$SNMP_COMMUNITY}'}, 'port': '161'} ]
    else:
        params['host'] = host['host'].strip()
        params['interfaces'] = [ {'type': '1', 'useip': '0', 'dns': host['host'], 'main': '1', 'ip': '', 'port': '10050'}, {'type': '2', 'useip': '0', 'dns': host['host'], 'main': '1', 'ip': '','details' : {'version' : 2, 'bulk' : 1,'community' : '{$SNMP_COMMUNITY}'}, 'port': '161'} ]
    if host.get('name', False):
        params['name'] = host['name']
    if host.get('macros', False):
        params['macros'] = host['macros']

    if host_has_invalid_chars(params['host']):
        params['host'],params['name'] = host_replace_invalid_chars(params['host'])

    try:
        hostid = get_hostid_from_cache(cache=cache,fields=['name','host'],host_field=tmp_name)
        if hostid: # se o host existe..
            if args.recreate: # recrio
                try:
                    zapi.globo.deleteMonitors(params.get('name', params['host']))
                    out = zapi.host.create(**params)
                    logger.info('Success: created host "{}", hostid "{}", templates "{}" and proxy "{}"'.format(params['host'],out['hostids'][0],host['templates'],host['proxy']))
                    return True
                except Exception as f:
                    logger.error('Erro[2] desconhecido criar host "{}": {}'.format(params['host'],f))
                    return False
            elif args.update: # atualizo
                try:
                    params['hostid'] = hostid
                    interfaces = zapi.host.get(selectInterfaces='extend',output=['hostid'],hostids=[hostid])
                    params['interfaces'][0]['interfaceid'] = interfaces[0]['interfaces'][0]['interfaceid']
                    params['interfaces'][0]['hostid'] = interfaces[0]['interfaces'][0]['hostid']
                    params['interfaces'][1]['interfaceid'] = interfaces[0]['interfaces'][1]['interfaceid']
                    params['interfaces'][1]['hostid'] = interfaces[0]['interfaces'][1]['hostid']
                    zapi.host.update(**params)
                    logger.info('Success: updated host "{}", hostid "{}", templates "{}" and proxy "{}"'.format(params['host'],params['hostid'],host['templates'],host['proxy']))
                    return True
                except Exception as g:
                    logger.error('Erro[3] desconhecido criar host "{}": {}'.format(params['host'],g))
                    return False
            else: # Ou nada. Esse erro ja eh tratado no comeco da funcao.
                logger.warning('Host ja existe: "{}"'.format(params['host']))
                return True
        out = zapi.host.create(host=params['name'],interfaces=params['interfaces'],groups=params['groups'],proxy_hostid=params['proxy_hostid'],macros=params['macros'])
        logger.info('Success: host "{}", hostid "{}", templates "{}" and proxy "{}"'.format(params['host'],out['hostids'][0],host['templates'],host['proxy']))
        return True
    except Exception as e:
        logger.error('Erro[1] desconhecido criar host "{}": {}'.format(params['host'],e))
        return False

cache = {}
cache['templates'] = tpl_cache()
if len(cache['templates']) > 0:
    logger.info('Templates cached: {}'.format(len(cache['templates'])))

cache['hostgroups'] = hg_cache()
if len(cache['hostgroups']) > 0:
    logger.info('Hostgroups cached: {}'.format(len(cache['hostgroups'])))

cache['hosts'] = host_cache()
if len(cache['hosts']) > 0:
    logger.info('Hosts cached: {}'.format(len(cache['hosts'])))

cache['proxies'] = prx_cache()
if len(cache['proxies']) > 0:
    logger.info('Proxies cached: {}'.format(len(cache['proxies'])))

if args.file and args.filetype == 'json':
    with open(args.file) as f:
        hosts = tuple(f.readlines())
    manage_json(cache=cache,hosts=hosts)
elif args.file and args.filetype == 'csv':
    hosts = list()
    with open("input_format/createHost_telefonia.csv", mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=args.filedelimiter)
        [ hosts.append(row) for row in csv_reader ]
    manage_csv(cache=cache,hosts=hosts)
else:
    logger.error('Specify --file!')

graceful_exit()
