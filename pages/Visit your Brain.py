import streamlit as st
import http.client
import json
import requests  
import os
from dotenv import load_dotenv
import json
import requests
import http.client
import streamlit as st

# Load environment variables from .env file
load_dotenv()

# Function to retrieve documents from Vectara
def retrieve_documents():
    conn = http.client.HTTPSConnection("api.vectara.io")
    payload = json.dumps({
        "corpusId": int(os.getenv('CORPUS_ID')),
        "numResults": 1000,
        "pageKey": "",
        "metadataFilter": ""
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'x-api-key': os.getenv('VECTARA_API_KEY')
    }
    try:
        conn.request("POST", "/v1/list-documents", payload.encode('utf-8'), headers)
        res = conn.getresponse()
        data = res.read()
        documents = json.loads(data.decode("utf-8"))
        return documents['document']
    except Exception as e:
        st.error(f"Failed to retrieve documents from Vectara: {e}")
        return None

# Function to delete document from Vectara
def delete_document(document_id):
    url = "https://api.vectara.io/v1/delete-doc"
    payload = json.dumps({
        "customerId": os.getenv('CUSTOMER_ID'),
        "corpusId": int(os.getenv('CORPUS_ID')),
        "documentId": document_id
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'x-api-key': os.getenv('VECTARA_API_KEY')
    }
    try:
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code == 200:
            return True
        else:
            st.error(f"Failed to delete document {document_id}. Error: {response.status_code} - {response.reason}")
            return False
    except Exception as e:
        st.error(f"An error occurred while deleting document {document_id}: {e}")
        return False

# Retrieve documents from Vectara
documents = retrieve_documents()

# Display documents and delete button for each document
if documents:
    st.title("What's in your Brain?")
    st.caption("With this feature, you have a convenient list of all the notes and documents you've uploaded, right at your fingertips. 📝 Each item is displayed with clarity, making it easy to see what's stored in your digital brain. And if you ever need to remove something from your collection, simply hit the delete button next to it, and poof! It's gone. 🗑️ Keep your digital workspace clean and clutter-free, ensuring that only the most relevant and important information remains to assist you in your creative endeavors. 🧠💡")

    st.write("## My Notes:")
    for document in documents:
        with st.container():
            st.info(f"**{document['id']}**")
            delete_button_key = f"delete_button_{document['id']}"  # Unique key for delete button
            if st.button("Delete", key=delete_button_key):
                if delete_document(document['id']):
                    st.success(f"Document {document['id']} deleted successfully.")
                else:
                    st.error(f"Failed to delete document {document['id']}.")
else:
    st.error("No documents found.")
