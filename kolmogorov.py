import numpy as np

n = 7  # 1 type
m = 5  # 2 type
k = 4  # repair devices
h1 = 0.007  # 1 type failure rate
h2 = 0.003  # 2 type failure rate
mu1 = 3  # 1 type repair rate
mu2 = 4  # 2 type repair rate

# 1 столбец

col1 = (
    (h2 * n, mu2),
    (h2 * n - 1, mu2 * 2)
)


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


def _link_h(links, left, right, n_repairs, n_devices, is_self_left):
    mu = right.t1
    if mu > n_repairs:
        mu = n_repairs
    lam = n_devices - left.t1
    # print("{} -> {}: mu1*{}*{}".format(right, left, mu, right))
    links[right][left] = mu * mu1
    # print("{} -> {}: la1*{}*{}".format(left, right, lam, left))
    links[left][right] = lam * h1


def _link_v(links, bottom, top, n_repairs, n_devices, is_self_bottom):
    mu = bottom.t2
    if mu > n_repairs:
        mu = n_repairs
    lam = n_devices - top.t2
    if mu:
        # print("{} -> {}: mu2*{}*{}".format(bottom, top, mu, bottom))
        links[bottom][top] = mu * mu2
    # print("{} -> {}: la2*{}*{}".format(top, bottom, lam, top))
    links[top][bottom] = lam * h2


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


def generate_col_matrix(n_column, n_row, repairs):
    links = dict()
    for column in range(n_column + 1):
        for row in range(n_row + 1):
            self = P(column, row)

            # print(self, "*" * 4, possibilities)

            for p in get_p(self, n_column, n_row):
                links.setdefault(self, {})
                links.setdefault(p, {})
                if self.is_left(p):
                    _link_h(links, self, p, repairs, n_column, True)
                if self.is_right(p):
                    _link_h(links, p, self, repairs, n_column, False)

                n_repairs = repairs - self.t1 if repairs - self.t1 > 0 else 0
                if self.is_higher(p):
                    _link_v(links, p, self, n_repairs, n_row, False)
                if self.is_below(p):
                    _link_v(links, self, p, n_repairs, n_row, True)
    return links


links = generate_col_matrix(n, m, k)


def xprint(n_column, n_row):
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
            print(st[1:], "= 0")
    return rows


def resolve(coefs):
    rows = coefs[:-1]  # Drop last, it is redundantly
    rows.append([1] * ((n + 1) * (m + 1)))  # add normalization condition

    left = np.array(rows)
    # print(left)
    right = np.array([0] * ((n + 1) * (m + 1) - 1) + [1])
    answer = np.linalg.solve(left, right)
    return answer


print("Уравнения")
rows = xprint(n, m)
answer = resolve(rows)

print("Решение:")
for column in range(n + 1):
    st = ""
    for row in range(m + 1):
        st += "{:.4e}\t".format(answer[P(column, row).number()])
    st = st[:-1]
    print(st)
