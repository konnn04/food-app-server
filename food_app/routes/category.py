from flask import Blueprint
from flasgger import swag_from
from food_app.models.category import Category
from food_app.utils.responses import success_response, error_response

category_bp = Blueprint('category', __name__)

@category_bp.route('/', methods=['GET'])
@swag_from({'tags': ['Category'], 'summary': 'List all categories'})
def list_categories():
    try:
        cats = Category.query.order_by(Category.id.asc()).all()
        return success_response('OK', [
            {
                'id': c.id,
                'name': c.name,
                'description': c.description
            } for c in cats
        ])
    except Exception as e:
        return error_response(f'Lỗi server: {str(e)}', 500)


