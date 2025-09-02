import os
from food_app import create_app
from flasgger import swag_from

app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.route('/')
def root():
    return {'message': 'Food App Server', 'docs': '/apidocs/'}, 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)