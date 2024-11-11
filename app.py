import json
import streamlit as st
from dotenv import load_dotenv
import os
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from src.document_processor import traiter_articles, recherche_chromadb
from src.rag_chain import creer_modele_generation
import torch

# Charger le fichier .env pour accéder au token Hugging Face 
load_dotenv()
huggingface_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Modèle de génération de texte
modele_generation = pipeline(
    "text2text-generation",
    model="google/flan-t5-large",
    model_kwargs={"temperature": 0.3, "max_length": 200, "top_p": 0.9},
    framework="pt"
)
modele_embedding = SentenceTransformer("all-MiniLM-L6-v2")

# charger les articles depuis JSON
def charger_articles_depuis_json(chemin_fichier):
    with open(chemin_fichier, "r") as fichier:
        return json.load(fichier)

# Charger et indexer les articles avec ChromaDB
def charger_et_indexer_articles(donnees_articles=None):
    if not donnees_articles:
        donnees_articles = charger_articles_depuis_json("articles.json")
    
    if "collection" not in st.session_state:
        collection = traiter_articles(donnees_articles)
        if collection is None:
            raise ValueError("La collection n'a pas pu être créée.")
        st.session_state["collection"] = collection
    else:
        collection = st.session_state["collection"]
    
    return collection

# analyser le type de question
def analyser_type_question(question):
    mots_cles_factuels = ["quoi", "qui", "qu'est-ce", "définition", "description"]
    mots_cles_ouverts = ["comment", "pourquoi", "quel impact", "quels sont"]

    if any(mot in question.lower() for mot in mots_cles_factuels):
        return "factuelle"
    elif any(mot in question.lower() for mot in mots_cles_ouverts):
        return "ouverte"
    else:
        return "générale"

#  générer la réponse en fonction de la question
def generer_reponse(question, contexte, modele_generation, historique):
    type_question = analyser_type_question(question)

    # Construire le prompt en fonction de la question
    if type_question == "factuelle":
        prompt = f"Question: {question}\nContexte: {contexte}\nRépondez de manière précise et concise."
    elif type_question == "ouverte":
        prompt = f"Question: {question}\nContexte: {contexte}\nRépondez de manière détaillée et nuancée."
    else:
        prompt = f"Question: {question}\nContexte: {contexte}\nRépondez de manière générale."

    return modele_generation(prompt)[0]["generated_text"]

# Application principale Streamlit
def main():
    st.title("Agent Conversationnel Ecofin")

    #bouton pour réinitialiser la conversation
    if st.button('Réinitialiser la conversation'):
        st.session_state["historique_chat"] = []
        st.session_state["collection"] = None
        st.session_state["collection"] = charger_et_indexer_articles()
        st.success("La conversation a été réinitialisée.")

    # Barre de progression
    with st.spinner("Chargement des articles..."):
        if "collection" not in st.session_state:
            try:
                donnees_articles = charger_articles_depuis_json("articles.json")
                st.session_state["collection"] = charger_et_indexer_articles(donnees_articles)
                st.success("Articles chargés et indexés avec succès.")
            except ValueError as e:
                st.error(str(e))

    # Initialiser l'historique des conversations
    if "historique_chat" not in st.session_state:
        st.session_state["historique_chat"] = []

    # Barre de saisie de la question
    question = st.text_input("Posez votre question :")
    if question:
        # Recherche des segments pertinents
        seuil_pertinence = 0.8
        docs_relevants = recherche_chromadb(query=question, collection=st.session_state["collection"], modele_embedding=modele_embedding, seuil_pertinence=seuil_pertinence, k=3)
        contexte = " ".join(docs_relevants)

        # Générer la réponse en fonction  de la question et de l'historique
        reponse = generer_reponse(question, contexte, modele_generation, st.session_state["historique_chat"])

        # Stocker la question et la réponse dans l'historique
        st.session_state["historique_chat"].append({"question": question, "response": reponse, "segments": docs_relevants})

    # Affichage sous forme de conversation
    st.subheader("Historique de la conversation")
    for exchange in st.session_state["historique_chat"]:
        st.write(f"**Vous** : {exchange['question']}")
        st.write(f"**Agent** : {exchange['response']}")
        with st.expander(f"Segments utilisés", expanded=False):
            for doc in exchange["segments"]:
                st.write(f"- {doc}")

if __name__ == "__main__":
    main()
