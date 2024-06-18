import streamlit as st
import tempfile
from st_components.upload_file import upload_file_to_vectara  # Importing the function from upload_file.py

def main():
    st.title("📝 Note Taker")
    st.caption("Say goodbye to your ideas languishing in the forgotten corners of your phone!")
    st.caption("📝 Our note-taking feature transforms your instant ideas and thoughts into valuable assets stored in your digital brain. 🧠 Instead of simply jotting down notes that collect virtual dust, every snippet of brilliance becomes a cornerstone of your digital universe. 🌟 Your notes don't just sit idly; they actively assist you, serving as fuel for creativity, problem-solving, and inspiration. 💡 Harness the power of your thoughts and let them propel you forward on your journey to greatness!")
    # Note input widget
    note_content = st.text_area("Enter your note here:")
    
    # Create a temporary text file to save the note content
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as temp_file:
        temp_file.write(note_content)
        temp_file_path = temp_file.name
    
    # Save button
    if st.button("Save"):
        if note_content.strip():
            st.success("Note saved successfully!")
        else:
            st.warning("Please enter a note before saving.")
    
    doc_metadata = '{}'
    
    # Check if the file exists and upload it
    if st.button("Upload"):
        try:
            # Open the temporary file
            with open(temp_file_path, "rb") as file:
                # Call function to upload file to Vectara
                upload_result = upload_file_to_vectara(file, doc_metadata)
                
            # Provide feedback to the user
            if upload_result['success']:
                st.success(upload_result['message'])
            else:
                st.error(upload_result['message'])
        except FileNotFoundError:
            st.error("File not found. Please provide a valid file path.")

if __name__ == "__main__":
    main()
