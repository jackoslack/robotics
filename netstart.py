from secret import SSID, PASSWORD

def do_connect():

    import network 
    import webrepl
    import time

    sta_if = network.WLAN(network.STA_IF)
    for _ in range(10):
        try:
            sta_if.connect('SSID', 'PASS')
            time.sleep(1)
        except:
            continue
    
        print('Trying to connect')
        
        if sta_if.isconnected():
            print('Connected.')
            break
            time.sleep(11)
        else:
            print('Fail')

    ap_if = network.WLAN(network.AP_IF)
    if ap_if.active():
        ap_if.active(False)
    
    if not sta_if.isconnected():
        print(b'connecting to network...')
        sta_if.active(True)
        
        sta_if.connect(SSID, PASSWORD)
        
        while not sta_if.isconnected():
            pass
        
    print('Network configuration:', sta_if.ifconfig())
    
    print("About to start webrepl.")
    time.sleep(2)
    
do_connect()

