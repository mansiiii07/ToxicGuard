# -*- coding: utf-8 -*-
"""Toxic_Comments_Classification.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1GlBryLxJBcHi6ImJVcC4_WzpAWrZQoy0

# Importing Libraries
"""

from google.colab import drive
drive.mount('/content/drive')

! pip install talos

# Commented out IPython magic to ensure Python compatibility.
import numpy as np, pandas as pd

!pip install Keras-Preprocessing


import re
import spacy
from spacy.lang.en import English
from spacy.lang.en.stop_words import STOP_WORDS
from nltk.tokenize import word_tokenize
import nltk
from nltk.stem import WordNetLemmatizer
nltk.download('wordnet')
import string
from string import ascii_lowercase

from tqdm import tqdm_notebook
import itertools
import io

import matplotlib.pyplot as plt
# %matplotlib inline

from functools import reduce
from tensorflow import keras
from keras.preprocessing.text import Tokenizer
from keras_preprocessing.sequence import pad_sequences
from keras.layers import Dense, Input, LSTM, Embedding, Dropout, Activation
from keras.layers import Bidirectional, GlobalMaxPool1D
from keras.models import Model
from keras.models import Sequential
from keras.layers import Conv1D, MaxPooling1D
from keras.layers import BatchNormalization
from keras import initializers, regularizers, constraints, optimizers, layers
import talos

"""# Importing Data"""

train=pd.read_csv('/content/drive/MyDrive/train.csv/train.csv')
train.head()

test=pd.read_csv('/content/drive/MyDrive/test.csv/test.csv')
test.head()

"""Data Exploration

Checking for missing values
"""

train.shape

test.shape

train.isnull().any()

test.isnull().any()

Classification_labels = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']
y = train[Classification_labels].values

"""Data Pre-processing

Text Normalization
"""

regex_patterns = {
    ' american ':
        [
            'amerikan'
        ],

    ' adolf ':
        [
            'adolf'
        ],


    ' hitler ':
        [
            'hitler'
        ],

    ' fuck':
        [
            '(f)(u|[^a-z0-9 ])(c|[^a-z0-9 ])(k|[^a-z0-9 ])([^ ])*',
            '(f)([^a-z]*)(u)([^a-z]*)(c)([^a-z]*)(k)',
            ' f[!@#\$%\^\&\*]*u[!@#\$%\^&\*]*k', 'f u u c',
            '(f)(c|[^a-z ])(u|[^a-z ])(k)', r'f\*',
            'feck ', ' fux ', 'f\*\*', 'f**k','fu*k',
            'f\-ing', 'f\.u\.', 'f###', ' fu ', 'f@ck', 'f u c k', 'f uck', 'f ck'
        ],

    ' ass ':
        [
            '[^a-z]ass ', '[^a-z]azz ', 'arrse', ' arse ', '@\$\$',
            '[^a-z]anus', ' a\*s\*s', '[^a-z]ass[^a-z ]',
            'a[@#\$%\^&\*][@#\$%\^&\*]', '[^a-z]anal ', 'a s s','a55', '@$$'
        ],

    ' ass hole ':
        [
            ' a[s|z]*wipe', 'a[s|z]*[w]*h[o|0]+[l]*e', '@\$\$hole', 'a**hole'
        ],

    ' bitch ':
        [
            'b[w]*i[t]*ch', 'b!tch',
            'bi\+ch', 'b!\+ch', '(b)([^a-z]*)(i)([^a-z]*)(t)([^a-z]*)(c)([^a-z]*)(h)',
            'biatch', 'bi\*\*h', 'bytch', 'b i t c h', 'b!tch', 'bi+ch', 'l3itch'
        ],

    ' bastard ':
        [
            'ba[s|z]+t[e|a]+rd'
        ],

    ' trans gender':
        [
            'transgender'
        ],

    ' gay ':
        [
            'gay'
        ],

    ' cock ':
        [
            '[^a-z]cock', 'c0ck', '[^a-z]cok ', 'c0k', '[^a-z]cok[^aeiou]', ' cawk',
            '(c)([^a-z ])(o)([^a-z ]*)(c)([^a-z ]*)(k)', 'c o c k'
        ],

    ' dick ':
        [
            ' dick[^aeiou]', 'deek', 'd i c k', 'dik'
        ],

    ' suck ':
        [
            'sucker', '(s)([^a-z ]*)(u)([^a-z ]*)(c)([^a-z ]*)(k)', 'sucks', '5uck', 's u c k'
        ],

    ' cunt ':
        [
            'cunt', 'c u n t'
        ],

    ' bull shit ':
        [
            'bullsh\*t', 'bull\$hit'
        ],

    ' homo sex ual':
        [
            'homosexual'
        ],

    ' jerk ':
        [
            'jerk'
        ],

    ' idiot ':
        [
            'i[d]+io[t]+', '(i)([^a-z ]*)(d)([^a-z ]*)(i)([^a-z ]*)(o)([^a-z ]*)(t)', 'idiots'
                                                                                      'i d i o t'
        ],

    ' dumb ':
        [
            '(d)([^a-z ]*)(u)([^a-z ]*)(m)([^a-z ]*)(b)'
        ],

    ' shit ':
        [
            'shitty', '(s)([^a-z ]*)(h)([^a-z ]*)(i)([^a-z ]*)(t)', 'shite', '\$hit', 's h i t', '$h1t'
        ],

    ' shit hole ':
        [
            'shythole'
        ],

    ' retard ':
        [
            'returd', 'retad', 'retard', 'wiktard', 'wikitud'
        ],

    ' rape ':
        [
            ' raped'
        ],

    ' dumb ass':
        [
            'dumbass', 'dubass'
        ],

    ' ass head':
        [
            'butthead'
        ],

    ' sex ':
        [
            'sexy', 's3x', 'sexuality'
        ],


    ' nigger ':
        [
            'nigger', 'ni[g]+a', ' nigr ', 'negrito', 'niguh', 'n3gr', 'n i g g e r'
        ],

    ' shut the fuck up':
        [
            'stfu', 'st*u'
        ],

    ' pussy ':
        [
            'pussy[^c]', 'pusy', 'pussi[^l]', 'pusses', 'p*ssy'
        ],

    ' faggot ':
        [
            'faggot', ' fa[g]+[s]*[^a-z ]', 'fagot', 'f a g g o t', 'faggit',
            '(f)([^a-z ]*)(a)([^a-z ]*)([g]+)([^a-z ]*)(o)([^a-z ]*)(t)', 'fau[g]+ot', 'fae[g]+ot',
        ],

    ' mother fucker':
        [
            ' motha ', ' motha f', ' mother f', 'motherucker',
        ],

    ' whore ':
        [
            'wh\*\*\*', 'w h o r e'
        ],
    ' fucking ':
        [
            'f*$%-ing'
        ],
}

def clean_text(text,repeat_text=True, patterns_text=True, is_lower=True):

  if is_lower:
    text=text.lower()

  if patterns_text:
    for target, patterns in regex_patterns.items():
      for pat in patterns:
        text=str(text).replace(pat, target)

  if repeat_text:
    text = re.sub(r'(.)\1{2,}', r'\1', text)

  text = str(text).replace("\n", " ")
  text = re.sub(r'[^\w\s]',' ',text)
  text = re.sub('[0-9]',"",text)
  text = re.sub(" +", " ", text)
  text = re.sub("([^\x00-\x7F])+"," ",text)
  return text

"""Cleaning Training Data"""

train['comment_text']=train['comment_text'].apply(lambda x: clean_text(x))
train['comment_text'][1]

"""Cleaning Test Data"""

test['comment_text']=test['comment_text'].apply(lambda x: clean_text(x))
test['comment_text'][1048]

"""Lemmatization"""

comments_train=train['comment_text']
comments_test=test['comment_text']

comments_train=list(comments_train)
comments_test=list(comments_test)

wordnet_lemmatizer = WordNetLemmatizer()

def lemma(text, lemmatization=True):
  output=""
  if lemmatization:
    text=text.split(" ")
    for word in text:
       word1 = wordnet_lemmatizer.lemmatize(word, pos = "n")
       word2 = wordnet_lemmatizer.lemmatize(word1, pos = "v")
       word3 = wordnet_lemmatizer.lemmatize(word2, pos = "a")
       word4 = wordnet_lemmatizer.lemmatize(word3, pos = "r")
       output=output + " " + word4
  else:
    output=text

  return str(output.strip())

"""Lemmatizing Training Data"""

lem_train_data = []

for line in tqdm_notebook(comments_train, total=159571):
    lem_train_data.append(lemma(line))

lem_train_data[152458]

"""Lemmatizing Test Data"""

lem_test_data = []

for line in tqdm_notebook(comments_test, total=len(comments_test)):
    lem_test_data.append(lemma(line))

"""Stopwords Removal"""

Total_stopword=STOP_WORDS

"""# Removing Stopwords from Training Data"""

def stopwords(text, rem_stop_wrds=True):
  output_text = ""
  if rem_stop_wrds:
    text=text.split(" ")
    for word in text:
      if word not in Total_stopword:
        output_text=output_text + " " + word
  else :
    output_text=text

  return str(output_text.strip())

proc_train_data = []

for line in tqdm_notebook(lem_train_data, total=159571):
    proc_train_data.append(stopwords(line))

proc_train_data[152458]

"""Removing Stopwords from Test Data"""

proc_test_data = []

for line in tqdm_notebook(lem_test_data, total=153164):
    proc_test_data.append(stopwords(line))

"""Model Building"""

max_features=100000
maxpadlen = 200
val_split = 0.2
embed_dim_fasttext = 300

"""Tokenization"""

tokenizer = Tokenizer(num_words=max_features)
tokenizer.fit_on_texts(list(proc_train_data))
list_tokenized_train = tokenizer.texts_to_sequences(proc_train_data)
list_tokenized_test = tokenizer.texts_to_sequences(proc_test_data)

word_index=tokenizer.word_index
print("Words in Vocabulary: ",len(word_index))

"""Padding"""

X_t=pad_sequences(list_tokenized_train, maxlen=maxpadlen, padding = 'post')
X_te=pad_sequences(list_tokenized_test, maxlen=maxpadlen, padding = 'post')

print('Tokenized sentences: \n', X_t[10])
print('One hot label: \n', y[10])

indices = np.arange(X_t.shape[0])
np.random.shuffle(indices)

X_t = X_t[indices]
labels = y[indices]

"""Splitting data into Training and Validation Set"""

num_val_samples = int(val_split*X_t.shape[0])
x_tr = X_t[: -num_val_samples]
y_tr = labels[: -num_val_samples]
x_val = X_t[-num_val_samples: ]
y_val = labels[-num_val_samples: ]

print('Number of entries in each category:')
print('training entries: ', y_tr.sum(axis=0))
print('validation entries: ', y_val.sum(axis=0))

"""Importing Fast tex"""

embed_index_fasttext = {}
f = open('/content/drive/MyDrive/wiki-news-300d-1M.vec', encoding='utf8')
for line in f:
    values = line.split()
    word = values[0]
    embed_index_fasttext[word] = np.asarray(values[1:], dtype='float32')
f.close()

embed_matrix_fasttext = np.random.random((len(word_index) + 1, embed_dim_fasttext))
for word, i in word_index.items():
    embed_vector = embed_index_fasttext.get(word)
    if embed_vector is not None:
        embed_matrix_fasttext[i] = embed_vector
print(" Task Completed")

"""Creating Model

Talos Grid Search for LSTM Model
"""

def toxic_comment_classifier(x_train,y_train,x_val,y_val,params):

  inp=Input(shape=(maxpadlen, ),dtype='int32')

  embedding_layer = Embedding(len(word_index) + 1,
                           embed_dim_fasttext,
                           weights = [embed_matrix_fasttext],
                           input_length = maxpadlen,
                           trainable=False,
                           name = 'embeddings')
  embedded_sequences = embedding_layer(inp)

  x = LSTM(params['output_count_lstm'], return_sequences=True,name='lstm_layer')(embedded_sequences)

  x = GlobalMaxPool1D()(x)

  x = Dropout(params['dropout'])(x)

  x = Dense(params['output_count_dense'], activation=params['activation'], kernel_initializer='he_uniform')(x)

  x = Dropout(params['dropout'])(x)

  preds = Dense(6, activation=params['last_activation'], kernel_initializer='glorot_uniform')(x)

  model = Model(inputs=inp, outputs=preds)

  model.compile(loss=params['loss'], optimizer=params['optimizer'], metrics=['accuracy'])

  model_info=model.fit(x_train,y_train, epochs=params['epochs'], batch_size=params['batch_size'],  validation_data=(x_val, y_val))

  return model_info, model

p={
    'output_count_lstm': [40,50,60],
    'output_count_dense': [30,40,50],
    'batch_size': [32],
    'epochs':[2],
    'optimizer':['adam'],
    'activation':['relu'],
    'last_activation': ['sigmoid'],
    'dropout':[0.1,0.2],
    'loss': ['binary_crossentropy']
}

drscan_results = talos.Scan(x=x_tr,
               y=y_tr,
               x_val=x_val,
               y_val=y_val,
               model=toxic_comment_classifier,
               params=p,
               experiment_name='tcc',
               print_params=True)

model_id = drscan_results.data['val_accuracy'].astype('float').argmax()
model_id

analyze_object = talos.Analyze(drscan_results)

analyze_object.best_params('val_accuracy', ['accuracy', 'loss', 'val_loss'])

analyze_object.plot_line('val_accuracy')

analyze_object.plot_line('accuracy')

"""Talos Grid Search for LSTM-CNN Model"""

def toxic_classifier(x_train,y_train,x_val,y_val,params):

  inp=Input(shape=(maxpadlen, ),dtype='int32')

  embedding_layer = Embedding(len(word_index) + 1,
                           embed_dim_fasttext,
                           weights = [embed_matrix_fasttext],
                           input_length = maxpadlen,
                           trainable=False,
                           name = 'embeddings')
  embedded_sequences = embedding_layer(inp)

  x = LSTM(params['output_count_lstm'], return_sequences=True,name='lstm_layer')(embedded_sequences)

  x = Conv1D(filters=params['filters'], kernel_size=params['kernel_size'], padding='same', activation='relu', kernel_initializer='he_uniform')(x)

  x = MaxPooling1D(params['pool_size'])(x)

  x = GlobalMaxPool1D()(x)

  x = BatchNormalization()(x)

  x = Dense(params['output_1_count_dense'], activation=params['activation'], kernel_initializer='he_uniform')(x)

  x = Dropout(params['dropout'])(x)

  x = Dense(params['output_2_count_dense'], activation=params['activation'], kernel_initializer='he_uniform')(x)

  x = Dropout(params['dropout'])(x)

  preds = Dense(6, activation=params['last_activation'], kernel_initializer='glorot_uniform')(x)

  model = Model(inputs=inp, outputs=preds)

  model.compile(loss=params['loss'], optimizer=params['optimizer'], metrics=['accuracy'])

  model_info=model.fit(x_train,y_train, epochs=params['epochs'], batch_size=params['batch_size'],  validation_data=(x_val, y_val))

  return model_info, model

p={
    'output_count_lstm': [50,60],
    'output_1_count_dense': [40,50],
    'output_2_count_dense': [30,40],
    'filters' : [64],
    'kernel_size' : [3],
    'batch_size': [32],
    'pool_size': [3],
    'epochs':[2],
    'optimizer':['adam'],
    'activation':['relu'],
    'last_activation': ['sigmoid'],
    'dropout':[0.1,0.2],
    'loss': ['binary_crossentropy']
}

scan_results = talos.Scan(x=x_tr,
               y=y_tr,
               x_val=x_val,
               y_val=y_val,
               model=toxic_classifier,
               params=p,
               experiment_name='tcc',
               print_params=True)

model_id = scan_results.data['val_accuracy'].astype('float').argmax()
model_id

scan_results.data[8:9]

analyze_object = talos.Analyze(scan_results)

analyze_object.best_params('val_accuracy', ['accuracy', 'loss', 'val_loss'])

analyze_object.plot_line('val_accuracy')

analyze_object.plot_line('accuracy')

"""Training Model with Best Parameters

LSTM
"""

inp=Input(shape=(maxpadlen, ),dtype='int32')

embedding_layer = Embedding(len(word_index) + 1,
                           embed_dim_fasttext,
                           weights = [embed_matrix_fasttext],
                           input_length = maxpadlen,
                           trainable=False,
                           name = 'embeddings')
embedded_sequences = embedding_layer(inp)

x = LSTM(40, return_sequences=True,name='lstm_layer')(embedded_sequences)
x = GlobalMaxPool1D()(x)
x = Dropout(0.1)(x)
x = Dense(30, activation="relu", kernel_initializer='he_uniform')(x)
x = Dropout(0.1)(x)
preds = Dense(6, activation="sigmoid", kernel_initializer='glorot_uniform')(x)

model_1 = Model(inputs=inp, outputs=preds)
model_1.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

model_1.summary()

model_info_1=model_1.fit(x_tr,y_tr, epochs=2, batch_size=32,  validation_data=(x_val, y_val))

"""LSTM-CNN"""

inp=Input(shape=(maxpadlen, ),dtype='int32')

embedding_layer = Embedding(len(word_index) + 1,
                           embed_dim_fasttext,
                           weights = [embed_matrix_fasttext],
                           input_length = maxpadlen,
                           trainable=False,
                           name = 'embeddings')
embedded_sequences = embedding_layer(inp)

x = LSTM(50, return_sequences=True,name='lstm_layer')(embedded_sequences)
x = Conv1D(filters=64, kernel_size=3, padding='same', activation='relu', kernel_initializer='he_uniform')(x)
x = MaxPooling1D(3)(x)
x = GlobalMaxPool1D()(x)
x = BatchNormalization()(x)
x = Dense(40, activation="relu", kernel_initializer='he_uniform')(x)
x = Dropout(0.2)(x)
x = Dense(30, activation="relu", kernel_initializer='he_uniform')(x)
x = Dropout(0.2)(x)
preds = Dense(6, activation="sigmoid", kernel_initializer='glorot_uniform')(x)

model_2 = Model(inputs=inp, outputs=preds)
model_2.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

model_2.summary()

model_info_2=model_2.fit(x_tr,y_tr, epochs=2, batch_size=32,  validation_data=(x_val, y_val))

"""Plotting Graphs

LSTM
"""

loss = model_info_1.history['loss']
val_loss = model_info_1.history['val_loss']

epochs = range(1, len(loss)+1)

plt.plot(epochs, loss, label='Training loss')
plt.plot(epochs, val_loss, label='Validation loss')
plt.title('Training and Validation loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show();

accuracy = model_info_1.history['accuracy']
val_accuracy = model_info_1.history['val_accuracy']

plt.plot(epochs, accuracy, label='Training accuracy')
plt.plot(epochs, val_accuracy, label='Validation accuracy')
plt.title('Training and validation accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epochs')
plt.legend()
plt.show();

"""LSTM-CNN"""

loss = model_info_2.history['loss']
val_loss = model_info_2.history['val_loss']

epochs = range(1, len(loss)+1)

plt.plot(epochs, loss, label='Training loss')
plt.plot(epochs, val_loss, label='Validation loss')
plt.title('Training and Validation loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show();

accuracy = model_info_2.history['accuracy']
val_accuracy = model_info_2.history['val_accuracy']

plt.plot(epochs, accuracy, label='Training accuracy')
plt.plot(epochs, val_accuracy, label='Validation accuracy')
plt.title('Training and validation accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epochs')
plt.legend()
plt.show();

"""Saving the model"""

model_1.save(filepath="/content/model1.h5")

model_2.save(filepath="/content/model2.h5")

"""Loading saved model"""

loaded_model_1 = keras.models.load_model(filepath="/content/model1.h5")

loaded_model_2 = keras.models.load_model(filepath="/content/model2.h5")

"""Generating the output

LSTM
"""

test_values_1 = loaded_model_1.predict([X_te], batch_size=1, verbose=1)

sample_submission = pd.read_csv('/content/drive/MyDrive/test.csv/test.csv')
test_values_1=pd.DataFrame(test_values_1,columns=['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate'])
submission = pd.DataFrame(sample_submission["id"])
combined_submission=pd.concat([submission,test_values_1],axis=1)
combined_submission.to_csv('/content/drive/MyDrive/Submission_LSTM.csv', index=False)

"""LSTM-CNN"""

test_values_2 = loaded_model_2.predict([X_te], batch_size=1, verbose=1)

sample_submission = pd.read_csv('/content/drive/MyDrive/test.csv/test.csv')
test_values_2=pd.DataFrame(test_values_2,columns=['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate'])
submission = pd.DataFrame(sample_submission["id"])
combined_submission=pd.concat([submission,test_values_2],axis=1)
combined_submission.to_csv('/content/drive/MyDrive/Submission_CNN.csv', index=False)

"""Testing the created model"""

def toxicity_level(string):
    new_string = [string]
    new_string = tokenizer.texts_to_sequences(new_string)
    new_string = pad_sequences(new_string, maxlen=maxpadlen, padding='post')

    prediction = model_1.predict(new_string)

    print("Toxicity levels for '{}':".format(string))
    print('Toxic:         {:.0%}'.format(prediction[0][0]))
    print('Severe Toxic:  {:.0%}'.format(prediction[0][1]))
    print('Obscene:       {:.0%}'.format(prediction[0][2]))
    print('Threat:        {:.0%}'.format(prediction[0][3]))
    print('Insult:        {:.0%}'.format(prediction[0][4]))
    print('Identity Hate: {:.0%}'.format(prediction[0][5]))
    print()

    return

toxicity_level('go jump off a bridge jerk')

toxicity_level('i will kill you')

def toxicity_level_2(string):
    new_string = [string]
    new_string = tokenizer.texts_to_sequences(new_string)
    new_string = pad_sequences(new_string, maxlen=maxpadlen, padding='post')

    prediction = model_2.predict(new_string)

    print("Toxicity levels for '{}':".format(string))
    print('Toxic:         {:.0%}'.format(prediction[0][0]))
    print('Severe Toxic:  {:.0%}'.format(prediction[0][1]))
    print('Obscene:       {:.0%}'.format(prediction[0][2]))
    print('Threat:        {:.0%}'.format(prediction[0][3]))
    print('Insult:        {:.0%}'.format(prediction[0][4]))
    print('Identity Hate: {:.0%}'.format(prediction[0][5]))
    print()

    return

toxicity_level_2('go jump off a bridge jerk')

toxicity_level_2('have a nice day')

toxicity_level_2('fuck ofF!!')

toxicity_level_2('get the fuck away from me @sshole!!')

toxicity_level_2('Hello, How are you?')

toxicity_level('fuck ofF!!')

toxicity_level('get the fuck away from me @sshole!!')

toxicity_level('Hello, How are you?')