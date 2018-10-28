import numpy as np 
import tensorflow as tf 
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

housing = fetch_california_housing()

# splitting the dataset to train and test set 
train_X, test_X, train_y, test_y = train_test_split(housing.data, housing.target, test_size=0.2, random_state=42)
print("Shape after splitting into train and test set:", train_X.shape, test_X.shape, train_y.shape, train_y.shape)

# adding bias to existing features and reshaping y to (rows, 1)
train_X_plus_bias = np.c_[np.ones((train_X.shape[0], 1)), train_X]
test_X_plus_bias = np.c_[np.ones((test_X.shape[0], 1)), test_X]
train_y_reshaped = train_y.reshape(-1, 1)
test_y_reshaped = test_y.reshape(-1, 1)
print("\nShape after adding bias and reshaping y:", train_X_plus_bias.shape, test_X_plus_bias.shape, train_y_reshaped.shape, test_y_reshaped.shape)

# creating tensorflow input nodes of computational graph 
X_train = tf.constant(train_X_plus_bias, dtype=tf.float32, name="X_train")
y_train = tf.constant(train_y_reshaped, dtype=tf.float32, name="Y_train")
X_test = tf.constant(test_X_plus_bias, dtype=tf.float32, name="X_test")
y_test = tf.constant(test_y_reshaped, dtype=tf.float32, name="y_test")
X_train_transpose = tf.transpose(X_train)

## METHOD 1: Using Normal equations to find parameters for linear systems

# creating compututational graph node for finding theta 0 = (XT. X)-1 . XT . y 
theta = tf.matmul(tf.matmul(tf.matrix_inverse(tf.matmul(X_train_transpose, X_train)), X_train_transpose), y_train, name="theta")

# predicting y using test y and theta value 
y_predicted = tf.matmul(X_test, theta)

# creating tensorflow session to run the computational graph 
with tf.Session() as sess:
    tf.global_variables_initializer().run()
    y_predicted_value = y_predicted.eval()
    y_test_value = y_test.eval()

print("Mean Absolute Error of Normal Equation: ", mean_absolute_error(y_predicted_value, y_test_value))
