import hashlib
import json
import os
import time
from datetime import datetime

import config

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_key(query, context=None, location=None):
    """Generate a unique cache key based on query and context"""
    # Use the last message from context if available
    context_key = ""
    if context and len(context) > 0:
        context_key = context[-1].get('content', '')
    
    # Create a combined key with query, last context message, and location
    combined = f"{query}::{context_key}::{location or ''}"
    return hashlib.md5(combined.encode('utf-8')).hexdigest()

def get_cached_response(query, context=None, location=None):
    """Get a cached response if available and not expired"""
    if not config.ENABLE_CACHE:
        return None
        
    cache_key = get_cache_key(query, context, location)
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    
    if not os.path.exists(cache_file):
        return None
    
    # Check if cache is expired
    file_time = os.path.getmtime(cache_file)
    if time.time() - file_time > config.CACHE_EXPIRY:
        # Cache expired, remove file
        os.remove(cache_file)
        return None
    
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def save_to_cache(query, response, context=None, location=None):
    """Save a response to cache"""
    if not config.ENABLE_CACHE:
        return
        
    cache_key = get_cache_key(query, context, location)
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(response, f)
    except Exception as e:
        print(f"Error saving to cache: {str(e)}")