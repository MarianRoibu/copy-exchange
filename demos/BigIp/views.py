from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import json
from .functions import *
import pandas as pd


# Create your views here.
@csrf_exempt
def test_view(request):
        apiToken = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQ0MjAyMzA5MywiYWFpIjoxMSwidWlkIjo2ODQwNzM4MCwiaWFkIjoiMjAyNC0xMS0yN1QxNjowMzoxMi4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjY0MzQxODcsInJnbiI6ImV1YzEifQ.yLuTp99bi-USR0zNNZowT0LIh9ncT4W-9zD0vBup19Y"
        print(f"esto es el request {request}")
        params = json.loads(request.body.decode('utf-8'))
        print(f"esto es el request {params}")
        pulse_id = params["payload"]["inboundFieldValues"]["itemId"]
        print(f"esto es el item id {pulse_id}")

        board_id = params["payload"]["inboundFieldValues"]["boardId"]
        print(f"esto es el board id {board_id}")
        
        item_data = get_item_data(pulse_id)
        print(f"esto es item data {item_data}")
        column_values = item_data['data']['items'][0]['column_values']
        print(f"esto es column_values {column_values}")
        item_name = item_data['data']['items'][0]['name']
        print(f"esto es item name {item_name}")

        item_data_to_df = {item['column']['id']: [item['text']] for item in column_values}
        
        df_item_data = pd.DataFrame(item_data_to_df)
        print("Contenido del DataFrame:")
        print(df_item_data)
        print("Columnas del DataFrame:")
        print(df_item_data.columns)

        countries_list = df_item_data[target_countries_item_column_id].iloc[0].split(', ')
        request_value = df_item_data[request_item_column_id].iloc[0]
        source_language = df_item_data[source_language_item_column_id].iloc[0]

        if request_value == 'EP':
            if source_language == 'English':
                countries_query_df = get_board_items(ep_en_board_id)
                print(f'countries_ep English= {countries_query_df}')
                pass
            
            elif source_language == 'German':
                countries_query_df = get_board_items(ep_de_board_id)
                print(f'countries_ep German= {countries_query_df}')
                pass
            
            elif source_language == 'French':
                countries_query_df = get_board_items(ep_fr_board_id)
                print(f'countries_ep French= {countries_query_df}')
                pass
        if request_value == 'PCT':
            countries_query_df = get_board_items(pct_board_id)
            print(f'countries_pct = {countries_query_df}')
            pass
        
        
        for country in countries_list:
            print('entro en for')
            subitem_name = item_name+'-'+country
            created_item = create_subitem(pulse_id,subitem_name)
            print(f'Created item en for country = {created_item}')
            specific_country_query_values = countries_query_df.loc[countries_query_df['name']==country]
            populate_subitem(created_item,source_language, specific_country_query_values,country,request_value)
            
        change_status_trigger(pulse_id,board_id)
            
        return HttpResponse("CREATED", status=200)