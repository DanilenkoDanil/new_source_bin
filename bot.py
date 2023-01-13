import configparser
import json
import asyncio

from telethon.sync import TelegramClient
from telethon import connection

# для корректного переноса времени сообщений в json
from datetime import date, datetime

# классы для работы с каналами
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

# класс для работы с сообщениями
from telethon.tl.functions.messages import GetHistoryRequest

from binance.client import Client
import requests


def convert_to_dict(symbols: list):
    result_dict = {}
    for i in symbols:

        if i['symbol'] in result_dict.keys() and float(i['stopPrice']) > float(result_dict[i['symbol']]['stopPrice']):
            result_dict[i['symbol']] = i
        elif i['symbol'] not in result_dict.keys():
            result_dict[i['symbol']] = i
    return result_dict


# Считываем учетные данные
config = configparser.ConfigParser()
config.read("config.ini")

old_message = []
pub = 'TmCZsJp55qJPOWgleRLsWv8VBmFq4BIBQMCy2nWQI4t48fTT7x6ums4keMXL7Azv'
pri = 'sYMXl1urFA8TlU71BvV4JeDAcs3r89bXFou2vDVDQNhudo7hW4oNJ6QNRqUb9iCG'
url = 'http://185.231.155.38'

client_bin = Client(pub, pri)
exchange = convert_to_dict(client_bin.futures_exchange_info()['symbols'])

with open("setting.json", 'r', encoding='utf8') as out:
    setting = json.load(out)

    client = TelegramClient(
        setting['account']['session'],
        setting['account']['api_id'],
        setting['account']['api_hash']
    )

    client.start()


async def change_user_links_text(message: str, username: str) -> str:
    for item in message.split():
        if '@' in item:
            print('!!!!!!!!!!!!!!!!!!!!!!!')
            if not item[1].isdigit():
                message = message.replace(item, username)

    return message


def check_msg(text):
    if "LONG" in text:
        return True
    if "лонг" in text:
        return True
    if "Лонг" in text:
        return True
    if "Long" in text:
        return True
    if "Short" in text:
        return True
    if "SHORT" in text:
        return True
    if "Шорт" in text:
        return True
    if "шорт" in text:
        return True
    if '📈' in text:
        return True

    return False


async def dump_all_messages(channel):
    """Записывает json-файл с информацией о всех сообщениях канала/чата"""

    history = await client(GetHistoryRequest(
        peer=channel,
        offset_id=0,
        offset_date=None, add_offset=0,
        limit=10, max_id=0, min_id=0,
        hash=0))
    messages = list(history.messages)
    messages.reverse()
    for message in messages:
        if int(message.id) not in old_message:
            try:
                if check_msg(message.message):
                    msg = message.message
                    print('!!!!!!!!!!!!!!!!!!!!!!!!!')
                    print(msg)
                    print('!!!!!!!!!!!!!!!!!!!!!!!!!')
                    print('tttttttttttttt')
                    symbol = msg.split('#')[2].split['\n'][0]
                    print('tttttttttttttt')
                    amount_precision = int(exchange[symbol]['pricePrecision'])

                    now_price = round(float(convert_to_dict(client_bin.get_ticker())[symbol]['lastPrice']),
                                      amount_precision)
                    if '#LONG' in msg:
                        take_profit_1 = round(float(now_price) / 100 * (100 + 1), amount_precision)
                        take_profit_2 = round(float(now_price) / 100 * (100 + 2), amount_precision)
                        take_profit_3 = round(float(now_price) / 100 * (100 + 3), amount_precision)
                        stop_loss = round(float(now_price) / 100 * (100 - 7), amount_precision)
                        type_buy = 'LONG'
                    elif '#SHORT' in msg:
                        take_profit_1 = round(float(now_price) / 100 * (100 - 1), amount_precision)
                        take_profit_2 = round(float(now_price) / 100 * (100 - 2), amount_precision)
                        take_profit_3 = round(float(now_price) / 100 * (100 - 3), amount_precision)
                        stop_loss = round(float(now_price) / 100 * (100 + 7), amount_precision)
                        type_buy = 'SHORT'
                    elif 'лонг' in str(msg).lower() and 'шорт' in str(msg).lower():
                        continue
                    elif 'лонг' in msg or 'Long' in msg or 'Лонг' in msg:
                        take_profit_1 = round(float(now_price) / 100 * (100 + 1), amount_precision)
                        take_profit_2 = round(float(now_price) / 100 * (100 + 2), amount_precision)
                        take_profit_3 = round(float(now_price) / 100 * (100 + 3), amount_precision)
                        stop_loss = round(float(now_price) / 100 * (100 - 7), amount_precision)
                        type_buy = 'LONG'
                    else:
                        take_profit_1 = round(float(now_price) / 100 * (100 - 1), amount_precision)
                        take_profit_2 = round(float(now_price) / 100 * (100 - 2), amount_precision)
                        take_profit_3 = round(float(now_price) / 100 * (100 - 3), amount_precision)
                        stop_loss = round(float(now_price) / 100 * (100 + 7), amount_precision)
                        type_buy = 'SHORT'

                    res = f"""
hahScalp

hah{symbol} - hah{type_buy}

Entry: {now_price}
Take profit: {take_profit_1}, {take_profit_2}, {take_profit_3}
Stop loss: {stop_loss}

hahFutures
"""
                    print(res)
                    result = requests.get(f'{url}/api/send-message/?message={res}')
                    print(result.text)
            except Exception as e:
                print(e)

            old_message.append(int(message.id))


async def main():
    dialogs = await client.get_dialogs()

    for index, dialog in enumerate(dialogs):
        if index < 250:
            print(dialog.name)
            if str(dialog.id) == '-1001297150391':
                channel = dialog
                print('+')

    while True:
        try:
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print('Скан')
            await dump_all_messages(channel)
            await asyncio.sleep(30)
        except Exception as e:
            print(e)
            await asyncio.sleep(300)

with client:
    client.loop.run_until_complete(main())
