fibb = [1, 1]
print(1)
print(1)

for _ in range(20):
    fibb.append(fibb[-2] + fibb[-1])
    print(fibb[-1])
