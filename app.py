import json
import re

import pandas as pd
import requests
import spacy
from flask import Flask, jsonify, request
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app, origins=['http://localhost:8000', 'https://yourdomain.com'])

nlp = spacy.load("en_core_web_md")

try:
    url = 'http://127.0.0.1:8000/chatbot/cambodia_travel_data.json'
    response = requests.get(url)
    response.raise_for_status()
    travel_data = response.json()
except requests.exceptions.RequestException as e:
    print(f"Error fetching data from {url}: {e}")
    try:
        with open('cambodia_travel_data.json', 'r') as f:
            travel_data = json.load(f)
        print("Using local cambodia_travel_data.json file")
    except FileNotFoundError:
        print("ERROR: Could not load travel data from URL or local file")
        travel_data = []

df = pd.DataFrame(travel_data)

if df.empty:
    print("WARNING: No travel data loaded. The chatbot may not function properly.")
else:
    print(f"Successfully loaded {len(df)} travel questions and answers")

def clean_text(text):
    if not isinstance(text, str):
        return ""
    
    text = text.lower()
    text = re.sub(r'[^\w\s$%]', ' ', text)
    text = ' '.join(text.split())
    
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc 
              if not token.is_stop and not token.is_punct and len(token.text) > 2]
    
    return ' '.join(tokens)

if not df.empty:
    df['cleaned_question'] = df['question'].apply(clean_text)
    
    vectorizer = TfidfVectorizer(
        max_features=1000,
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95,
        stop_words='english'
    )
    tfidf_matrix = vectorizer.fit_transform(df['cleaned_question'])
else:
    vectorizer = None
    tfidf_matrix = None

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    user_message = data.get('message', '')
    context = data.get('context', [])
    
    if df.empty or vectorizer is None:
        return jsonify({
            'message': 'Sorry, I cannot access the travel data at the moment. Please try again later.',
            'suggestions': [],
            'confidence': 0.0
        })
    
    if not user_message.strip():
        return jsonify({
            'message': 'Please ask me something about traveling in Cambodia!',
            'suggestions': get_top_suggestions(),
            'confidence': 0.0
        })
    
    doc = nlp(user_message)
    intent = detect_intent(doc, user_message)
    
    if intent == 'greeting':
        return jsonify({
            'message': 'Hello! I can help you with information about traveling in Cambodia, especially Phnom Penh, Siem Reap, and Battambang. What would you like to know?',
            'suggestions': get_top_suggestions(),
            'confidence': 1.0
        })
    
    elif intent == 'thank_you':
        return jsonify({
            'message': "You're welcome! Is there anything else you'd like to know about Cambodia?",
            'suggestions': get_top_suggestions(),
            'confidence': 1.0
        })
    
    elif intent == 'goodbye':
        return jsonify({
            'message': 'Safe travels! Feel free to ask if you need more information about Cambodia.',
            'suggestions': [],
            'confidence': 1.0
        })
    
    cleaned_user_message = clean_text(user_message)
    user_vector = vectorizer.transform([cleaned_user_message])
    similarities = cosine_similarity(user_vector, tfidf_matrix)[0]
    
    max_sim_idx = similarities.argmax()
    confidence = float(similarities[max_sim_idx])
    
    if confidence < 0.2:
        return jsonify({
            'message': "I'm not sure I understand your question about Cambodia travel. Here are some popular topics I can help with:",
            'suggestions': get_dynamic_suggestions(user_message),
            'confidence': confidence
        })
    
    elif confidence < 0.4:
        response_msg = f"{df.iloc[max_sim_idx]['answer']}\n\nI'm not entirely sure this answers your question. Here are some related topics:"
        return jsonify({
            'message': response_msg,
            'suggestions': get_related_suggestions(max_sim_idx),
            'confidence': confidence
        })
    
    else:
        return jsonify({
            'message': df.iloc[max_sim_idx]['answer'],
            'suggestions': get_related_suggestions(max_sim_idx),
            'confidence': confidence
        })

def detect_intent(doc, raw_message):
    raw_lower = raw_message.lower()
    
    greeting_patterns = [
        'hello', 'hi', 'hey', 'greetings', 'good morning', 
        'good afternoon', 'good evening', 'howdy', 'what\'s up'
    ]
    
    thank_you_patterns = [
        'thank you', 'thanks', 'thank u', 'thx', 'appreciate', 
        'grateful', 'cheers'
    ]
    
    goodbye_patterns = [
        'bye', 'goodbye', 'see you', 'farewell', 'take care',
        'see ya', 'catch you later', 'until next time'
    ]
    
    for pattern in greeting_patterns:
        if pattern in raw_lower:
            return 'greeting'
    
    for pattern in thank_you_patterns:
        if pattern in raw_lower:
            return 'thank_you'
    
    for pattern in goodbye_patterns:  
        if pattern in raw_lower:
            return 'goodbye'
    
    return 'query'

def get_top_suggestions():
    return [
        'What are the must-see attractions in Phnom Penh?',
        'How do I get from Phnom Penh to Siem Reap?',
        'What is the best time to visit Angkor Wat?',
        'What are recommended hotels in Battambang?'
    ]

def get_dynamic_suggestions(user_message):
    user_lower = user_message.lower()
    
    if 'phnom penh' in user_lower:
        return [
            'What are the top attractions in Phnom Penh?',
            'Best restaurants in Phnom Penh?',
            'How to get around Phnom Penh?',
            'Where to stay in Phnom Penh?'
        ]
    elif 'siem reap' in user_lower:
        return [
            'What to see in Siem Reap besides Angkor?',
            'Best time to visit Angkor Wat?',
            'Siem Reap restaurant recommendations?',
            'Transportation in Siem Reap?'
        ]
    elif 'battambang' in user_lower:
        return [
            'What to do in Battambang?',
            'Battambang accommodation options?',
            'How to get to Battambang?',
            'Battambang local experiences?'
        ]
    
    elif any(word in user_lower for word in ['food', 'eat', 'restaurant']):
        return [
            'Best Cambodian dishes to try?',
            'Restaurant recommendations in Phnom Penh?',
            'Street food safety in Cambodia?',
            'Vegetarian options in Cambodia?'
        ]
    elif any(word in user_lower for word in ['hotel', 'stay', 'accommodation']):
        return [
            'Budget accommodation in Cambodia?',
            'Luxury hotels in Siem Reap?',
            'Guesthouse vs hotel in Cambodia?',
            'Booking accommodation in Cambodia?'
        ]
    elif any(word in user_lower for word in ['transport', 'travel', 'get around']):
        return [
            'Transportation between cities in Cambodia?',
            'Tuk-tuk vs taxi in Cambodia?',
            'Bus travel in Cambodia?',
            'Motorbike rental in Cambodia?'
        ]
    
    return get_top_suggestions()

def get_related_suggestions(main_idx):
    try:
        main_location = df.iloc[main_idx]['location']
        location_questions = df[df['location'] == main_location]
        
        if len(location_questions) > 1:
            related_df = location_questions[location_questions.index != main_idx]
            sample_size = min(3, len(related_df))
            if sample_size > 0:
                related = related_df.sample(sample_size)['question'].tolist()
                return related
        
        return get_top_suggestions()[:3]
        
    except (KeyError, IndexError):
        return get_top_suggestions()[:3]

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'Cambodia Travel Bot'})

@app.route('/suggestions', methods=['GET'])
def get_suggestions():
    return jsonify({
        'suggestions': get_top_suggestions()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)