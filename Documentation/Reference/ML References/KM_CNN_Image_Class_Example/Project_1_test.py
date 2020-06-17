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
import math
from keras import backend as K
from keras.engine.topology import Layer
from keras import optimizers
import tensorflow as tf
import time
from keras.models import load_model

' Test Data Script '

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
test_dir = data_path + "test/"

test_datagen = ImageDataGenerator(shear_range=0.2, zoom_range=0.2, horizontal_flip=True, fill_mode='nearest', rescale=1./225, height_shift_range=0.2, width_shift_range=0.2, rotation_range=40)

def predict_test(model, test_generator):
    test_dirs = os.listdir(test_dir)
    correct = 0
    count = 0
    for f in test_dirs:
        if os.path.isdir(test_dir+f):
            img_path = glob.glob(test_dir+f+"/"+"*.jpg")
            for i in range(0, len(img_path)):
                img = image.load_img(img_path[i], target_size=(150, 150))
                x = image.img_to_array(img)
                x = np.expand_dims(x, axis=0)
                x = preprocess_input(x)
                preds = model.predict(x)
                ind = np.argmax(preds)
                if ind == test_generator.class_indices[f]:
                    correct += 1
                count += 1
    return float(correct)/float(count)

# Batch Data
test_generator = test_datagen.flow_from_directory(test_dir, target_size=(150,150), class_mode='categorical', batch_size=16)

# Load Model
# model = load_model('current_model.h5')

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

# Evaluate test data on model
acc_stage1 = predict_test(model, test_generator)
print(acc_stage1)

del model
