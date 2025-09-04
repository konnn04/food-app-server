import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Tính khoảng cách giữa hai điểm tọa độ theo công thức Haversine
    Trả về khoảng cách tính bằng km
    """
    # Chuyển đổi độ sang radian
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Bán kính trái đất (km)
    R = 6371
    
    # Công thức Haversine
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    distance = R * c
    
    return round(distance, 2)

def is_within_radius(lat1, lon1, lat2, lon2, radius_km):
    """
    Kiểm tra xem điểm có nằm trong bán kính không
    """
    distance = calculate_distance(lat1, lon1, lat2, lon2)
    return distance <= radius_km
