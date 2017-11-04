import numpy as np

n = 1  # 1 type
m = 1  # 2 type
k = 2  # repair devices
h1 = 0.0346  # 1 type failure rate
h2 = 0.0112  # 2 type failure rate
mu1 = 1  # 1 type repair rate
mu2 = 1  # 2 type repair rate


class P:
    def __init__(self, type1, type2):
        self.t1 = type1
        self.t2 = type2

    def __eq__(self, other):
        return self.t1 == other.t1 and self.t2 == other.t2

    def __hash__(self):
        return str(self).__hash__()

    def __str__(self):
        return "P({},{})".format(self.t1, self.t2)

    def __repr__(self):
        return str(self)

    def is_left(self, other):
        return self.t1 < other.t1

    def is_right(self, other):
        return self.t1 > other.t1

    def is_higher(self, other):
        return self.t2 < other.t2

    def is_below(self, other):
        return self.t2 > other.t2

    def number(self):
        return self.t1 * (m + 1) + self.t2


def _link_h(links, left, right, n_repairs, n_devices, h, m):
    mu = right.t1
    if mu > n_repairs:
        mu = n_repairs
    lam = n_devices - left.t1
    # print("{} -> {}: mu1*{}*{}".format(right, left, mu, right))
    links[right][left] = mu * m
    # print("{} -> {}: la1*{}*{}".format(left, right, lam, left))
    links[left][right] = lam * h


def _link_v(links, bottom, top, n_repairs, n_devices, h, m):
    mu = bottom.t2
    if mu > n_repairs:
        mu = n_repairs
    lam = n_devices - top.t2
    if mu:
        # print("{} -> {}: mu2*{}*{}".format(bottom, top, mu, bottom))
        links[bottom][top] = mu * m
    # print("{} -> {}: la2*{}*{}".format(top, bottom, lam, top))
    links[top][bottom] = lam * h


def get_p(self, n_column, n_row):
    possibilities = {self}
    column = self.t1
    row = self.t2
    if row > 0:  # up
        possibilities.add(P(column, row - 1))
    if row < n_row:  # down
        possibilities.add(P(column, row + 1))
    if column > 0:  # left
        possibilities.add(P(column - 1, row))
    if column < n_column:  # right
        possibilities.add(P(column + 1, row))
    return possibilities


def generate_col_matrix(n_column, n_row, repairs, h1, h2, mu1, mu2):
    links = dict()
    for column in range(n_column + 1):
        for row in range(n_row + 1):
            self = P(column, row)

            # print(self, "*" * 4, possibilities)

            for p in get_p(self, n_column, n_row):
                links.setdefault(self, {})
                links.setdefault(p, {})
                if self.is_left(p):
                    _link_h(links, self, p, repairs, n_column, h1, mu1)
                if self.is_right(p):
                    _link_h(links, p, self, repairs, n_column, h1, mu1)

                n_repairs = repairs - self.t1 if repairs - self.t1 > 0 else 0
                if self.is_higher(p):
                    _link_v(links, p, self, n_repairs, n_row, h2, mu2)
                if self.is_below(p):
                    _link_v(links, self, p, n_repairs, n_row, h2, mu2)
    return links


def xprint(links, n_column, n_row):
    rows = []
    for column in range(n_column + 1):
        for row in range(n_row + 1):
            new_row = [0] * ((n_column + 1) * (n_row + 1))
            self = P(column, row)
            st = ""
            for p in get_p(self, n_column, n_row):
                _in = links.get(p, {}).get(self, 0)
                if _in:
                    new_row[p.number()] += _in
                    if _in < 1:
                        st += "+{:.3f}{}".format(_in, p)
                    else:
                        st += "+{}{}".format(_in, p)

                _out = links.get(self, {}).get(p, 0)
                if _out:
                    if _out < 1:
                        st += "-{:.3f}{}".format(_out, self)
                    else:
                        st += "-{}{}".format(_out, self)
                    new_row[self.number()] -= _out
            rows.append(new_row)
            # print(st[1:], "= 0")
    return rows


def resolve(coefs):
    rows = coefs[:-1]  # Drop last, it is redundantly
    rows.append([1] * ((n + 1) * (m + 1)))  # add normalization condition

    left = np.array(rows)
    # print(left)
    right = np.array([0] * ((n + 1) * (m + 1) - 1) + [1])
    answer = np.linalg.solve(left, right)
    return answer


# links = generate_col_matrix(n, m, k, h1, h2, mu1, mu2)
# print("Уравнения")
# rows = xprint(links, n, m)
# answer = resolve(rows)
#
# print("Решение:")
# print(answer[P(0,0).number()])

cpus = [
    (1.98575E-06, 10400),
    (1.68966E-06, 16500),
    (1.44737E-06, 17000)
]
disks = [
    (2.937E-06, 11800),
    (2.46944E-06, 9000),
]
mothers = [
    (3.42279E-06, 8500),
    (5.12457E-06, 24500),
    (2.78332E-06, 12500),
    (4.76712E-06, 9900)
]
rams = [
    (4.01972E-06, 3900),
    (3.15977E-06, 6750),
    (5.60736E-07, 5000),
]


kgs = []

for a in cpus:
    for b in disks:
        links = generate_col_matrix(n, m, k, a[0], b[0], mu1, mu2)
        rows = xprint(links, n, m)
        answer = resolve(rows)
        kgs.append((answer[P(0, 0).number()], a, b, a[1] + b[1]))

kgs2 = []
for a in rams:
    for b in mothers:
        links = generate_col_matrix(n, m, k, a[0], b[0], mu1, mu2)
        rows = xprint(links, n, m)
        answer = resolve(rows)
        kgs2.append((answer[P(0, 0).number()], a, b, a[1] + b[1]))

result = []
for value in kgs:
    for value2 in kgs2:
        result.append((value[0] * value2[0], value[3] + value2[3], list(value[1:3] + value2[1:3])))

min_price = min([r[1] for r in result])
max_price = max(r[1] for r in result)

finish = []
last_max = 0
for price in range(min_price, max_price + 1):
    tmp = [r for r in result if r[1] < price]
    if not tmp:
        continue
    maxim = max(tmp, key=lambda x: x[0])
    if last_max < maxim[0]:
        finish.append(maxim)
        last_max = maxim[0]

for i in result:
    print(i[1])
for i in finish:
    print(i[:2])
