from flask import Flask, render_template, request, jsonify
from textblob import TextBlob
from dataclasses import dataclass
import json
import numpy as np
import nltk
import pickle
import random

from nltk.stem import WordNetLemmatizer

from tensorflow.keras.models import load_model

lemmatizer = WordNetLemmatizer()
intents = json.loads(open('intents.json').read())

with open('words.pkl', 'rb') as file:
    # Load the pickled object
    words = pickle.load(file)
with open('classes.pkl', 'rb') as file:
    # Load the pickled object
    classes = pickle.load(file)

model = load_model('vui_model.h5')

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    print(sentence_words)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list

def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result

workshops = [ {"date": "2024-03-15", "title": "Neurodiversity Workshop", "description": "Celebrating Neurodiversity in the Student Community"},
    {"date": "2024-03-20", "title": "Stress Management", "description": "Dealing with Stress as a University Student"}
    ]


podcasts = [
      {"date": "2024-03-10", "title": "Podcast 1", "description": "Description 1"},
    {"date": "2024-03-17", "title": "Podcast 2", "description": "Description 2"}
]


#class to store mental state based on sentiment analysis 
#@param rating is the rating given for each utterance based on
#whether it is within the normal threshold or not 
#@param mood is the polarity float created during evaluation 
#of the utterance 

@dataclass 
class mental_state:
    rating: str
    sentiment: float

#sentiment analysis of user's chosen words 
    
def getMental_State(words: str, *, threshold: float) -> mental_state:
    sentiment: float = TextBlob(words).sentiment.polarity

    normal_threshold: float = threshold
    alarming_threshold: float = -threshold

    if sentiment >= normal_threshold:
        return mental_state("good", sentiment)
    
    elif sentiment <= alarming_threshold:
        return mental_state("alarming", sentiment)
    
    else: 
        return mental_state("neutral", sentiment)
    

#create flask app instance 
app = Flask(__name__)

#render index screen at index route 
@app.route('/')
def home():
    return render_template(r'index.html')

@app.route('/workshops')
def get_workshops():
    return jsonify(workshops)

@app.route('/podcasts')
def get_podcasts():
    return jsonify(podcasts)

#receive user's utterances 
@app.route('/speech', methods = ['POST'])
def speech():
    data = request.json
    ints = predict_class(data)
    res = get_response(ints, intents)
    mood: mental_state = getMental_State(data, threshold=0.2)
    print(f'{mood.rating}  ({mood.sentiment})')
    return res, 200


@app.route('/home')
def main_page():
    return render_template(r'main.html')

if __name__ == "__main__":
    app.run(debug=True)
