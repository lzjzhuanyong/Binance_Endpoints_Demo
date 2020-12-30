import requests
import hmac
import hashlib
import time
import urllib.parse
import base64
import json

api_key = ""
secret_key= ""
base_url = "https://api.binance.com"
path = '/sapi/v1/sub-account/universalTransfer'
timestamp = round(time.time()*1000)
params = {
    "timestamp": timestamp,
    "recvWindow": 5000, 
    "fromEmail": "xxxxxx@xxxx.com",
    "toEmail": "xxxxxx@xxxx.com",
    "fromAccountType": "SPOT",
    "toAccountType": "SPOT",
    "asset": "XTZ",
    "amount": 1,

}
querystring = urllib.parse.urlencode(params)

#urlencode会将特殊字符，如@，转义为，%40。以此查询字符串，query string计算获得的签名是以其中的"%40"计算获得的。
#而以request body的方式传递参数是直接将dict类型中的"@"字符传递给服务器，服务器会以其中的"@"字符直接计算签名跟用户传递的签名对比，会导致两者的签名不同，报-1022错误。
#如果以request body传，需要在前面获得签名时，提前将"%40"替换为"@"。或者直接以query string的方式进行请求。

querystring = querystring.replace("%40","@")
print(querystring)

signature = hmac.new(secret_key.encode('utf-8'),msg = querystring.encode('utf-8'), digestmod = hashlib.sha256).hexdigest()
print(signature)

#signature1 = base64.b64encode(hmac.new(secret_key.encode('utf-8'),msg = querystring.encode('utf-8'), digestmod = hashlib.sha256).digest())
#print(signature1)

url = base_url + path #+ '?' + querystring + '&signature='+ signature

params["signature"]= signature

payload = params

headers= {
    'Content-Type':'application/x-www-form-urlencoded',
    'X-MBX-APIKEY': api_key
}

response = requests.request("POST", url, headers=headers, data = payload)
print(response.text.encode('utf8'))
