from flask import Flask, request, jsonify, render_template
import streamlit as st
import requests
import gradio as gr

app = Flask(__name__)

# Data: List of tourism values
tourism_values = [
    "viewpoint", "picnic_site", "camp_site", "caravan_site", "museum",
    "gallery", "castle", "monument", "ruins", "archaeological_site",
    "theme_park", "water_park", "zoo", "aquarium"
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
    else:
        return None

# Function to build Overpass API query
def get_query(location, tag_key, tag_values, radius=50000):
    node = ""
    for tag_value in tag_values:
        node += f"""node["{tag_key}"="{tag_value}"](around:{radius},{location['lat']},{location['lon']});"""
    return f"[out:json];({node});out;"

# Function to fetch nearby places
def get_nearby_places(location, tag_key, tag_values, radius=50000, limit=100):
    query = get_query(location, tag_key, tag_values, radius)
    url = "https://overpass-api.de/api/interpreter"
    response = requests.post(url, data={'data': query})
    if response.status_code == 200:
        data = response.json()
        results = [
            {
                'name': element.get('tags', {}).get('name', 'Unknown'),
                'lat': element['lat'],
                'lon': element['lon'],
                'link': f"https://www.openstreetmap.org/node/{element['id']}"
            }
            for element in data.get('elements', [])
        ][:limit]
        return results
    else:
        return []



# Route to handle search requests
@app.route('/search', methods=['POST'])
def search_places(place_name=None):
    place_name = request.form.get('place_name')
    if not place_name:
        return "No place name provided."
    location = get_geolocation(place_name)
    if not location:
        return jsonify({'error': 'Invalid place name. Please try again.'})

    # Fetch data for different categories
    attractions = get_nearby_places(location, "tourism", tourism_values, limit=500)
    hotels = get_nearby_places(location, "tourism", ["hotel"], limit=10)
    restaurants = get_nearby_places(location, "amenity", ["restaurant"], limit=10)

    return jsonify({
        'attractions': attractions,
        'hotels': hotels,
        'restaurants': restaurants
    })
    return f"Results for {place_name}"

# Custom CSS for styling
custom_css = """
<style>
    body {
        font-family: 'Arial', sans-serif;
        background: linear-gradient(to bottom, #87CEEB, #4682B4); /* Light blue to steel blue gradient */
        color: #FFFFFF; /* White text for better readability */
        margin: 0;
        padding: 0;
    }
    .gradio-container {
        background-color: rgba(255, 255, 255, 0.8); /* Semi-transparent white background */
        border: 1px solid #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.25); /* Subtle shadow */
        backdrop-filter: blur(10px); /* Frosted glass effect */
    }
    .gr-button {
        background-color: #1E90FF; /* Dodger blue button */
        color: #FFFFFF;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-size: 16px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    .gr-button:hover {
        background-color: #4682B4; /* Steel blue on hover */
    }
    .gr-textbox {
        font-size: 14px;
        border: 2px solid #87CEEB; /* Light blue border */
        border-radius: 5px;
        padding: 10px;
    }
</style>
"""

# Gradio interface setup
gr_interface = gr.Interface(
    fn=search_places,
    inputs=gr.Textbox(label="Enter a Place Name"),
    outputs=gr.Textbox(label="Results", lines=200),
    title="Visit And Vibe",
    description="Enter a place name to find nearby tourist attractions, hotels, and restaurants with map links.",
   
)


@app.route('/')
def index():
    return render_template('index.html')  # Your HTML file for the homepage


if __name__ == "__main__":
    interface = gr.Interface(fn=search_places, inputs=gr.Textbox(label="Place Name"), outputs="text")  # Launch Gradio interface inline      gr_interface.launch(inline=True)
    app.run(debug=True, use_reloader=False) 
