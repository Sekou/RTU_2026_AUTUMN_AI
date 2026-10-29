
import numpy as np

def get_neighborhood(M, i0, j0): #окрестность Мура
    res, w, h=[], M.shape[1], M.shape[0]
    for i in range(-1+i0,2+i0):
        for j in range(-1+j0,2+j0):
            if i==i0 and j==j0: continue
            if i<0 or i>=h or j<0 or j>=w: continue
            res.append(M[i,j])
    return res

M=\
["D1", "D3", "", "", "M3", 
"D1", "D3", "", "D1", "M3",
"M3", "D1", "D2", "", "",
"M3", "M3", "S", "D3", "D3",
"", "", "M2", "M1", "D3",
"D3", "M1", "", "M3", "M1",
"D3", "D3", "", "M3", "M1"
]

M=np.reshape(M, (7,5))


nb=get_neighborhood(M, 4, 1)
nb=[v for v in nb if len(v)]
print(nb)


elements, counts = np.unique(nb, return_counts=True)
print(elements)
print(counts)

i=np.argmax(counts)
print(elements[i])

# ii=np.argsort(counts)
# print(elements[ii[-1]])

def recover_mat(M):
    M2=M.copy()
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            if M[i,j]!="": continue
            nb=get_neighborhood(M, i,j)
            nb=[v for v in nb if len(v)]
            elements, counts = np.unique(nb, return_counts=True)
            if len(counts)>0:
                k=np.argmax(counts)
                M2[i,j]=elements[k]
    return M2

M2=recover_mat(M)

print("M2=", M2)


M3=\
["D1", "D3", "", "", "M3", 
"D1", "D3", "", "", "M3",
"", "", "", "", "",
"M3", "", "", "", "D3",
"", "", "", "", "D3",
"D3", "", "", "M3", "M1",
"D3", "D3", "", "", "M1"
]
M3=np.reshape(M3, (7,5))
M4=recover_mat(M3)
print("M4=", M4)
M5=recover_mat(M4)
print("M5=", M5)