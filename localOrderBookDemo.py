import websocket
import json
import requests
import urllib.parse

def step1_connectWSS(symbol):
    ws = websocket.create_connection("wss://stream.binance.com:9443/ws/"+symbol.lower()+"@depth")
    return ws

def step2_getDiffDepth(wss):
    return json.loads(wss.recv())

def step3_getRestDepth(symbol,limit):
    api_key = ''
    base_url = "https://api.binance.com"
    endpoint_path = '/api/v3/depth'
    params = {
        "symbol":symbol,
        "limit": limit,
    }

    querystring = urllib.parse.urlencode(params)

    url = base_url + endpoint_path + "?" + querystring

    payload = {}

    #print(payload)

    headers= {
        'Content-Type':'application/x-www-form-urlencoded',
        'X-MBX-APIKEY': api_key
    }

    response = requests.request("GET", url, headers=headers, data = payload)
    return response.json()

#print(bidsPrice)
def ste4n5_matchDepth(wsdepthdata,restdepthdata):
    while True:
        if wsdepthdata["U"]<= restdepthdata["lastUpdateId"] + 1 and wsdepthdata["u"] >= restdepthdata["lastUpdateId"] + 1:
            #print(wsdepthdata["U"],restdepthdata["lastUpdateId"],wsdepthdata["u"])
            break
            # while True:
            #     wsdepthdata = json.loads(ws.recv())
        elif restdepthdata["lastUpdateId"] + 1 > wsdepthdata["u"]:
            wsdepthdata = step2_getDiffDepth(wss)
            #print(wsdepthdata["U"],restdepthdata["lastUpdateId"],wsdepthdata["u"])
        elif restdepthdata["lastUpdateId"] + 1 < wsdepthdata["U"]:
            restdepthdata = step3_getRestDepth()
            #print(wsdepthdata["U"],restdepthdata["lastUpdateId"],wsdepthdata["u"])
    return (wsdepthdata,restdepthdata)

def updateOrderBook(wsdepthdata,restdepthdata): 
    finalBidsPrices = list()
    #finalBidsQtys = list()

    finalAsksPrices = list()
    #finalAsksQtys = list()

    finalBids = restdepthdata["bids"]
    finalAsks = restdepthdata["asks"]

    for element in range(len(finalBids)):
        finalBidsPrices.append(float(finalBids[element][0]))
        #finalBidsQtys.append(float(finalBids[element][1]))
        finalAsksPrices.append(float(finalAsks[element][0]))
        #finalAsksQtys.append(float(finalAsks[element][1]))


    updateBids = wsdepthdata["b"]
    updateAsks = wsdepthdata["a"]


    updateBidsPrices = list()
    #updateBidsQtys = list()

    updateAsksPrices = list()
    #updateAsksQtys = list()

    for upbid in updateBids:
        updateBidsPrices.append(float(upbid[0]))
        #updateBidsQtys.append(float(upbid[1]))

    for upask in updateAsks:
        updateAsksPrices.append(float(upask[0]))
        #updateAsksQtys.append(float(upask[1]))

    #insert bids
    for upBidPrice in updateBidsPrices:

        #check if the price has in the depth
        if upBidPrice in finalBidsPrices:

            finalIndex = finalBidsPrices.index(upBidPrice)
            updateIndex = updateBidsPrices.index(upBidPrice)
            
            #delete the depth with quantity 0
            if float(updateBids[updateIndex][1]) == 0:
                finalBidsPrices.pop(finalIndex)
                #finalBidsQtys.pop(finalIndex)

                finalBids.pop(finalIndex)

            else:

                #finalBidsQtys[finalIndex] = updateBidsQtys[updateIndex]
                
                finalBids[finalIndex] = updateBids[updateIndex]
        else:

            updateIndex = updateBidsPrices.index(upBidPrice)
            if float(updateBids[updateIndex][1]) > 0: 
                
                if len(finalBidsPrices) == 0: 
                    updateIndex = updateBidsPrices.index(upBidPrice)

                    
                    finalBidsPrices.insert(0,upBidPrice)
                    #finalBidsQtys.insert(0,updateBidsQtys[updateIndex])

                    finalBids.insert(0,updateBids[updateIndex])
                else: 
                #insert the depth into the final data
                    if upBidPrice < finalBidsPrices[0] and upBidPrice > finalBidsPrices[len(finalBidsPrices)-1]:
                        for i in range(len(finalBidsPrices)-1):
                            if (finalBidsPrices[i]-upBidPrice)*(finalBidsPrices[i+1]-upBidPrice) < 0:

                                updateIndex = updateBidsPrices.index(upBidPrice)

                                finalBidsPrices.insert(i+1,upBidPrice)
                                #finalBidsQtys.insert(i+1,updateBidsQtys[updateIndex])

                                finalBids.insert(i+1,updateBids[updateIndex])

                                if(len(finalBids) > limit):
                                    finalBidsPrices.pop()
                                    #finalBidsQtys.pop()
                                    finalBids.pop()
                    
                    #insert the depth as the best one
                    elif upBidPrice > finalBidsPrices[0] :

                        updateIndex = updateBidsPrices.index(upBidPrice)

                        
                        finalBidsPrices.insert(0,upBidPrice)
                        #finalBidsQtys.insert(0,updateBidsQtys[updateIndex])

                        finalBids.insert(0,updateBids[updateIndex])
                        
                        if(len(finalBids) > limit):
                            finalBidsPrices.pop()
                            #finalBidsQtys.pop()
                            finalBids.pop()

                    #inserrt the depth as the last one
                    elif len(finalBids) < limit and upBidPrice < finalBidsPrices[len(finalBidsPrices)-1]:
                        updateIndex = updateBidsPrices.index(upBidPrice)

                        finalBidsPrices.append(upBidPrice)
                        #finalBidsQtys.append(updateBidsQtys[updateIndex])
                        finalBids.append(updateBids[updateIndex])

    #insert asks
    for upAskPrice in updateAsksPrices:

        #check if the price has in the depth
        if upAskPrice in finalAsksPrices:

            finalIndex = finalAsksPrices.index(upAskPrice)
            updateIndex = updateAsksPrices.index(upAskPrice)
            
            #delete the depth with quantity 0
            if float(updateAsks[updateIndex][1]) == 0:
                finalAsksPrices.pop(finalIndex)
                #finalAsksQtys.pop(finalIndex)
                finalAsks.pop(finalIndex)

            else:

                #finalAsksQtys[finalIndex] = updateAsksQtys[updateIndex]
                
                finalAsks[finalIndex] = updateAsks[updateIndex]
        else:
            updateIndex = updateAsksPrices.index(upAskPrice)

            if float(updateAsks[updateIndex][1]) > 0:
                #insert the depth into the final data
                if len(finalAsksPrices) == 0:
                    updateIndex = updateAsksPrices.index(upAskPrice)

                    

                    finalAsksPrices.insert(0,upAskPrice)
                    #finalAsksQtys.insert(0,updateAsksQtys[updateIndex])

                    finalAsks.insert(0,updateAsks[updateIndex])

                else:
                    if upAskPrice > finalAsksPrices[0] and upAskPrice < finalAsksPrices[len(finalAsksPrices)-1]:
                        for i in range(len(finalAsksPrices)-1):
                            if (finalAsksPrices[i]-upAskPrice)*(finalAsksPrices[i+1]-upAskPrice) < 0:

                                updateIndex = updateAsksPrices.index(upAskPrice)

                                finalAsksPrices.insert(i+1,upAskPrice)
                                #finalAsksQtys.insert(i+1,updateAsksQtys[updateIndex])

                                finalAsks.insert(i+1,updateAsks[updateIndex])

                                if(len(finalAsks) > limit):
                                    finalAsksPrices.pop()
                                    #finalAsksQtys.pop()
                                    finalAsks.pop()
                    
                    #insert the depth as the best one
                    elif upAskPrice < finalAsksPrices[0] :

                        updateIndex = updateAsksPrices.index(upAskPrice)

                        

                        finalAsksPrices.insert(0,upAskPrice)
                        #finalAsksQtys.insert(0,updateAsksQtys[updateIndex])

                        finalAsks.insert(0,updateAsks[updateIndex])
                        
                        if(len(finalAsks) > limit):
                            finalAsksPrices.pop()
                            #finalAsksQtys.pop()
                            finalAsks.pop()

                    #insert the depth as the last one
                    elif len(finalAsks) < limit and upAskPrice > finalAsksPrices[len(finalAsksPrices)-1]:
                        updateIndex = updateAsksPrices.index(upAskPrice)

                        finalAsksPrices.append(upAskPrice)
                        #finalAsksQtys.append(updateAsksQtys[updateIndex])
                        finalAsks.append(updateAsks[updateIndex])

    return (finalBids,finalAsks)


limit = 100
symbol = "BTCUSDT"

wss = step1_connectWSS(symbol)
wsdepthdata = step2_getDiffDepth(wss)
restdepthdata = step3_getRestDepth(symbol,limit)

#print(wsdepthdata["U"],restdepthdata["lastUpdateId"],wsdepthdata["u"])

(wsdepthdata, restdepthdata) = ste4n5_matchDepth(wsdepthdata,restdepthdata)

#print(wsdepthdata["U"],restdepthdata["lastUpdateId"],wsdepthdata["u"])

(Bids,Asks) = updateOrderBook(wsdepthdata,restdepthdata)


while True:
    newWsDepthData = step2_getDiffDepth(wss)

    if newWsDepthData["U"] == wsdepthdata["u"]+1:
        (Bids,Asks) = updateOrderBook(newWsDepthData,restdepthdata)
        print("Asks",Asks)
        print("Bids",Bids)
    else:
        newRestDepthData = step3_getRestDepth(symbol,limit)
        #print(newWsDepthData["U"],newRestDepthData["lastUpdateId"],newWsDepthData["u"])

        (wsdepthdata, restdepthdata) = ste4n5_matchDepth(newWsDepthData,newRestDepthData)

        #print(wsdepthdata["U"],restdepthdata["lastUpdateId"],wsdepthdata["u"])

        (Bids,Asks) = updateOrderBook(wsdepthdata,restdepthdata)
        print("Asks",Asks)
        print("Bids",Bids)
        
