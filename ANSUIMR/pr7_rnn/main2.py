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
        tf.keras.layers.LSTM(units=64), #, return_sequences=False, return_state=True
        tf.keras.layers.Dense(units=64, input_shape=[64]),
        tf.keras.layers.Dense(units=nouts, activation=tf.nn.softmax)
    ])
    return model

def prob_sel(probs): # вероятностный выбор индекса элемента
    m, s, r=sum(probs), 0, np.random.rand()
    if m==0: return np.random.randint(len(probs))
    for i in range(len(probs)):
        s+=probs[i]/m
        if s>=r: return i
    return -1

def train_net(text, MODE=2):
    n_abc=34
    model=create_model(n_abc, n_abc)
    model.summary()

    if MODE==1: #Mean Absolute Error или Средняя абсолютная ошибка
        code='mae'
    if MODE==2: #Категориальная кросс-энтропия (Categorical Cross-Entropy) 
        code='categorical_crossentropy'

    model.compile(optimizer='adam', loss=code)

    def encode_letter(letter, num):
        res=[0]*num
        i="абвгдеёжзийклмнопрстуфхцчшщъыьэюя ".index(letter)
        res[i]=1
        return res
    def decode_letter(enc):
        return "абвгдеёжзийклмнопрстуфхцчшщъыьэюя "[np.argmax(enc)]
    def decode_letter_prob(enc):
        pp=np.array(enc).copy()[0]
        print(pp)
        pp-=np.min(pp)
        print(pp)
        pp/=np.sum(pp)
        i = prob_sel(pp)
        #print("decode")
        #print(pp)
        #print(i)
        return "абвгдеёжзийклмнопрстуфхцчшщъыьэюя "[i]

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


    if MODE==1: #Mean Absolute Error или Средняя абсолютная ошибка
        X_train=np.expand_dims(X_train, axis=1) #(1,34) -> (1,1,34)
        Y_train=np.expand_dims(Y_train, axis=1)
        X_val=np.expand_dims(X_val, axis=1)
        Y_val=np.expand_dims(Y_val, axis=1)
    if MODE==2: #Категориальная кросс-энтропия (Categorical Cross-Entropy) 
        X_train=np.expand_dims(X_train, axis=1) #(1,34) -> (1,1,34)
        X_val=np.expand_dims(X_val, axis=1)

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
        inp=np.expand_dims(inp, axis=1)
        result=model.predict(inp)
        # outp=decode_letter(result, n_abc)
        outp=decode_letter_prob(result)
        # print(result)
        print(outp)
        letter=outp

    print(result_str)

if __name__=="__main__":
    with open("text.txt", "r", encoding="utf-8") as f:
        train_net(f.read())
