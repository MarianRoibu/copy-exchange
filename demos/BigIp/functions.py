import requests
import time
from .values import *
import pandas as pd
import json

def monday_request(query):
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization": api_token, "API-Version": "2023-10"}
    data = {"query": query}

    try:
        # Realiza la solicitud POST
        r = requests.post(url=apiUrl, json=data, headers=headers)
        print(f"Respuesta de la solicitud a Monday.com: {r.text}")  # Depuración de la respuesta

        # Verifica si la solicitud fue exitosa (código de estado 200)
        if r.status_code != 200:
            print(f"Error en la respuesta de la API: {r.status_code} - {r.text}")
            return {"errors": [{"message": "Error en la respuesta de la API"}]}

        # Verificar si el contenido de la respuesta está vacío
        if not r.text:
            print("La respuesta está vacía")
            return {"errors": [{"message": "La respuesta está vacía"}]}

        # Intenta decodificar la respuesta JSON
        response_json = r.json()
        
        # Verificar si hay errores en la respuesta JSON
        if "errors" in response_json:
            print("Entro en error_code")

            # Manejar un error de complejidad
            if response_json.get("error_code") == 'ComplexityException':
                print("Entro en complexity error")
                seconds_to_wait = int(response_json["errors"][0]["message"].split()[-2]) + 1
                print(f"Complexity budget exhausted, waiting {seconds_to_wait} segundos")
                
                # Esperar antes de reintentar
                time.sleep(seconds_to_wait + 1)
                return monday_request(query)
            else:
                print(f"ERROR EN MONDAY REQUEST = {response_json}")
                return {"errors": [{"message": "Otro error en la solicitud a Monday.com"}]}
        
        # Si no hubo errores, devuelve la respuesta JSON
        return response_json

    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con la API de Monday.com: {e}")
        return {"errors": [{"message": "Error de conexión con la API"}]}

    except json.JSONDecodeError as e:
        print("Error al decodificar la respuesta JSON")
        return {"errors": [{"message": "Error al decodificar la respuesta JSON"}]}
# def create_item( apiToken):
#     mutation = '''mutation {
#   create_item (board_id: 1722056941, item_name: "item test created") {
#     id
#   }
# }

# '''
#     request = monday_request(mutation, apiToken)
#     return request

def get_item_data(item_id):
    query = '''
             query {
                items (ids: %s) {
                    name
                    column_values {
                    column {
                        id
                        title
                    }
                    id
                    type
                    value
                    text
                    }
                }
                }
             '''%(item_id)
    request = monday_request(query)
    print(f'Request en get_item_data = {request}')
    return request


def create_subitem(item_id, subitem_name):
    query = '''
             mutation {
                    create_subitem (parent_item_id: %s, item_name: "%s") {
                        id
                    }
                    }
             '''%(item_id,
                  subitem_name)
    request = monday_request(query)
    subitem_created_id = request['data']['create_subitem']['id']
    print(f'Request en create_subitem = {request}')
    print(f'Created subitem id = {subitem_created_id}')
    return subitem_created_id

def populate_subitem(created_item,source_language, specific_country_query_values,country,request_value):
    print(f'specific_country_query_values en populate_subitem = {specific_country_query_values}')
    print(f'Subitem id en populate_subitem = {created_item}')
    print(f'Source language en populate_subitem = {source_language}')
    if specific_country_query_values.empty:
        print("El DataFrame está vacío")
        print(f'Created_item en populate_subitem = {created_item}')

        subitem_board_id = get_subitem_board_id(created_item)
        print(f'Created item en populate_subitem = {created_item}')
        print(f'Subitem board id en populate_subitem = {subitem_board_id}')
        population_query = '''mutation {change_multiple_column_values(item_id: %s board_id: %s create_labels_if_missing:true column_values: "{\\"status\\" : \\"Does not exist in country list\\" , \\"men__desplegable__1\\" : \\"%s\\"}") {id}} '''%(created_item,subitem_board_id,country)
        print(f'Population query en populate_subitem = {population_query}')
        request = monday_request(population_query)
        # Manejo de DataFrame vacío
        # Por ejemplo, podrías establecer valores predeterminados, emitir una advertencia, etc.
    else:
        
        if request_value == 'EP':
            target_language = str(specific_country_query_values['Language'].iloc[0])
            translation_requirements = specific_country_query_values['Translation Requirement'].iloc[0]
            additional_translation_requirement = specific_country_query_values['Additional Translation Requirement'].iloc[0] if 'Additional Translation Requirement' in specific_country_query_values else 'None'
            print(f'Target language en else populate_subitem = {target_language,type(target_language)}')
            print(f'Translation requirements en else populate_subitem = {translation_requirements,type(translation_requirements)}')
            print(f'Additional translation requirement en else populate_subitem = {additional_translation_requirement,type(additional_translation_requirement)}')
            subitem_board_id = get_subitem_board_id(created_item)
            population_query = '''mutation { change_multiple_column_values( item_id: %s  board_id: %s  create_labels_if_missing:true  column_values: "{\\"men__desplegable__1\\" : \\"%s\\",\\"men__desplegable6__1\\":\\"%s\\",\\"estado_1__1\\":\\"%s\\", \\"estado_12__1\\":\\"%s\\"}") {id}}'''%(created_item,subitem_board_id,country,target_language,translation_requirements,additional_translation_requirement)
            print(f'Population query en else populate_subitem = {population_query}')
            request = monday_request(population_query)
            print("El DataFrame tiene datos")
            
        if request_value == 'PCT':
            print('Entro en else PCT')
            target_language = str(specific_country_query_values['Language'].iloc[0])
            subitem_board_id = get_subitem_board_id(created_item)
            
            population_query = '''mutation { change_multiple_column_values( item_id: %s  board_id: %s  create_labels_if_missing:true  column_values: "{\\"men__desplegable6__1\\" : \\"%s\\",\\"men__desplegable__1\\":\\"%s\\"}") {id}} '''%(created_item,subitem_board_id,country,target_language)
            request = monday_request(population_query)

            
            pass
    
    pass


def get_board_items(board_id):

    query_init = '''
             query {
                boards(ids: %s) {
                    items_page(limit: 50) {
                    cursor
                    items{
                        name
                        column_values{
                        column{
                            title
                            id
                        }
                        text
                        }
                    }
                    }
                }
                }
             '''%(board_id)
    request = monday_request(query_init)
    
    # Extraer los elementos
    items = request['data']['boards'][0]['items_page']['items']
    print(f"esto son los items {request['data']['boards']}")
    data = []
    for item in items:
        row = {'name': item['name']}
        for column_value in item['column_values']:
            row[column_value['column']['title']] = column_value['text']
        data.append(row)

    # Crear el DataFrame
    items_df = pd.DataFrame(data)
    cursor = request['data']['boards'][0]['items_page']['cursor']
    
    while cursor!= None:
        query_cursor = '''
                 query {
                    next_items_page(limit:50,cursor:"%s"){
                        cursor
                        items{
                        name
                        column_values{
                            column{
                            title
                            id
                            }
                            text
                        }
                        }
                    }
                    }
                '''%(cursor)
        request = monday_request(query_cursor)
        # print(f'Request en get_board_items_cursor = {request}')
        # print(f"Request cursor en get_board_items_cursor = {request['data']}")
        cursor = request['data']['next_items_page']['cursor']
        # Procesar los nuevos elementos
        new_items = request['data']['next_items_page']['items']
        new_data = []
        for item in new_items:
            new_row = {'name': item['name']}
            for column_value in item['column_values']:
                new_row[column_value['column']['title']] = column_value['text']
            new_data.append(new_row)

        # Añadir los nuevos datos al DataFrame existente
        new_items_df = pd.DataFrame(new_data)
        items_df = pd.concat([items_df, new_items_df], ignore_index=True)
    
    
    # print(f'Cursor = {cursor}')
    
    # print(f'DAtaframe = {items_df.head(5)}')
    
    # print(f'Request en get_board = {request}')
    return items_df
    
    
def get_subitem_board_id(subitem_id):
    query = '''
                    query{
                        items(ids: %s){board{id}}}
                    '''%(subitem_id)
    print(f'Query en get_subitem_board_id = {query}')
    subitem_board_id = monday_request(query)['data']['items'][0]['board']['id']
    print(f'Get Subitem board id = {subitem_board_id}')
    return subitem_board_id

def change_status_trigger(Pulse_id,board_id):
    population_query ='''
                        mutation {
                            change_multiple_column_values(
                                item_id: %s 
                                board_id: %s 
                                create_labels_if_missing:true 
                                column_values: "{\\"status__1\\" : \\"Created\\" 
                                }") {id}} '''%(Pulse_id,board_id)
    monday_request(population_query)
