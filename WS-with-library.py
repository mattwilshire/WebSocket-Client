import websocket
import _thread
import time
import rel
import json

def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("Opened connection")
    x = {
      "Identifier": 123,
      "Message": "playerlist",
      "Name": "WebRcon"
    }

    ws.send(json.dumps(x))

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://127.0.0.1:28016/test",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)

    ws.run_forever(dispatcher=rel)
    rel.signal(2, rel.abort)
    rel.dispatch()