import requests

def fetch_restaurants_from_api(api_key: str, location: str, radius: int):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        'location': location,
        'radius': radius,
        'type': 'restaurant',
        'key': api_key
    }

    try:
        response = requests.get(url, params=params)
        # print(f"API Response Status Code: {response.status_code}") 
        
        if response.status_code == 200:
            json_response = response.json()
            # print(f"API Response JSON: {json_response}") 
            return json_response.get('results', [])
        else:
            # print(f"Error fetching restaurants: {response.status_code} - {response.text}") 
            return []
    except requests.exceptions.RequestException as e:
        # print(f"Request failed: {e}")
        return []

def fetch_place_details(place_id: str, api_key: str):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        'place_id': place_id,
        'key': api_key
    }

    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            json_response = response.json()
            # print(f"Fetch place details API Response JSON: {json_response}") 
            return response.json().get('result', {})
        else:
            return {}
    except requests.exceptions.RequestException as e:
        print(f"Request failed - fetch place details: {e}")
        return {}