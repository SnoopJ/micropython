```
 _    _       _       _    ______
| |  | |     | |     | |   | ___ \
| |  | | __ _| |_ ___| |__ | |_/ /   _
| |/\| |/ _` | __/ __| '_ \|  __/ | | |
\  /\  / (_| | || (__| | | | |  | |_| |
 \/  \/ \__,_|\__\___|_| |_\_|   \__, |
                                  __/ |
                                 |___/
```

## Dependencies

Incomplete and guessing-heavy list until this project stabilizes

* [MicroPython](http://micropython.org/)
* [ESP-IDF](https://github.com/espressif/esp-idf)
* Arduino (arduino-base? arduino-esp32? probably not the esp32 one)
* [Adafruit_GFX](https://github.com/adafruit/Adafruit-GFX-Library)
* [GxEPD2](https://github.com/ZinggJM/GxEPD2)

## What is this?

I'm learning how to customize [MicroPython](http://micropython.org/),
the [Python](https://www.python.org/) runtime that is _"optimised to run
on microcontrollers and in constrained environments."_

More specifically, I would like to create a build that includes the
[GxEPD2](https://github.com/ZinggJM/GxEPD2) display library or something like it
for e-ink screens, and some other libraries.

## More information

I recently got a [Watchy](https://watchy.sqfmi.com/), an open-source smartwatch
designed around the [ESP32](https://en.wikipedia.org/wiki/ESP32) system-on-a-chip.
To my great delight, it can run Python! I'd like to do more than evaluate `print("Hello world!")`
in a REPL over a serial connection, though, so some drivers are needed to interact
with the watch's hardware.

## Supported hardware features (in order of approximate priority)

* [x] ESP32 capabilities (thanks to MicroPython's `GENERIC` board build!)
* [ ] E-ink display ([GDEH0154D67](doc/reference/GDEH0154D67-0111.pdf))
  * It turns out the GxEPD2 library is GPLv3, which is a hard incompatibility
    with MicroPython's MIT license.
* [ ] Hardware buttons
* [ ] Real-time controller (RTC) (DS3231MZ)
  * My Watchy was one of the [unlucky few](https://github.com/sqfmi/Watchy/issues/40#issuecomment-873029971)
    that was assembled with a malfunctioning RTC clock. Until that's fixed, I
    won't be able to test the clock functionality.
  * I'd like to support the [stable workaround](https://github.com/sqfmi/Watchy/issues/40#issuecomment-865497570)
    for the above flaw in this project, which should be pretty free because of MicroPython's close compatibility
    with ESP-IDF.
* [ ] Vibration motor
* [ ] Accelerometer (BMA423)
