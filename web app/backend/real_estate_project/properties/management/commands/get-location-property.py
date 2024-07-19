import requests
from time import sleep
import csv

locations = [
    "Le Chaland, South",
    "The Vale, North",
    "Pointe aux Sables, West",
    "Bel Ombre, South",
    "Vacoas, Center",
    "Hermitage, Center",
    "Helvetia, Center",
    "Arsenal, North",
    "Chamouny, South",
    "Mont Piton, North",
    "Trou d'Eau Douce, East",
    "St François, North",
    "Khoyratty, North",
    "Plaine Magnien, South",
    "Nouvelle France, South",
    "La Preneuse, West",
    "Petit Raffray, North",
    "Vieux Grand Port, South",
    "Candos, Center",
    "St Antoine, North",
    "Pomponnette, South",
    "Calebasses, North",
    "Trois Boutiques, South",
    "Côte d'Or, Center",
    "Forbach, North",
    "Chamarel, West",
    "l'Avenir, Center",
    "Poste Lafayette, East",
    "Ebène, Center",
    "Camp Diable, South",
    "Grande Rivière Noire, West",
    "Bon Espoir, North",
    "Piton, North",
    "Pierrefonds, West",
    "Quatre Bornes, Center",
    "Constance, East",
    "Forest Side, Center",
    "Palmar, East",
    "Belle Vue Harel, North",
    "Baie du Cap, South",
    "New Grove, South",
    "Quartier Militaire, Center",
    "Camp Fouquereau, Center",
    "Gris Gris, South",
    "Roches Noires, North",
    "Verdun, Center",
    "Pailles, Center",
    "Roche Terre, North",
    "Mon Désert, South",
    "Ville Noire, South",
    "Port Louis, North",
    "Mon Choisy, North",
    "Beaux Songes, West",
    "Pamplemousses, North",
    "Mon Loisir, North",
    "Bras d'Eau, East",
    "Beau Champ, East",
    "Roches Brunes, Center",
    "Plaine Lauzun, North",
    "Haute Rive, North",
    "Petite Rivière Noire, West",
    "Poste de Flacq, East",
    "The Mount, North",
    "Castel, Center",
    "Péreybère, North",
    "Choisy, East",
    "La Cambuse, South",
    "Terre Rouge, North",
    "St Paul, Center",
    "Pointe aux Piments, North",
    "Rose Belle, South",
    "Albion, West",
    "Savannah, South",
    "Trou aux Biches, North",
    "Britannia, South",
    "Fond du Sac, North",
    "Sottise, North",
    "Pointe d'Esny, South",
    "Tyack, South",
    "Pointe aux Biches, North",
    "Solférino, Center",
    "Charmoze, North",
    "Camp Levieux, Center",
    "St Jean, Center",
    "Melville, North",
    "d'Epinay, North",
    "Phoenix, Center",
    "St Pierre, Center",
    "Ilot Fortier, West",
    "Goodlands, North",
    "Riche Terre, North",
    "Beau Vallon, South",
    "Le Bouchon, South",
    "Balaclava, North",
    "Mahébourg, South",
    "Belle Rose (Centre), Center",
    "Sorèze, North",
    "Palma, West",
    "Cassis, North",
    "Rose Hill, Center",
    "Bain Boeuf, North",
    "Gros Bois, South",
    "Petit Camp, Center",
    "Floréal, Center",
    "Mont Mascal, North",
    "La Louise, Center",
    "Surinam, South",
    "Flacq, East",
    "Les Salines (Port Louis), North",
    "Bagatelle, Center",
    "Tamarin, West",
    "Beau Bassin, Center",
    "Sébastopol, East",
    "Coromandel, Center",
    "Dagotière, Center",
    "Mare d'Albert, South",
    "Le Hochet, North",
    "Rivière du Rempart, North",
    "Petite Rivière, West",
    "Glen Park, Center",
    "Cap Malheureux, North",
    "Beau Plan, North",
    "Grand Gaube, North",
    "Moka, Center",
    "Blue Bay, South",
    "La Mivoie, West",
    "Pointe aux Canonniers, North",
    "Trianon, Center",
    "Flic en Flac, West",
    "Belle Étoile, Center",
    "Plaine Verte, North",
    "Triolet, North",
    "Calodyne, North",
    "Midlands, Center",
    "Ste Croix, North",
    "Tombeau Bay, North",
    "Riambel, South",
    "Eau Coulée, Center",
    "Belle Mare, East",
    "Rodrigues",
    "Le Morne, West",
    "Curepipe, Center",
    "Argy, East",
    "Cascavelle, West",
    "Black River, West",
    "Lallmatie, East",
    "Sodnac, Center",
    "Grand Bay, North",
    "Mapou, North",
    "Highlands, Center",
    "Bambous, West",
    "Anna, West",
    "Wooton, Center",
    "La Gaulette, West",
    "Wolmar, West",
    "Grand River North West, North",
    "Forêt Daruty, North",
    "Souillac, South"
]

headers = {
    'User-Agent': 'YourAppName/1.0 (yourname@domain.com)'  # Replace with your app name and contact info
}

def fetch_coordinates(location, retries=3):
    location_name = location.split(',')[0]
    location_name = location_name + ", Mauritius"
    print(f"Fetching coordinates for {location_name}...")
    url = f"https://nominatim.openstreetmap.org/search?q={location_name}&format=json"
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data:
                return {
                    'location': location,
                    'latitude': data[0]['lat'],
                    'longitude': data[0]['lon']
                }
            else:
                return {
                    'location': location,
                    'latitude': None,
                    'longitude': None
                }
        except requests.exceptions.RequestException as e:
            print(f"Request error for {location}: {e}")
            sleep(2 ** attempt)  # Exponential backoff
        except requests.exceptions.JSONDecodeError as e:
            print(f"JSON decode error for {location}: {e}")
            sleep(2 ** attempt)  # Exponential backoff
    return {
        'location': location,
        'latitude': None,
        'longitude': None
    }

# Open the CSV file in append mode
with open('location_coordinates.csv', 'a', newline='') as csvfile:
    fieldnames = ['location', 'latitude', 'longitude']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    # Write header only if the file is empty
    if csvfile.tell() == 0:
        writer.writeheader()
    
    coordinates = []
    for location in locations:
        coord = fetch_coordinates(location)
        coordinates.append(coord)
        writer.writerow(coord)  # Save each coordinate immediately
        print(f"Coordinates for {location}: {coord}")
        # To avoid making too many requests in a short time period
        sleep(1)

print("Coordinates have been saved to location_coordinates.csv")