import time

def rticket():
    ticket = str(time.time() * 1000).split(".")[0]
    return ticket

def ts():
    timestamp = str(time.time()).split(".")[0]
    return timestamp