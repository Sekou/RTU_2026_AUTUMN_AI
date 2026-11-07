#2024, S. Diane, tensorflow/keras neural network example

import tensorflow as tf
import numpy as np

def create_model(ninps, nouts):
    # model = tf.keras.Sequential([
    #     tf.keras.layers.Dense(units=64, activation='relu',
    #                           input_shape=[ninps]),
    #     tf.keras.layers.Dense(units=64, activation='relu'),
    #     tf.keras.layers.Dense(units=nouts)#, activation=tf.nn.softmax
    # ])
    model = tf.keras.Sequential([
        tf.keras.layers.LSTM(units=64, return_sequences=True, return_state=True,
                              input_shape=[ninps]),
        tf.keras.layers.Dense(units=nouts)#, activation=tf.nn.softmax
    ])
    return model

def prob_sel(probs): # вероятностный выбор индекса элемента
    m, s, r=sum(probs), 0, np.random.rand()
    if m==0: return np.random.randint(len(probs))
    for i in range(len(probs)):
        s+=probs[i]/m
        if s>=r: return i
    return -1

def train_net(text):
    n_abc=34
    model=create_model(n_abc, n_abc)
    model.summary()

    model.compile(optimizer='adam', loss='mae')

    def encode_letter(letter, num):
        res=[0]*num
        i="абвгдеёжзиклмнопрстуфхцчшщъыьэюя ".index(letter)
        res[i]=1
        return res
    def decode_letter(enc, num):
        return "абвгдеёжзиклмнопрстуфхцчшщъыьэюя "[np.argmax(enc)]
    def decode_letter_prob(enc, num):
        pp=np.array(enc).copy()[0]
        print(pp)
        pp-=np.min(pp)
        print(pp)
        pp/=np.sum(pp)
        i = prob_sel(pp)
        return "абвгдеёжзиклмнопрстуфхцчшщъыьэюя "[i]

    X=[]
    Y=[]
    for i in range(len(text)-1):
        letter1=text[i]
        letter2=text[i+1]
        X.append(encode_letter(letter1, n_abc))
        Y.append(encode_letter(letter2, n_abc))

    k_train=0.7
    n1=int(len(X)*k_train)

    X_train=X[:n1]
    Y_train=Y[:n1]

    X_val=X[n1:]
    Y_val=Y[n1:]

    #обучение
    losses = model.fit(np.array(X_train), np.array(Y_train),
                       validation_data=(np.array(X_val), np.array(Y_val)),
                       batch_size=1,
                       epochs=15)
    #проверка
    letter="м"

    result_str=""
    for i in range(100):
        result_str=result_str+str(letter)
        inp=np.array([encode_letter(letter, n_abc)])
        result=model.predict(inp)
        # outp=decode_letter(result, n_abc)
        outp=decode_letter_prob(result, n_abc)
        # print(result)
        print(outp)
        letter=outp

    print(result_str)

if __name__=="__main__":
    with open("text.txt", "r", encoding="utf-8") as f:
        train_net(f.read())
