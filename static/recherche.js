// Fonction pour rechercher des restaurants
function searchRestaurants() {
    // Récupère la valeur de la barre de recherche et supprime les espaces en début et fin de chaîne
    const query = document.getElementById("search-bar").value.trim();
    // Sélectionne la section des résultats de recherche
    const searchResultsSection = document.getElementById("search-results");
    // Sélectionne la section des restaurants recommandés
    const recommendedRestaurantsSection = document.getElementById("recommended-restaurants");
    // Sélectionne la section des boulangeries recommandées
    const recommendedBoulangeriesSection = document.getElementById("recommended-boulangeries");

    // Si la requête est vide, cache la section des résultats de recherche et affiche les sections recommandées
    if (query === "") {
        searchResultsSection.classList.remove("active");
        recommendedRestaurantsSection.classList.add("active");
        recommendedBoulangeriesSection.classList.add("active");
        searchResultsSection.querySelector(".restaurant-grid").innerHTML = "";
        return;
    }

    // Affiche la section des résultats de recherche et cache les sections recommandées
    searchResultsSection.classList.add("active");
    recommendedRestaurantsSection.classList.remove("active");
    recommendedBoulangeriesSection.classList.remove("active");

    // Envoie une requête GET au serveur pour rechercher des restaurants et boulangeries
    fetch(`/recherche?q=${encodeURIComponent(query)}`)
        .then(response => response.json()) // Convertit la réponse en JSON
        .then(data => {
            // Sélectionne le conteneur où les résultats seront affichés
            const container = document.querySelector("#search-results .restaurant-grid");
            container.innerHTML = ""; // Vide le conteneur

            // Si aucun résultat n'est trouvé, affiche un message
            if (data.length === 0) {
                container.innerHTML = "<p>Aucun résultat trouvé.</p>";
                return;
            }

            // Pour chaque élément dans les résultats, crée une carte de restaurant
            data.forEach(item => {
                const card = document.createElement("div");
                card.classList.add("restaurant-card");

                // Crée une image ou un message si aucune image n'est disponible
                const img = item['COL 15'] ?
                    `<img src="${item['COL 15']}" alt="${item['COL 2']}" class="restaurant-image">` :
                    '<div class="no-image">Pas d\'image</div>';

                // Optionnel : ajoute un label pour différencier restaurant / boulangerie
                const labelType = item.type === 'restaurant' ? 'Restaurant' : 'Boulangerie';

                // Définit le contenu HTML de la carte de restaurant
                card.innerHTML =
                    `${img}
                    <h3>${item['COL 2']} <small>(${labelType})</small></h3>
                    <p class="type">Type : ${item['COL 6']}</p>
                    <p class="address">Adresse : ${item['COL 7']}</p>
                    <p class="price">Prix : ${item['COL 5']}</p>
                    <p class="rating">${item['COL 3']}/5 (${item['COL 4']} avis)</p>
                    ${item['COL 1'] ? `<a href="${item['COL 1']}" class="view-more" target="_blank">Voir sur Google Maps</a>` : ""}`;

                // Ajoute la carte de restaurant au conteneur
                container.appendChild(card);
            });
        });
}
