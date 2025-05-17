# app.py
import json

import pandas as pd
import spacy
from flask import Flask, jsonify, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Load spaCy language model
nlp = spacy.load("en_core_web_md")

# Load the travel data
with open('cambodia_travel_data.json', 'r') as f:
    travel_data = json.load(f)

# Create a DataFrame from the travel data
df = pd.DataFrame(travel_data)

# Create TF-IDF vectorizer
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(df['question'])

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    user_message = data.get('message', '')
    context = data.get('context', [])
    
    # Process the user message
    doc = nlp(user_message)
    
    # Basic intent detection
    intent = detect_intent(doc)
    
    if intent == 'greeting':
        return jsonify({
            'message': 'Hello! I can help you with information about traveling in Cambodia, especially Phnom Penh, Siem Reap, and Battambang. What would you like to know?',
            'suggestions': get_top_suggestions()
        })
    
    # Find the most similar question in our database
    user_vector = vectorizer.transform([user_message])
    similarities = cosine_similarity(user_vector, tfidf_matrix)[0]
    
    # Get the most similar question
    max_sim_idx = similarities.argmax()
    
    # If the similarity is too low, provide a generic response
    if similarities[max_sim_idx] < 0.3:
        return jsonify({
            'message': "I'm not sure I understand. Could you please rephrase your question about Cambodia travel?",
            'suggestions': get_top_suggestions()
        })
    
    # Return the answer for the most similar question
    return jsonify({
        'message': df.iloc[max_sim_idx]['answer'],
        'suggestions': get_related_suggestions(max_sim_idx)
    })

def detect_intent(doc):
    greeting_words = ['hello', 'hi', 'hey', 'greetings', 'morning', 'afternoon', 'evening']
    
    for token in doc:
        if token.text.lower() in greeting_words:
            return 'greeting'
    
    return 'query'

def get_top_suggestions():
    return [
        'What are the must-see attractions in Phnom Penh?',
        'How do I get from Phnom Penh to Siem Reap?',
        'What is the best time to visit Angkor Wat?',
        'Recommended hotels in Battambang?'
    ]

def get_related_suggestions(main_idx):
    # Get the location from the main response
    main_location = df.iloc[main_idx]['location']
    
    # Find other questions about the same location
    related = df[df['location'] == main_location].sample(min(3, len(df[df['location'] == main_location]))).question.tolist()
    
    return related

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)