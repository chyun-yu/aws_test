

import jwt
import uuid
import hashlib
from urllib.parse import urlencode
import requests
import threading
import time
import pyupbit

from math import *


# start setting value   1.84254606
access_key = "bGQG9aMhdHw6nJWL8rgGQDbxUyeHQiOvAnfNNC3F"
secret_key = "EoJUGQ4Wx7qVIGwNuCIbhY2ebKb6L2fNocIEw73E"
server_url = 'https://api.upbit.com'
had_cur = {}   # 초기화 계좌
standard_price = 5100
margin_rate = 0.017


def get_cell_price(price):
    if price >= 2000000:
        tick_size = ceil(price / 1000) * 1000
    elif price >= 1000000:
        tick_size = ceil(price / 500) * 500
    elif price >= 500000:
        tick_size = ceil(price / 100) * 100
    elif price >= 100000:
        tick_size = ceil(price / 50) * 50
    elif price >= 10000:
        tick_size = ceil(price / 10) * 10
    elif price >= 1000:
        tick_size = ceil(price / 5) * 5
    elif price >= 100:
        tick_size = ceil(price / 1) * 1
    elif price >= 10:
        tick_size = ceil(price / 0.1) * 0.1
    else:
        tick_size = ceil(price / 0.01) * 0.01
    return tick_size

def get_buy_price(price):
    if price >= 2000000:
        tick_size = floor(price / 1000) * 1000
    elif price >= 1000000:
        tick_size = floor(price / 500) * 500
    elif price >= 500000:
        tick_size = floor(price / 100) * 100
    elif price >= 100000:
        tick_size = floor(price / 50) * 50
    elif price >= 10000:
        tick_size = floor(price / 10) * 10
    elif price >= 1000:
        tick_size = floor(price / 5) * 5
    elif price >= 100:
        tick_size = floor(price / 1) * 1
    elif price >= 10:
        tick_size = floor(price / 0.1) * 0.1
    else:
        tick_size = floor(price / 0.01) * 0.01
    return tick_size

def order_cancle(order_uuid):

    query = {
        'uuid': order_uuid,
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    requests.delete(server_url + "/v1/order", params=query, headers=headers)

def limit_buy_order(ticker, volume, price):

    query = {
        'market': ticker,
        'side': 'bid',
        'volume': str(volume),
        'price': str(price),
        'ord_type': 'limit',
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.post(server_url + "/v1/orders", params=query, headers=headers)
    d = res.json()
    buy_uuids = d['uuid']
    return buy_uuids

def limit_cell_order(ticker, volume, price):

    query = {
        'market': ticker,
        'side': 'ask',
        'volume': str(volume),
        'price': str(price),
        'ord_type': 'limit',
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.post(server_url + "/v1/orders", params=query, headers=headers)
    b = res.json()
    cell_uuids = b['uuid']
    return cell_uuids

def order_info(order_uuid):

    query = {
        'uuid': order_uuid,
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.get(server_url + "/v1/order", params=query, headers=headers)
    order_in = res.json()

    return order_in

def load_account():
    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
    }

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.get(server_url + "/v1/accounts", headers=headers)
    return res


def post_message(text):
    requests.post("https://slack.com/api/chat.postMessage",
                  headers={"Authorization": "Bearer " + "xoxb-2044675961683-2050629280372-uAxtjmyUSzMKJkusqS3vbU9u"},
                  data={"channel": "#auto-tc", "text": text}
                  )

def mainloop():
    while True:
        time.sleep(0.3)
        acount = load_account()  # 계좌조회

        road_list = []  # 조회되는 list 초기화
        no_trade_list = ["KRW"]
        for i in acount.json():
            c, b, l = (i['currency'], round(float(i['balance']), 8), round(float(i['locked']), 8))  # 보유종목, 보유양, 묶인양 조회
            road_list.append(c)  # 조회 리스트에 추가....

            if c in no_trade_list:  # 원화
                pass
            else:
                ticker = str("KRW-" + c)
                price = pyupbit.get_current_price(ticker)  # 현재가 조회
                if c not in had_cur:  # 초기 실행시 매수매도 주문을 위함 and 신규로 종목이 추가

                    buy_price = get_buy_price ( price * (1 - margin_rate))  # 매수가 조회하고
                    buy_vol = round(standard_price / buy_price, 8)  # 매수량 결정
                    buy_uuid = limit_buy_order(ticker, str(buy_vol), str(buy_price))  # 매수주문

                    cell_price = get_cell_price(price * (1+margin_rate))  # 매도가 조회하고
                    ppung = price * b

                    if ppung >= (standard_price * 2):  # 2배이상이면 매도 일반적주문
                        cell_vol = round(standard_price * (1+margin_rate) / cell_price, 8)
                        cell_uuid = limit_cell_order(ticker, str(cell_vol), str(cell_price))
                        had_cur[c] = {'balance': b, 'locked': l, 'buy_uuid': buy_uuid, 'cell_uuid': cell_uuid}  # 보유 계좌에 추가

                    elif ppung >= standard_price:  # 1번밖에 못팔면 전량매도
                        post_message(c + "전량 매도 주문")
                        cell_uuid = limit_cell_order(ticker, str(b), str(cell_price))
                        had_cur[c] = {'balance': b, 'locked': l, 'buy_uuid': buy_uuid, 'cell_uuid': cell_uuid}  # 보유 계좌에 추가
                    elif ppung < standard_price:  # 총량이 적으면
                        post_message(c + " 매도 못해")
                        had_cur[c] = {'balance': b, 'locked': l, 'buy_uuid': buy_uuid}

                    time.sleep(0.3)

                else:  # 보유종목이면
                    # 양을비교해서 or 최근 매수 주문, 매도주문을 조회해서
                    if round(float(had_cur[c]['balance'])+float(had_cur[c]['locked']), 8) < (b+l):  # 양이 늘었네, 매수됬네
                        boi = order_info(had_cur[c]['buy_uuid'])  # 매수정보를 조회
                        cus = boi['state']  # 상태조회

                        if cus == 'done' or cus == 'cancel':  # 완료면
                            b_price = float(boi['price'])  # 산 가격

                            new_standard_price = float(boi['price'])

                            buy_price = get_buy_price(price * (1-margin_rate))
                            buy_vol = round(standard_price / buy_price, 8)
                            buy_uuid = limit_buy_order(ticker, str(buy_vol), str(buy_price))
                            cell_price = get_cell_price(new_standard_price * (1 + margin_rate))

                            if b_price * (b+l) >= (standard_price * 2):  # 2배이상이면 매도 일반적주문
                                order_cancle(had_cur[c]['cell_uuid'])

                                cell_vol = round(standard_price * (1 + margin_rate) / cell_price, 8)
                                cell_uuid = limit_cell_order(ticker, str(cell_vol), str(cell_price))
                                had_cur[c] = {'balance': b, 'locked': l, 'buy_uuid': buy_uuid,
                                              'cell_uuid': cell_uuid}  # 보유 계좌에 추가
                            elif b_price * (b+l) >= standard_price:  # 1~2배 사이면 전량매도

                                post_message(c + "전량 매도주문")
                                cell_uuid = limit_cell_order(ticker, str(b+l), str(cell_price))
                                had_cur[c] = {'balance': b, 'locked': l, 'buy_uuid': buy_uuid,
                                              'cell_uuid': cell_uuid}  # 보유 계좌에 추가
                        print(had_cur)

                    elif round(float(had_cur[c]['balance'])+float(had_cur[c]['locked']), 8) > (b+l):  # 양이 감소, 매도
                        coi = order_info(had_cur[c]['cell_uuid'])
                        cus = coi['state']

                        if cus == 'done' or cus == 'cancel':

                            c_price = float(coi['price'])  # 판가격

                            order_cancle(had_cur[c]['buy_uuid'])  # 매수주문취소
                            new_standard_price = float(coi['price'])

                            buy_price = get_buy_price(new_standard_price * (1 - margin_rate))
                            buy_vol = round(standard_price / buy_price, 8)
                            buy_uuid = limit_buy_order(ticker, str(buy_vol), str(buy_price))

                            cell_price = get_cell_price(new_standard_price * (1 + margin_rate))

                            if c_price * (b+l) >= (standard_price * 2):  # 2배이상이면 일반적 매도 주문

                                cell_vol = round(standard_price * (1 + margin_rate) / cell_price, 8)
                                cell_uuid = limit_cell_order(ticker, str(cell_vol), str(cell_price))
                                had_cur[c] = {'balance': b, 'locked': l, 'buy_uuid': buy_uuid,
                                              'cell_uuid': cell_uuid}  # 보유 계좌에 추가

                            elif c_price * (b+l) >= standard_price:  # 1~2배 사이면 전량매도

                                post_message(c + "전량 매도주문")
                                cell_uuid = limit_cell_order(ticker, str(b + l), str(cell_price))
                                had_cur[c] = {'balance': b, 'locked': l, 'buy_uuid': buy_uuid,
                                              'cell_uuid': cell_uuid}  # 보유 계좌에 추가

                            elif c_price * (b+l) < standard_price:  # 총량이 적으면 매도 불가
                                post_message(c + " 매도 못해")
                                had_cur[c] = {'balance': b, 'locked': l, 'buy_uuid': buy_uuid}
                        print(had_cur)

                    else:
                        had_cur[c]['balance'] = b
                        had_cur[c]['locked'] = l

        remain_item = ((set(had_cur.keys())) - (set(road_list)))

        for i in remain_item:
            order_cancle(had_cur[i]['buy_uuid'])
            post_message(i + "가 전량 매도")
            del had_cur[i]

threading.Thread(target=mainloop).start()
