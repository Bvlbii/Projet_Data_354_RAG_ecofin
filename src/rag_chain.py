from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from langchain.llms import BaseLLM
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import torch

# Modèle de génération de texte
class ModeleHuggingFace(BaseLLM):
    def __init__(self, nom_modele: str, nom_tokenizer: str):
        self.nom_modele = nom_modele
        self.tokenizer = AutoTokenizer.from_pretrained(nom_tokenizer)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(nom_modele)
    
    def _call(self, prompt: str) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True)
        with torch.no_grad():
            outputs = self.model.generate(input_ids=inputs["input_ids"], max_length=200, temperature=0.3, top_p=0.9)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    def _identifying_params(self) -> str:
        return self.nom_modele

# Création de la chaine de RAG avec ChromaDB
def creer_modele_generation():
    nom_modele = "google/flan-t5-large"
    return ModeleHuggingFace(nom_modele=nom_modele, nom_tokenizer=nom_modele)

def creer_chaine_rag_chromadb(vectorstore):
    modele_generation = creer_modele_generation()
    chaine_rag_chromadb = RetrievalQA.from_chain_type(
        llm=modele_generation,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
        prompt="Répondez de manière complète et précise, en vous basant sur les segments de texte fournis."
    )
    return chaine_rag_chromadb
