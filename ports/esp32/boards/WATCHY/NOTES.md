## Notes (in reverse chronological order)

* or I think you can define `sdfconfig.ext` in the boards/ subdir directly?
* mpconfigboard.cmake is where ESP-IDF settings (i.e. CONFIG_ESP32_RTC_CLOCK_SOURCE_INTERNAL_8MD256) get into the build
* idf.py workflow likely to be least headache at first
* a bunch of sdkconfig files get smushed together and you end up in ESP-IDF at the end of the day, with a project named micropython
* not sure how a new module gets into the build...

## References

* [Implementing a Module](http://docs.micropython.org/en/latest/develop/library.html) - "This chapter details how to implement a core module in MicroPython."
