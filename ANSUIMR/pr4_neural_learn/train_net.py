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
        arr=np.array(eval(f.read()))
        num_imputs, num_outputs = len(arr[0][1]), len(arr[0][1])
        N = len(arr)
        X=arr[:, 1]
        Y=arr[:, 0] #.reshape((N, num_outputs))

    model = create_model(num_imputs, num_outputs)
    model.summary()
    model.compile(optimizer='adam', loss='mae')


    n1=int(N*0.7)

    X_train=X[:n1]
    Y_train=Y[:n1]

    X_val=X[n1:]
    Y_val=Y[n1:]

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