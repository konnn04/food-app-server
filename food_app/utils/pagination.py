from config import Config

def paginate(data, page: int = None, per_page: int = None):
    """
    Paginate data (SQLAlchemy query or list)
    
    Args:
        data: SQLAlchemy query object or list
        page: Page number (default from config)
        per_page: Items per page (default from config)
    
    Returns:
        tuple: (paginated_items, pagination_info)
    """
    # Use config defaults
    page = max(int(page or Config.DEFAULT_PAGE), 1)
    per_page = min(max(int(per_page or Config.DEFAULT_PER_PAGE), Config.MIN_PER_PAGE), Config.MAX_PER_PAGE)
    
    # Check if data is SQLAlchemy query or list
    if hasattr(data, 'limit') and hasattr(data, 'count'):
        # SQLAlchemy query
        items = data.limit(per_page).offset((page - 1) * per_page).all()
        total = data.order_by(None).count()
    else:
        # List or other iterable
        total = len(data)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        items = data[start_idx:end_idx]
    
    pagination_info = {
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': (total + per_page - 1) // per_page,
        'has_next': page < (total + per_page - 1) // per_page,
        'has_prev': page > 1
    }
    
    return items, pagination_info


