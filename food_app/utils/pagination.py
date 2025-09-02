def paginate_query(query, page: int = 1, per_page: int = 20):
    page = max(int(page or 1), 1)
    per_page = min(max(int(per_page or 20), 1), 100)
    items = query.limit(per_page).offset((page - 1) * per_page).all()
    total = query.order_by(None).count()
    return items, {
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': (total + per_page - 1) // per_page
    }


