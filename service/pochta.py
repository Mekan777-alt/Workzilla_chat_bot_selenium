import os
import pandas as pd
import asyncio
from openpyxl import load_workbook
from openpyxl.styles import Border, Side
from config import bot, my_login, my_password
from zeep import Client, Settings
from zeep.helpers import serialize_object
import json
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)


# Функция для почты
async def get_tracking_info(track_number, user_id):
    url = 'https://tracking.russianpost.ru/rtm34?wsdl'
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=url, settings=settings)

    operation_history_request = {
        'Barcode': track_number,
        'MessageType': '0',
        'Language': 'RUS'
    }

    authorization_header = {
        'login': my_login,
        'password': my_password
    }

    try:
        result = client.service.getOperationHistory(
            OperationHistoryRequest=operation_history_request,
            AuthorizationHeader=authorization_header
        )
        serialized_result = serialize_object(result)
        json_result = json.dumps(serialized_result, indent=4, ensure_ascii=False, default=str)

        data = json.loads(json_result)

        try:
            first_item = data[0] if data else None
            last_item = data[-1] if data else None
            middle_items = data[1:-1] if len(data) > 2 else []

            barcode = track_number

            index = first_item['AddressParameters']['DestinationAddress'].get('Index')
            description = first_item['AddressParameters']['DestinationAddress'].get('Description')

            rcpn = first_item['UserParameters']['Rcpn']
            sndr = first_item['UserParameters']['Sndr']

            oper_type_1 = last_item['OperationParameters']['OperType']['Name'] \
                if last_item['OperationParameters']['OperType']['Name'] else ''
            oper_attr_1 = last_item['OperationParameters']['OperAttr']['Name'] \
                if last_item['OperationParameters']['OperAttr']['Name'] else ''
            oper_date_1 = last_item['OperationParameters']['OperDate'] \
                if last_item['OperationParameters']['OperDate'] else ''

            oper_address_1_index = last_item['AddressParameters']['OperationAddress']['Index'] \
                if last_item['AddressParameters']['OperationAddress']['Index'] else ''
            oper_address_1_address = last_item['AddressParameters']['OperationAddress']['Description'] \
                if last_item['AddressParameters']['OperationAddress']['Description'] else ''

            oper_type_2 = first_item['OperationParameters']['OperType']['Name'] \
                if first_item['OperationParameters']['OperType']['Name'] else ''
            oper_attr_2 = first_item['OperationParameters']['OperAttr']['Name'] \
                if first_item['OperationParameters']['OperAttr']['Name'] else ''
            oper_date_2 = first_item['OperationParameters']['OperDate'] \
                if first_item['OperationParameters']['OperDate'] else ''

            oper_address_2_index = first_item['AddressParameters']['OperationAddress']['Index'] \
                if first_item['AddressParameters']['OperationAddress']['Index'] else ''
            oper_address_2_address = first_item['AddressParameters']['OperationAddress']['Description'] \
                if first_item['AddressParameters']['OperationAddress']['Description'] else ''

            complex_item_name = first_item['ItemParameters']['ComplexItemName'] \
                if first_item['ItemParameters']['ComplexItemName'] else ''

            middle_operations = [{
                'OperType': item['OperationParameters']['OperType']['Name'] if item['OperationParameters']['OperType'][
                    'Name'] else '',
                'OperAttr': item['OperationParameters']['OperAttr']['Name'] if item['OperationParameters']['OperAttr'][
                    'Name'] else '',
                'OperDate': item['OperationParameters']['OperDate'] if item['OperationParameters']['OperDate'] else '',
                'OperationAddressIndex': item['AddressParameters']['OperationAddress']['Index'] if
                item['AddressParameters']['OperationAddress']['Index'] else '',
                'OperationAddressDescription': item['AddressParameters']['OperationAddress']['Description'] if
                item['AddressParameters']['OperationAddress']['Description'] else ''
            } for item in middle_items]

            return {
                'Barcode': barcode,
                'DestIndex': index,
                'DestDesc': description,
                'Rcpn': rcpn,
                'OperType1': oper_type_1,
                'OperAttr1': oper_attr_1,
                'OperDate1': oper_date_1,
                'OperationAddress1Index': oper_address_1_index,
                'OperationAddress1Address': oper_address_1_address,
                'OperType2': oper_type_2,
                'OperAttr2': oper_attr_2,
                'OperDate2': oper_date_2,
                'OperationAddress2Index': oper_address_2_index,
                'OperationAddress2Address': oper_address_2_address,
                'Sndr': sndr,
                'ComplexItemName': complex_item_name,
                'MiddleOperations': middle_operations
            }
        except Exception as e:
            print(e)
            await bot.send_message(user_id, f"Ошибка при выполнении запроса для трек-номера {track_number}: {str(e)}")
    except Exception as e:
        print(e)
        await bot.send_message(user_id, f"Ошибка при подключении к сервису отслеживания: {str(e)}")
        return None


async def get_track_info(file_name, user_id):
    df = pd.read_excel(f"{os.getcwd()}\\files\\{file_name}")

    drop_list = ['ФИО']
    df = df.drop(columns=drop_list, errors='ignore')

    # Почта
    count_pochta = 1
    for index, row in df.iterrows():

        track_number = row['Barcode']
        tracking_info = await get_tracking_info(track_number, user_id)

        if tracking_info:
            df.at[index, 'DestinationIndex'] = f"{tracking_info['DestIndex']}"
            df.at[index, 'DestinationAddress'] = f"{tracking_info['DestDesc']}"
            df.at[index, 'Rcpn'] = str(tracking_info['Rcpn'])
            df.at[index, 'OperType1'] = str(tracking_info['OperType1'])
            df.at[index, 'OperAttr1'] = str(tracking_info['OperAttr1'])
            df.at[index, 'OperDate1'] = str(tracking_info['OperDate1'])
            df.at[index, 'OperationIndex1'] = f"{tracking_info['OperationAddress1Index']}"
            df.at[index, 'OperationAddress1'] = f"{tracking_info['OperationAddress1Address']}"
            df.at[index, 'OperType2'] = str(tracking_info['OperType2'])
            df.at[index, 'OperAttr2'] = str(tracking_info['OperAttr2'])
            df.at[index, 'OperDate2'] = str(tracking_info['OperDate2'])
            df.at[index, 'OperationIndex2'] = f"{tracking_info['OperationAddress2Index']}"
            df.at[index, 'OperationAddress2'] = f"{tracking_info['OperationAddress2Address']}"
            df.at[index, 'Sndr'] = str(tracking_info['Sndr'])
            df.at[index, 'ComplexItemName'] = str(tracking_info['ComplexItemName'])

            # Запись остальных операций
            middle_operations = tracking_info['MiddleOperations']
            for i, operation in enumerate(middle_operations):
                df.at[index, f'MiddleOperType_{i + 1}'] = operation['OperType']
                df.at[index, f'MiddleOperAttr_{i + 1}'] = operation['OperAttr']
                df.at[index, f'MiddleOperDate_{i + 1}'] = operation['OperDate']
                df.at[index, f'MiddleOperationIndex_{i + 1}'] = operation['OperationAddressIndex']
                df.at[index, f'MiddleOperationAddress_{i + 1}'] = operation['OperationAddressDescription']

            df.to_excel('result.xlsx', index=False)

            await asyncio.sleep(30)

        count_pochta += 1

    df.to_excel('result.xlsx', index=False)
