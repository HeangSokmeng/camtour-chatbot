def detect_intent(message):
    """Detect basic intents from user message"""
    message = message.lower()
    
    # Greeting intent
    greeting_words = ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening', 'howdy']
    
    for greeting in greeting_words:
        if greeting in message:
            return 'greeting'
    
    # Future: Add more intents like 'help', 'booking', etc.
    
    return 'query'  # Default intent