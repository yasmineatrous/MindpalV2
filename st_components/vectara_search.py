import requests
import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env file
load_dotenv()

# Initialize session state with API keys (only if not already set)
if 'VECTARA_API_KEY' not in st.session_state:
    st.session_state['VECTARA_API_KEY'] = os.getenv('VECTARA_API_KEY')
if 'CUSTOMER_ID' not in st.session_state:
    st.session_state['CUSTOMER_ID'] = os.getenv('CUSTOMER_ID')
if 'CORPUS_ID' not in st.session_state:
    st.session_state['CORPUS_ID'] = int(os.getenv('CORPUS_ID'))

def perform_vectara_search(query):
    VECTARA_API_KEY = st.session_state['VECTARA_API_KEY']
    VECTARA_ENDPOINT = os.getenv('VECTARA_ENDPOINT')
    CUSTOMER_ID = st.session_state['CUSTOMER_ID']
    CORPUS_ID = st.session_state['CORPUS_ID']
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'customer-id': CUSTOMER_ID,
        'x-api-key': VECTARA_API_KEY,
    }

    data = {
            "query": [
                {
                "query": query,
                "queryContext": "",
                "start": 0,
                "numResults": 10,
                "contextConfig": { 
                    "charsBefore": 0,
                    "charsAfter": 0,
                    "sentencesBefore": 2,
                    "sentencesAfter": 2,
                    "startTag": "%START_SNIPPET%",
                    "endTag": "%END_SNIPPET%"
                },
                "corpusKey": [
                    {
                        "customerId": int(CUSTOMER_ID),
                        "corpusId": int(CORPUS_ID),
                        "semantics": 0,
                        "metadataFilter": "part.lang = 'eng'",
                            "lexicalInterpolationConfig": {
                                "lambda": 0.025
                        },
                        "dim": []
                    }
                ],
                "summary": [
                    {
                        "maxSummarizedResults": 2,
                        "responseLang": "eng",
                        "summarizerPromptName": "vectara-summary-ext-v1.2.0"
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(VECTARA_ENDPOINT, headers=headers, json=data)
        # Check if the request was successful
        if response.status_code == 200:
            return response.json()
        else:
            # Log the status code and response content for debugging
            st.error(f"Error in Vectara API request: Status code {response.status_code}")
            st.json(response.json())
            return None
    except requests.exceptions.RequestException as e:
        # Handle any errors that occur during the request
        st.error(f"An error occurred while making a request to Vectara: {e}")
        return None
    

def find_highest_score_and_texts(stored_results):
    # If stored_results is empty, return None
    if not stored_results:
        return None, None
    
    # Get the highest score (Python dictionaries are unordered, so we need to sort by key)
    highest_score = max(stored_results.keys())
    # Get all texts associated with the highest score
    highest_score_texts = stored_results[highest_score]
    
    return highest_score, highest_score_texts


def display_vectara_results(vectara_results):
    stored_results = {}
    if 'responseSet' in vectara_results:
        for result in vectara_results['responseSet'][0]['response']:
            text = result['text']
            score = result['score']
            if score not in stored_results:
                # If the score doesn't exist as a key, create a new list
                stored_results[score] = [text]
            else:
                # If the score does exist, append the text to the existing list
                stored_results[score].append(text)
                
                
            # Using columns to align score and text neatly
            col1, col2 = st.columns([1, 4])
            
            with col1:
                st.metric(label="Score", value=f"{score:.2f}")
            
            with col2:
                st.text_area("", value=text, height=100, key=f"result_{score}", disabled=True)
    else:
        st.error("No results found in Vectara.")
    print(stored_results)
    highest_score, highest_score_texts = find_highest_score_and_texts(stored_results)
    print(f"Highest Score: {highest_score}")
    print("Texts with the highest score:")
    for text in highest_score_texts:
        print(text)