from flask import Blueprint, request
from food_app.controllers.search_controller import SearchController
from flasgger import swag_from

search_bp = Blueprint('search', __name__)

@search_bp.route('/', methods=['GET'])
@swag_from({'tags': ['Search'], 'summary': 'Search restaurants and foods', 'parameters': [
    {'in': 'query', 'name': 'q', 'schema': {'type': 'string'}, 'description': 'Search keyword for food or restaurant name'},
    {'in': 'query', 'name': 'lat', 'schema': {'type': 'number', 'format': 'float'}, 'description': 'Current latitude'},
    {'in': 'query', 'name': 'lon', 'schema': {'type': 'number', 'format': 'float'}, 'description': 'Current longitude'},
    {'in': 'query', 'name': 'min_price', 'schema': {'type': 'number', 'format': 'float'}, 'description': 'Minimum price'},
    {'in': 'query', 'name': 'max_price', 'schema': {'type': 'number', 'format': 'float'}, 'description': 'Maximum price'},
    {'in': 'query', 'name': 'sort_by', 'schema': {'type': 'string', 'enum': ['distance', 'price']}, 'description': 'Sort by distance or price'},
    {'in': 'query', 'name': 'sort_order', 'schema': {'type': 'string', 'enum': ['asc', 'desc']}, 'description': 'Sort order'},
    {'in': 'query', 'name': 'page', 'schema': {'type': 'integer'}, 'description': 'Page number'},
    {'in': 'query', 'name': 'per_page', 'schema': {'type': 'integer'}, 'description': 'Items per page'}
], 'responses': {
    '200': {
        'description': 'Success',
        'schema': {
            'type': 'object',
            'properties': {
                'success': {'type': 'boolean'},
                'message': {'type': 'string'},
                'data': {
                    'type': 'object',
                    'properties': {
                        'items': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer'},
                                    'name': {'type': 'string'},
                                    'address': {'type': 'string'},
                                    'phone': {'type': 'string'},
                                    'email': {'type': 'string'},
                                    'description': {'type': 'string'},
                                    'image_url': {'type': 'string'},
                                    'latitude': {'type': 'number'},
                                    'longitude': {'type': 'number'},
                                    'distance_km': {'type': 'number'},
                                    'is_active': {'type': 'boolean'},
                                    'opening_hours': {'type': 'object'},
                                    'searched_foods': {
                                        'type': 'array',
                                        'items': {
                                            'type': 'object',
                                            'properties': {
                                                'id': {'type': 'integer'},
                                                'name': {'type': 'string'},
                                                'description': {'type': 'string'},
                                                'price': {'type': 'number'},
                                                'image_url': {'type': 'string'},
                                                'available': {'type': 'boolean'}
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        'total': {'type': 'integer'},
                        'page': {'type': 'integer'},
                        'per_page': {'type': 'integer'},
                        'pages': {'type': 'integer'}
                    }
                }
            }
        }
    }
}})
def search():
    """Tìm kiếm nhà hàng và món ăn"""
    return SearchController.search()
