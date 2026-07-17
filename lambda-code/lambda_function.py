

import json
import re
import random
import os
import nltk
from textblob import TextBlob
import spacy
from collections import Counter
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

# Set NLTK data path to /tmp (writable in Lambda)
NLTK_DATA_PATH = '/tmp/nltk_data'
os.makedirs(NLTK_DATA_PATH, exist_ok=True)
nltk.data.path.append(NLTK_DATA_PATH)







# Download NLTK data to /tmp if not present
def download_nltk_data():
    """Download required NLTK data to /tmp directory"""
    try:
        # Check if data exists, download if not
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', download_dir=NLTK_DATA_PATH)
        nltk.download('averaged_perceptron_tagger', download_dir=NLTK_DATA_PATH)
        nltk.download('wordnet', download_dir=NLTK_DATA_PATH)
        nltk.download('punkt_tab', download_dir=NLTK_DATA_PATH)

# Download NLTK data on cold start
download_nltk_data()

# Initialize spaCy
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # If model not found, download it (but this might not work in Lambda due to size)
    # Better to include it in the Docker image
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

# Product description templates
PRODUCT_TEMPLATES = {
    'power_tools': [
        "The {name} is a professional-grade {category} featuring {features}, designed for {usage}.",
        "Designed for {usage}, this {name} delivers {features} for exceptional {category} performance.",
        "Experience superior {category} with the {name}, featuring {features} for {usage}."
    ],
    'construction': [
        "This {name} is built for {usage}, offering {features} that ensure durability and reliability.",
        "For demanding construction needs, the {name} provides {features} with unmatched {category} quality."
    ],
    'safety': [
        "Stay protected with the {name}, featuring {features} for maximum {category} safety.",
        "The {name} delivers {features} to ensure your safety during {usage}."
    ],
    'hand_tools': [
        "The {name} offers precision {category} with {features}, ideal for {usage}.",
        "Perfect for {usage}, this {name} combines {features} with professional-grade {category}."
    ],
    'default': [
        "The {name} is a high-quality {category} featuring {features}, perfect for {usage}.",
        "Enhance your work with the {name}, offering {features} for superior {category} results."
    ]
}

# Feature keywords for different product types
FEATURE_KEYWORDS = {
    'power_tools': ['heavy duty', 'variable speed', 'cordless', 'brushless motor', 'high torque', 
                    'adjustable', 'ergonomic', 'durable', 'professional grade'],
    'construction': ['heavy duty', 'durable', 'weather resistant', 'reinforced', 'high strength',
                    'load bearing', 'sturdy', 'long lasting'],
    'safety': ['impact resistant', 'high visibility', 'ansi approved', 'comfortable', 'adjustable',
              'breathable', 'lightweight'],
    'hand_tools': ['ergonomic', 'high strength', 'non slip', 'precision', 'durable',
                  'comfort grip', 'rust resistant']
}

# Usage scenarios by product type
USAGE_SCENARIOS = {
    'power_tools': ['construction sites', 'heavy-duty work', 'professional workshops', 
                    'industrial applications', 'home improvement projects'],
    'construction': ['building projects', 'structural work', 'concrete work', 'steel construction',
                    'foundation work'],
    'safety': ['construction zones', 'industrial environments', 'hazardous areas', 'height work'],
    'hand_tools': ['precise work', 'maintenance tasks', 'repair jobs', 'handyman projects']
}

def lambda_handler(event, context):
    """
    Lambda function to generate product description
    
    Handles multiple input formats:
    1. Direct invocation: {"product_name": "..."}
    2. Lambda URL: {"body": "...", ...}
    3. API Gateway: {"body": "...", ...}
    """
    try:
        print(f"Received event: {json.dumps(event)[:500]}")
        
        # Parse input - handle different formats
        parsed_event = parse_event(event)
        
        product_name = parsed_event.get('product_name', '').strip()
        category = parsed_event.get('category', 'Construction Equipment').strip()
        product_type = parsed_event.get('product_type', 'default')
        features_list = parsed_event.get('features', [])
        usage = parsed_event.get('usage', None)
        
        print(f"Parsed: product_name={product_name}, category={category}, product_type={product_type}")
        
        if not product_name:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'product_name is required',
                    'received': parsed_event
                })
            }
        
        # Generate description
        description = generate_description(
            product_name=product_name,
            category=category,
            product_type=product_type,
            features_list=features_list,
            usage=usage
        )
        
        # Generate short description (meta)
        short_description = generate_short_description(description)
        
        # Generate keywords for SEO
        keywords = generate_keywords(product_name, category, features_list)
        
        response_body = {
            'description': description,
            'short_description': short_description,
            'keywords': keywords,
            'product_name': product_name,
            'category': category,
            'product_type': product_type
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(response_body)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }

def parse_event(event):
    """
    Parse event from different sources and extract the actual data
    """
    
    
    
    
    print("========== EVENT ==========")
    print(json.dumps(event, indent=2))
    print("===========================")
    
    
    print("========== EVENT ==========")
    print(json.dumps(event, indent=2))
    print("===========================")

    
    

    
    # If event is a string, parse it
    if isinstance(event, str):
        try:
            event = json.loads(event)
        except:
            return {'product_name': '', 'error': 'Invalid JSON'}
    
    # If event is not a dict, return empty
    if not isinstance(event, dict):
        return {'product_name': '', 'error': 'Invalid event format'}
    
    # Check if this is from Lambda URL or API Gateway (has 'body' field)
    if 'body' in event and event['body']:
        try:
            body = event['body']
            # If body is a string, parse it
            if isinstance(body, str):
                body_data = json.loads(body)
                # If the parsed body is a dict, use it
                if isinstance(body_data, dict):
                    return body_data
            # If body is already a dict, use it
            elif isinstance(body, dict):
                return body
        except json.JSONDecodeError:
            # Body is not JSON, return as is
            return event
    
    # If there are query string parameters, merge them
    if 'queryStringParameters' in event and event['queryStringParameters']:
        for key, value in event['queryStringParameters'].items():
            event[key] = value
    
    # Return the event as is (direct invocation)
    return event

def generate_description(product_name, category, product_type='default', features_list=None, usage=None):
    """Generate product description using templates and NLP"""
    
    # Extract features from product name using NLP
    if not features_list:
        features_list = extract_features_from_name(product_name)
    
    # Add default features based on product type
    if product_type in FEATURE_KEYWORDS:
        default_features = FEATURE_KEYWORDS[product_type]
        # Add 2-3 random features
        num_features = min(3, len(default_features))
        features_list.extend(random.sample(default_features, num_features))
    
    # Remove duplicates
    features_list = list(set(features_list))
    
    # Format features string
    if len(features_list) > 2:
        features_str = ', '.join(features_list[:-1]) + f" and {features_list[-1]}"
    elif len(features_list) == 2:
        features_str = f"{features_list[0]} and {features_list[1]}"
    elif len(features_list) == 1:
        features_str = features_list[0]
    else:
        features_str = "high-quality construction"
    
    # Get usage scenario
    if not usage:
        if product_type in USAGE_SCENARIOS:
            usage = random.choice(USAGE_SCENARIOS[product_type])
        else:
            usage = random.choice(USAGE_SCENARIOS.get('construction', ['your projects']))
    
    # Select template
    if product_type in PRODUCT_TEMPLATES:
        templates = PRODUCT_TEMPLATES[product_type]
    else:
        templates = PRODUCT_TEMPLATES['default']
    
    template = random.choice(templates)
    
    # Fill template
    description = template.format(
        name=product_name,
        category=category,
        features=features_str,
        usage=usage
    )
    
    return description

def extract_features_from_name(name):
    """Extract features from product name using NLP"""
    features = []
    
    try:
        # Use spaCy for entity recognition
        doc = nlp(name)
        
        # Extract adjectives and nouns
        for token in doc:
            if token.pos_ in ['ADJ', 'NOUN', 'PROPN']:
                if token.text.lower() not in ['product', 'tool', 'machine', 'equipment']:
                    features.append(token.text.lower())
    except:
        pass
    
    try:
        # Use TextBlob for noun phrases
        blob = TextBlob(name)
        for np in blob.noun_phrases:
            if len(np.split()) > 1:
                features.append(np)
    except:
        pass
    
    # Remove duplicates and limit
    features = list(set(features))[:4]
    
    return features

def generate_short_description(description):
    """Generate short description (meta description)"""
    # Truncate to 150 characters with proper sentence boundary
    if len(description) <= 155:
        return description
    
    # Find the first sentence boundary within 150 chars
    sentences = description.split('.')
    short_desc = ''
    for sentence in sentences:
        if len(short_desc + sentence + '.') <= 155:
            short_desc += sentence + '.'
        else:
            break
    
    return short_desc or description[:150] + '...'

def generate_keywords(product_name, category, features):
    """Generate SEO keywords from product data"""
    keywords = []
    
    # Add product name components
    name_parts = product_name.split()
    keywords.extend(name_parts)
    
    # Add category
    keywords.append(category)
    keywords.append(category.lower())
    
    # Add features
    keywords.extend(features)
    
    # Add common construction keywords
    construction_keywords = ['construction', 'building', 'heavy duty', 'professional', 'quality']
    keywords.extend(construction_keywords)
    
    # Remove duplicates and clean
    keywords = list(set(keywords))
    
    # Remove common words
    stop_words = ['the', 'a', 'an', 'and', 'or', 'for', 'with', 'of', 'to']
    keywords = [k for k in keywords if k.lower() not in stop_words and len(k) > 2]
    
    # Add combinations (2-word phrases)
    combined = []
    for i in range(len(keywords)-1):
        combined.append(f"{keywords[i]} {keywords[i+1]}")
    
    keywords.extend(combined)
    
    # Return top 10 keywords
    return list(set(keywords))[:10]