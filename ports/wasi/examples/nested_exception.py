def f():
    try:
        g()
    except Exception as exc:
        raise RuntimeError('f exception')


def g():
    raise RuntimeError('g exception')


f()
