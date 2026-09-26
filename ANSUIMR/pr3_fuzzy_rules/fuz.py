
#S. Diane, 2024 - 2025, fuzzy logic example

import matplotlib.pyplot as plt
import numpy as np

class Term:
    def __init__(self, name, x0, w):
        self.name=name
        self.x0=x0
        self.w=w
        self.left=False
        self.right=False
        self.activation=0
    def F(self, x):
        if self.left and x<=self.x0: return 1
        if self.right and x>=self.x0: return 1
        if x<self.x0-self.w/2: return 0
        elif x<self.x0: return -(2*self.x0 / self.w - 1) + 2/self.w*x
        elif x<self.x0+self.w/2: return (2*self.x0 / self.w + 1) - 2/self.w*x
        else: return 0
    def calc(self, x):
        self.last_input=x
        self.activation=self.F(x)
        return self.activation
    def draw(self, plt, xmin, xmax):
        N = 100
        dx = (xmax - xmin) / N
        xx = [xmin + i * dx for i in range(N)]
        yy = [self.F(x) for x in xx]
        plt.plot(xx, yy)

class FuzzyVar:
    def __init__(self, xmin, xmax):

        self.terms = []
        self.xmin = xmin
        self.xmax = xmax

    def add_term(self, name, x0, w):
        self.terms.append(Term(name, x0, w))

    def draw(self, plt):
        for t in self.terms:
            t.draw(plt, self.xmin, self.xmax)

    def calc(self, x):
        return [t.calc(x) for t in self.terms]

    def defuzz_term_name(self, term_name):
        tt=[t for t in self.terms if t.name==term_name]
        return tt[0].x0 if len(tt) else None

    def defuzz_mamdani(self, x, rules, fv_out, split=100):
        # активация входных термов
        aa = [t.calc(x) for t in self.terms]
        # применение правил и определение выходных термов
        terms2 = [fv_out.terms[rules[i][1]] for i in range(len(rules))]
        # дефаззификация выходного нечеткого множества
        J, M = 0, 0
        step=(fv_out.xmax - fv_out.xmin)/split
        for x_ in np.arange(fv_out.xmin, fv_out.xmax, step):
            v = max([min(a, t.calc(x_)) for a, t in zip(aa, terms2)])
            J += v * x_
            M += v
        return J / M

if __name__ == "__main__":
    fv_inp = FuzzyVar(0, 100)
    fv_inp.add_term("DSmall", 0, 100)
    fv_inp.add_term("DMid", 50, 100)
    fv_inp.add_term("DBig", 100, 100)
    fv_inp.draw(plt)
    plt.show()
    fv_out = FuzzyVar(0, 80)
    fv_out.add_term("VSmall", 0, 80)
    fv_out.add_term("VMid", 40, 80)
    fv_out.add_term("VBig", 80, 80)
    fv_out.draw(plt)
    plt.show()

    # цикл активации термов при линейном изменении входной координаты
    for x in range(100):
        aa = fv_inp.calc(x)
    print(aa)

    # тестовая база правил, отображающая нечеткие значения сами в себя
    rules = [[0, 0], [1, 1], [2, 2]]  # при наблюдении нечеткого значения i выдать нечеткое значение j
    xx = np.arange(0, 100, 1)
    yy = [fv_inp.defuzz_mamdani(x, rules, fv_out) for x in xx]
    plt.plot(xx, yy)
    plt.show()