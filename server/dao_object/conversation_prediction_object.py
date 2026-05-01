


from DataBase.database_helper import db
from datetime import datetime


class ConversationPredictionDAO(db.Model):
        __tablename__ = 'conversation_predictions'
        
        conversationId =  db.Column(db.String, primary_key=True)
        basic_algorithm_result = db.Column(db.String)
        GSR = db.Column(db.Float)
        IMSR = db.Column(db.Boolean)
        max_GSR = db.Column(db.Float)
        status = db.Column(db.String)
        last_message_id = db.Column(db.String, primary_key=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)


