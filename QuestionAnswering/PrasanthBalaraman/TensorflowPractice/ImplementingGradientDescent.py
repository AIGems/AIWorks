import numpy as np
import tensorflow as tf
from sklearn.datasets import fetch_california_housing 
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error

# data preparation
housing = fetch_california_housing()
train_X, test_X, train_y, test_y = train_test_split(housing.data, housing.target, test_size=0.2, random_state=42)

# scaling the data as gradient descent performs faster when all features are in same scale
train_scaler = StandardScaler()
train_x = train_scaler.fit_transform(train_X)
test_scalar = StandardScaler() 
test_X = test_scalar.fit_transform(test_X)

train_X_plus_bias = np.c_[np.ones((train_X.shape[0], 1)), train_X]
test_X_plus_bias = np.c_[np.ones((test_X.shape[0], 1)), test_X]
train_y_reshaped = train_y.reshape(-1, 1)
test_y_reshaped = test_y.reshape(-1, 1)
print("Shape after adding bias and reshaping y: ", train_X_plus_bias.shape, test_X_plus_bias.shape, train_y_reshaped.shape, test_y_reshaped.shape)

# defining hyperparameters
epochs = 100000
learning_rate = 0.000001   # for gradients computed manually please set learning rate minimum 0.00000001 

# defining the network/computational graph
X_train = tf.constant(train_X_plus_bias, dtype=tf.float32, name="X_train")
y_train = tf.constant(train_y_reshaped, dtype=tf.float32, name="y_train")
X_test = tf.constant(test_X_plus_bias, dtype=tf.float32, name="X_test")
y_test = tf.constant(test_y_reshaped, dtype=tf.float32, name="y_test")
theta = tf.Variable(tf.random_uniform([train_X_plus_bias.shape[1], 1], -1.0, 1.0), dtype=tf.float32, name="theta")
y_predicted = tf.matmul(X_train, theta, name="predictions")
error = y_predicted - y_train
root_mean_squared_error = tf.sqrt(tf.reduce_mean(tf.square(error), name="rmse"))
# manually computing gradients from normal quation
#gradients = 2/train_X_plus_bias.shape[0] * tf.matmul(tf.transpose(X_train), error)
# using autodiff/auto differentiation feature of tensorflow 
gradients = tf.gradients(root_mean_squared_error, [theta])[0]
training_ops = tf.assign(theta, theta - learning_rate*gradients)

# training and testing  the network
with tf.Session() as sess:
    tf.global_variables_initializer().run()

    # network training 
    for epoch in range(epochs):
        if epoch%1000==0:
            print("Epoch", epoch, "RMSE: ", root_mean_squared_error.eval())
            # print("Errors:", error.eval())
            # print("Transpose input features:", tf.transpose(X_train).eval())
            # print("theta:", theta.eval())
            #print("X_train * theta - learning_rate * 2/m * XT * error:", tf.matmul(X_train, (theta - learning_rate*2/train_X_plus_bias.shape[0]*tf.matmul(tf.transpose(X_train), error))).eval())
            #print("y_predicted: ", y_predicted.eval())
        sess.run(training_ops)
    
    # network testing 
    y_test_predicted = tf.matmul(X_test, theta, name="test_predictioms")
    mae = mean_absolute_error(y_test.eval(), y_test_predicted.eval())
    print("Mean Absolute Error on implemented Gradient Descent: ", mae)