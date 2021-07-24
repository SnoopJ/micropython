"""
Watchy e-ink display driver

(extremely WIP)
"""

from machine import Pin, I2C
import micropython
import struct
import time

# NOTE: these are GPIO pin numbers (i.e. IOxx on the Watchy sheet)
# Most pins initialized to HIGH
PIN_SCK = Pin(22, value=1)
PIN_SDA = Pin(23, value=1)

PIN_CS   = Pin(5, Pin.OUT, value=1)
PIN_DC   = Pin(10, Pin.OUT, value=1)
PIN_RES  = Pin(9, Pin.OUT, value=1)
PIN_BUSY = Pin(19, Pin.OUT, value=1)

PIN_VIB_MOTOR = Pin(13)

_CMD_DRIVER_CTL      = 0x01
_CMD_GATE_VOLTS_CTL  = 0x03
_CMD_SRC_VOLTS_CTL   = 0x04

_CMD_DEEP_SLEEP      = 0x10
_CMD_DATA_ENTRY      = 0x11
_CMD_SW_RESET        = 0x12

_CMD_MASTER_ACTIV    = 0x20  # "Activate Display Update Sequence"
                             # BUSY pad will output high during operation
_CMD_DISP_UPDATE1    = 0x21  # "RAM content option for Display Update"
_CMD_DISP_UPDATE2    = 0x22  # "Display Update Sequence Option: Enable the stage for Master Activation"
_CMD_WRITE_RAM_BW    = 0x24
_CMD_WRITE_RAM_RED   = 0x26

_CMD_RAM_OFFSETS_X   = 0x44  # DATA: 2 bytes (low 6 bits each) specifying X start/end offsets
_CMD_RAM_OFFSETS_Y   = 0x45  # DATA: 4 bytes (8+1 lowest bits x2 each) specifying Y start/end offsets
_CMD_RAM_START_X     = 0x4E  # DATA: 1 bytes, low 6 bits
_CMD_RAM_START_Y     = 0x4F  # DATA: 2 bytes, 8+1 low bits

def rev(buf):
    return bytearray(reversed(buf))

def EPD_wait(MAX_WAIT=1000e-3):
    print("Waiting on PIN_BUSY")
    start = time.time()
    PIN_BUSY.init(mode=Pin.OUT, value=1)
    PIN_BUSY.on()
    PIN_BUSY.init(mode=Pin.IN)
    dump_pins()
    time.sleep(1e-3)
    while PIN_BUSY() > 0:
        print("BUSY")
        if time.time() - start >= MAX_WAIT:
            raise RuntimeError("Timed out waiting on PIN_BUSY")
        time.sleep(1e-3)
    else:
        print("PIN_BUSY is low, done waiting after {:.3e} sec".format(time.time() - start))


def dump_pins():
    names = ("PIN_CS", "PIN_DC", "PIN_RES", "PIN_BUSY")
    PIN_BUSY.init(mode=Pin.IN)
    vals = (PIN_CS(), PIN_DC(), PIN_RES(), PIN_BUSY())

    for n in names:
        print("{:>12s}".format(n), end="")
    print()
    for v in vals:
        print("{:>12d}".format(v), end="")
    print()


def CMD(cmd, data=None, comment=""):
    # don't forget to call EPD_wait() before using!
    print("CMD>> {:<10s} {:02x} | ".format(comment, cmd), end="")

    if isinstance(cmd, int):
        assert 0 < cmd < 256
        cmd = struct.pack("B", cmd)

    # print("setting CS=OFF, DC=OFF")
    PIN_CS.off()
    PIN_DC.off()

    COMM.write(cmd)

    PIN_DC.on()
    # print("PIN_DC (on?) >> {}".format(PIN_DC()))

    if data != None:
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("data must be bytes or bytearray")
        SPI.write(data)
        for cnt, b in enumerate(data[:10]):
            print("{:02x}".format(b), end=" ")
            if cnt and cnt % 16 == 0:
                print("\n\t", end="")
        if len(data) > 10:
            print(" ... ({:d} bytes)".format(len(data)))
        else:
            print()

    else:
        print("<no DATA>")

    PIN_DC.off()
    PIN_CS.on()
    # print("PIN_CS (on?) >> {}".format(PIN_CS()))
    # print("PIN_DC (off?) >> {}".format(PIN_DC()))


def EPD_hw_reset():
    # NOTE: the datasheet doesn't explicitly mention doing this after sending commands etc.,
    #       but I'm pretty sure this can be done at any point after applying VCI
    #       (i.e. while Watchy is powered on), especially since it's called "Software Reset"
    # print("Beginning soft reset")
    EPD_RESET_TIME = 10e-3  # datasheet calls for 10 ms

    PIN_DC.on()
    PIN_CS.on()
    PIN_SDA.on()
    PIN_SCK.on()
    PIN_RES.on()
    PIN_BUSY.init(mode=Pin.OUT)
    PIN_BUSY.on()

    print("RES: ", PIN_RES())

    PIN_RES.off()
    print("RES: ", PIN_RES())
    time.sleep(EPD_RESET_TIME)
    PIN_RES.on()
    print("RES: ", PIN_RES())
    time.sleep(EPD_RESET_TIME)

    CMD(_CMD_SW_RESET, comment="SW_RESET")
    time.sleep(EPD_RESET_TIME)

    # print("Panel soft reset complete")


def EPD_init():
    # print("Sending initialization code")
    CMD(_CMD_DRIVER_CTL, b"\xc7\x00\x00", comment="DRVR_CTL")
    #   9 bits (2 bytes) of gate MUX
    # + 3 bits (1 byte) of gate driver scanning order
    #   xxxxxxxx  # 8 bits MUX
    #   0000000x  # 1 bit MUX
    #   00000xxx  # 3 bits scan order

    # These...don't match the datasheet? But both GxEPD2 and the sample do this
    # print("Setting border waveform")
    CMD(0x3C, data=b"\x05", comment="??")  # BorderWavefrom
    # print(""""Reading" the temperature sensor""")
    CMD(0x18, data=b"\x80", comment="??")  # Reading temperature sensor
    # CMD(0x1A, b"\x0190", comment="??")
    # CMD(0x22, b"\xb1", comment="??")
    # CMD(_CMD_MASTER_ACTIV, comment="M_ACTIV")


dump_pins()

# print("Initialize SPI")
# COMM = SoftSPI(sck=PIN_SCK, mosi=PIN_SDA, miso=PIN_SDA)
# COMM.init()
COMM = I2C("GDEH0154D67", scl=PIN_SCK, sda=PIN_SDA)
COMM.start()
dump_pins()

EPD_hw_reset()
EPD_init()
dump_pins()

# Configure address counter order (01 = decrementing Y, incrementing X)
# print("Configure address counter order")
CMD(_CMD_DATA_ENTRY, b"\x03", comment="DATA_ENTRY")

# Configure X/Y RAM extent
#
# NOTE: original sample says "0x0C --> (18+1)*8 = 200" and I have no idea what the 0x0C is...
#
# 0xc7 = 199, so the Y part of this makes sense to me
# which I think means there are 0x19 = 25 addressable lines of 8 pixels apiece (25*8 = 200)
# i.e. I know the screen is logically divided up like:
#
#       ,_____,_____,_____,       ,______,______,______,
#       |     |     |     |       |      |      |      |
#       | x=0 | x=1 | x=2 |  ...  | x=23 | x=24 | x=25 |
#       | y=0 | y=0 | y=0 |       | y=0  | y=0  | y=0  |
#       `-----´-----`-----´       `------´------`------´
#       ,_____,_____,_____,       ,_____,_____,_____,
#       |     |     |     |       |     |     |     |
#       | x=0 | x=1 | x=2 |  ...  | x17 | x18 | x19 |
#       | y=1 | y=1 | y=1 |       |     |     |     |
#       `-----´-----`-----´       `-----´-----`-----´
#
# and since we know X is addressed with fewer bits, its probably laid out in 
# memory like this:
#
#           ---------SCREEN RAM BEGIN-------------
#                                                 
#  $00000      XX XX XX XX  |  x =  0,  y =   0   
#  $00004      XX XX XX XX  |  x =  1,  y =   0   
#  $00008      XX XX XX XX  |  x =  2,  y =   0   
#                          ...                    
#  $09c38      XX XX XX XX  |  x = 24,  y =   0   
#  $09c3c      XX XX XX XX  |  x = 25,  y =   0   
#                                                 
#           ----------HLINE BOUNDARY--------------
#                                                 
#  $09c40      XX XX XX XX  |  x =  0,  y =   1   
#  $09c44      XX XX XX XX  |  x =  1,  y =   1   
#  $09c48      XX XX XX XX  |  x =  2,  y =   1   
#                                                 
#                          ...                    
#                                                 
#  $13878      XX XX XX XX  |  x = 24,  y =   1   
#  $1387c      XX XX XX XX  |  x = 25,  y =   1   
#                                                 
#           ----------HLINE BOUNDARY--------------
#                                            
#                  ... and so on ...         
#                                            
#            ------SCREEN RAM END------------
#
# and given x,y, you calculate the offset from $BEGIN as:
#       px = $BEGIN + y*199 + x
#
# print("Configure screen layout")
CMD(_CMD_RAM_OFFSETS_X, b"\x00\x18")
CMD(_CMD_RAM_OFFSETS_Y, b"\x00\x00\xc7\x00")
# print("Setting border waveform")
# print("Setting initial X/Y address counts")
CMD(_CMD_RAM_START_X, data=b"\00")        # set RAM x address count to 0
CMD(_CMD_RAM_START_Y, data=b"\x00\x00")  # set RAM y address count to 199
CMD(_CMD_DISP_UPDATE2, data=b"\xF8")
CMD(_CMD_MASTER_ACTIV)

EPD_wait()

def EPD_screen_ready():
    CMD(_CMD_DATA_ENTRY, b"\x03", comment="DATA_ENTRY")
    CMD(_CMD_RAM_OFFSETS_X, b"\x00\x18")
    CMD(_CMD_RAM_OFFSETS_Y, b"\x00\x00\xc7\x00")
    CMD(_CMD_RAM_START_X, data=b"\00")        # set RAM x address count to 0
    CMD(_CMD_RAM_START_Y, data=b"\x00\x00")  # set RAM y address count to 199


def EPD_screen_update():
    # print("Performing screen update")
    CMD(_CMD_DISP_UPDATE2, b"\xf4", comment="DISP_UP2")
    CMD(_CMD_MASTER_ACTIV, comment="M_ACTIV")


# 5000 bytes of image to write into RAM
blank = b"\x00" * 5000
img = b"\x00\xFF" * 2500

EPD_screen_ready()
CMD(_CMD_WRITE_RAM_RED, img)
CMD(_CMD_DISP_UPDATE2, data=b"\xFC")
CMD(_CMD_MASTER_ACTIV, comment="M_ACTIV")
EPD_screen_ready()
CMD(_CMD_WRITE_RAM_BW, img)
CMD(_CMD_DISP_UPDATE2, data=b"\x83")
CMD(_CMD_MASTER_ACTIV, comment="M_ACTIV")
CMD(_CMD_SW_RESET, comment="SW_RESET")
EPD_init()
EPD_screen_ready()
EPD_screen_update()
EPD_wait()
