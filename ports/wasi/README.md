MicroPython WebAssembly
=======================

MicroPython for [WebAssembly](https://webassembly.org/) using the
[WebAssembly System Interface (WASI)](https://wasi.dev/).

NOTE: I make no guarantees about the functionality or safety of this port, it
was built in the spirit of experimentation, and I provide this code without
warranty.

Dependencies
------------

### WASM only

* [Emscripten SDK](https://github.com/emscripten-core/emsdk/)

### Custom runtime

* [WASI SDK](https://github.com/WebAssembly/wasi-sdk)
* [wabt](https://github.com/WebAssembly/wabt/)
  * NOTE: the version of `wasm2c` shipped with Ubuntu 20.04 is too old to build
    this project. For best results, use `wabt` from source.
* [uvwasi](https://github.com/nodejs/uvwasi)
  * NOTE: `uvwasi` depends on [`libuv`](https://github.com/libuv/libuv), I have
    been using the version provided by Ubuntu 20.04's `libuv1-dev==1.34.2-1ubuntu1.3`

Building
--------

Before building, copy [`wasmenv.mk.example`](wasmenv.mk.example) to `wasmenv.mk`
and edit the paths therein to locate the dependencies listed above.

### WASM only

Only the Emscripten SDK is required to build the WASM version of MicroPython.

```
make build/wasm/micropython.wasm
```

This will produce an output WASM file that can be run in any WASM runtime that
supports the [WASM exceptions](https://github.com/WebAssembly/exception-handling)
proposal and provides support for WASI. Support for exceptions is required to
support the `setjmp, longjmp` implementation of MicroPython's handling of
Python exceptions, and WASI support is required to support the "OS-like"
functionality of the interpreter.

### Custom runtime

This port is also capable of building a shared library that contains MicroPython
compiled for WASM as well as a WASM runtime using the reference implementations
provided by `wasm2c` and `uvwasi`.

All dependencies listed above are required to build the custom runtime, which
can be performed by running the appropriate target:

```
make build/micropython.so
```

Usage
-----

An example wrapper of the output library and some toy programs are included in
the [`examples/`](examples/) directory. Try running:

```
python3 examples/micropython_wrapper.py examples/hello.py
python3 examples/micropython_wrapper.py examples/fibb.py
python3 examples/micropython_wrapper.py -c "print('An inline code example')"
```

Misc. Notes
-----------

* The custom runtime build is somewhat fragile when it comes to exception
  handling, it will segfault if an exception occurs in a build with `-DNDEBUG`.
  I've tried to track down the cause of this, but cannot determine if it is a
  problem in the `wasm2c` runtime or undefined behavior caused by other
  components.
* If you would like to debug the WASM build with a C debugger, add
  `--profiling-funcs` to the Emscripten invocation to preserve function names.
* The lifetime of the WASM module is not controlled particularly closely in
  the custom runtime. In particular, the module and runtime are never freed or
  deinitialized. See `wasm_runtime/uvwasi-rt-main.c` for details.
