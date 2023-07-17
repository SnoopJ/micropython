def recurse(n):
    if n <= 1:
        raise RuntimeError("bonk! 💥")

    recurse(n-1)


recurse(3)
