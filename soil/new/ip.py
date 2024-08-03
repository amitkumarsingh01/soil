import network

def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    while not wlan.isconnected():
        pass
    
    print('Network config:', wlan.ifconfig())

# Replace with your network credentials
connect_to_wifi('Project', '12345678')

