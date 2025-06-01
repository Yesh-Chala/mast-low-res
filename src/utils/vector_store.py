from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings


def load_vector_retriever(file_path, api_key):
        # Load the saved _retriever object from file
        saved_db = FAISS.load_local(file_path, embeddings=OpenAIEmbeddings(openai_api_key=api_key),
                                    allow_dangerous_deserialization=True)

        return saved_db.as_retriever(search_kwargs={"k": 10})