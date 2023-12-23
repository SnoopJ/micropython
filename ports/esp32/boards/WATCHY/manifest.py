# this is executable Python, see micropython/tools/makemanifest.py
# note: interpolation of $VALUEs is done in makemanifest.py:convert_path(), not
# cmake or anything weird

freeze("$(PORT_DIR)/modules")
# freeze("$(MPY_DIR)/tools", ("upip.py", "upip_utarfile.py"))
# freeze("$(MPY_DIR)/ports/esp8266/modules", "ntptime.py")
# freeze("$(MPY_DIR)/drivers/dht", "dht.py")
# freeze("$(MPY_DIR)/drivers/onewire")
freeze("$(MPY_DIR)/ports/esp32/boards/WATCHY/modules", "wink.py")
# include("$(MPY_DIR)/extmod/uasyncio/manifest.py")
# include("$(MPY_DIR)/extmod/webrepl/manifest.py")

freeze("$(MPY_DIR)/ports/esp32/boards/WATCHY/", ("boot.py", "main.py"))
