const WebSocket = require("ws")

const wss = new WebSocket("wss://stream.binance.com:9443/stream")

function timeNow(){
    let timestamp = Date.now();
    let date = new Date(timestamp);
    //console.log(date)
    date = date.toUTCString();
    //let 
    return date;
}
//ping pong test
wss.on('open', ()=>{
    console.log("open :" + timeNow())
    wss.ping();
})

wss.on('ping',()=>{
    console.log("ping :" + timeNow())
    wss.pong();
})

//ping is sended from the server, pong will reply by client as the client received the ping
wss.on('pong',()=>{
    console.log("pong :" + timeNow())
})

wss.on('close',()=>{
    console.log("close :" + timeNow())
})

wss.on('message', data=>{
    //console.log(typeof data)
    //onsole.log(data)
    //let body = JSON.parse(data)
    //console.log("current timestamp:",Date.now());
    //console.log("The timestamp the data sent from server:",body[0].e);
    //let lagtime = Date.now() - body.data.E;
    //console.log("The lag of the time: ",lagtime)
    
})
