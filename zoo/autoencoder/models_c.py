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

import tensorflow as tf
from tensorflow.keras.layers import ReLU, Dense, Conv2D, Conv2DTranspose
from tensorflow.keras.regularizers import l2
import tensorflow.keras.backend as K

class Composable(object):
    ''' Composable base (super) class for Models '''
    init_weights = 'he_normal'	# weight initialization
    reg          = l2(0.001)    # kernel regularizer
    relu         = None         # ReLU max value

    def __init__(self, init_weights=None, reg=None, relu=None):
        """ Constructor
            init_weights :
            relu         :
        """
        if init_weights is not None:
            self.init_weights = init_weights
        if reg is not None:
            self.reg = reg
        if relu is not None:
            self.relu = relu

        # Feature maps encoding at the bottleneck layer in classifier (high dimensionality)
        self._encoding = None
        # Pooled and flattened encodings at the bottleneck layer (low dimensionality)
        self._embedding = None
        # Pre-activation conditional probabilities for classifier
        self._probabilities = None
        # Post-activation conditional probabilities for classifier
        self._softmax = None

        self._model = None

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, _model):
        self._model = _model

    @property
    def encoding(self):
        return self._encoding

    @encoding.setter
    def encoding(self, layer):
        self._encoding = layer

    @property
    def embedding(self):
        return self._embedding

    @embedding.setter
    def embedding(self, layer):
        self._embedding = layer

    @property
    def probabilities(self):
        return self._probabilities

    @probabilities.setter
    def probabilities(self, layer):
        self._probabilities = layer

    @staticmethod
    def ReLU(x):
        """ Construct ReLU activation function
            x  : input to activation function
        """
        x = ReLU(Composable.relu)(x)
        return x
	
    @staticmethod
    def HS(x):
        """ Hard Swish activation """
        return (x * K.relu(x + 3, max_value=6.0)) / 6.0

    @staticmethod
    def Dense(x, units, activation=None, use_bias=True, **hyperparameters):
        """ Construct Dense Layer
            x           : input to layer
            activation  : activation function
            use_bias    : whether to include the bias
            init_weights: kernel initializer
            reg         : kernel regularizer
        """
        if 'reg' in hyperparameters:
            reg = hyperparameters['reg']
        else:
            reg = Composable.reg
        if 'init_weights' in hyperparameters:
            init_weights = hyperparameters['init_weights']
        else:
            init_weights = Composable.init_weights
            
        x = Dense(units, activation, use_bias=use_bias,
                  kernel_initializer=init_weights, kernel_regularizer=reg)(x)
        return x

    @staticmethod
    def Conv2D(x, n_filters, kernel_size, strides=(1, 1), padding='valid', activation=None, use_bias=True, **hyperparameters):
        """ Construct a Conv2D layer
            x           : input to layer
            n_filters   : number of filters
            kernel_size : kernel (filter) size
            strides     : strides
            padding     : how to pad when filter overlaps the edge
            activation  : activation function
            use_bias    : whether to include the bias
            init_weights: kernel initializer
            reg         : kernel regularizer
        """
        if 'reg' in hyperparameters:
            reg = hyperparameters['reg']
        else:
            reg = Composable.reg
        if 'init_weights' in hyperparameters:
            init_weights = hyperparameters['init_weights']
        else:
            init_weights = Composable.init_weights

        x = Conv2D(n_filters, kernel_size, strides=strides, padding=padding, activation=activation, use_bias=use_bias,
                   kernel_initializer=init_weights, kernel_regularizer=reg)(x)
        return x

    @staticmethod
    def Conv2DTranspose(x, n_filters, kernel_size, strides=(1, 1), padding='valid', activation=None, use_bias=True, **hyperparameters):
        """ Construct a Conv2DTranspose layer
            x           : input to layer
            n_filters   : number of filters
            kernel_size : kernel (filter) size
            strides     : strides
            padding     : how to pad when filter overlaps the edge
            activation  : activation function
            use_bias    : whether to include the bias
            init_weights: kernel initializer
            reg         : kernel regularizer
        """
        if 'reg' in hyperparameters:
            reg = hyperparameters['reg']
        else:
            reg = Composable.reg
        if 'init_weights' in hyperparameters:
            init_weights = hyperparameters['init_weights']
        else:
            init_weights = Composable.init_weights

        x = Conv2DTranspose(n_filters, kernel_size, strides=strides, padding=padding, activation=activation, use_bias=use_bias,
                            kernel_initializer=init_weights, kernel_regularizer=reg)(x)
        return x
