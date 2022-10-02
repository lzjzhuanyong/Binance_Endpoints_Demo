import requests
import hmac
import hashlib
import time
import urllib.parse
import json

api_key = ""
secret_key= ""
base_url = "https://testnet.binancefuture.com"
endpoint_path = '/fapi/v1/batchOrders'

sub_order1 = {

    "strategySubId": "1",
    "firstDrivenId":"0", #没有首次触发限制，直接下单
    "secondDrivenId": "0", #没有二次触发操作

    "symbol": "BTCUSDT",
    "side": "BUY",
    "type": "LIMIT",
    "quantity": "0.001",
    "price": "10000",
    "positionSide": "LONG",
    "timeInForce": "GTC",
    "newClientOrderId": "web-strategy1190874-1",
}

sub_order2 = {
    "strategySubId": "2",

    "firstDrivenId": "1",  #受1号订单影响首次触发
    "firstDrivenOn": "PARTIALLY_FILLED_OR_FILLED",  #1号订单部分成交首次触发本订单
    "firstTrigger": "PLACE_ORDER", #首次触发后本订单执行下单操作

    "secondDrivenId": "3",  #受3号订单状态影响二次触发操作
    "secondDrivenOn": "FILLED",  #3号订单完全成交二次触发本订单
    "secondTrigger": "CANCEL_ORDER",  #二次触发后本订单执行撤单操作
                    
    "symbol": "BTCUSDT",
    "side": "SELL",                               
    "positionSide": "LONG",
    "type": "TAKE_PROFIT_MARKET",                        
    #"price": "22000",                              
    "stopPrice": "22000",                     
    "timeInForce": "GTE_GTC",   #使用GTE类型的tif
    "quantity": "0.001",
    "workingType": "MARK_PRICE",
    "newClientOrderId": "web-strategy1190874-2"
}

sub_order3 = {
    "strategySubId": "3",

    "firstDrivenId": "1",  #受1号订单影响首次触发
    "firstDrivenOn": "PARTIALLY_FILLED_OR_FILLED",  #1号订单部分成交首次触发本订单
    "firstTrigger": "PLACE_ORDER",   #首次触发后本订单执行下单操作

    "secondDrivenId": "2",   #受2号订单状态影响二次触发操作
    "secondDrivenOn": "FILLED",   #2号订单完全成交二次触发本订单
    "secondTrigger": "CANCEL_ORDER",    #二次触发后本订单执行撤单操作
                    
    "symbol": "BTCUSDT",
    "side": "SELL",                                 
    "positionSide": "LONG",
    "type": "STOP_MARKET",                             
    #"price": "12000",                           
    "stopPrice": "12000",
    "timeInForce": "GTE_GTC",                    
    "quantity": "0.001",                                                         
    "workingType": "MARK_PRICE",  
    "newClientOrderId": "web-strategy1190874-3"           
           
}

#batchOrders = '[{"symbol":"BTCUSDT","side":"BUY","type":"MARKET","quantity":"0.001"},{"symbol":"ETHUSDT","side":"BUY","type":"MARKET","quantity":"0.01"}]'
#batchOrders = "[{'symbol':'BTCUSDT','side':'BUY','positionSide':'LONG','type':'LIMIT','quantity':'0.1','price':'40000','timeInForce':'GTC'},{'symbol':'BTCUSDT','side':'BUY','positionSide':'LONG','type':'LIMIT','quantity':'0.1','price':'38000','timeInForce':'GTC'}]"

batchOrders = '[' + json.dumps(sub_order1) + "," + json.dumps(sub_order2) + "," + json.dumps(sub_order3) + ']'

params = {
    "batchOrders": batchOrders,
    "timestamp" : round(time.time()*1000),
    "recvWindow" : 50000
}
querystring = urllib.parse.urlencode(params)
print(querystring,"\n")

signature = hmac.new(secret_key.encode('utf-8'),msg = querystring.encode('utf-8'), digestmod = hashlib.sha256).hexdigest()
url = base_url + endpoint_path + "?" + querystring + "&signature=" + signature
print(url,"\n")

#params["signature"] = signature
payload = {}
headers= {
    'Content-Type':'application/x-www-form-urlencoded',
    'X-MBX-APIKEY': api_key
}

response = requests.request("POST", url, headers=headers, data = payload)
print(response.text.encode('utf8'))
