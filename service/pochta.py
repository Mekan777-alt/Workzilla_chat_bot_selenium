import os
import warnings
from datetime import datetime
from config import bot
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
async def get_tracking_info(track_number, user_id):
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

        try:
            # Ваши операции с данными, как ранее
            mail_type = data['detailedTrackings'][0]['formF22Params']['MailTypeText']
            recipient_index = data['detailedTrackings'][0]['trackingItem']['indexTo']
            destination_city = data['detailedTrackings'][0]['trackingItem']['destinationCityName']
            recipient = data['detailedTrackings'][0]['trackingItem']['recipient']
            status = data['detailedTrackings'][0]['trackingItem']['commonStatus']
            sender = data['detailedTrackings'][0]['trackingItem']['sender']

            receive_status = next((entry['humanStatus'] for entry in data['detailedTrackings'][0]['trackingItem']
                ['trackingHistoryItemList'] if "Принято в отделении связи" in entry.get('humanStatus')), None)
            receive_index = next((entry['index'] for entry in data['detailedTrackings'][0]['trackingItem']
                ['trackingHistoryItemList'] if "Принято в отделении связи" in entry.get('humanStatus')), None)
            receive_city = next((entry['cityName'] for entry in data['detailedTrackings'][0]['trackingItem']
                ['trackingHistoryItemList'] if "Принято в отделении связи" in entry.get('humanStatus')), None)

            try:
                receive_date = datetime.strptime(
                        next(entry['date'] for entry in
                             data['detailedTrackings'][0]['trackingItem']['trackingHistoryItemList']
                             if "Принято в отделении связи" in entry.get('humanStatus')),
                        "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%d.%m.%Y")
            except StopIteration:
                receive_date = None

            pod_status = None
            pod_status_index = None
            pod_status_city = None
            pod_status_date = None

            if "Аннулировано" in status:

                pod_status = next((entry['humanStatus'] for entry in data['detailedTrackings'][0]['trackingItem']
                ['trackingHistoryItemList'] if entry.get('humanStatus') == "Неудачная попытка вручения"), None)

                pod_status_index = next((entry['index'] for entry in data['detailedTrackings'][0]['trackingItem']
                ['trackingHistoryItemList'] if entry.get('humanStatus') == "Неудачная попытка вручения"), None)

                pod_status_city = next((entry['cityName'] for entry in data['detailedTrackings'][0]['trackingItem']
                ['trackingHistoryItemList'] if entry.get('humanStatus') == "Неудачная попытка вручения"), None)

                try:
                    pod_status_date = datetime.strptime(
                        next(entry['date'] for entry in
                             data['detailedTrackings'][0]['trackingItem']['trackingHistoryItemList']
                             if "Неудачная попытка вручения" in entry.get('humanStatus')),
                        "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%d.%m.%Y")
                except StopIteration:
                    pod_status_date = None


            elif any(s in status for s in
                     ["Покинуло сортировочный центр", "Направлено для передачи на временное хранение",
                      "Возвращено отправителю", "Временное хранение", "Хранится в отделении до",
                      "Срок хранения истекает", "Прибыло в сортировочный центр", "Срок хранения истек"]):

                pod_status = next((entry['humanStatus'] for entry in data['detailedTrackings'][0]['trackingItem']
                ['trackingHistoryItemList'] if "Неудачная попытка вручения" in entry.get('humanStatus')), None)

                pod_status_index = next((entry['index'] for entry in data['detailedTrackings'][0]['trackingItem']
                ['trackingHistoryItemList'] if "Неудачная попытка вручения" in entry.get('humanStatus')), None)

                pod_status_city = next((entry['cityName'] for entry in data['detailedTrackings'][0]['trackingItem']
                ['trackingHistoryItemList'] if "Неудачная попытка вручения" in entry.get('humanStatus')), None)

                try:
                    pod_status_date = datetime.strptime(
                        next(entry['date'] for entry in
                             data['detailedTrackings'][0]['trackingItem']['trackingHistoryItemList']
                             if "Неудачная попытка вручения" in entry.get('humanStatus')),
                        "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%d.%m.%Y")
                except StopIteration:
                    pod_status_date = None

            elif "Вручено" in status:
                "Вручение адресату"
                pod_status = next((entry['humanStatus'] for entry in data['detailedTrackings'][0]['trackingItem']
                ['trackingHistoryItemList'] if "Вручение адресату" in entry.get('humanStatus')), None)

                pod_status_index = next((entry['index'] for entry in data['detailedTrackings'][0]['trackingItem']
                ['trackingHistoryItemList'] if "Вручение адресату" in entry.get('humanStatus')), None)

                pod_status_city = next((entry['cityName'] for entry in data['detailedTrackings'][0]['trackingItem']
                ['trackingHistoryItemList'] if "Вручение адресату" in entry.get('humanStatus')), None)
                try:
                    pod_status_date = datetime.strptime(
                        next(entry['date'] for entry in
                             data['detailedTrackings'][0]['trackingItem']['trackingHistoryItemList']
                             if "Вручение адресату" in entry.get('humanStatus')),
                        "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%d.%m.%Y")
                except StopIteration:
                    pod_status_date = None

            arrival_event = any(entry['humanStatus'] == "Прибыло в место вручения" for entry in
                                data['detailedTrackings'][0]['trackingItem']['trackingHistoryItemList'])

            if arrival_event:
                arrival_date = datetime.strptime(
                    next(entry['date'] for entry in
                         data['detailedTrackings'][0]['trackingItem']['trackingHistoryItemList']
                         if entry['humanStatus'] == "Прибыло в место вручения"),
                    "%Y-%m-%dT%H:%M:%S.%f%z"
                ).strftime("%d.%m.%Y")
                index = next(
                    entry['index'] for entry in data['detailedTrackings'][0]['trackingItem']['trackingHistoryItemList']
                    if entry['humanStatus'] == "Прибыло в место вручения")
                city = next(
                    entry['cityName'] for entry in
                    data['detailedTrackings'][0]['trackingItem']['trackingHistoryItemList']
                    if entry['humanStatus'] == "Прибыло в место вручения")
            else:
                arrival_date = ""
                index = ""
                city = ""
            return {
                'TrackNumber': track_number,
                'RecipientIndex': recipient_index,
                'DestinationCity': destination_city,
                'Recipient': recipient,
                'Status': status,
                'PodStatus': pod_status,
                'PodStatusDate': pod_status_date,
                'PodStatusIndex': pod_status_index,
                'PodStatusCity': pod_status_city,
                'ReceiveStatus': receive_status,
                'ReceiveStatusDate': receive_date,
                'ReceiveStatusIndex': receive_index,
                'ReceiveStatusCity': receive_city,
                'ArrivalDate': arrival_date,
                'IndexGet': index,
                'CityGet': city,
                'MailType': mail_type,
                'Sender': sender,
            }
        except Exception as e:
            print(e)
            await bot.send_message(user_id,
                                   f"Ошибка при выполнении запроса для трек-номера {track_number}: {str(e)}")
    else:
        await bot.send_message(user_id,
                               f"Ошибка при выполнении запроса для трек-номера {track_number}: {response.status_code}")
        return None


async def get_track_info(file_name, user_id):
    # Загружаем данные из экселя
    df = pd.read_excel(f"{os.getcwd()}/files/{file_name}")

    drop_list = ['ФИО']
    df = df.drop(columns=drop_list, errors='ignore')
    # Почта
    count_pochta = 1
    for index, row in df.iterrows():

        track_number = row['Трек-номер']
        tracking_info = await get_tracking_info(track_number, user_id)

        if tracking_info:
            df.at[index, 'Куда Индекс'] = str(tracking_info['RecipientIndex'])
            df.at[index, 'Куда Место'] = str(tracking_info['DestinationCity'])
            df.at[index, 'Кому'] = str(tracking_info['Recipient'])
            df.at[index, 'Статус'] = str(tracking_info['Status'])
            df.at[index, 'Подстатус'] = str(tracking_info['PodStatus'])
            df.at[index, 'Подстатус - дата'] = str(tracking_info['PodStatusDate'])
            df.at[index, 'Подстатус - индекс'] = str(tracking_info['PodStatusIndex'])
            df.at[index, 'Подстатус - место'] = str(tracking_info['PodStatusCity'])
            df.at[index, 'Принято'] = str(tracking_info['ReceiveStatus'])
            df.at[index, 'Принято - дата'] = str(tracking_info['ReceiveStatusDate'])
            df.at[index, 'Принято - индекс'] = str(tracking_info['ReceiveStatusDate'])
            df.at[index, 'Принято - место'] = str(tracking_info['ReceiveStatusCity'])
            df.at[index, 'Дата - прибыло в место вручения'] = str(tracking_info['ArrivalDate'])
            df.at[index, 'Индекс - Прибыло в место вручения'] = str(tracking_info['IndexGet'])
            df.at[index, 'Место - Прибыло в место вручения'] = str(tracking_info['CityGet'])
            df.at[index, 'Вид отправления'] = str(tracking_info['MailType'])
            df.at[index, 'От кого:'] = str(tracking_info['Sender'])

        count_pochta += 1
    # Сохраняем обновленные данные в новый эксель файл
    df.to_excel('result.xlsx', index=False)
