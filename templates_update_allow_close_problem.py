
import time
from pyzabbix import ZabbixAPI
import csv
from argparse import ArgumentParser

start_time = time.time()
parser = ArgumentParser(description='Verifica e habilita o "Close Problem" manual em templates e hosts no Zabbix')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')
args = parser.parse_args()

if not args.url_api or not args.user or not args.password:
    print("Por favor, forneça a URL da API Zabbix, usuário e senha.")
    exit(1)

try:
    zapi = ZabbixAPI(args.url_api, timeout=600.0)
    zapi.login(args.user, args.password)
    print("Logged")
except Exception as e:
    print("Unable to login:", e)
    exit(1)

def write_templates_and_trigger_ids_to_csv(template_trigger_data, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['Template Name', 'Trigger ID', 'Atualizado']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for data in template_trigger_data:
            writer.writerow({
                'Template Name': data['template_name'],
                'Trigger ID': data['trigger_id'],
                'Atualizado': data['atualizado']
            })

def get_templates_with_disabled_manual_close_triggers(zapi):
        templates = zapi.template.get(output=["templateid", "name"])
        template_trigger_data = []
        for template in templates:
            template_id = template['templateid']
            triggers = zapi.trigger.get(
                output=["triggerid", "description", "manual_close"],
                templateids=[template_id]
            )
            atualizado = "Não" 

            for trigger in triggers:
                trigger_id = trigger['triggerid']
                allow_manual_close_desabilitado = trigger['manual_close'] == "0"

                if allow_manual_close_desabilitado:
                    #zapi.trigger.update(triggerid=trigger_id, manual_close="1")
                    atualizado = "Sim"

            if atualizado == "Sim":
                template_trigger_data.append({
                    'template_name': template['name'],
                    'trigger_id': trigger_id,
                    'atualizado': atualizado
                })

        return template_trigger_data

def main():
        output_file = "updated_templates_with_disabled_manual_close.csv" 
        template_trigger_data = get_templates_with_disabled_manual_close_triggers(zapi)
        if template_trigger_data:
            print("Templates atualizados com pelo menos uma trigger com 'Allow Manual Close' desabilitado:")
            for data in template_trigger_data:
                print(f"Template Name: {data['template_name']}, Trigger ID: {data['trigger_id']}, "
                      f"Atualizado: {data['atualizado']}")
                
            write_templates_and_trigger_ids_to_csv(template_trigger_data, output_file)
            print(f"Resultados escritos em '{output_file}'")
        else:
            print("Nenhum template encontrado com pelo menos uma trigger com 'Allow Manual Close' desabilitado ou atualizado.")

if __name__ == "__main__":
    main()
