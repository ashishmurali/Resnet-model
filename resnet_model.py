# -*- coding: utf-8 -*-
"""Resnet-model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1BNbs6WktEGCV2jZ5lSMnWJs_uq7TpcGR
"""

import numpy as np
import tensorflow as tf
from numpy import size
from keras.layers import Input, Add, Dense, Activation, ZeroPadding2D, BatchNormalization, Flatten, Conv2D, AveragePooling2D, Lambda
from keras.models import Model
from keras.initializers import glorot_uniform
from matplotlib import pyplot as plt

import keras.backend as K
K.set_image_data_format('channels_last')

def convert_to_one_hot(Y, C):
    Y = np.eye(C)[Y.reshape(-1)].T
    return Y

def identity_block(X,f):
    
    X_shortcut = X
    
    # First component of main path
    X = ZeroPadding2D((1,1))(X)
    X = Conv2D(filters = f, kernel_size = (3, 3), strides = (1,1), padding = 'valid',  kernel_initializer = glorot_uniform())(X)
    X = BatchNormalization(axis = 3)(X)
    X = Activation('relu')(X)

    # Second component of main path 
    X = ZeroPadding2D((1,1))(X)
    X = Conv2D(filters = f, kernel_size = (3, 3), strides = (1,1), padding = 'valid',  kernel_initializer = glorot_uniform())(X)
    X = BatchNormalization(axis = 3)(X)

    # Add shortcut value to main path, and pass it through a RELU activation
    X = Add()([X,X_shortcut])
    X = Activation('relu')(X)
    
    return X

def downsampling_block(X, filters,pad):
     
    X_shortcut = X
    
    # First component of main path
    X = ZeroPadding2D((1,1))(X)
    X = Conv2D(filters = filters, kernel_size = (3, 3), strides = (2,2), padding = 'valid',  kernel_initializer = glorot_uniform())(X)
    X = BatchNormalization(axis = 3)(X)
    X = Activation('relu')(X)

    # Second component of main path 
    X = ZeroPadding2D((1,1))(X)
    X = Conv2D(filters = filters, kernel_size = (3, 3), strides = (1,1), padding = 'valid',  kernel_initializer = glorot_uniform())(X)
    X = BatchNormalization(axis = 3)(X)

    # downsampling
    X_shortcut = Lambda(lambda x: x[:,0:int(size(x,1)/2), 0:int(size(x,2)/2),:])(X_shortcut)
    X_shortcut = ZeroPadding2D((0,pad),data_format="channels_first")(X_shortcut) 

    # Add shortcut value to main path, and pass it through a RELU activation
    X = Add()([X,X_shortcut])
    X = Activation('relu')(X)
    
    
    return X

def bottleneck_identity_block(X,filters):
    
    F1, F2, F3 = filters
    
    X_shortcut = X
    
    # First component of main path
    X = Conv2D(filters = F1, kernel_size = (1, 1), strides = (1,1), padding = 'valid' ,kernel_initializer = glorot_uniform())(X)
    X = BatchNormalization(axis = 3)(X)
    X = Activation('relu')(X)
    
    # Second component of main path 
    X = Conv2D(filters = F2, kernel_size = (3, 3), strides = (1,1), padding = 'same', kernel_initializer = glorot_uniform())(X)
    X = BatchNormalization(axis = 3)(X)
    X = Activation('relu')(X)

    # Third component of main path
    X = Conv2D(filters = F3, kernel_size = (1, 1), strides = (1,1), padding = 'valid', kernel_initializer = glorot_uniform())(X)
    X = BatchNormalization(axis = 3)(X)

    # Add shortcut value to main path, and pass it through a RELU activation
    X = Add()([X,X_shortcut])
    X = Activation('relu')(X)
    
    return X

def bottleneck_downsampling_block(X,filters, s = 2,pad=8):
    
    F1, F2, F3 = filters
    
    X_shortcut = X

    # First component of main path 
    X = Conv2D(F1, (1, 1), strides = (s,s),padding = 'valid', kernel_initializer = glorot_uniform())(X)
    X = BatchNormalization(axis = 3)(X)
    X = Activation('relu')(X)

    # Second component of main path 
    X = Conv2D(F2, (3,3), strides = (1,1), padding = 'same', kernel_initializer = glorot_uniform())(X)
    X = BatchNormalization(axis = 3)(X)
    X = Activation('relu')(X)

    # Third component of main path 
    X = Conv2D(F3, (1, 1), strides = (1,1), padding = 'valid', kernel_initializer = glorot_uniform())(X)
    X = BatchNormalization(axis = 3)(X)

    if s==2:
      X_shortcut = Lambda(lambda x: x[:,0:int(size(x,1)/2), 0:int(size(x,2)/2),:])(X_shortcut)
    X_shortcut = ZeroPadding2D((0,pad),data_format="channels_first")(X_shortcut) 

    # Add shortcut value to main path, and pass it through a RELU activation
    X = Add()([X,X_shortcut])
    X = Activation('relu')(X)
    
    return X

def ResNet(input_shape = (32, 32, 3), classes = 10,type='basic'):

    if type == 'basic':

      # if type = basic our ResNet will be a 32 weighted layers model with basic residual block
      X_input = Input(input_shape)
      
      # 1st layer
      X = ZeroPadding2D((1,1))(X_input)
      X = Conv2D(16, (3,3), strides = (1, 1),padding='valid', kernel_initializer = glorot_uniform())(X)
      X = BatchNormalization(axis = 3)(X)
      X = Activation('relu')(X)

      
      X = identity_block(X,16)
      X = identity_block(X,16)
      X = identity_block(X,16)
      X = identity_block(X,16)
      X = identity_block(X,16)

      X = downsampling_block(X,32,8)
      X = identity_block(X,32)
      X = identity_block(X,32)
      X = identity_block(X,32)
      X = identity_block(X,32)

      X = downsampling_block(X,64,16)
      X = identity_block(X,64)
      X = identity_block(X,64)
      X = identity_block(X,64)
      X = identity_block(X,64)

      X = AveragePooling2D((2,2))(X)

      X = Flatten()(X)

      X = Dense(classes, activation='softmax',  kernel_initializer = glorot_uniform())(X)
      
      # Create model
      model = Model(inputs = X_input, outputs = X, name='ResNet32')
      
    if type== 'bottleneck':
      # if type = bottleneck out ResNet will be a 50 weighted layer network with bottleneck residual blocks
      X_input = Input(input_shape)
      
      X = ZeroPadding2D((1, 1))(X_input)
      
      # Layer 1
      X = Conv2D(16, (3, 3), strides = (1, 1),padding='valid', kernel_initializer = glorot_uniform())(X)
      X = BatchNormalization(axis = 3)(X)
      X = Activation('relu')(X)

      X = bottleneck_downsampling_block(X, filters = [16, 16, 64],s = 1,pad =24)
      X = bottleneck_identity_block(X,[16, 16, 64])
      X = bottleneck_identity_block(X,[16, 16, 64])

      X = bottleneck_downsampling_block(X, filters = [32,32,128],s = 2,pad =32)
      X = bottleneck_identity_block(X, [32,32,128])
      X = bottleneck_identity_block(X, [32,32,128])
      X = bottleneck_identity_block(X, [32,32,128])

      X = bottleneck_downsampling_block(X, filters = [64,64,256], s = 2,pad=64)
      X = bottleneck_identity_block(X,  [64,64,256])
      X = bottleneck_identity_block(X,  [64,64,256])
      X = bottleneck_identity_block(X,  [64,64,256])
      X = bottleneck_identity_block(X,  [64,64,256])
      X = bottleneck_identity_block(X,  [64,64,256])

      X = bottleneck_downsampling_block(X, filters = [128,128,512], s = 2,pad =128)
      X = bottleneck_identity_block(X, [128,128,512])
      X = bottleneck_identity_block(X, [128,128,512])

      X = AveragePooling2D((2,2))(X)

      X = Flatten()(X)

      X = Dense(classes, activation='softmax', kernel_initializer = glorot_uniform())(X)

      # Create model
      model = Model(inputs = X_input, outputs = X, name='ResNet50')   


    return model

# basic residual block
model1 = ResNet(input_shape = (32, 32, 3), classes = 10,type='basic')

model1.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

(x_train_origin, y_train_origin), (x_test_origin, y_test_origin) = tf.keras.datasets.cifar10.load_data()
x_train = x_train_origin/255.
x_test = x_test_origin/255.
y_train = convert_to_one_hot(y_train_origin, 10).T
y_test = convert_to_one_hot(y_test_origin, 10).T

h = model1.fit(x_train, y_train,validation_data=(x_test, y_test),epochs=80, batch_size=128)

preds = model1.evaluate(x_test, y_test)
print ("Loss = " + str(preds[0]))
print ("Test Accuracy = " + str(preds[1]))

losses = h.history['loss']
accs = h.history['accuracy']
val_losses = h.history['val_loss']
val_accs = h.history['val_accuracy']
epochs = len(losses)

plt.figure(figsize=(12, 4))
for i, metrics in enumerate(zip([losses, accs], [val_losses, val_accs], ['Loss', 'Accuracy'])):
    plt.subplot(1, 2, i + 1)
    plt.plot(range(epochs), metrics[0], label='Training {}'.format(metrics[2]))
    plt.plot(range(epochs), metrics[1], label='Validation {}'.format(metrics[2]))
    plt.legend()
plt.show()

# bottleneck residual block
model2 = ResNet(input_shape = (32, 32, 3), classes = 10,type='bottleneck')

model2.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

H = model2.fit(x_train, y_train,validation_data=(x_test, y_test),epochs=80, batch_size=128)

preds = model2.evaluate(x_test, y_test)
print ("Loss = " + str(preds[0]))
print ("Test Accuracy = " + str(preds[1]))

losses = H.history['loss']
accs = H.history['accuracy']
val_losses = H.history['val_loss']
val_accs = H.history['val_accuracy']
epochs = len(losses)

plt.figure(figsize=(12, 4))
for i, metrics in enumerate(zip([losses, accs], [val_losses, val_accs], ['Loss', 'Accuracy'])):
    plt.subplot(1, 2, i + 1)
    plt.plot(range(epochs), metrics[0], label='Training {}'.format(metrics[2]))
    plt.plot(range(epochs), metrics[1], label='Validation {}'.format(metrics[2]))
    plt.legend()
plt.show()

