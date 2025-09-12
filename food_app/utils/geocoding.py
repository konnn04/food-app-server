import requests
import json

def coordinates_to_address(lat, lon):
    """
    Chuyển tọa độ thành địa chỉ sử dụng Nominatim (OpenStreetMap)
    Trả về địa chỉ dạng string
    """
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
        headers = {
            'User-Agent': 'FoodApp/1.0'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            address = data.get('display_name', '')
            return address
        else:
            return f"Tọa độ: {lat}, {lon}"
            
    except Exception as e:
        print(f"Lỗi chuyển tọa độ sang địa chỉ: {str(e)}")
        return f"Tọa độ: {lat}, {lon}"

def address_to_coordinates(address):
    """
    Chuyển địa chỉ thành tọa độ sử dụng Nominatim (OpenStreetMap)
    Trả về tuple (lat, lon)
    """
    try:
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={address}&limit=1"
        headers = {
            'User-Agent': 'FoodApp/1.0'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return lat, lon
            else:
                return None, None
        else:
            return None, None
            
    except Exception as e:
        print(f"Lỗi chuyển địa chỉ sang tọa độ: {str(e)}")
        return None, None
