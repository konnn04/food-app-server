import os
from app import create_app

app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.route('/')
def index():
    return {
        'message': 'Food Ordering API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth',
            'food': '/api/food',
            'order': '/api/order'
        }
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)