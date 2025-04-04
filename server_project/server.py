import logging

from AI.analyzer import Analyzer
from objects.conversation_cache import *
from lp_api_manager.lp_conversations_grabber import LpConversationGrabber
from lp_api_manager.lp_utils import LpUtils
from utils.config_util import ConfigUtil
from utils.logger import Logger
from api.server_api import ServerAPI #, app
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from DataBase import database_helper
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
CORS(app)                                             

def init_system():
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # db.init_app(app)
    # with app.app_context():
        # db.create_all()
        # print("Database created successfully!")
    database_helper.DataBaseHelper(app)
    ConfigUtil().init()  # Init singleton
    ServerAPI(app)
    Logger()
    logging.debug("Start system initiation")
    lp_utils = LpUtils()
    conversation_cache = ConversationCache() # Ni Change
    conversation_predictions = database_helper.DataBaseHelper.get() # Nir Add
    print("total conversation predictions")
    print(len(conversation_predictions))
    conversation_cache.initialize(conversation_predictions) #Nir Add
    Analyzer()
    logging.info("Finished system initiation successfully")
    lp_conversation_grabber=  LpConversationGrabber()
    return lp_conversation_grabber


def grab(grabber):
    while True:
        try:
            grabber.grab()
        except Exception as e:
            logging.error(f"Grabber finished unsuccessfully. Error message: {e}")
        time.sleep(ConfigUtil().get_config_attribute("grabber_interval"))


grabber = init_system()
threading.Thread(target=grab, args=(grabber,), daemon=True).start()

if __name__ == "__main__":
    pass
    
    