"""
Setup script to create ChromaDB vector database from MongoDB data
Run this once to initialize the vector database for RAG chatbot
"""
import os
import sys
import json
import shutil

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME', 'learning_buddy_db')
CHROMA_PERSIST_DIR = "backend/chroma_db"

def fetch_mongodb_data():
    """Fetch all data from MongoDB Atlas"""
    print("📊 Connecting to MongoDB...")
    
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.server_info()  # Test connection
        
        db = client[DB_NAME]
        all_docs = []
        
        unique_course_set = set()
        unique_course_docs = []
        
        print("📥 Fetching data from collections...")
        
        for collection_name in db.list_collection_names():
            collection = db[collection_name]
            docs = list(collection.find())
            
            for doc in docs:
                doc.pop("_id", None)
                
                # 1. Save original document
                doc_original = doc.copy()
                doc_original["_collection"] = collection_name
                all_docs.append(json.dumps(doc_original, ensure_ascii=False))
                
                # 2. Create unique course entries from LP+Course
                if collection_name == "LP+Course":
                    lp_name = doc.get('learning_path_name')
                    c_name = doc.get('course_name')
                    c_level = doc.get('course_level_str')
                    
                    signature = (lp_name, c_name, c_level)
                    
                    if signature not in unique_course_set:
                        unique_course_set.add(signature)
                        
                        new_doc = {
                            "learning_path_name": lp_name,
                            "course_name": c_name,
                            "course_level_str": c_level,
                            "_collection": "Unique_Course"
                        }
                        
                        unique_course_docs.append(json.dumps(new_doc, ensure_ascii=False))
        
        # 3. Combine all documents
        all_docs.extend(unique_course_docs)
        
        print(f"✅ Fetched {len(all_docs)} documents from {len(db.list_collection_names())} collections")
        
        return all_docs
        
    except Exception as e:
        print(f"❌ MongoDB connection error: {e}")
        return []


def create_vector_database(all_docs):
    """Create ChromaDB vector database with embeddings"""
    print("\n🔄 Processing documents...")
    
    # Format data with metadata
    texts = []
    metadatas = []
    
    for doc_str in all_docs:
        try:
            item = json.loads(doc_str)
            
            collection_name = item.pop('_collection', 'Umum')
            item.pop('_id', None)
            
            # Create readable text content
            content_parts = []
            for key, value in item.items():
                if value:
                    clean_key = key.replace('_', ' ').title()
                    content_parts.append(f"{clean_key}: {str(value)}")
            
            text_content = "\n".join(content_parts)
            
            texts.append(text_content)
            metadatas.append({"source": collection_name})
            
        except json.JSONDecodeError:
            continue
    
    print(f"✅ Processed {len(texts)} documents")
    
    # Split into chunks
    print("\n📄 Splitting into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )
    
    docs = text_splitter.create_documents(texts, metadatas=metadatas)
    print(f"✅ Created {len(docs)} chunks")
    
    # Initialize embedding model
    print("\n⏳ Loading embedding model...")
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    print("✅ Embedding model loaded")
    
    # Create vector database
    print(f"\n💾 Creating vector database at {CHROMA_PERSIST_DIR}...")
    
    # Remove existing database
    if os.path.exists(CHROMA_PERSIST_DIR):
        print(f"🗑️  Removing existing database...")
        shutil.rmtree(CHROMA_PERSIST_DIR)
    
    vectordb = Chroma.from_documents(
        documents=docs,
        embedding=embedding_model,
        persist_directory=CHROMA_PERSIST_DIR
    )
    
    print(f"✅ Vector database created successfully!")
    print(f"📍 Location: {CHROMA_PERSIST_DIR}")
    
    return vectordb


def main():
    """Main setup function"""
    print("="*60)
    print("🚀 Learning Buddy - Vector Database Setup")
    print("="*60)
    
    # Check MongoDB connection
    if not MONGO_URI:
        print("❌ Error: MONGO_URI not found in environment variables")
        print("Please set MONGO_URI in .env file")
        return
    
    # Fetch data from MongoDB
    all_docs = fetch_mongodb_data()
    
    if not all_docs:
        print("❌ No data fetched from MongoDB")
        return
    
    # Create vector database
    vectordb = create_vector_database(all_docs)
    
    print("\n" + "="*60)
    print("✅ Vector Database Setup Complete!")
    print("="*60)
    print("\nYou can now use the chatbot with RAG functionality.")
    print("Run the Flask server to start chatting!")


if __name__ == "__main__":
    main()

