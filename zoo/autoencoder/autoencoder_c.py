# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# AutoEncoder

import tensorflow as tf
from tensorflow.keras import Model, Input
from tensorflow.keras.layers import Conv2D, Conv2DTranspose, ReLU, BatchNormalization

import sys
sys.path.append('../')
from models_c import Composable

class AutoEncoder(Composable):
    ''' Construct an AutoEncoder '''
    # metaparameter: number of filters per layer
    layers = [ {'n_filters': 64 }, { 'n_filters': 32 }, { 'n_filters': 16 } ]

    def __init__(self, layers=None, input_shape=(32, 32, 3),
                 init_weights='he_normal', reg=None):
        ''' Construct an AutoEncoder
            input_shape : input shape to the autoencoder
            layers      : the number of filters per layer
            init_weights: kernel initializer
            reg         : kernel regularizer
        '''
        # Configure base (super) class
        super().__init__(init_weights=init_weights, reg=reg)

        if layers is None:
           layers = AutoEncoder.layers

        # remember the layers
        self.layers = layers

        # remember the input shape
        self.input_shape = input_shape

        inputs = Input(input_shape)
        encoder = AutoEncoder.encoder(inputs, layers=layers)
        outputs = AutoEncoder.decoder(encoder, layers=layers)
        self._model = Model(inputs, outputs)

    @staticmethod
    def encoder(x, init_weights=None, **metaparameters):
        ''' Construct the Encoder 
            x     : input to the encoder
            layers: number of filters per layer
            reg   : kernel regularizer
        '''
        layers = metaparameters['layers']
        if 'reg' in metaparameters:
            reg = metaparameters['reg']
        else:
            reg = AutoEncoder.reg
        if 'init_weights' in metaparameters:
            init_weights = metaparameters['init_weights']
        else:
            init_weights = AutoEncoder.init_weights

        # Progressive Feature Pooling
        for layer in layers:
            n_filters = layer['n_filters']
            x = Conv2D(n_filters, (3, 3), strides=2, padding='same',
                       kernel_initializer=init_weights, kernel_regularizer=reg)(x)
            x = BatchNormalization()(x)
            x = Composable.ReLU(x)

        # The Encoding
        return x

    @staticmethod
    def decoder(x, init_weights=None, **metaparameters):
        ''' Construct the Decoder
            x     : input to the decoder
            layers: number of filters per layer
            reg   : kernel regularizer
        '''
        layers = metaparameters['layers']
        if 'reg' in metaparameters:
            reg = metaparameters['reg']
        else:
            reg = AutoEncoder.reg
        if 'init_weights' in metaparameters:
            init_weights = metaparameters['init_weights']
        else:
            init_weights = AutoEncoder.init_weights

        # Progressive Feature Unpooling
        for _ in range(len(layers)-1, 0, -1):
            n_filters = layers[_]['n_filters']
            x = Conv2DTranspose(n_filters, (3, 3), strides=2, padding='same',
                                kernel_initializer=init_weights, kernel_regularizer=reg)(x)
            x = BatchNormalization()(x)
            x = Composable.ReLU(x)

        # Last unpooling and match shape to input
        x = Conv2DTranspose(3, (3, 3), strides=2, padding='same',
                            kernel_initializer=init_weights, kernel_regularizer=reg)(x)
        x = BatchNormalization()(x)
        x = Composable.ReLU(x)

        # The decoded image
        return x

    def compile(self, optimizer='adam'):
        ''' Compile the model using Mean Square Error loss '''
        self._model.compile(loss='mse', optimizer=optimizer, metrics=['accuracy'])

    def extract(self):
        ''' Extract the pretrained encoder
        '''
        # Get the trained weights from the autoencoder
        weights = self._model.get_weights()

        # Extract out the weights for just the encoder  (6 sets per layer)
        encoder_weights = weights[0 : int((6 * len(self.layers)))]
  
        # Construct a copy the encoder
        inputs = Input(self.input_shape)
        outputs = self.encoder(inputs, layers=self.layers)
        encoder = Model(inputs, outputs)

        # Initialize the encoder with the pretrained weights
        encoder.set_weights(encoder_weights)

        return encoder

# Example autoencoder
# autoencoder = AutoEncoder()

# Train the model, and extract pretrained encoder
# e = autoencoder.extract()
