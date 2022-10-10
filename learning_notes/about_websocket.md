### 关于python的[websocket-client](https://pypi.org/project/websocket-client/)库的学习

  对该库作了一番探索，虽然还没有针对较为底层对socket网络处理有深入的了解，但对该模块在建立连接后的处理有了一些深入的了解。
  
  首先_app.py文件中的WebSocketApp类和_core.py文件中的WebSocket类是两个独立的类，并非相互继承关系，这点之前没有关注到。
  
  另外，WebSocket实例是Iterator对象，可以用next持续获取下一个新数据。
  
  这几天最令人困扰的一个问题是，WebSocketApp实例在on_message方法中主动进行close，却无法触发编写好的on_close函数。
  但是在on_open中进行close，却能成功触发on_close，非常令人费解。
  
  *One of the most troubling issues these days is that WebSocketApp instances that actively close in the on_message function do not trigger the pre-written on_close function.
  However, when I do close in on_open function, it successfully triggers on_close, which is very puzzling.*
  
  深入研究了_app.py后才发现，在on_open中直接调用WebSocketApp实例的close()，会导致在run_forever的过程中self.sock从WebSocket实例[^注一]转变为None，然后导致异常抛出[^注二]。
  抛出异常后，会去运行run_forever中except部分的代码，先去调用on_error，然后再调用teardown()，而teardown中正好会去回调(callback)on_close。
  自此，on_open中进行close可以正常触发on_close的逻辑得到了理顺，剩下的就是为什么on_message中调用close无法触发on_close。
  
  [^注一]: 是的，WebSocketApp实例在运行的过程中仍旧需要新建一个WebSocket实例，虽然他们两者没有继承关系，但他们之间仍有功能上但联系
  [^注二]: 应该是在dispatcher调用read时抛出的异常。
  
  我查看了WebSocketApp类中的close方法的代码，发现还是挺简单的，就只有关闭websocket连接的逻辑，没有进行回调函数的代码，应该是这个原因。
  然后我就手动在close方法里加了回调on_close的代码，但是运行时仍旧无法触发on_close，这时候就更令人疑惑了。
  在仔细来回看许多遍close和_callback的代码后，才发现是因为加的回调函数，在调用on_close时，参数没对上。
  在写的on_close函数中需要三个参数(ws,close_status_code,close_msg)，但之前设置回调的时候就没有传参，结果就是函数没正常调用。
  由于是在库里加的，实例化后也没报错，就有点摸不着头脑了。后面在设置了正确的参数后，就能正常回调触发on_close了，算是最终也搞定了后面那个问题。
  
        # websocket-client/websocket/_app.py
        
        def close(self, **kwargs):
        """
        close websocket connection.
        """
        self.keep_running = False
        if self.sock:
            self.sock.close(**kwargs)
            self.sock = None
        #manually added
        self._callback(self.on_close,None,None)
   
  但是手动在库里加东西总也不是个事，而要在外部主动关闭连接时去触发on_close，就只能手动去调了。
        
        # WebSocketApp instance example
        
        import websocket
        import time

        def on_message(ws, message):
            print(message)

            time.sleep(3)
            ws.close()
            
        def on_error(ws, error):
            print(error)
            print("error")

        def on_close(ws, close_status_code, close_msg):
            print("### closed ###")
            #print(close_status_code,close_msg)

        def on_open(ws):
            print("Opened connection")
            #ws.close()
            #ws.send('{"method": "SUBSCRIBE","params":["btcusdt@aggTrade","btcusdt@depth"],"id": 1}')

        if __name__ == "__main__":
            #websocket.enableTrace(True)
            ws = websocket.WebSocketApp("wss://stream.binance.com:9443/stream?streams=btcusdt@aggTrade",
                                      on_open=on_open,
                                      on_message=on_message,
                                      on_error=on_error,
                                      on_close=on_close)

            ws.run_forever()
  
  
至此，这个疑问算是结束了。后续有新的问题，继续探索学习。
  
