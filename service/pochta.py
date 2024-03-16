import os
import warnings
from datetime import datetime

import pandas as pd
import requests

# Игнорировать незначительные ошибки.
warnings.simplefilter(action='ignore', category=FutureWarning)

# Заголовки
headers = {
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Referer': 'https://www.pochta.ru/tracking?barcode=10204289519872',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'accept': 'application/json',
    'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}


# Функция для почты
def get_tracking_info(track_number):
    params = {
        'language': 'ru',
        'track-numbers': track_number,
    }

    response = requests.get(
        'https://www.pochta.ru/api/tracking/api/v1/trackings/by-barcodes',
        params=params,
        headers=headers,
    )

    if response.status_code == 200:
        data = response.json()

        # Ваши операции с данными, как ранее
        mail_type = data['detailedTrackings'][0]['formF22Params']['MailTypeText']
        weight = data['detailedTrackings'][0]['formF22Params']['WeightGr']
        formatted_accepted_date = datetime.strptime(
            max(entry['date'] for entry in data['detailedTrackings'][0]['trackingItem']['trackingHistoryItemList']
                if entry['humanStatus'] == "Принято в отделении связи"),
            "%Y-%m-%dT%H:%M:%S.%f%z"
        ).strftime("%d.%m.%Y")

        first_event = data['detailedTrackings'][0]['trackingItem']['trackingHistoryItemList'][0]
        status_date = datetime.strptime(first_event['date'], "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%d-%m-%Y")

        status_date = f"{status_date} / {first_event['humanStatus']}"

        sender = data['detailedTrackings'][0]['trackingItem']['sender']
        recipient = data['detailedTrackings'][0]['trackingItem']['recipient']
        destination_city = data['detailedTrackings'][0]['trackingItem']['destinationCityName']
        index_to = data['detailedTrackings'][0]['trackingItem']['indexTo']
        destination_info = f"{destination_city} / {index_to}"

        arrival_event = any(entry['humanStatus'] == "Прибыло в место вручения" for entry in
                            data['detailedTrackings'][0]['trackingItem']['trackingHistoryItemList'])

        if arrival_event:
            event_status = "Да"
            arrival_date = datetime.strptime(
                next(entry['date'] for entry in data['detailedTrackings'][0]['trackingItem']['trackingHistoryItemList']
                     if entry['humanStatus'] == "Прибыло в место вручения"),
                "%Y-%m-%dT%H:%M:%S.%f%z"
            ).strftime("%d.%m.%Y, %H:%M")
        else:
            event_status = "Нет"
            arrival_date = ""

        delivery_attempt_events = [entry for entry in
                                   data['detailedTrackings'][0]['trackingItem']['trackingHistoryItemList']
                                   if entry['humanStatus'] in ["Вручение адресату", "Неудачная попытка вручения",
                                                               "Вручение адресату почтальоном"]]
        latest_delivery_attempt = max(delivery_attempt_events, key=lambda x: x['date'], default=None)

        if latest_delivery_attempt:
            delivery_status = latest_delivery_attempt['humanStatus']
            delivery_date = datetime.strptime(latest_delivery_attempt['date'], "%Y-%m-%dT%H:%M:%S.%f%z").strftime(
                "%d-%m-%Y, %H:%M")
        else:
            delivery_status = ""
            delivery_date = ""

        return {
            'MailTypeText': mail_type,
            'WeightGr': weight,
            'LastAcceptedDate': formatted_accepted_date,
            'StatusDate': status_date,
            'Sender': sender,
            'Recipient': recipient,
            'DestinationInfo': destination_info,
            'ArrivalEvent': event_status,
            'ArrivalDate': arrival_date,
            'DeliveryStatus': delivery_status,
            'DeliveryDate': delivery_date
        }
    else:
        print(f"Ошибка при выполнении запроса для трек-номера {track_number}: {response.status_code}")
        return None


def get_track_info(file_name):
    # Загружаем данные из экселя
    df = pd.read_excel(f"{os.getcwd()}/files/{file_name}")

    # Почта
    count_pochta = 1
    for index, row in df.iterrows():

        track_number = row['Трек-номер']
        tracking_info = get_tracking_info(track_number)

        if tracking_info:
            df.at[index, 'Отправление'] = str(tracking_info['MailTypeText'])
            df.at[index, 'Принято'] = str(tracking_info['LastAcceptedDate'])
            df.at[index, 'Статус'] = str(tracking_info['StatusDate'])
            df.at[index, 'От кого'] = str(tracking_info['Sender'])
            df.at[index, 'Кому'] = str(tracking_info['Recipient'])
            df.at[index, 'Куда'] = str(tracking_info['DestinationInfo'])
            df.at[index, 'Прибыло'] = str(tracking_info['ArrivalEvent'])
            df.at[index, 'Дата прибытия'] = str(tracking_info['ArrivalDate'])
            df.at[index, 'Событие'] = str(tracking_info['DeliveryStatus'])
            df.at[index, 'Дата события'] = str(tracking_info['DeliveryDate'])
        print(f'Почта: {count_pochta} из {len(df)}')
        count_pochta += 1
    # Сохраняем обновленные данные в новый эксель файл
    df.to_excel('result.xlsx', index=False)
    print('Таблица создана. ')
