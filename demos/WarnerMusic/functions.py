import requests
import time
import json
import pandas as pd
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

def monday_request(query, apiToken):
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization": apiToken, "API-Version": "2023-10"}
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
    

# def create_item(apiToken):
#     mutation = '''mutation {
# create_item (board_id: 1735985410, item_name: "item test created") {
#     id
# }
# }

# '''
#     request = monday_request(mutation, apiToken)
#     return request

# def get_connected_ids(item_id, apiToken):
#     query = '''query {
#                         items(ids: %s) {
#                             name
#                             column_values {
#                             id
#                             text
#                             value
#                             ... on BoardRelationValue {
#                                 linked_item_ids
#                                 linked_items {
#                                 id
#                                 name
#                                 column_values {
#                                     id
#                                     text
#                                     value
#                                     ... on BoardRelationValue {
#                                     linked_item_ids
#                                     linked_items {
#                                         id
#                                         name
#                                         column_values {
#                                             id
#                                             text
#                                             value
#                                             ... on BoardRelationValue {
#                                             linked_item_ids
#                                             linked_items {
#                                                 id
#                                                 name
#                                             }
#                                             }
#                                         }
#                                     }
#                                     }
#                                 }
#                                 }
#                             }
#                             }
#                         }
#                         }
#                         ''' % item_id
#     request = monday_request(query, apiToken)
#     column_values = request["data"]["items"][0]["column_values"]
#     print(f"esto es column values {column_values}")
#     return column_values

    
# def extract_linked_ids(column_values):
#     linked_ids = []

#     # Queue to manage processing of items
#     queue = column_values[:]

#     while queue:
#         # Pop the first element from the queue
#         current_item = queue.pop(0)

#         # Check if 'linked_item_ids' exist and add them to the linked_ids list
#         if 'linked_item_ids' in current_item and current_item['linked_item_ids']:
#             linked_ids.extend(current_item['linked_item_ids'])

#         # If 'linked_items' exist, add them to the queue for further processing
#         if 'linked_items' in current_item and current_item['linked_items']:
#             queue.extend(current_item['linked_items'])
        
#         print(f"estos son los item ids {linked_ids}")

#     return linked_ids



# def create_item(apiToken, contact_data):
#     board_id = 1741413024
    
#     # Basic data cleaning
#     item_name = str(contact_data.get('First Name', '')).strip()
#     if not item_name:
#         item_name = str(contact_data.get('Last Name', 'New Contact')).strip()
    
#     # Email formatting
#     email = str(contact_data.get('Email (Business)', '')).strip()
#     email_value = json.dumps({"email": email, "text": email})
    
#     # Tags handling
#     tags = contact_data.get('Tags', '')
#     tags_value = {"labels": []}  # Simplified to always use empty list
    
#     # Simple value cleaning function
#     def clean(value):
#         if pd.isna(value):
#             return ""
#         return str(value).strip()
    
#     # Phone formatting
#     mobile = str(contact_data.get('Mobile', '')).strip()
#     phone_value = {}
    
#     if mobile and mobile.lower() != 'nan':
#         # Remove spaces and any special characters
#         clean_number = ''.join(filter(str.isdigit, mobile))
#         if clean_number:
#             phone_value = json.dumps({
#                 "phone": clean_number,  # Only digits
#                 "countryShortName": "GB"
#             })
#             phone_value = json.loads(phone_value)
    
#     # Column values mapping
#     column_values = {
#         "texto_Mjj58DHe": clean(contact_data.get('assigned_user_name')),
#         "fecha_1_Mjj5f9zl": pd.to_datetime(contact_data['Created Time']).strftime('%Y-%m-%d'),
#         "texto_1_Mjj5ca4r": clean(contact_data.get('Last Name')),
#         "correo_electr_nico_Mjj5RqEY": json.loads(email_value),
#         "texto_largo_Mjj5bka6": clean(contact_data.get('Description')),
#         "men__desplegable_Mjj5Ahi7": tags_value,
#     }
    
#     # Only add phone if we have a valid value
#     if phone_value:
#         column_values["tel_fono_Mjj525ip"] = phone_value
    
#     # Create mutation
#     column_values_json = json.dumps(column_values, ensure_ascii=False)
#     mutation = f"""mutation {{
#         create_item (
#             board_id: {board_id},
#             item_name: "{item_name}",
#             column_values: {json.dumps(column_values_json)}
#         ) {{
#             id
#         }}
#     }}"""
    
#     return monday_request(mutation, apiToken)

# def create_multiple_items(apiToken, contacts_list):
#     created_items = []
#     for contact in contacts_list:
#         result = create_item(apiToken, contact)
#         created_items.append(result)
#         time.sleep(1)
#     return created_items

# def filter_contacts_by_date(csv_file_path):
#     # Read CSV file
#     df = pd.read_csv(csv_file_path, quoting=1)
    
#     # Define columns to keep
#     columns_to_keep = [
#         'Created Time', 'Modified Time', 'First Name', 'Last Name',
#         'Email (Business)', 'Office Phone', 'Mobile', 'Company Name',
#         'Tags', 'Description', 'Lead Source', 'assigned_user_name',
#         'Contact Type'
#     ]
    
#     # Keep only existing columns
#     available_columns = [col for col in columns_to_keep if col in df.columns]
#     df = df[available_columns]
    
#     # Filter by date
#     df['Created Time'] = pd.to_datetime(df['Created Time'])
#     df = df[df['Created Time'] >= '2018-01-01']
    
#     # Get random sample
#     sample_size = min(5, len(df))
#     random_contacts = df.sample(n=sample_size)
    
#     # Convert to list format
#     contacts_list = random_contacts.to_dict('records')
    
#     # Print results
#     for contact in contacts_list:
#         print("\n---Contact---")
#         for key, value in contact.items():
#             if pd.notna(value) and value not in ['0', '0.0', '--None--', '0000-00-00']:
#                 print(f"{key}: {value}")
    
#     return contacts_list

def get_item(item_id, apiToken):
    query = '''query {
  items (ids: %s) {
    name
    column_values{
      id
      text
      column{
        title
      
      }
    }
  }
}''' % item_id
    request = monday_request(query, apiToken)
    item_data = request["data"]["items"][0]["column_values"]
    print(f"esto es el item {item_data}")
    return item_data

def get_exchange_rate(dollars):
    # Calculate the date range for the last two days
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    euro = "EUR"
    usd = "USD"
    # Define the API endpoint with date filtering
    api_url = f"https://data-api.ecb.europa.eu/service/data/EXR/D.{usd}.{euro}.SP00.A?startPeriod={start_date}&endPeriod={end_date}"

    try:
        # Make a GET request to the API
        response = requests.get(api_url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the XML response to extract the exchange rate
            root = ET.fromstring(response.content)
            namespaces = {
                'message': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message',
                'generic': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic'
            }
            for series in root.findall('.//generic:Series', namespaces):
                for obs in series.findall('.//generic:Obs', namespaces):
                    rate = float(obs.find('.//generic:ObsValue', namespaces).attrib['value'])  # Convert rate to float
                    print(f"esto es el rate {rate}")
                    rate_multiplied = rate * dollars
                    print(f"esto es el rate multiplicado {rate_multiplied}")

                    return rate   # Return the latest rate as a float
                
        else:
            return None
    except (requests.exceptions.RequestException, ET.ParseError):
        return None
    
def change_column_value(board_id, item_id, new_value, apiToken):
    column_id = "n_meros_mkkawtmd"
    
    query = '''mutation {
            change_simple_column_value (board_id: %s, item_id: %s, column_id: "%s", value: "%s") {
            id
        }
    }''' % (board_id, item_id, column_id, new_value)
    request = monday_request(query, apiToken)
    return request
