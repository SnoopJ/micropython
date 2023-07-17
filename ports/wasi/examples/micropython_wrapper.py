import argparse
import code
import ctypes
import sys
from pathlib import Path


HERE = Path(__file__).parent
MICROPY_LIB = HERE.joinpath("..", "build", "micropython.so")

MICROPY_FUNC_SIGS = (
    # func, argtypes, restype
    ("main", [ctypes.c_int, ctypes.c_void_p], ctypes.c_int),
    ("mp_do_str", [ctypes.c_char_p], ctypes.c_int),

    # NOTE:snoopj:these signatures are unused
    ("wasm_rt_init", [], None),
    ("wasm_rt_free", [], None),
    # note: return value of True means only that someone called wasm_rt_init()
    # at some point, but does NOT indicate that the runtime is in a valid state
    # (i.e. someone may have called wasm_rt_free() after calling wasm_rt_init())
    ("wasm_rt_is_initialized", [], ctypes.c_bool),
)


class MicroPythonWrapper:
    """Wrapper class for MicroPython running in WASM"""
    # NOTE:snoopj:this must NOT be set higher than the size of `warehouse` in main.c
    SRC_MAXSIZE = 4096

    def __init__(self, soname):
        if not Path(soname).exists():
            raise RuntimeError(f"Path does not exist: {str(soname)!r}")

        self._lib = self._load_micropython(soname)

    @staticmethod
    def _load_micropython(soname: str) -> ctypes.CDLL:
        libmicropy = ctypes.CDLL(soname)

        for funcname, argtypes, restype in MICROPY_FUNC_SIGS:
            try:
                func = getattr(libmicropy, funcname)
                func.argtypes = argtypes
                func.restype = restype
            except Exception as exc:
                raise RuntimeError(f"Cannot set signature for func {funcname!r}") from exc

        argc = 0
        args = []
        ARGV_T = ctypes.c_char_p * len(args)
        argv = ARGV_T(*args)

        ret = libmicropy.main(argc, argv)
        assert ret == 0

        return libmicropy

    def run(self, src: str):
        if isinstance(src, str):
            buf = src.encode()
        elif isinstance(src, bytes):
            buf = src
        else:
            raise TypeError(f"src must be of type str or bytes, got {type(src)!r}")

        assert len(buf) < self.SRC_MAXSIZE, "Input is too large"

        self._lib.mp_do_str(buf)


parser = argparse.ArgumentParser()
parser.add_argument("progfile", nargs='?', help="Program to run in MicroPython, if given")
parser.add_argument("--lib", "-l", default=str(MICROPY_LIB), help=".so file from which to load MicroPython")
parser.add_argument("--source", "-c", nargs='*', help="Source to run (mutually exclusive with progfile)")


def main():
    args = parser.parse_args()
    soname = Path(args.lib).resolve()
    if args.progfile and args.source:
        raise RuntimeError("Cannot specify both progfile and --source")

    micropython = MicroPythonWrapper(soname)
    print("MicroPython initialized")
    micropython.run("import sys; print(sys.version)")
    print()

    src = None
    if args.progfile:
        pth = Path(args.progfile)
        if not pth.exists():
            raise RuntimeError(f"Path does not exist: {str(pth)!r}")
        src = pth.read_text()
    elif args.source:
        src = "".join(args.source)

    if src:
        micropython.run(src)
    else:
        banner= "No input program given, dropping you to interactive prompt…\nUse micropython.run() to evaluate Python source\n"
        code.interact(banner=banner, local=locals())


if __name__ == "__main__":
    main()
