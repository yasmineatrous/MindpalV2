import streamlit as st
import requests
from urllib.parse import urlencode

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize session state with API keys
st.session_state['VECTARA_API_KEY'] = os.getenv('VECTARA_API_KEY')
st.session_state['CUSTOMER_ID'] = os.getenv('CUSTOMER_ID')
st.session_state['CORPUS_ID'] = int(os.getenv('CORPUS_ID'))
st.session_state['TOGETHER_IO_API_KEY'] = os.getenv('TOGETHER_IO_API_KEY')

# Vectara configuration
VECTARA_UPLOAD_ENDPOINT = os.getenv('VECTARA_UPLOAD_ENDPOINT')
VECTARA_ENDPOINT = os.getenv('VECTARA_ENDPOINT')
TOGETHER_IO_ENDPOINT = os.getenv('TOGETHER_IO_ENDPOINT')


# Function to get JWT token from Vectara
def get_vectara_jwt(client_id, client_secret, auth_url):
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(auth_url, data=urlencode(data), headers=headers)
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        raise Exception(f"Error retrieving JWT token: {response.text}")


# Function to perform a search in Vectara
def perform_vectara_search(query):
    VECTARA_API_KEY = st.session_state['VECTARA_API_KEY']
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
        return None


# Function to ask a question using Together.io
def ask_together_io(query, vectara_text, together_api_key):
    full_query = f"{vectara_text} {query}"
    headers = {
        'Authorization': f'Bearer {together_api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        "messages": [
            {"role": "system", "content": "you are a creative assistant designed to to fuel the imagination, organize thoughts and ideas, and guide through any creative process."},
            {"role": "user", "content": full_query}
        ],
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1"
    }
    try:
        response = requests.post(TOGETHER_IO_ENDPOINT, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Failed to retrieve response from Together.io. Status code: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"An error occurred while making a request to Together.io: {e}"

customer_id = os.getenv('CUSTOMER_ID')
corpus_id = int(os.getenv('CORPUS_ID'))
vectara_api_key = os.getenv('VECTARA_API_KEY')
together_api_key = os.getenv('TOGETHER_IO_API_KEY')



# Initialize chat history list in session state
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Function to display chat history
def display_chat_history():
    # Reverse the chat history list before displaying it
    reversed_chat_history = reversed(st.session_state.chat_history)
    for msg in reversed_chat_history:
        st.chat_message(msg['role']).write(msg['content'])

# Streamlit UI
st.title("💬 Talk to your brain")
st.caption("📌A chatbot powered by Vectara and Together.io")
st.caption("This feature revolutionizes the way you interact with your digital workspace. Instead of sifting through countless notes and documents, you can simply engage in a conversation with your Note Taker interface. Whether it's retrieving specific information, brainstorming ideas, or seeking inspiration, you can converse naturally, just like chatting with a friend. 🗨️ Your second brain is always there to provide instant responses, recall specific details from your notes, and offer valuable suggestions to support your creative process or problem-solving journey. 🧠✨")
query = st.text_input("")
if st.button("Ask Your Brain"):
    
    # Perform search in Vectara and display results
    vectara_results = perform_vectara_search(query)
    if vectara_results:
        # Extract relevant information from Vectara results
        if 'responseSet' in vectara_results and vectara_results['responseSet']:
            # Assuming the first response is the most relevant
            first_response = vectara_results['responseSet'][0]['response'][0]
            vectara_text = first_response['text']
            
            # Ask a question using Together.io based on Vectara response
            together_io_response = ask_together_io(query, vectara_text, together_api_key)
            
            # Append user query, Vectara's response, and Together.io's response to chat history
            
            
            st.session_state.chat_history.append({"role": "assistant", "content": together_io_response})
            st.session_state.chat_history.append({"role": "user", "content": query})

            # Display updated chat history
display_chat_history()


customer_id = '1684960646'
corpus_id = 3
vectara_api_key = 'zut_ZG51hgFBpvAKaem8jerpiN-_zFpKN65NhCXV1A'
together_api_key = "c44f121e33ff52bcadc0925c8e4a0ec9f75055cffb13f68f292caed6149930d6" 




import streamlit as st

# Initialize chat history list in session state
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Function to display chat history
def display_chat_history():
    # Reverse the chat history list before displaying it
    reversed_chat_history = reversed(st.session_state.chat_history)
    for msg in reversed_chat_history:
        st.chat_message(msg['role']).write(msg['content'])
