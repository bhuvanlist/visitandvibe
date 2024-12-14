from flask import Flask, request, render_template
import requests
import streamlit as st

app = Flask(__name__)

tourism_values = [
    "viewpoint", "picnic_site", "camp_site", "caravan_site", "museum", "gallery",
    "castle", "monument", "ruins", "archaeological_site", "theme_park",
    "water_park", "zoo", "aquarium", "fort", "temples"
]

# Function to get geolocation of a place
def get_geolocation(place_name):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        headers = {"User-Agent": "TourismApp/1.0 (contact@example.com)"}
        params = {'q': place_name, 'format': 'json', 'limit': 1}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if data:
            return {'lat': float(data[0]['lat']), 'lon': float(data[0]['lon'])}
    except Exception as e:
        print(f"Geolocation error: {e}")
    return None

# Function to generate Overpass API query
def get_query(location, tag_key, tag_values, radius=50000):
    nodes = "".join(
        f"""node["{tag_key}"="{tag_value}"](around:{radius},{location['lat']},{location['lon']});"""
        for tag_value in tag_values
    )
    return f"[out:json];({nodes});out;"

# Fetch nearby places using Overpass API
def get_nearby_places(location, tag_key, tag_values, radius=50000, limit=100):
    try:
        query = get_query(location, tag_key, tag_values, radius)
        url = "https://overpass-api.de/api/interpreter"
        response = requests.post(url, data={'data': query})
        response.raise_for_status()
        data = response.json()
        return [
            {
                'name': element.get('tags', {}).get('name','new_location'),
                'lat': element['lat'],
                'lon': element['lon'],
                'link': f"https://www.openstreetmap.org/node/{element['id']}"
            } for element in data.get('elements', []) if element.get('tags', {})
        ][:limit]
    except Exception as e:
        print(f"Overpass API error: {e}")
    return []

# Main function to search for nearby places
def search_places(place_name):
    location = get_geolocation(place_name)
    if not location:
        return None, None, None

    attractions = get_nearby_places(location, "tourism", tourism_values, limit=50)
    hotels = get_nearby_places(location, "tourism", ["hotel"], limit=10)
    restaurants = get_nearby_places(location, "amenity", ["restaurant"], limit=10)
    return attractions, hotels, restaurants

# Flask Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    place_name = request.form.get('place_name')
    if not place_name:
        return render_template("error.html", message="Place name is required!")

    attractions, hotels, restaurants = search_places(place_name)
    if not attractions and not hotels and not restaurants:
        return render_template("error.html", message=f"No data found for {place_name}!")

    return render_template(
        "results.html",
        place_name=place_name,
        attractions=attractions,
        hotels=hotels,
        restaurants=restaurants
    )

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
