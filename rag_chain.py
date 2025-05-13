import os
import time

from pathlib import Path

from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from google.cloud import translate_v2 as translate


def get_folder_path(folder_name):
    folder_path = os.path.join(os.getcwd(), folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path


def detect_language(google_translate_client, text):
    language_response = google_translate_client.detect_language(text)
    return language_response["language"]


def translate_text(client, target_language, source_language, text):
    translate_response = client.translate(
        text,
        source_language=source_language,
        target_language=target_language,
    )
    return translate_response["translatedText"]


class RagChain:
    def __init__(self, data_folder_name, pc_index_name, pinecone_api_key, google_api_key,
                 translate_client_config_file_path):
        self.data_folder_path = get_folder_path(data_folder_name)
        self.embedding_model = FastEmbedEmbeddings()
        self.vector_store = self.process_vector_store(pinecone_api_key, pc_index_name)
        self.llm = GoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=google_api_key)
        self.prompt_template = PromptTemplate(
            template="""You are a helpful and knowledgeable AI assistant that provides accurate and clear information about the registration of births, marriages, and deaths in Sri Lanka. You support responses in English (en), Sinhala (si), or Tamil (ta) based on the user's query language.

Use only the information from the retrieved documents to answer. Follow these instructions:

- Only answer questions related to registration information.
If the user's question is unrelated or the answer cannot be found in the retrieved documents, respond politely with:
"I'm sorry, I can’t help with that."

- Present the response in a clear, organized format using bullet points or numbered lists where appropriate.

- If relevant, include links from the 'Important Links' section (If exists) to guide users to official resources.

- At the end of the response, include a "For more information" link if available and relevant to the query.

Maintain a professional and helpful tone. Do not invent or assume information. Answer in the language used by the user in their query.
---
Context:
{context}

user: {question}
Assistant:
""",
            input_variables=["context", "question"],
        )
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 3}),
            chain_type="stuff",
            return_source_documents=True,
            chain_type_kwargs={"prompt": self.prompt_template},
        )
        try:
            self.google_translate_client = translate.Client.from_service_account_json(translate_client_config_file_path)
        except Exception as e:
            raise ValueError(f"Failed to initialize Google Translate client: {e}")

    def process_vector_store(self, pinecone_api_key, pc_index_name):
        pc = Pinecone(api_key=pinecone_api_key)

        existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

        if pc_index_name not in existing_indexes:
            print(f"Vector store index '{pc_index_name}' not found. Create new...")

            pc.create_index(
                name=pc_index_name,
                dimension=384,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )

            while not pc.describe_index(pc_index_name).status['ready']:  # Wait for the index to be ready
                time.sleep(1)
            print(f"Successfully created vector store index '{pc_index_name}'. Adding pdf files to new index...")

            index = pc.Index(pc_index_name)
            vector_store = PineconeVectorStore(index=index, embedding=self.embedding_model)

            print(f"Adding documents to index '{pc_index_name}'.")

            if os.path.exists(self.data_folder_path):
                md_files = list(Path(self.data_folder_path).rglob('*.md'))
                print(f"Found '{len(md_files)}' files to process.")
                for file_path in md_files:
                    print(f"Processing file: '{file_path}'.")
                    loader = TextLoader(file_path, encoding='utf-8')
                    documents = loader.load()
                    vector_store.add_documents(documents)
            else:
                print(f"Error: No found folder '{self.data_folder_path}'.")
            return vector_store

        print(f"Existing vector store found. Returning it: '{pc_index_name}'.")
        index = pc.Index(pc_index_name)
        return PineconeVectorStore(index=index, embedding=self.embedding_model)

    def process_query(self, query, user_input_language):
        english_query = query if user_input_language == "en" \
            else translate_text(self.google_translate_client, "en", user_input_language, query)
        return english_query

    def process_response(self, response, user_input_language):
        english_query = response if user_input_language == "en" \
            else translate_text(self.google_translate_client, user_input_language, "en", response)
        return english_query

    def run(self, user_input_query):
        user_input_language = detect_language(self.google_translate_client, user_input_query)
        query = self.process_query(user_input_query, user_input_language)
        llm_response = self.qa_chain.invoke({"query": f"{query}. Please provide your answer in {user_input_language}"})
        return llm_response['result']
