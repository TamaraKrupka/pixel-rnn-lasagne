import theano.tensor as T
import lasagne

from masks import mask_a, mask_b


class MaskedConv2D(lasagne.layers.Conv2DLayer):
    """
    Note: the layer does not have a non-linearity on top of it
    """

    def __init__(self, incoming, num_filters, filter_size, mask="a", stride=(1, 1), untie_biases=False,
                 W=lasagne.init.GlorotUniform(),
                 b=lasagne.init.Constant(0.),
                 nonlinearity=lasagne.nonlinearities.identity, **kwargs):
        super(MaskedConv2D, self).__init__(incoming, num_filters, filter_size, stride=stride,
                                           pad="same", untie_biases=untie_biases, W=W, b=b,
                                           nonlinearity=nonlinearity,
                                           convolution=T.nnet.conv2d, **kwargs)
        self.mask = mask

    def convolve(self, input, **kwargs):
        if self.mask == "a":
            W = mask_a(self.W)
        elif self.mask == "b":
            W = mask_b(self.W)
        conved = self.convolution(input, W,
                                  self.input_shape, self.get_W_shape(),
                                  subsample=self.stride,
                                  border_mode='half',
                                  filter_flip=False)
        return conved


if __name__ == "__main__":
    import theano
    import numpy as np

    input = T.tensor4("filter")

    input_layer = lasagne.layers.InputLayer(input_var=input, shape=(None, 3, 9, 9))
    network = MaskedConv2D(incoming=input_layer, num_filters=4, filter_size=(3, 3))
    output = lasagne.layers.get_output(network)
    f = theano.function(inputs=[input], outputs=output)
    convolved = f(np.ones((1, 3, 9, 9), dtype=np.float32))
    print(convolved)
