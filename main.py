import os
import streamlit as st

from dotenv import load_dotenv
from rag_chain import RagChain
from views import show_sidebar, select_language, show_title

# Load environment variables
load_dotenv()

# Check for required environment variables
required_keys = ["GOOGLE_API_KEY", "PINECONE_API_KEY", "GOOGLE_TRANSLATE_CONFIG_PATH"]
for key in required_keys:
    if not os.getenv(key):
        st.error(f"Missing environment variable: {key}")
        st.stop()

# Initialize RagChain
folder_name = "rgd_data"
pc_index_name = "rgd-data"
google_api_key = os.getenv("GOOGLE_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
translate_client_config_file_path = os.getenv("GOOGLE_TRANSLATE_CONFIG_PATH")

rag_chain = RagChain(
    data_folder_name=folder_name,
    pc_index_name=pc_index_name,
    pinecone_api_key=pinecone_api_key,
    google_api_key=google_api_key,
    translate_client_config_file_path=translate_client_config_file_path
)

# Show the sidebar and language selection
show_sidebar()
language, placeholder, title = select_language()
show_title(title)

# Query input
query = st.text_input(placeholder, key="query")

# Process query if submitted
if query:
    try:
        response = rag_chain.run(query)
        st.markdown(response, unsafe_allow_html=True)
    except Exception as e:
        print(f"Error processing the query: {str(e)}")
        st.error(f"Unexpected error occurred. Try again later.")

