#2024, S. Diane, tensorflow/keras neural network example with dataset loading from file
import numpy as np
import tensorflow as tf

def create_model(num_imputs, num_outputs):
    model = tf.keras.Sequential([

        tf.keras.layers.Dense(units=64, activation='relu',
                              input_shape=[num_imputs]),
        tf.keras.layers.Dense(units=64, activation='relu'),
        tf.keras.layers.Dense(units=num_outputs) #, activation=tf.nn.softmax
    ])
    return model

def train_net():

    with open("samples.txt", "r") as f:
        arr=eval(f.read())
        num_imputs, num_outputs = len(arr[0][1]), len(arr[0][0])
        print(f"ni = {num_imputs}, no = {num_outputs}")
        N = len(arr)
        X=np.array([b for a,b in arr])
        Y=np.array([a for a,b in arr]) #.reshape((N, num_outputs))

    model = create_model(num_imputs, num_outputs)
    model.summary()
    model.compile(optimizer='adam', loss='mae')
    # model.compile(optimizer='adam', loss='cosine_similarity')

    n1=int(N*0.7)

    X_train=X[:n1]
    print(X_train.shape)
    Y_train=Y[:n1]
    print(Y_train.shape)

    X_val=X[n1:]
    print(X_val.shape)
    Y_val=Y[n1:]
    print(Y_val.shape)

    losses = model.fit(X_train, Y_train,
                       validation_data=(X_val, Y_val),
                       batch_size=1,
                       epochs=100)

    for x, y in zip(X_val[:5], Y_val[:5]):
        result = model.predict(np.array([x.tolist()]))
        print(f"X={x}, Y={result[0]} //{y}")

    model.save_weights("net.weights.h5")

if __name__=="__main__":
    train_net()