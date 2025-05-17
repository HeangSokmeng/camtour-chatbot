import google.generativeai as genai

import config

# Configure the API
genai.configure(api_key=config.https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=GEMINI_API_KEY)

def get_gemini_response(system_prompt, user_message, context=None):
    """Get response from Google's Gemini API"""
    if context is None:
        context = []
    
    # Format context and current message
    conversation = []
    for msg in context[-5:]:
        role = "user" if msg.get('role') == 'user' else "model"
        conversation.append({
            "role": role,
            "parts": [{"text": msg.get('content', '')}]
        })
    
    # Add system prompt as first user message if no context
    if not conversation:
        conversation.append({
            "role": "user",
            "parts": [{"text": system_prompt}]
        })
        conversation.append({
            "role": "model",
            "parts": [{"text": "I understand. I'll act as a specialized Cambodia travel assistant."}]
        })
    
    # Add current message
    conversation.append({
        "role": "user",
        "parts": [{"text": user_message}]
    })
    
    # Generate response
    model = genai.GenerativeModel('gemini-pro')
    chat = model.start_chat(history=conversation)
    response = chat.send_message(user_message)
    
    answer = response.text
    suggestions = generate_suggestions(answer, user_message)
    
    return {
        'message': answer,
        'suggestions': suggestions
    }