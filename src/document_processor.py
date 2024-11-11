from chromadb import Client
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import CharacterTextSplitter

# Traitement des articles
def traiter_articles(donnees_articles):
    client = Client(Settings(persist_directory="chroma_db"))  
    collection = client.create_collection("articles")  
    modele_embedding = SentenceTransformer("all-MiniLM-L6-v2")

    passages = [article['Résumé'] for article in donnees_articles if 'Résumé' in article and article['Résumé']]
    if not passages:
        print("Aucun résumé valide trouvé.")
        return None

    splitter = CharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    segments = [chunk for passage in passages for chunk in splitter.split_text(passage)]

    identifiants_documents = [str(i) for i in range(len(segments))]  
    embeddings = [modele_embedding.encode(segment).tolist() for segment in segments]
    metadonnees = [{"segment": segment} for segment in segments]  

    collection.add(
        documents=segments,
        embeddings=embeddings,
        metadatas=metadonnees,
        ids=identifiants_documents
    )

    print("L'index des textes a été créé avec succès dans ChromaDB.")
    return collection

# Recherche des segments pertinents
def recherche_chromadb(query, collection, modele_embedding, seuil_pertinence=0.5, k=3):
    embedding_requete = modele_embedding.encode(query).tolist()
    resultats = collection.query(
        query_embeddings=[embedding_requete],
        n_results=k
    )

    # Récupérer les documents et scores
    documents = resultats["documents"][0]
    scores = resultats["distances"][0]
    
    print(f"Documents trouvés : {documents}")
    print(f"Scores de pertinence : {scores}")
    
    if scores[0] < seuil_pertinence:
        return ["Désolé, aucune information pertinente trouvée."]
    
    return documents
