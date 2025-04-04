import pytz
from flask import Flask, request, jsonify
import jwt
from jwt import jwk
from jwt.jwk import OctetJWK
from functools import wraps
from objects.conversation_cache import ConversationCache
from lp_api_manager.lp_utils import LpUtils
from utils.config_util import ConfigUtil
from readerwriterlock import rwlock
import threading
import time
from datetime import datetime, timedelta
import secrets
import logging

app = Flask(__name__)

class ServerAPI:
    def __init__(self, app):
        self.api_lock = rwlock.RWLockFair()
        self.app = app
        self.secret_key = OctetJWK(key=secrets.token_bytes(32))
        self.api_cache = {}
        self.jwt_key=jwt.JWT()
        self.cache_update_interval = ConfigUtil().get_config_attribute("cache_update_interval")

        threading.Thread(target=self.update_api_cache, daemon=True).start()
        self._setup_routes()


    def _setup_routes(self):
        @self.app.route("/login", methods=['POST', 'OPTIONS'])
        def login():
            return self.login()
         
        @self.app.route("/get_history_calls", methods=["GET"])
        @self.token_required
        def get_history_calls():
            return self.get_history_calls()

        @self.app.route("/get_open_calls", methods=["GET"])
        @self.token_required
        def get_open_calls():
            return self.get_open_calls()

    def token_required(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get("Authorization")
            if not token:
                return jsonify({"message": "Token is missing!"}), 403
            try:
                self.jwt_key.decode(token, self.secret_key, algorithms=["HS256"])
            except Exception as e:
                print(f"Token decoding failed: {e}")
                return jsonify({"message": "Token is invalid!"}), 403
            return f(*args, **kwargs) 
        return decorated_function

    def update_api_cache(self):
        while True:
            with self.api_lock.gen_wlock():
                self.api_cache["open_conversations"] = ConversationCache().get_json_open_conversations()
                self.api_cache["closed_conversations"] = ConversationCache().get_closed_conversations()
            time.sleep(self.cache_update_interval)

    def login(self):
        try:
            print(request.json)
            if request.method == 'OPTIONS':
                response = jsonify({})
            else:
                username = request.json.get("username")
                password = request.json.get("password")
                account_id = request.json.get("account_id")
                login_res = LpUtils().lp_login(username, password, account_id, 1)
                if login_res is not None and login_res.status_code in range(200, 300):
                    now = datetime.utcnow()
                    exp = now + timedelta(hours=24)
                    token = self.jwt_key.encode(
                        {
                            "sub": username,
                            "iat": int(now.timestamp()),
                            "exp": int(exp.timestamp()),
                        },
                        self.secret_key,
                    )
                    response = jsonify({"token": token})
                else:
                    response = jsonify({"message": "Invalid credentials"}), 401
            origin = request.headers.get('Origin')
            if origin is not None:
                response.headers.add('Access-Control-Allow-Origin', origin)
                response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            return response
        except Exception as e:
            return jsonify({"message": f"An error occurred: {str(e)}"}), 500

    def get_history_calls(self):
        minutes = 60
        try:
            minutes = int(request.args.get("minutes_to_fetch"))
            print("minutes from args", minutes)
        except Exception as e:
            print("failed to fetch minutes from the request", e)
        closed_conversations = {}
        with self.api_lock.gen_rlock():
            closed_conversations = self.api_cache.get("closed_conversations", [])

        print("nir here is closed conversations ", closed_conversations)
        # VERIFY The time 
        print("fetch from nir ", datetime.utcnow() - timedelta(minutes=minutes))
        time_threshold = int((datetime.utcnow() - timedelta(minutes=minutes)).timestamp() * 1000)
        print("time threshold is : ", time_threshold)

        recent_conversations = {
            conv_id: record
            for conv_id, record in closed_conversations.items()
            if record.conversationEndTimeL and record.conversationEndTimeL >= time_threshold  # Ensure startTime is a datetime object
        }
        for conv_id, record in closed_conversations.items():
            print("conv startTime ", record.conversationEndTime)
            print("conv startTimeL ", record.conversationEndTimeL)

        print("=============================")
        print(time_threshold)
        print(recent_conversations)
        print(len(recent_conversations))
        for conv_id, record in recent_conversations.items():
            print("conv startTime ", record.conversationEndTime)
            print("conv startTimeL ", record.conversationEndTimeL)
        # print(len(recent_conversations))
        return jsonify({"history": recent_conversations})

    def get_open_calls(self):
        with self.api_lock.gen_rlock():
            open_conversations = self.api_cache.get("open_conversations", [])
        for d in open_conversations:
            print(d.get("GSR"))
        return jsonify({"data": open_conversations})

    def run(self):
         self.app.run(host='127.0.0.1',
                      ssl_context=('/etc/letsencrypt/live/saharassociation.cs.bgu.ac.il/fullchain.pem', '/etc/letsencrypt/live/saharassociation.cs.bgu.ac.il/privkey.pem'),
                      port=5000, threaded=True)

if __name__ == "__main__":
     #server_api = ServerAPI()
     #server_api.run()
     pass