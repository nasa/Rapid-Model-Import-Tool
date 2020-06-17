#from keras.applications.inception_v3 import InceptionV3, preprocess_input
from keras.applications.vgg19 import VGG19, preprocess_input
from keras.applications.xception import Xception, preprocess_input, decode_predictions
#from keras.applications.vgg16 import VGG16, preprocess_input
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Model
from keras.models import Sequential
from keras.callbacks import TensorBoard
from keras.layers import Dense, GlobalAveragePooling2D, Dropout, MaxPooling2D, Flatten, Conv2D
from keras import backend as K
import os
import glob
import numpy as np
from keras import backend as K
from keras.engine.topology import Layer
from keras import optimizers
import tensorflow as tf
import time

' Train Data Script '

' Project 1 '
' Kyle Mott '
' 03/04/19 '

NAME = "project-1-cnn-test-{}".format(int(time.time()))

tensorboard = TensorBoard(log_dir='logs/{}'.format(NAME))

# Checking GPU
from tensorflow.python.client import device_lib
print(device_lib.list_local_devices())

# Initialization
n_classes = 11
class_set = ["creamy_paste", "diced", "floured", "grated", "juiced", "jullienne", "mixed", "other", "peeled", "sliced", "whole"]
data_path = "dataset/"
train_dir = data_path + "train/"
valid_dir = data_path + "valid/"

train_datagen = ImageDataGenerator(shear_range=0.2, zoom_range=0.2, horizontal_flip=True, fill_mode='nearest', rescale=1./225, height_shift_range=0.2, width_shift_range=0.2, rotation_range=40)
valid_datagen = ImageDataGenerator(shear_range=0.2, zoom_range=0.2, horizontal_flip=True, fill_mode='nearest', rescale=1./225, height_shift_range=0.2, width_shift_range=0.2, rotation_range=40)

# Batch Data
train_generator = train_datagen.flow_from_directory(train_dir, target_size=(150,150), class_mode='categorical', batch_size=16)
valid_generator = valid_datagen.flow_from_directory(valid_dir, target_size=(150,150), class_mode='categorical', batch_size=16)

# create the base pre-trained model
# base_model = Sequential()
base_model = VGG19(weights="imagenet", include_top=False, input_shape=(150,150,3))
# base_model = Xception(weights="imagenet", include_top=False, input_shape=(150,150,3))

# add a global spatial average pooling layer
model = base_model.output
# x = MaxPooling2D(pool_size=(4, 4), strides=None, padding="valid", data_format=None)(x)
model = GlobalAveragePooling2D()(model)
# x = filterReductionLayer()(x)

# i.e. freeze all convolutional InceptionV3 layers
for layer in base_model.layers:
    layer.trainable = False

model = Conv2D(32, padding='same', kernel_size=(3, 3), activation='relu')(base_model.input)
model = Conv2D(32, kernel_size=(3, 3), activation='relu')(model)
model = MaxPooling2D(pool_size=(2, 2))(model)
model = Dropout(0.25)(model)

model = Conv2D(64, padding='same', kernel_size=(3, 3), activation='relu')(model)
model = Conv2D(64, kernel_size=(3, 3), activation='relu')(model)
model = MaxPooling2D(pool_size=(2, 2))(model)
model = Dropout(0.25)(model)

model = Conv2D(64, padding='same', kernel_size=(3, 3), activation='relu')(model)
model = Conv2D(64, kernel_size=(3, 3), activation='relu')(model)
model = MaxPooling2D(pool_size=(2, 2))(model)
model = Dropout(0.25)(model)

# model = Conv2D(64, padding='same', kernel_size=(3, 3), activation='relu')(model)
# model = Conv2D(64, kernel_size=(3, 3), activation='relu')(model)
# model = MaxPooling2D(pool_size=(2, 2))(model)
# model = Dropout(0.25)(model)
#
# model = Conv2D(64, padding='same', kernel_size=(3, 3), activation='relu')(model)
# model = Conv2D(64, kernel_size=(3, 3), activation='relu')(model)
# model = MaxPooling2D(pool_size=(2, 2))(model)
# model = Dropout(0.25)(model)

model = Flatten()(model)
model = Dense(512, activation='relu')(model)
model = Dropout(0.5)(model)

# Output Layer
model = Dense(11, activation='softmax')(model)

# this is the model we will train
model = Model(inputs=base_model.input, outputs=model)

# freezing layers
for layer in model.layers[:20]:
    layer.trainable = False
for layer in model.layers[20:]:
    layer.trainable = True

# Compile Model
# model.compile(optimizers.RMSprop(lr=0.01, decay=0.0), loss='categorical_crossentropy', metrics=['accuracy'])
# model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])
model.compile(optimizers.Adam(lr=0.0003), loss='categorical_crossentropy', metrics=['accuracy'])

# loading weights
model.load_weights("weights.h5")

# train the model on the new data for a few epochs
model.fit_generator(train_generator, steps_per_epoch=6348 // 16,
                    validation_data=valid_generator, validation_steps=1377 // 16, epochs=50, callbacks=[tensorboard])

# saving weights
model.save_weights('weights_new.h5')

# saving model
model.save('current_model.h5')

# deleting model
del model


# # Conv, Pooling
# model = Conv2D(32, activation="relu", kernel_size=(3,3))(model)
# model = MaxPooling2D(pool_size=(2,2))(model)
#
# # Conv, Pooling (2)
# model = Conv2D(100, activation="relu", kernel_size=(3,3))(model)
# model = MaxPooling2D(pool_size=(2,2))(model)
#
# # Flatten, Dense
# model = Flatten()(model)
# # model = Dense(64)(model)

# model = Dense(16, activation='relu')(model)
# model = Dropout(0.2)(model)

