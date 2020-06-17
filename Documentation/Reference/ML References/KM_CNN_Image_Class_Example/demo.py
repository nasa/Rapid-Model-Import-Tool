# https://keras.io/applications/

import keras
#from keras.applications.inception_v3 import InceptionV3, preprocess_input
from keras.applications.vgg19 import VGG19, preprocess_input
#from keras.applications.xception import Xception, preprocess_input, decode_predictions
#from keras.applications.vgg16 import VGG16, preprocess_input
from keras.preprocessing import image
from keras.models import Model
from keras.layers import Dense, GlobalAveragePooling2D, Dropout, MaxPooling2D
from keras import backend as K
import os
import glob
import numpy as np
from keras import backend as K
from keras.engine.topology import Layer
from keras import optimizers 

lr1 = 0.01
lr2 = 0.0001
iter1 = 10
iter2 = 10
n_classes = 11
data_path = "dataset/"
train_dir = data_path + "train/"
test_dir = data_path + 'test/'

def predict_test(model,train_generator):
	test_dirs = os.listdir(test_dir)
	correct = 0
	count = 0
	for f in test_dirs:
		if os.path.isdir(test_dir+f):
			img_path = glob.glob(test_dir+f+"/"+"*.png")
			for i in range(0,len(img_path)):
				img = image.load_img(img_path[i], target_size=(150, 150))
				x = image.img_to_array(img)
				x = np.expand_dims(x, axis=0)
				x = preprocess_input(x)
				preds = model.predict(x)
				ind = np.argmax(preds)
				if ind == train_generator.class_indices[f]:
					correct += 1
				count += 1
	return float(correct)/float(count)

# create the base pre-trained model
base_model = VGG19(weights='imagenet', include_top=False)
#base_model = Xception(weights='imagenet', include_top=False)

# add a global spatial average pooling layer
x = base_model.output
#x = MaxPooling2D(pool_size=(4, 4), strides=None, padding='valid', data_format=None)(x)
x = GlobalAveragePooling2D()(x)
#x = filterReductionLayer()(x)

# let's add a fully-connected layer
x = Dense(16, activation='relu')(x)
x = Dropout(0.2)(x)
# and a logistic layer -- let's say we have 5 classes
predictions = Dense(n_classes, activation='softmax')(x)

# this is the model we will train
model = Model(inputs=base_model.input, outputs=predictions)

# first: train only the top layers (which were randomly initialized)
# i.e. freeze all convolutional InceptionV3 layers
for layer in base_model.layers:
	layer.trainable = False

# compile the model (should be done *after* setting layers to non-trainable)
model.compile(optimizers.RMSprop(lr=lr1, decay=0.0), loss='categorical_crossentropy')

#train_datagen = image.ImageDataGenerator(rescale=1./255, shear_range=0.2, zoom_range=0.2, horizontal_flip=True)
train_datagen = image.ImageDataGenerator(shear_range=0.2, zoom_range=0.2, horizontal_flip=True)

train_generator = train_datagen.flow_from_directory(train_dir,target_size=(150, 150),batch_size=64,class_mode='categorical')

print (model.summary())

# train the model on the new data for a few epochs
model.fit_generator(train_generator,samples_per_epoch=200, epochs=iter1)

# at this point, the top layers are well trained and we can start fine-tuning
# convolutional layers from inception V3. We will freeze the bottom N layers
# and train the remaining top layers.

# let's visualize layer names and layer indices to see how many layers
# we should freeze:
for i, layer in enumerate(base_model.layers):
	print(i, layer.name)

acc_stage1 = predict_test(model,train_generator)

print(acc_stage1)

# -------------------------------------------


# we chose to train the top 2 inception blocks, i.e. we will freeze
# the first 249 layers and unfreeze the rest:
for layer in model.layers[:20]:
	layer.trainable = False
for layer in model.layers[20:]:
	layer.trainable = True

# we need to recompile the model for these modifications to take effect
# we use SGD with a low learning rate
from keras.optimizers import SGD
model.compile(optimizer=SGD(lr=lr2, momentum=0.9), loss='categorical_crossentropy')

# we train our model again (this time fine-tuning the top 2 inception blocks
# alongside the top Dense layers
model.fit_generator(train_generator,samples_per_epoch=300, epochs=iter2)

acc_stage2 = predict_test(model,train_generator)

print(acc_stage2)
