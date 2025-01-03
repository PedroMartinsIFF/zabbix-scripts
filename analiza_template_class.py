import yaml
import json
import re
import jsonpath_ng as jp
import langid
import logging
from os import path

PATH_YAML = "../template.yaml"
PATH_JSON = "../template.json"
PATH_LOGS = "logs/analiza_template.log"

SCORE = 0

logger = logging.getLogger(__name__)
logging.basicConfig(filename='logs/analiza_template.log', encoding='utf-8', level=logging.DEBUG)

def increase_score():
    global SCORE
    SCORE += 1
    logging.info('Increasing score by 1')
    

class Template:
        def __init__(self,template):
            for key,value in template.items():
                setattr(self,key,value)

        def get_templates(self):
            return self.templates
        
        def get_title(self):
            return self.templates[0]['template']
        
        def get_macros(self):
            return self.templates[0]['macros']

def convert_yaml_to_json():
    logging.debug('Convertendo do arquivo yaml para json')

    # Read the YAML file
    try:
        with open(PATH_YAML, "r") as yaml_in:
            yaml_object = yaml.safe_load(yaml_in)  # yaml_object will be a list or a dict
    except:
        logging.error('Template nao encontrado')

    # Write the JSON data to a file
    try:
        with open(PATH_JSON, "w") as json_out:
            json.dump(yaml_object, json_out, indent=2)
    except:
        logging.error('Erro ao converter template para json')

def score_title(instance):

    title = instance.get_title()
    #Verifica se o Titulo inicia com "Template"
    if title.startswith('Template'):
        logging.debug('Titutlo inicia com "Template"')

    #Verifica se o Titulo está dentro do pattern
    pattern = r'^(.+)\.(.+)$'
    match = re.match(pattern, title)
    if match:
        logging.debug('Tempalte dentro do padrão')
    else:
        logging.debug("Template fora do padrão")
    
def score_item_tag(instance):

    templates = instance.get_templates()

    #Verifica se todo item tem a tag Application
    items = templates[0]['items']
    for item in items:
        tags = item['tags']
        for dict_ in tags:
            if 'Application' in dict_.values():
                continue
            else:
                logging.debug("Nem todo item possui a tag Application")

def score_trigger_expression(instance):

    templates = instance.get_templates()
    items=templates[0]['items']
    for item in items:
        triggers = item['triggers']
        for dict_ in triggers:
            expression = dict_.get('expression')
            recovery_expression = dict_.get('recovery_expression')

            #Verifica se todas as triggers tem recovery expression
            if recovery_expression is None:
                trigger_name = dict_.get('name')
                logging.debug(f'{trigger_name} |  Sem recovery expression')

            #Verifica se a expression possui uma macro
            pattern = r'\{\$.*?\}'
            if re.search(pattern, expression):
                logging.debug('Expression is using macro')
            else:
                logging.debug('Expression not using macro')
            

def score_macros(instance):

    macros = instance.get_macros()

    for dict_ in macros:
        description = dict_.get('description')
        macro = dict_.get('macro')

        #Verifica se toda macro tem description
        if description is None:
            logging.debug(f'{macro} | Sem descrição')

        #Verifica se toda macro atende o padrão
        pattern = r'\{\$[A-Z]+\.[A-Z]+\.[A-Z]+\}'
        match = re.match(pattern, macro)
        if match:
            logging.debug(f'Macro {macro} dentro do padrão')
        else:
            logging.debug(f"Macro {macro} fora do padrão")

def main():
    #convert_yaml_to_json()
    with open(PATH_JSON, "r") as template_json:
        template = json.load(template_json)
    
    instance = Template(template['zabbix_export'])
    score_title(instance)
    score_item_tag(instance)
    score_trigger_expression(instance)
    score_macros(instance)

main()
