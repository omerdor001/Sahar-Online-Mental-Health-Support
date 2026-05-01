from flask_sqlalchemy import SQLAlchemy
import sys
from datetime import datetime
from sqlalchemy.sql import func

db = SQLAlchemy()

class DataBaseHelper:
    def __init__(self,app):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database_test.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
        db.app = app

        with app.app_context():
            db.create_all()
            print("dataBase created succesfully")

    @staticmethod
    def add_b(obj_to_add):
        with db.app.app_context():
            try:
                db.session.merge(obj_to_add)
                db.session.commit()
            except Exception as e:
                db.session.rollback()


    def get():
        from dao_object.conversation_prediction_object import ConversationPredictionDAO
        
        fifteen_min_ago = datetime.now().timestamp() - 3600  # 15 minutes ago
        with db.app.app_context():
            try:
                latest_message_subquery = db.session.query(
                    ConversationPredictionDAO.conversationId,
                    func.max(ConversationPredictionDAO.last_message_id).label("max_message_id")
                ).filter(
                    ConversationPredictionDAO.created_at >= fifteen_min_ago,
                    ConversationPredictionDAO.status == 'CLOSE'
                ).group_by(ConversationPredictionDAO.conversationId).subquery()

                # Main query: Fetch only records that match the latest message_id for each conversationId
                latest_predictions = db.session.query(ConversationPredictionDAO).join(
                    latest_message_subquery,
                    (ConversationPredictionDAO.conversationId == latest_message_subquery.c.conversationId) &
                    (ConversationPredictionDAO.last_message_id == latest_message_subquery.c.max_message_id)
                ).all()
                print(latest_predictions)
                return latest_predictions
            except Exception as e :
                print("Failed to fetch records from DB: ", str(e))


