EMSCRIPTEN_SDK_ROOT=/path/to/emsdk
WASI_SDK_ROOT=/path/to/wasi-sdk/
WABT_ROOT=/path/to/wabt
UVWASI_ROOT=/path/to/uvwasi

EMCC = $(EMSCRIPTEN_SDK_ROOT)/upstream/emscripten/emcc

WASM2C = $(WABT_ROOT)/bin/wasm2c
# NOTE: the 'real' clang, not Emscripten's faux clang
WASM2C_CC = clang
