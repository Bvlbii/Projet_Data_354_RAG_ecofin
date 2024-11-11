import requests
from bs4 import BeautifulSoup
import re
import json
import csv
from datetime import datetime
import os

# Fonction pour nettoyer le texte
def nettoyer_texte(texte):
    texte = texte.strip()
    texte = re.sub(r'\s+', ' ', texte)  # Supprime les espaces multiples
    return texte

# Fonction de scraping
def scraper_articles():
    url_base = 'https://www.agenceecofin.com/a-la-une/recherche-article/articles'
    params = {
        'submit_x': 20,
        'submit_y': 31,
        'filterTousLesFils': 'Tous',
        'filterCategories': 'Sous-rubrique',
        'filterDateFrom': '2024-11-01',
        'filterDateTo': '2024-11-10',
        'filterFrench': 'French',
        'userSearch': 1,
        'testlimitstart': 0
    }
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; Chrome/79.0.3945.74 Safari/537.36'}
    nombre_pages = 10

    donnees_articles = []
    for page in range(1, nombre_pages + 1):
        params['testlimitstart'] = (page - 1) * 10
        reponse = requests.get(url_base, headers=headers, params=params)
        if reponse.status_code == 200:
            soup = BeautifulSoup(reponse.text, 'html.parser')
            articles = soup.find_all('table', class_='ts')
            for article in articles:
                try:
                    titre = nettoyer_texte(article.find('h3', class_='r').text)
                    lien = 'https://www.agenceecofin.com' + article.find('h3', class_='r').a['href']
                    
                    # Extraction et conversion de la date
                    date = nettoyer_texte(article.find('span', class_='f nsa').text)
                    date = re.sub(r'[^\d/]', '', date)
                    date = datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d")

                    resume = nettoyer_texte(article.find('div', class_='st').text)
                    resume = re.sub(r'\(\.\.\.lien\)', '', resume)
                    
                    # Extraction de la catégorie
                    categorie = nettoyer_texte(article.find('span', class_='news-source').text.split('(')[-1].replace(')', '').strip()) if article.find('span', class_='news-source') else "Non spécifiée"
                    
                    # Ajout dans la liste de données
                    donnees_articles.append({
                        'Titre': titre,
                        'Lien': lien,
                        'Date': date,
                        'Résumé': resume,
                        'Catégorie': categorie
                    })

                except AttributeError as e:
                    print(f"Un élément manquant dans cet article : {e}")

        else:
            print(f"Erreur lors de la récupération de la page {page} : Code {reponse.status_code}")

    # Sauvegarde des données en JSON et CSV
    with open('articles1.json', 'w', encoding='utf-8') as json_file:
        json.dump(donnees_articles, json_file, ensure_ascii=False, indent=4)
    with open('articles.csv', 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=['Titre', 'Lien', 'Date', 'Résumé', 'Catégorie'])
        writer.writeheader()
        writer.writerows(donnees_articles)

    print("Les données ont été sauvegardées en formats JSON, CSV.")
    return donnees_articles

# Exécution du scraping
scraper_articles()
