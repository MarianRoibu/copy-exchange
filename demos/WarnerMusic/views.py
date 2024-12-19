from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import json
from .functions import *

# Create your views here.
@csrf_exempt
def warner_music(request):
    apiToken = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQ0MjAyMzA5MywiYWFpIjoxMSwidWlkIjo2ODQwNzM4MCwiaWFkIjoiMjAyNC0xMS0yN1QxNjowMzoxMi4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjY0MzQxODcsInJnbiI6ImV1YzEifQ.yLuTp99bi-USR0zNNZowT0LIh9ncT4W-9zD0vBup19Y"
    print(f"esto es el request {request}")
    params = json.loads(request.body.decode('utf-8'))
    print(f"esto es el request {params}")
    item_id = params["payload"]["inboundFieldValues"]["itemId"]
    board_id = params["payload"]["inboundFieldValues"]["boardId"]
    print(f"esto es el board_id {board_id}")
    print(f"esto es el item_id {item_id}")
    # item_id = params["payload"]["inboundFieldValues"]["itemId"]
    # print(f"esto es el request {params}")
    # connected_items_column_values = get_connected_ids(item_id, apiToken)
    # all_item_ids = extract_linked_ids(connected_items_column_values)


    # csv_file_path = "c:/Users/mrusu/Downloads/Contacts.csv"  # Usar directamente el archivo original
    # contacts = filter_contacts_by_date(csv_file_path)
    # results = create_multiple_items(apiToken, contacts)


    amount_in_euro = 100
    number_of_dollars = 122
    amount_in_usd = get_exchange_rate(number_of_dollars)
    print(f"esto es el amount_in_usd {amount_in_usd}")
    get_item_data = get_item(item_id, apiToken)
    for item in get_item_data:
        print(f"esto es el item {item}")
        if item['id'] == "n_meros_mkkcxx9c":
            deal_value = item['text']
    deal_value_number = float(deal_value)
    final_value = deal_value_number / amount_in_usd
    print(f"esto es el final_value {final_value}")
    print(f"esto es el deal_value {deal_value}")
    print(f"esto es el item column value {item}")
    change_column_value(board_id, item_id, final_value, apiToken)
    return JsonResponse({"status": "success"})

