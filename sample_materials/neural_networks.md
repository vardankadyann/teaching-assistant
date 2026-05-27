# Neural Networks Fundamentals

## Perceptron to Multi-Layer Networks

A single neuron computes: output = activation(weighted sum of inputs + bias). Stacking layers of neurons creates a **multi-layer perceptron (MLP)** capable of learning non-linear decision boundaries.

## Activation Functions

- **ReLU**: f(x) = max(0, x) — default for hidden layers; avoids vanishing gradients in many cases
- **Sigmoid**: outputs in (0, 1) — common for binary classification output
- **Softmax**: converts logits to a probability distribution — used for multi-class output

## Forward and Backward Pass

**Forward pass**: inputs flow through layers to produce predictions and loss.

**Backward pass (backpropagation)**: the chain rule computes gradients of the loss with respect to each weight. Optimizers (SGD, Adam) use these gradients to update weights.

## Batch Size and Epochs

- **Batch**: number of samples per gradient update
- **Epoch**: one full pass through the training set
- **Mini-batch SGD**: balances noise (small batches) with hardware efficiency (larger batches)

## Common Architectures

- **CNNs**: exploit spatial structure in images (convolution + pooling)
- **RNNs / LSTMs**: sequence modeling (older approach for text)
- **Transformers**: self-attention; dominant in modern NLP and increasingly in vision

## Regularization in Deep Learning

- **Dropout**: randomly zero activations during training
- **Weight decay**: L2 penalty on weights
- **Early stopping**: halt training when validation loss stops improving
- **Data augmentation**: synthetic variety for images/text

## Vanishing / Exploding Gradients

Very deep networks can suffer from gradients that shrink or grow exponentially. Solutions include ReLU, residual connections (ResNet), gradient clipping, and careful initialization.
