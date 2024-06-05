import pwn
def ping(port , address):
    try:
        print(port)
        instance = pwn.remote(address, port,timeout=10)
        state = instance.recvline()
        instance.close()
        print(state)
        return {"state": "online"}
    except Exception as e:
        return {"state": 'offline'}

print(ping(49039, '192.168.109.145'))