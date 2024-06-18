import streamlit as st
from st_components.upload_file import upload_file_to_vectara  

def main():
    # Streamlit UI
    st.title("Upload File to your Brain")
    st.caption("📌powered by vectara")

    st.caption("With this feature you can effortlessly incorporate existing notes or documents into your digital workspace. 🌟 Whether it's a detailed writing structure for your next novel or a comprehensive guide on productivity techniques, you can simply drag and drop these resources into your Note Taker interface. Voila! 🎩 They're now part of your digital brain, ready to fuel your creativity and productivity whenever you need them.")
# User input
    # File uploader widget
    uploaded_file = st.file_uploader("Choose a file to upload to you brain 🧠", type=['txt', 'pdf'])

    doc_metadata = '{}'

    # Check if file is uploaded
    if uploaded_file is not None:
        # If metadata is not provided, use an empty string
        if not doc_metadata:
            doc_metadata = '{}'
        
        # Call function to upload file to Vectara
        upload_result = upload_file_to_vectara(uploaded_file, doc_metadata)
        
        # Provide feedback to the user
        if upload_result['success']:
            st.success(upload_result['message'])
        else:
            st.error(upload_result['message'])

if __name__ == "__main__":
    main()
