import pwn
class Executor:
    def __init__(self, inputed_type):
        self.type = inputed_type
    
    def ping(self , port , address):
        try:
            print(port)
            instance = pwn.remote(address, port,timeout=10)
            state = instance.recvline()
            instance.close()
            print(state)
            return {"state": "online"}
        except Exception as e:
            print(e)
            return {"state": 'offline'}
        