# Importation des modules nécessaires
from flask import Flask, render_template, request, jsonify
import mysql.connector
import random

# Création de l'application Flask
app = Flask(__name__)

# Connexion à la base de données MySQL
conn = mysql.connector.connect(
    user="root",
    password="Chambeat",
    host="localhost",
    port="3306",
    database="chambe_eat",
    auth_plugin='mysql_native_password'
)

# Dictionnaire de mapping pour les coups de cœur
COUPS_DE_COEUR_MAPPING = {
    'A': {'prenom': 'Anna', 'photo': 'static/image/anna.webp'},
    'B': {'prenom': 'Baptiste', 'photo': 'static/image/baptiste.webp'},
    'C': {'prenom': 'César', 'photo': 'static/image/cesar.webp'},
    'E': {'prenom': 'Esther', 'photo': 'static/image/esther.webp'},
    'M': {'prenom': 'Maurine', 'photo': 'static/image/maurine.png'},
    'Y': {'prenom': 'Cyprien', 'photo': 'static/image/cyprien.webp'},
}

def ajouter_coups_de_coeur(restaurants):
    """Ajoute les informations sur les coups de cœur à la liste des restaurants."""
    for restaurant in restaurants:
        coups_de_coeur_str = restaurant.get('COL 16', '')
        restaurant['coups_de_coeur'] = [
            COUPS_DE_COEUR_MAPPING[lettre]
            for lettre in coups_de_coeur_str.upper() if lettre in COUPS_DE_COEUR_MAPPING
        ]
    return restaurants

def obtenir_restaurants():
    """Récupère les restaurants depuis la base de données et ajoute les informations sur les coups de cœur."""
    curseur = conn.cursor(dictionary=True)
    curseur.execute("SELECT * FROM restaurants")
    tous_restaurants = curseur.fetchall()
    return ajouter_coups_de_coeur(tous_restaurants)

def obtenir_types_uniques():
    """Récupère les types uniques de restaurants depuis la base de données."""
    curseur = conn.cursor(dictionary=True)
    curseur.execute("SELECT DISTINCT `COL 6` FROM restaurants ORDER BY `COL 6`")
    types = curseur.fetchall()
    return sorted({t['COL 6'].strip() for t in types if t['COL 6']})

def obtenir_boulangeries():
    """Récupère les boulangeries depuis la base de données."""
    curseur = conn.cursor(dictionary=True)
    curseur.execute("SELECT * FROM boulangeries")
    return curseur.fetchall()

def obtenir_types_boulangeries():
    """Récupère les types uniques de boulangeries depuis la base de données."""
    curseur = conn.cursor(dictionary=True)
    curseur.execute("SELECT DISTINCT `COL 6` FROM boulangeries ORDER BY `COL 6`")
    types = curseur.fetchall()
    return sorted({t['COL 6'].strip() for t in types if t['COL 6']})

def obtenir_fourchettes_prix():
    """Retourne une liste de fourchettes de prix pour les restaurants."""
    return [
        (1, 10), (10, 20), (20, 30), (30, 40), (40, 50),
        (50, 60), (80, 90), (90, 100),
        (100, 110)
    ]

def obtenir_fourchettes_prix_boulangeries():
    """Retourne une liste de fourchettes de prix pour les boulangeries."""
    all_ranges = [
        (1, 10), (10, 20), (20, 30), (30, 40),
    ]
    return all_ranges

def parse_interval(valeur):
    """Parse une valeur de prix en un intervalle de deux floats."""
    try:
        if isinstance(valeur, str) and '–' in valeur:
            partie_basse, partie_haute = valeur.split('–')
            return float(partie_basse.strip()), float(partie_haute.strip())
        else:
            v = float(valeur)
            return v, v
    except:
        return None

def intervalles_chevauchent(a1, a2, b1, b2):
    """Vérifie si deux intervalles se chevauchent."""
    return a1 < b2 and b1 < a2

@app.route('/recherche')
def search():
    """Recherche des restaurants et boulangeries en fonction d'une requête."""
    query = request.args.get('q', '').lower()
    curseur = conn.cursor(dictionary=True)
    curseur.execute("SELECT *, 'restaurant' AS type FROM restaurants WHERE LOWER(`COL 2`) LIKE %s OR LOWER(`COL 7`) LIKE %s", ('%' + query + '%', '%' + query + '%'))
    restaurants = curseur.fetchall()
    curseur.execute("SELECT *, 'boulangerie' AS type FROM boulangeries WHERE LOWER(`COL 2`) LIKE %s OR LOWER(`COL 7`) LIKE %s", ('%' + query + '%', '%' + query + '%'))
    boulangeries = curseur.fetchall()
    resultats = restaurants + boulangeries
    return jsonify(resultats)

@app.route('/filter-restaurants', methods=['POST'])
def filter_restaurants():
    """Filtre les restaurants en fonction des critères donnés."""
    data = request.json
    filtres_type = data.get('types', [])
    filtres_prix = data.get('prices', [])
    seulement_coups_de_coeur = data.get('seulement_coups_de_coeur', False)
    coup_de_coeur_personne = data.get('coup_de_coeur_personne', [])

    tous_restaurants = obtenir_restaurants()
    restaurants_filtres = tous_restaurants

    if seulement_coups_de_coeur:
        restaurants_filtres = [r for r in restaurants_filtres if r['coups_de_coeur']]
    elif coup_de_coeur_personne:
        restaurants_filtres = [
            r for r in restaurants_filtres
            if any(c['prenom'] in coup_de_coeur_personne for c in r['coups_de_coeur'])
        ]

    if filtres_type:
        filtres_type_normalises = [t.strip().lower() for t in filtres_type]
        restaurants_filtres = [
            r for r in restaurants_filtres
            if r['COL 6'] and r['COL 6'].strip().lower() in filtres_type_normalises
        ]

    if filtres_prix:
        resultat = []
        for r in restaurants_filtres:
            borne = parse_interval(r['COL 5'])
            if borne:
                for lower, upper in filtres_prix:
                    if intervalles_chevauchent(borne[0], borne[1], lower, upper):
                        resultat.append(r)
                        break
        restaurants_filtres = resultat

    return jsonify(restaurants_filtres)

@app.route('/filter-boulangeries', methods=['POST'])
def filter_boulangeries():
    """Filtre les boulangeries en fonction des critères donnés."""
    data = request.json
    filtres_type = data.get('types', [])
    filtres_prix = data.get('prices', [])

    toutes_boulangeries = obtenir_boulangeries()
    boulangeries_filtres = toutes_boulangeries

    if filtres_type:
        filtres_type_normalises = [t.strip().lower() for t in filtres_type]
        boulangeries_filtres = [
            r for r in boulangeries_filtres
            if r['COL 6'] and r['COL 6'].strip().lower() in filtres_type_normalises
        ]

    if filtres_prix:
        resultat = []
        for r in boulangeries_filtres:
            borne = parse_interval(r['COL 5'])
            if borne:
                for lower, upper in filtres_prix:
                    if intervalles_chevauchent(borne[0], borne[1], lower, upper):
                        resultat.append(r)
                        break
        boulangeries_filtres = resultat

    return jsonify(boulangeries_filtres)

@app.route('/')
def index():
    """Page d'accueil affichant des restaurants et boulangeries recommandés."""
    tous_restaurants = obtenir_restaurants()
    restaurants_recommandes = random.sample(tous_restaurants, min(3, len(tous_restaurants)))
    toutes_boulangeries = obtenir_boulangeries()
    boulangeries_recommandees = random.sample(toutes_boulangeries, min(3, len(toutes_boulangeries)))

    return render_template('index.html', recommended_restaurants=restaurants_recommandes, recommended_boulangeries=boulangeries_recommandees)

@app.route('/restaurants')
def restaurants():
    """Page listant tous les restaurants avec des options de filtrage."""
    tous_restaurants = obtenir_restaurants()
    types = obtenir_types_uniques()
    fourchettes_prix = obtenir_fourchettes_prix()
    coups_de_coeur_personnes = sorted(list({c['prenom'] for r in tous_restaurants for c in r.get('coups_de_coeur', [])}))
    return render_template('restaurants.html', restaurants=tous_restaurants, types=types, price_ranges=fourchettes_prix, coups_de_coeur_personnes=coups_de_coeur_personnes)

@app.route('/boulangeries')
def boulangeries():
    """Page listant toutes les boulangeries avec des options de filtrage."""
    tous_boulangeries = obtenir_boulangeries()
    types = obtenir_types_boulangeries()
    fourchettes_prix = obtenir_fourchettes_prix_boulangeries()
    return render_template('boulangeries.html', restaurants=tous_boulangeries, types=types, price_ranges=fourchettes_prix)

@app.route('/contact')
def contact():
    """Page de contact avec les informations des collaborateurs."""
    collaborateurs = [
        {"nom": "Guerra Elizondo", "prenom": "César", "email": "cesar.guerra-elizondo@etu.univ-smb.fr", "photo": "static/image/cesar.webp"},
        {"nom": "Bonnefond", "prenom": "Cyprien", "email": "cyprien.bonnefond@etu.univ-smb.fr", "photo": "static/image/cyprien.webp"},
        {"nom": "Déchelette", "prenom": "Esther", "email": "esther.dechelette@etu.univ-smb.fr", "photo": "static/image/esther.webp"}
    ]
    coups_de_coeur_personnes_contact = [
        {"prenom": "Anna", "photo": "static/image/anna.webp"},
        {"prenom": "Baptiste", "photo": "static/image/baptiste.webp"},
        {"prenom": "Maurine", "photo": "static/image/maurine.png"}
    ]
    return render_template('contact.html', collaborateurs=collaborateurs, coups_de_coeur_personnes=coups_de_coeur_personnes_contact)

if __name__ == '__main__':
    app.run(debug=True)
