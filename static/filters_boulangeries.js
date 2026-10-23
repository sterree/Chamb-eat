// Affiche un message dans la console pour indiquer que le script est chargé
console.log('filters_boulangeries.js chargé');

// Fonction pour appliquer les filtres aux boulangeries
function applyFiltersBoulangeries() {
    // Sélectionne toutes les cases à cocher de type qui sont cochées
    const typeCheckboxes = document.querySelectorAll('.type-checkbox:checked');
    // Sélectionne toutes les cases à cocher de prix qui sont cochées
    const priceCheckboxes = document.querySelectorAll('.price-checkbox:checked');

    // Convertit les valeurs des cases à cocher de type en un tableau de chaînes de caractères en minuscules
    const types = Array.from(typeCheckboxes).map(checkbox => checkbox.value.trim().toLowerCase());
    // Convertit les valeurs des cases à cocher de prix en un tableau de paires de nombres
    const prices = Array.from(priceCheckboxes).map(checkbox => {
        const [lower, upper] = checkbox.value.split('-');
        return [parseFloat(lower), parseFloat(upper)];
    });

    // Envoie une requête POST au serveur pour filtrer les boulangeries
    fetch('/filter-boulangeries', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ types, prices })
    })
    .then(response => response.json()) // Convertit la réponse en JSON
    .then(data => {
        // Sélectionne le conteneur où les résultats seront affichés
        const container = document.getElementById("restaurant-list");
        container.innerHTML = ""; // Vide le conteneur

        // Si aucun résultat n'est trouvé, affiche un message
        if (data.length === 0) {
            container.innerHTML = "<li>Aucune boulangerie trouvée.</li>";
            return;
        }

        // Pour chaque boulangerie dans les résultats, crée un élément de liste
        data.forEach(restaurant => {
            const item = document.createElement("li");
            item.classList.add("restaurant-item");

            // Crée une image ou un message si aucune image n'est disponible
            const img = restaurant['COL 15'] ?
                `<img src="${restaurant['COL 15']}" alt="${restaurant['COL 2']}" class="restaurant-list-image">` :
                '<div class="no-image-list">Pas d\'image</div>';

            // Définit le contenu HTML de l'élément de liste
            item.innerHTML = `
                <div class="restaurant-card">
                    <div class="restaurant-image-container">
                        ${img}
                    </div>
                    <div class="restaurant-details">
                        <h3>${restaurant['COL 2']}</h3>
                        <p class="address"><i class="fas fa-map-marker-alt"></i> Adresse : ${restaurant['COL 7']}</p>
                        <p class="price"><i class="fas fa-euro-sign"></i> Prix Moyen : ${restaurant['COL 5']}</p>
                        <p class="type"><i class="fas fa-utensils"></i> Type : ${restaurant['COL 6']}</p>
                        <p class="rating"><i class="fas fa-star"></i> Note : ${restaurant['COL 3']}/5 (${restaurant['COL 4']} avis)</p>
                        ${restaurant['COL 1'] ? `<a href="${restaurant['COL 1']}" class="view-more" target="_blank">Voir sur Google Maps</a>` : ''}
                    </div>
                    <div class="restaurant-schedule">
                        <h4>Horaires d'Ouverture</h4>
                        <table>
                            <tr>
                                <th>Lundi</th>
                                <td>${restaurant['COL 8']}</td>
                            </tr>
                            <tr>
                                <th>Mardi</th>
                                <td>${restaurant['COL 9']}</td>
                            </tr>
                            <tr>
                                <th>Mercredi</th>
                                <td>${restaurant['COL 10']}</td>
                            </tr>
                            <tr>
                                <th>Jeudi</th>
                                <td>${restaurant['COL 11']}</td>
                            </tr>
                            <tr>
                                <th>Vendredi</th>
                                <td>${restaurant['COL 12']}</td>
                            </tr>
                            <tr>
                                <th>Samedi</th>
                                <td>${restaurant['COL 13']}</td>
                            </tr>
                            <tr>
                                <th>Dimanche</th>
                                <td>${restaurant['COL 14']}</td>
                            </tr>
                        </table>
                    </div>
                </div>
            `;

            // Ajoute l'élément de liste au conteneur
            container.appendChild(item);
        });
    });
}
