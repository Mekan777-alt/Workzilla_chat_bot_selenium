import asyncio
import os
import warnings

from openpyxl.reader.excel import load_workbook
from openpyxl.styles import Border, Side

from config import bot, my_login, my_password
import pandas as pd
import json
from zeep import Client, Settings
from zeep.helpers import serialize_object

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
                if last_item['OperationParameters']['OperDate'] else ''

            oper_address_2_index = first_item['AddressParameters']['OperationAddress']['Index'] \
                if last_item['AddressParameters']['OperationAddress']['Index'] else ''
            oper_address_2_address = first_item['AddressParameters']['OperationAddress']['Description'] \
                if last_item['AddressParameters']['OperationAddress']['Description'] else ''

            complex_item_name = first_item['ItemParameters']['ComplexItemName'] \
                if first_item['ItemParameters']['ComplexItemName'] else ''

            return {
                'Barcode': barcode,
                'DestinationAddress': f'{index} {description}',
                'Rcpn': rcpn,
                'OperType1': oper_type_1,
                'OperAttr1': oper_attr_1,
                'OperDate1': oper_date_1,
                'OperationAddress1': f'{oper_address_1_index} {oper_address_1_address}',
                'OperType2': oper_type_2,
                'OperAttr2': oper_attr_2,
                'OperDate2': oper_date_2,
                'OperationAddress2': f'{oper_address_2_index} {oper_address_2_address}',
                'Sndr': sndr,
                'ComplexItemName': complex_item_name,
            }
        except Exception as e:
            print(e)
            await bot.send_message(user_id,
                                   f"Ошибка при выполнении запроса для трек-номера {track_number}: {str(e)}")
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
            df.at[index, 'DestinationAddress'] = str(tracking_info['DestinationAddress'])
            df.at[index, 'Rcpn'] = str(tracking_info['Rcpn'])
            df.at[index, 'OperType1'] = str(tracking_info['OperType1'])
            df.at[index, 'OperAttr1'] = str(tracking_info['OperAttr1'])
            df.at[index, 'OperDate1'] = str(tracking_info['OperDate1'])
            df.at[index, 'OperationAddress1'] = str(tracking_info['OperationAddress1'])
            df.at[index, 'OperType2'] = str(tracking_info['OperType2'])
            df.at[index, 'OperAttr2'] = str(tracking_info['OperAttr2'])
            df.at[index, 'OperDate2'] = str(tracking_info['OperDate2'])
            df.at[index, 'OperationAddress2'] = str(tracking_info['OperationAddress2'])
            df.at[index, 'Sndr'] = str(tracking_info['Sndr'])
            df.at[index, 'ComplexItemName'] = str(tracking_info['ComplexItemName'])

            await asyncio.sleep(30)

        count_pochta += 1
    df.to_excel('result.xlsx', index=False)
