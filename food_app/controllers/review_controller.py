from food_app.dao.review_dao import ReviewDAO
from food_app.utils.responses import success_response, error_response

class ReviewController:
    @staticmethod
    def create_review(data):
        try:
            if not data.get('customer_id') or not data.get('rating'):
                return error_response('Thiếu thông tin bắt buộc', 400)
            if not (1 <= int(data['rating']) <= 5):
                return error_response('Rating phải từ 1-5', 400)

            review = ReviewDAO.create_review(data)
            return success_response('Tạo đánh giá thành công', review.to_dict(), 201)
        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def get_restaurant_reviews(restaurant_id):
        try:
            reviews = ReviewDAO.get_reviews_for_restaurant(restaurant_id)
            return success_response('Lấy đánh giá thành công', [r.to_dict() for r in reviews])
        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def get_food_reviews(food_id):
        try:
            reviews = ReviewDAO.get_reviews_for_food(food_id)
            return success_response('Lấy đánh giá thành công', [r.to_dict() for r in reviews])
        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)


