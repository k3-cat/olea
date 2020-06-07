X = 67

for n in range(1, X):
    result = {(n**i) % X for i in range(X)}
    if len(result) == X - 1:
        print(n)
