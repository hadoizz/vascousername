from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)

# Allow all origins for development (Caution: restrict in production)
CORS(app, resources={r"/api/*": {"origins": "*", "allow_headers": "*", "methods": ["GET", "POST", "OPTIONS"]}})

@app.route('/api/vsco', methods=['GET'])
def fetch_vsco_user_media():
    username = request.args.get('username')

    if not username:
        return jsonify({'error': 'Username is required'}), 400

    site_url = f'https://vsco.co/api/2.0/sites?subdomain={username}'
    headers = {
        'Authorization': 'Bearer 7356455548d0a1d886db010883388d08be84d0c9',
        'User-Agent': 'vsco-get',
    }

    try:
        site_response = requests.get(site_url, headers=headers)
        site_response.raise_for_status()
        site_data = site_response.json()

        if not site_data.get('sites'):
            return jsonify({'error': 'User not found'}), 404

        user_id = site_data['sites'][0]['id']
        media_url = f'https://vsco.co/api/2.0/medias?site_id={user_id}'
        media_response = requests.get(media_url, headers=headers)
        media_response.raise_for_status()

        media_items = media_response.json().get('media', [])
        
        formatted_media = []
        for item in media_items:
            formatted_media.append({
                'id': item['_id'],
                'permalink': item['permalink'],
                'responsive_url': item['responsive_url'],
                'description': item.get('description', 'No description available'),
                'capture_date': item.get('capture_date'),
                'copyright': item.get('image_meta', {}).get('copyright', 'No copyright info')
            })

        return jsonify({'media': formatted_media}), 200

    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {str(err)}")
        return jsonify({'error': f'HTTP error occurred: {str(err)}'}), 500
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
