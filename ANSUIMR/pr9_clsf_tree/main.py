import math, numpy as np

#TODO: выписывать энтропию напротив каждого узла в выводимом в косоль дереве
arr=["red", "blue", "red", "red", "blue", "blue", "red"]
arr2=["red", "red", "red", "red", "red", "red", "red"]

def calc_entropy(arr):
    values, counts = np.unique(arr, return_counts=True)
    pp=[c/len(arr) for c in counts]
    H = sum([-p*math.log(p) for p in pp])
    return H

H=calc_entropy(arr)
print(H)
H2=calc_entropy(arr2)
print(H2)

def find_dichotomy(arr):
    i_best=-1
    H_min=calc_entropy(arr)
    for i in range(1, len(arr)):
        A,B=arr[:i], arr[i:]
        H=calc_entropy(A)*len(A)+calc_entropy(B)*len(B)
        H/=len(arr)
        if H < H_min: i_best, H_min=i,H
    if i_best<0: return [*arr], None
    return arr[:i_best], arr[i_best:]


D1=find_dichotomy(arr)
print(D1)

D2=find_dichotomy(arr2)
print(D2)

class Node:
    def __init__(self, arr):
        self.arr=arr
        self.childs=[]
    def split(self, recursive=False):
        self.childs=[Node(arr) for arr in\
                     find_dichotomy(self.arr) if arr is not None]
        if recursive: 
            for n in self.childs: 
                if len(n.arr)>1 and calc_entropy(n.arr)>0: 
                    n.split(True)
    def show(self, level=0, recursive=False):
        print(" "*(2*level) + str(self.arr))
        if recursive: 
            for n in self.childs: 
                n.show(level+1, True)

n=Node(arr)
n.split(True)

print("Tree:")
n.show(0, True)

print(555)
#2026, S. Diane
