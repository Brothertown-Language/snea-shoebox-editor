import numpy as np
import os
from huggingface_hub import InferenceClient
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
from tqdm import tqdm

# Load .env file
load_dotenv()

# ---------------------------------------------------------
# MODEL + API KEY
# ---------------------------------------------------------
MODEL_ID = "intfloat/multilingual-e5-small"
API_KEY = os.getenv("HF_API_TOKEN")

client = InferenceClient(model=MODEL_ID, token=API_KEY, timeout=60)

# ---------------------------------------------------------
# LEMMA LIST (variants included)
# ---------------------------------------------------------
lemmas = [
    "Abbamocho",
    "abockquósinash",
    "abohquas",
    "abohquos",
    "acawmen",
    "achm∞wonk",
    "adchau",
    "adhosu",
    "adhôsu",
    "adt",
    "át",
    "ahhut",
    "ahut",
    "adtah",
    "adtahshe",
    "adt‑tahshe",
    "adtahtou",
    "adtahtaush",
    "adtahtauau",
    "tahshinum",
    "tohshinum",
    "tashinum",
    "toshinum",
    "tahshinumauau",
    "tahshinau",
    "tohshinau",
]

# ---------------------------------------------------------
# EMBEDDING FUNCTION
# ---------------------------------------------------------
def embed(text):
    vec = client.feature_extraction(text)
    return np.array(vec, dtype=np.float32)

# ---------------------------------------------------------
# GENERATE EMBEDDINGS
# ---------------------------------------------------------
print("Generating embeddings...")
embeddings = np.vstack([embed(lemma) for lemma in tqdm(lemmas, desc="Embedding lemmas")])

# ---------------------------------------------------------
# COSINE SIMILARITY MATRIX
# ---------------------------------------------------------
sim_matrix = cosine_similarity(embeddings)

# ---------------------------------------------------------
# PRINT NEAREST NEIGHBORS
# ---------------------------------------------------------
def nearest_neighbors(idx, top_k=5):
    sims = sim_matrix[idx]
    order = np.argsort(-sims)
    return [(lemmas[j], float(sims[j])) for j in order[1:top_k+1]]

print("\nNearest neighbors:")
for i, lemma in enumerate(lemmas):
    print(f"\n{lemma}:")
    for neighbor, score in nearest_neighbors(i):
        print(f"   {neighbor:20s}  {score:.4f}")

# ---------------------------------------------------------
# OPTIONAL: PRINT FULL MATRIX
# ---------------------------------------------------------
print("\nCosine similarity matrix:")
print(sim_matrix)
