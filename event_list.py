import datetime
import csv
from zabbix_api import ZabbixAPI, Already_Exists

import argparse
from inspect import signature

class ListEvents():
    def __init__(self):
        parser = argparse.ArgumentParser(description='List events by hostgroupid')
        parser.add_argument('--url', help='URL do Zabbix')
        parser.add_argument('--username', help='Usuário do Zabbix')
        parser.add_argument('--password', help='Senha do Zabbix')
        parser.add_argument('--hostgroupid', help='ID do Grupo de Hosts, exemplo 50')
        parser.add_argument('--date_init', help='Dia de inicio exemplo: 01/04/2021')
        parser.add_argument('--date_finish', help='Dia de fim exemplo: 30/04/2021')

        subparsers = parser.add_subparsers()

        for name in dir(self):
            ''' Get name that not start with underscore'''
            if not name.startswith('_'):
                sub_command = subparsers.add_parser(name)
                ''' Get other functions on class '''
                method = getattr(self, name)
                ''' Get parameters of the each functions on other class '''
                parameters = signature(method).parameters.keys()
                ''' For each parameters add with argument on application in sub commands'''
                for param in parameters:
                    sub_command.add_argument(param)
                sub_command.set_defaults(func=method, argnames=parameters)

        self.args = parser.parse_args()

        self.url = self.args.url
        self.username = self.args.username
        self.password = self.args.password
        self.hostgroupid = self.args.hostgroupid
        self.date_init = self.args.date_init
        self.date_finish = self.args.date_finish

        try:
            param = self.args
            callargs = [getattr(param, name) for name in param.argnames]
            self._zbx_login()
            try:
                return self.args.func(*callargs)
            finally:
                pass
        except Exception as err:
            print(0)
            print(err)

    def _zbx_login(self):
        try:
            self.zapi = ZabbixAPI(self.url, validate_certs=False)
            self.zapi.login(user=self.username, password=self.password)
            print('Conected to Zabbix API')
        except Exception as err:
            print('Falha ao conectar na api: %s' %err)

    def _date_to_timestamp(self, date):
        '''
        Função que converte static em unix timestamp
        '''
        return int(datetime.datetime.strptime(date, '%d/%m/%Y').strftime('%s'))

    def _timestamp_to_date(self, timestamp):
        '''
        Função que converte unix timestamp em static e hora
        '''
        return datetime.datetime.fromtimestamp(int(timestamp)).strftime('%d/%m/%Y %H:%M')

    def _get_hostids_by_hostgroupid(self, hostgroupid):
        hosts = self.zapi.host.get({
            'output': [],
            'groupids': hostgroupid
        })
        hostids = [host['hostid'] for host in hosts]
        return hostids

    def _get_events_by_hostsids(self, hostids, time_from, time_till):
        events = self.zapi.event.get({
            "hostids": hostids,
            "output": ['objectid','value', 'r_eventid', 'clock', 'severity'],
            "time_from": time_from,
            "time_till": time_till,
            "selectHosts": ['host', 'name']
        })
        return events

    def _get_recovery_event(self, event_id):
        '''
        Função que retorna o clock de recuperação de um evento com base no eventid
        '''
        event_get = self.zapi.event.get(
            {"output": ['clock'], "eventids": str(event_id)})[0]['clock']
        return int(event_get)

    def _get_clock_r_eventid(self, list_events, r_eventid):
        for event in list_events:
            if event['eventid'] == r_eventid:
                return event['clock']

    def _get_trigger_name(self, triggerid):
        trigger = self.zapi.trigger.get({
            "output": ['description'],
            "triggerids": triggerid,
            "expandDescription": 1,
        })[0]['description']
        return trigger

    def extract_list(self):
        time_from = self._date_to_timestamp(self.date_init)
        time_till = self._date_to_timestamp(self.date_finish)
        with open('lista_eventos.csv', 'w', newline='',encoding='utf-8') as file:
            write = csv.writer(file, delimiter=';')
            header = ['Hostname', 'Visible name', 'Event ID', 'Status', 'Data do Evento', 'Data da recuperacao', 'Duracao', 'Trigger ID', 'Trigger Name', 'R EVENT ID']
            write.writerow(header)
            hostids = self._get_hostids_by_hostgroupid(self.hostgroupid)
            events = self._get_events_by_hostsids(hostids=hostids, time_from=time_from, time_till=time_till)
            for event in events:
                host = event['hosts'][0]['host']
                name = event['hosts'][0]['name']
                eventid = event['eventid']
                clock = int(event['clock'])
                event_date = self._timestamp_to_date(clock)
                event_r_eventid = event['r_eventid']
                event_objectid = event['objectid']
                event_trigger_description = self._get_trigger_name(triggerid=event_objectid)
                if event_r_eventid != '0':
                    #print('Entrou no r_event_id')
                    clock_r_event = self._get_clock_r_eventid(events, event_r_eventid)
                    if clock_r_event is None:
                        clock_r_event = self._get_recovery_event(event['eventid'])
                    if int(clock_r_event) < int(clock):
                        time_duration = int(clock) - int(clock_r_event)
                    else:
                        time_duration = int(clock_r_event) - int(clock)
                    time_duration = datetime.timedelta(seconds=time_duration)
                    event_recovery = self._timestamp_to_date(clock_r_event)
                    status = 'RESOLVIDO'
                    line = [host, name, eventid, status, event_date , event_recovery, time_duration, event_objectid, event_trigger_description, event_r_eventid]
                    print(host, name, eventid, status, event_date , event_recovery, time_duration, event_objectid, event_trigger_description, event_r_eventid, sep=';')
                    write.writerow(line)
                if event_r_eventid == '0' and event['value'] == '1':
                    status = 'PROBLEMA'    
                    event_recovery = ''
                    time_duration = ''  
                    line = [host, name, eventid, status, event_date , event_recovery, time_duration, event_objectid, event_trigger_description, event_r_eventid]
                    print(host, name, eventid, status, event_date , event_recovery, time_duration, event_objectid, event_trigger_description, event_r_eventid, sep=';')
                    write.writerow(line) 
        
if __name__ == "__main__":
    ListEvents()



"""
python3 event_list.py --url https://api.zabbix.staging.globoi.com --username backoffice.api --password globocom --hostgroupid 2367 --date_init "01/04/2021" --date_finish "06/05/2021" extract_list
"""
