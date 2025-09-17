import os
import PyPDF2
import docx
import pytesseract
from PIL import Image
from langdetect import detect
from deep_translator import GoogleTranslator
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
# Load embedding model (you can use "all-MiniLM-L6-v2" for speed & accuracy balance)
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Path for FAISS index
INDEX_PATH = "faiss_index"


def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text

    elif ext == ".docx":
        doc = docx.Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])

    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    elif ext in [".png", ".jpg", ".jpeg"]:
        img = Image.open(file_path)
        return pytesseract.image_to_string(img, lang="eng")  # default English OCR

    else:
        return "Unsupported file format"

def detect_and_translate(text):
    try:
        lang = detect(text)
    except:
        lang = "en"

    if lang != "en":
        try:
            translated = GoogleTranslator(source="auto", target="en").translate(text)
            return translated, lang
        except:
            return text, lang
    return text, "en"



# Create or load FAISS index
def get_faiss_index(d=384):  # 384 = embedding dimension of "all-MiniLM-L6-v2"
    if os.path.exists(f"{INDEX_PATH}.index"):
        index = faiss.read_index(f"{INDEX_PATH}.index")
        with open(f"{INDEX_PATH}_meta.pkl", "rb") as f:
            metadata = pickle.load(f)
    else:
        index = faiss.IndexFlatL2(d)
        metadata = []
    return index, metadata

# Save FAISS index
def save_faiss_index(index, metadata):
    faiss.write_index(index, f"{INDEX_PATH}.index")
    with open(f"{INDEX_PATH}_meta.pkl", "wb") as f:
        pickle.dump(metadata, f)

# Add text chunks to FAISS
def add_to_faiss(docs, doc_id):
    index, metadata = get_faiss_index()
    embeddings = embedding_model.encode(docs)
    index.add(np.array(embeddings, dtype=np.float32))
    metadata.extend([(doc_id, text) for text in docs])
    save_faiss_index(index, metadata)

# Search similar chunks
def search_faiss(query, top_k=3):
    index, metadata = get_faiss_index()
    query_emb = embedding_model.encode([query])
    D, I = index.search(np.array(query_emb, dtype=np.float32), top_k)
    results = [metadata[i] for i in I[0]]
    return results

def chunk_text(text, chunk_size=500):
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i+chunk_size])