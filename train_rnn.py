import csv
import pprint as pp
import numpy as np

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense, TimeDistributed
from keras.layers.embeddings import Embedding
from keras.layers.recurrent import GRU


def load_stories(read):
    with open(read, 'r') as csvfile:
        story_reader = csv.reader(csvfile, delimiter=',')
        story_lists = [row for row in story_reader]
    return [' '.join(story) for story in story_lists]


def build_rnn(vocab_size, embeddings, hidden, batch_size, timesteps):
    model = Sequential()
    model.add(Embedding(batch_input_shape=(batch_size, timesteps),
                        input_dim=vocab_size + 1,
                        output_dim=embeddings,
                        mask_zero=True))
    model.add(GRU(hidden,
                  return_sequences=True,
                  stateful=True))
    model.add(GRU(hidden,
                  return_sequences=True,
                  stateful=True))
    model.add(TimeDistributed(Dense(vocab_size + 1, activation='softmax')))
    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam')
    return model


def main(read):
    stories = load_stories(read)  # Load ROC dataset

    # Process story data with Keras tokenizer
    token = Tokenizer()
    token.fit_on_texts(stories)  # Splits stories into indexed words
    vocab_idxs = token.texts_to_sequences(stories)  # Vectorize story indexes
    max_len = max([len(story) for story in vocab_idxs])  # Longest story
    # Create matrix, X, where X[i, :] is a story vector
    story_matrix = pad_sequences(vocab_idxs, maxlen=max_len)

    # Offset each word by 1 so that every input word, x[i], maps to y[i + 1]
    X_train, y_train = story_matrix[:, :-1], story_matrix[:, 1:]
    pp.pprint(X_train[0])
    pp.pprint(y_train[0])

    # Graph RNN with input hyperparams
    batch_size = 20
    rnn_model = build_rnn(vocab_size=len(token.word_index),
                          embeddings=300,
                          hidden=500,
                          batch_size=batch_size,
                          timesteps=max_len - 1)

    # Train the RNN
    epochs = 10
    print("Training RNN on {} stories for {} epochs...".format(
        len(X_train), epochs)
    )
    for epoch in range(epochs):
        epoch_loss = []
        for batch in range(0, len(X_train)):
            batch_x = X_train[batch: batch + batch_size]
            batch_y = y_train[batch: batch + batch_size, :, None]
            batch_loss = rnn_model.train_on_batch(batch_x, batch_y)
            epoch_loss.append(batch_loss)
        print("Epoch: {} | Mean Error {%.3f}".format(
            epoch + 1, np.mean(epoch_loss))
        )


if __name__ == '__main__':
    main('data/roc_stories_full.csv')
    # main('data/test.csv')
