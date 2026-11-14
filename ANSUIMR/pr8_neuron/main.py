import numpy as np

#TODO: попробовать апроксимировать другую логическую функцию
#TODO: попробовать апроксимировать график одномерной величины y(x)
#TODO: попробовать подобрать параметры нейрона градиентным спуском

class Neuron:
    def __init__(self, num_inps):
        self.inps=[]
        self.weights=[0]*(num_inps+1) #N весов и 1 сигнал смещения (настраиваемые параметры)
        self.y=0 #выход

        for i in range(len(self.weights)):
            self.weights[i]=np.random.normal(0,0.01)

    def calc(self, inp_vec):
        self.inps=inp_vec
        s=np.dot(self.inps, self.weights[:-1])
        self.y=0.5+0.5*np.sign(s + self.weights[-1])
        return self.y


neuron = Neuron(3)

y=neuron.calc([1, 0, 1])
print(y)


#датасет говорит что число единиц 
#в бинарном представлении числа
#больше чем число нулей
dataset=\
[
[[0,0,0],[0]],
[[0,0,1],[0]],
[[0,1,0],[0]],
[[0,1,1],[1]],
[[1,0,0],[0]],
[[1,0,1],[1]],
[[1,1,0],[1]],
[[1,1,1],[1]]
]

#массивы бывают: ступенчатые по длине записей, негомогенные по скобкам


def calc_error(neuron, dataset, debug=False):
    s=0
    for sample in dataset:
        y=neuron.calc(sample[0])
        e=y-sample[1][0]
        if debug: 
            print(f"y={y}, y*={sample[1][0]}")
        s+=e**2
    return s/len(dataset)

e=calc_error(neuron, dataset)

print(f"Initial error: {e}")

import itertools

x=[list(range(3))]*3
print(x)

def optimize_neuron(neuron, dataset, num_steps):
    iii=list(itertools.product( *[list(range(num_steps))]*len(neuron.weights) ))
    #print(iii)
    min_e=100500
    best_ii=None
    def apply(neuron, ii):#декодируем комбинации
        for j in range(len(ii)): 
            neuron.weights[j]=\
                -1+2*ii[j]/(num_steps-1)
    for ii in iii:
        apply(neuron, ii)
        e=calc_error(neuron, dataset)
        if e<min_e:
            min_e, best_ii=e, ii
        apply(neuron, best_ii)

optimize_neuron(neuron, dataset, 4)

e=calc_error(neuron, dataset, debug=True)
print(f"Optimized error: {e}")


#2026, S. Diane