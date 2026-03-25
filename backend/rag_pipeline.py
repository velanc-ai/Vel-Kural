import os
import pandas as pd
from langchain_community.document_loaders import DataFrameLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

# Load environment variables (e.g., OPENAI_API_KEY)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

def create_embeddings():
    # Resolve the correct path to the CSV file
    csv_path = os.path.join(os.path.dirname(__file__), "data", "KURAL_DATASET.csv")
    if not os.path.exists(csv_path):
        csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "KURAL_DATASET.csv")
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}")

    print(f"Loading dataset from {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Combine diverse fields into a single 'combined_text' column for embedding.
    # We include both Tamil and English content for semantic matching in either language.
    print("Preparing text for embedding...")
    df['combined_text'] = df.apply(
        lambda row: f"Section: {row.get('ENGLISH_SECTION', '')} / {row.get('TAMIL_SECTION', '')}\n"
                    f"Chapter: {row.get('ENGLISH_CHAPTERS', '')} / {row.get('TAMIL_CHAPTERS', '')}\n"
                    f"Tamil Verse: {row.get('TAMIL_VERSE', '')}\n"
                    f"Tamil Meaning: {row.get('TAMIL_EXPLANATION', '')}\n"
                    f"English Verse: {row.get('ENGLISH_VERSE', '')}\n"
                    f"English Meaning: {row.get('ENGLISH_EXPLANATION', '')}", axis=1)

    # Load into Langchain Documents
    loader = DataFrameLoader(df, page_content_column="combined_text")
    documents = loader.load()

    print(f"Loaded {len(documents)} verse documents. Generating vector embeddings (this may take a few moments)...")
    
    # Initialize the OpenAI Embeddings model
    # Note: Ensure OPENAI_API_KEY is properly set in your environment
    embeddings_model = OpenAIEmbeddings()

    # Create the Vector Store
    vectorstore = FAISS.from_documents(documents, embeddings_model)
    
    # Define save path (we'll save it inside the backend directory)
    save_path = os.path.join(os.path.dirname(__file__), "faiss_index")
    vectorstore.save_local(save_path)
    
    print(f"Successfully generated and saved vector embeddings locally at: {save_path}")

if __name__ == "__main__":
    create_embeddings()
