import time
from machine import Pin


PIN_VIB = Pin(13, Pin.OUT)

def hullaballoo():
    for _ in range(4):
        PIN_VIB.on()
        time.sleep(0.100)
        PIN_VIB.off()
        time.sleep(0.110)

def caneck():
    for _ in range(2):
        PIN_VIB.on()
        time.sleep(0.100)
        PIN_VIB.off()
        time.sleep(0.150)

hullaballoo()
time.sleep(0.065)
caneck()
time.sleep(0.035)
caneck()

#try:
#    print("Trying to import wink...")
#    import wink
#except ImportError:
#    print("Can't import e-ink driver")
