#from keras.applications.inception_v3 import InceptionV3, preprocess_input
from keras.applications.vgg19 import VGG19, preprocess_input
from keras.applications.xception import Xception, preprocess_input, decode_predictions
#from keras.applications.vgg16 import VGG16, preprocess_input
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Model
from keras.models import Sequential
from keras.callbacks import TensorBoard, ModelCheckpoint
from keras.layers import Dense, GlobalAveragePooling2D, Dropout, MaxPooling2D, Flatten, Conv2D, Conv3D, LSTM, CuDNNLSTM
from keras import backend as K
import os
import glob
import numpy as np
import pandas as pd
from keras import backend as K
from keras.engine.topology import Layer
from keras import optimizers
import tensorflow as tf
import time
# from sklearn import cross_validation
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from matplotlib.pyplot import axes

' Train Data Script '

' Project 2 '
' Kyle Mott '
' 04/05/19 '

NAME = "project-2-rnn-test-{}".format(int(time.time()))

tensorboard = TensorBoard(log_dir='logs/{}'.format(NAME))

# Checking GPU
from tensorflow.python.client import device_lib
print(device_lib.list_local_devices())


# Parsing data input/target
total_data = np.load("array_train_cup.npy")
print(total_data.shape, "Total Data - 1307, 1099, 10\n")

input_total_data = total_data[:, :, [True, False, True, True, True, True, True, True, True, True]]  # data as input except f(t) from data
target_total_data = total_data[:, :, [False, True, False, False, False, False, False, False, False, False]]  # extracting f(t) from data

print(input_total_data.shape, "Total Input Data - 1307, 1099, 9")
print(target_total_data.shape, "Total Target Data - 1307, 1099, 1\n")


# Splitting Data into Train/Valid/Test
train_percentage = 0.80
valid_percentage = 0.15
test_percentage = 0.05

print(train_percentage*100, "Training Data Percentage")
print(valid_percentage*100, "Validation Data Percentage")
print(test_percentage*100, "Testing Data Percentage\n")

train_input, valid_test_input, train_target, valid_test_target = train_test_split(input_total_data, target_total_data, test_size=(1 - train_percentage), random_state=0)

print(train_input.shape, "Train Data Input")
print(train_target.shape, "Train Data Target")

valid_input, test_input, valid_target, test_target = train_test_split(valid_test_input, valid_test_target, test_size=(test_percentage / (valid_percentage + test_percentage)), random_state=0)

print(valid_input.shape, "Validation Data Input")
print(valid_target.shape, "Validation Data Target")
print(test_input.shape, "Test Data Input")
print(test_target.shape, "Test Data Target\n")


# Saving Test Data to Files
np.save("array_test_input.npy", test_input)
np.save("array_test_target.npy", test_target)


# # Plot Example of First Train Input Data Sequence (for visual)
# for i in range(9):
#     H = train_input[0]
#     H = H[:, [i]]
#     plt.figure(i)
#     plt.plot(H)
#     plt.autoscale(enable=True, axis='both', tight=None)
#     plt.show()
# # Plot Example of First Train Target Data Sequence (for visual)
# for i in range(1):
#     H = train_target[0]
#     H = H[:, [i]]
#     plt.figure(i)
#     plt.plot(H)
#     plt.autoscale(enable=True, axis='both', tight=None)
#     plt.show()


# Model

model = Sequential()

model.add(LSTM(16, input_shape=(input_total_data.shape[1:]), activation='tanh', recurrent_activation='sigmoid', return_sequences=True))
model.add(LSTM(16, activation='tanh', recurrent_activation='sigmoid', return_sequences=True))
model.add(LSTM(16, activation='tanh', recurrent_activation='sigmoid', return_sequences=True))
# model.add(LSTM(16, activation='tanh', recurrent_activation='sigmoid', return_sequences=True))
# model.add(LSTM(16, activation='tanh', recurrent_activation='sigmoid', return_sequences=True))
model.add(Dropout(0.3))
model.add(Dense(1, activation='tanh'))

# model.add(LSTM(16, activation='tanh',recurrent_activation='hard_sigmoid', return_sequences=True))
# model.add(Dropout(0.15))
# model.add(Dense(1, activation='linear'))

model.compile(optimizers.Adam(lr=0.0001), loss="mean_squared_error", metrics=['accuracy'])

model.summary()

checkpoint = ModelCheckpoint(filepath='current_model.h5', monitor='val_loss', verbose=1, save_weights_only=False, save_best_only=True, mode='min', period=1)

history = model.fit(train_input, train_target, validation_data=(valid_input, valid_target), epochs=25, callbacks=[checkpoint, tensorboard], batch_size=16)


# Plotting Loss vs Epochs
plt.plot(history.history['loss'], 'g', label='Training')
plt.plot(history.history['val_loss'], 'y', label='Validation')
plt.autoscale(enable=True, axis='both', tight=None)
plt.title('Loss vs Epochs')
plt.legend(loc='upper right')
plt.savefig('Loss_Graphs\Loss_Graph.jpg')
plt.show()

# Plotting Validation Loss vs Epochs
# plt.plot(history.history['val_loss'])
# plt.autoscale(enable=True, axis='both', tight=None)
# plt.title('Validation Loss vs Epochs')
# plt.show()






# # Removing Zeros
#
#
# # U[np.abs(U) < .1] = 0  # some zeros
# # U = np.ma.masked_equal(U, 0)
#
# new_train_input = []
# U = []
#
#
# for j in range(1):
#     for i in range(9):
#         new_train_input = train_input[j, :, :][:, i][(train_input[j, :, :][:, i] != 0)]
#
#
#         # print(U.shape)
#         # print(U, "U")
#         # print(U != 0)
#
#
#         # plt.figure(i)
#         # plt.plot(new_train_input)
#         # plt.autoscale(enable=True, axis='both', tight=None)
#         # plt.show()
#
#         np.dstack(new_train_input, )
#
# print(new_train_input.shape)
# plt.plot(new_train_input)
# plt.autoscale(enable=True, axis='both', tight=None)
# plt.show()
#
# for i in range(9):
#     H = train_input[0]
#     H = H[:, [i]]
#     plt.figure(i)
#     plt.plot(H)
#     plt.autoscale(enable=True, axis='both', tight=None)
#     plt.show()

