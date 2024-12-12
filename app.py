from flask import Flask, request, render_template
import streamlit as st
import requests

app = Flask(__name__)

tourism_values = [
    "viewpoint", "picnic_site", "camp_site", "caravan_site", "museum", "gallery",
    "castle", "monument", "ruins", "archaeological_site", "theme_park",
    "water_park", "zoo", "aquarium"
]

# Function to get geolocation of a place
def get_geolocation(place_name):
    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "YourAppName/1.0 (your_email@example.com)"}
    params = {'q': place_name, 'format': 'json', 'limit': 1}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return {'lat': float(data['lat']), 'lon': float(data['lon'])}
    return None

# Function to generate Overpass API query
def get_query(location, tag_key, tag_values, radius=50000):
    node = ""
    for tag_value in tag_values:
        node += f"""node["{tag_key}"="{tag_value}"](around:{radius},{location['lat']},{location['lon']});"""
    return f"[out:json];({node});out;"

# Function to fetch nearby places using Overpass API
def get_nearby_places(location, tag_key, tag_values, radius=50000, limit=100):
    query = get_query(location, tag_key, tag_values, radius)
    url = "https://overpass-api.de/api/interpreter"
    response = requests.post(url, data={'data': query})

    if response.status_code == 200:
        data = response.json()
        return [
            {
                'name': element.get('tags', {}).get('name', 'Unknown'),
                'lat': element['lat'],
                'lon': element['lon'],
                'link': f"https://www.openstreetmap.org/node/{element['id']}"
            } for element in data.get('elements', []) if element.get('tags', {})
        ][:limit]
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
    return "Server is running on Waitress!"

@app.route('/search', methods=['POST'])
def search():
    place_name = request.form.get('place_name')
    attractions, hotels, restaurants = search_places(place_name)
    return render_template("results.html", place_name=place_name,
                           attractions=attractions, hotels=hotels, restaurants=restaurants)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
