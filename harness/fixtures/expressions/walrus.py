# feature: expressions
# summary: assignment expressions in conditions, loops, comprehensions and call arguments


def source(values):
    it = iter(values)

    def nxt():
        v = next(it, None)
        print('read', v)
        return v
    return nxt


def observe():
    out = []
    read = source([3, 1, 4, 0, 5])
    while (x := read()):
        out.append(x)
    if (n := len(out)) > 2:
        out.append(('n', n))
    data = [1, 2, 3, 4, 5, 6]
    out.append([y for v in data if (y := v * v) % 2])
    out.append(y)
    out.append(max((z := 10), z + 1))
    out.append([last := i for i in range(3)])
    out.append(last)
    total = 0
    out.append([total := total + v for v in data])
    out.append(total)
    return out
