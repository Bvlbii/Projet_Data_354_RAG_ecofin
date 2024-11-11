

# Agent Conversationnel Ecofin

## Description
Ce projet est un agent conversationnel permettant de poser des questions sur les articles d'actualité Ecofin. Il utilise une chaîne de récupération générative (RAG) et inclut un scraping, un traitement, et une interface web conviviale.


## Fonctionnalités
    • Recherche Augmentée : Utilisation de ChromaDB pour indexer et récupérer les articles en fonction des questions. 
    • Modèle de Génération : Utilisation d'un modèle  (flan-t5) de Hugging Face pour générer des réponses basées sur le contexte. 
    • Interface Utilisateur : Application web développée avec Streamlit. 

## Structure du Projet
├── app.py : Interface principale Streamlit  
├── articles.json : Données d’articles en JSON  
├── Readme.md : Documentation  
└── src  
&nbsp;&nbsp;&nbsp;&nbsp;├── document_processor.py : Fonctions de traitement et d'indexation des articles  
&nbsp;&nbsp;&nbsp;&nbsp;├── rag_chain.py : Chaîne RAG pour générer les réponses  
&nbsp;&nbsp;&nbsp;&nbsp;└── scraper.py : Script de scraping des articles  

## Pré-requis
1. Python 3.x
2.  Token API Hugging Face (pour accéder au modèle de génération) : créez un compte sur Hugging Face pour obtenir un token gratuit.
3. Créez un environnement virtuel et activez-le :

Installation
 python -m venv env
 source env/bin/activate  # Sur macOS/Linux
 .\env\Scripts\activate   # Sur Windows

4. Installation des dépendances listées dans `requirements.txt`


## Installation
```bash
# Cloner le dépôt
git clone git@github.com:Bvlbii/Projet_Data_354_RAG_ecofin.git

# Se déplacer dans le répertoire du projet
cd Projet_Data_354_RAG_ecofin

# Installer les dépendances
pip install -r requirements.txt

Configurez votre fichier .env dans le répertoire principale
Ouvrez .env et ajoutez votre token Hugging Face :
HUGGINGFACEHUB_API_TOKEN=your_hugging_face_token_here

Utilisation
Scraper les articles : Exécute scraper.py pour générer articles.json avec python src/scraper.py
Lancer l’agent conversationnel : Exécute app.py en Streamlit avec streamlit run app.py.


Remarques
Pour modifier les paramètres du scraping, changez la plage de dates dans scraper.py.
<'filterDateFrom': '2024-11-01',
 'filterDateTo': '2024-11-10',>

Et Aussi <nombre_pages = 10> , à adapter selon vos besoins.

