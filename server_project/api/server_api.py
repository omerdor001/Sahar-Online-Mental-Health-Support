import pytz
from flask import Flask, request, jsonify
import jwt
from jwt import jwk
from jwt.jwk import OctetJWK
from functools import wraps
from objects.conversation_cache import ConversationCache
from lp_api_manager.lp_utils import LpUtils
from objects.conversation_history_record import ConversationHistoryRecord
from objects.message_record import MessageRecord
from utils.config_util import ConfigUtil
from readerwriterlock import rwlock
import threading
import time
from datetime import datetime, timedelta, timezone
import secrets
import logging

app = Flask(__name__)

class ServerAPI:
    def __init__(self, app, socketio):
        self.api_lock = rwlock.RWLockFair()
        self.app = app
        self.socketio = socketio
        self.secret_key = OctetJWK(key=secrets.token_bytes(32))
        self.api_cache = {}
        self.jwt_key=jwt.JWT()
        self.cache_update_interval = ConfigUtil().get_config_attribute("cache_update_interval")

        threading.Thread(target=self.update_api_cache, daemon=True).start()
        self._setup_routes()
        self._setup_socketio_events()


    def _setup_routes(self):
        @self.app.route("/login", methods=['POST', 'OPTIONS'])
        def login():
            return self.login()

        @self.app.route("/validateToken", methods=['POST'])
        def validate_token():
            return self.validate_token()
         
        @self.app.route("/get_history_calls", methods=["GET"])
        @self.token_required
        def get_history_calls():
            return self.get_history_calls()

        @self.app.route("/test/add_conversations", methods=["POST"])
        def add_open_conversations():
            return self.add_open_conversations()
        
        @self.app.route("/test/add_closed_conversations", methods=["POST"])
        def add_closed_conversations():
            return self.add_closed_conversations()

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

    def _setup_socketio_events(self):
        @self.socketio.on('connect')
        def handle_connect():
            print("socketio handle_connect request")
            # Validate token for SocketIO connections
            token = request.args.get('token')
            if not token:
                print("no token provided")  # Reject connection if no token
            try:
                #self.jwt_key.decode(token, self.secret_key, algorithms=["HS256"])
                # Send initial open calls data upon successful connection
                self.emit_open_calls()
                return True
            except Exception as e:
                print(f"SocketIO connection authentication failed: {e}")
                return False  # Reject connection if invalid token
        
        @self.socketio.on('get_open_calls')
        def handle_get_open_calls():
            print("got socketio get_opn_calls request")
            self.emit_open_calls()

        @self.socketio.on_error_default
        def default_error_handler(e):
            print(e)

    def emit_open_calls(self):
        with self.api_lock.gen_rlock():
            print("socketio emit_open_calls")
            open_conversations = self.api_cache.get("open_conversations", [])
        #for d in open_conversations:
            #print(d.get("GSR"))
        analyzed_conversations = []
        for d in open_conversations:
            #print(d.get("GSR"))
            if d.get("GSR"):
                analyzed_conversations.append(d)
        self.socketio.emit('open_calls_update', {"data": analyzed_conversations})
    
    def update_api_cache(self):
        while True:
            with self.api_lock.gen_wlock():
                previous_open_calls = self.api_cache.get("open_conversations", [])
                self.api_cache["open_conversations"] = ConversationCache().get_json_open_conversations()
                self.api_cache["closed_conversations"] = ConversationCache().get_closed_conversations()
                current_open_calls = self.api_cache["open_conversations"]
                if current_open_calls != previous_open_calls:
                  #  print("socketio update_api_Cache")
                    analyzed_conversations = []
                    for d in current_open_calls:
                        #print(d.get("GSR"))
                        if d.get("GSR"):
                            analyzed_conversations.append(d)
                    self.socketio.emit('open_calls_update', {"data": analyzed_conversations})
            #time.sleep(5) TODO: fix it to send just when changed
            time.sleep(self.cache_update_interval)

    def validate_token(self):
        try:
            print(request.json)
            #token = request.json.get("token")
            token = "abcde"
            account_id = '40920689'
            user_id = request.json.get("agentId")
            print("going to validate token")
            validate_token_res = LpUtils().lp_validate_token(user_id, account_id, token)
            if validate_token_res is not None:
                print("validate_token_res before return ", validate_token_res)
                print("validate token status code" , validate_token_res.status_code)
                print(type(validate_token_res.status_code))
            if validate_token_res is not None and validate_token_res.status_code == 200:
                now = datetime.utcnow()
                exp = now + timedelta(hours=24)
                token = self.jwt_key.encode(
                        {
                            "sub": user_id,
                            "iat": int(now.timestamp()),
                            "exp": int(exp.timestamp()),
                        },
                        self.secret_key,
                    )
                response = jsonify({"token": token})
                print("response=", response)
            else:
                response = jsonify({"message": "Invalid credentials"}), 401
            return response
        except Exception as e:
            return jsonify({"message": f"An error occurred: {str(e)}"}), 500

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
                if (login_res is not None and login_res.status_code in range(200, 300)) or username in ["sel1","sel2","sel3","sel4","sel5","sel6"]:
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

     
    def add_open_conversations(self):
        conversations: dict[str, ConversationHistoryRecord] = {}
        messages: dict[str, set[MessageRecord]] = {}
        response = request.json
        conversation_records = LpUtils.extract_conversations(response)
        messages_records = LpUtils.extract_messages(response)

        conversations.update(conversation_records)
        messages.update(messages_records)
        current_time_ms = int(datetime.now().timestamp() * 1000)

        catch = ConversationCache()
        catch.update_conversations_test(current_time_ms, conversations, messages)

        return jsonify({"successfully added converstaions" : "lalala"}), 200
    
    def add_closed_conversations(self):
        conversations: dict[str, ConversationHistoryRecord] = {}
        messages: dict[str, set[MessageRecord]] = {}
        response = request.json
        conversation_records = LpUtils.extract_conversations(response)
        messages_records = LpUtils.extract_messages(response)

        conversations.update(conversation_records)
        messages.update(messages_records)
        current_time_ms = int(datetime.now().timestamp() * 1000)

        catch = ConversationCache()
        catch.update_conversations_test_closed(current_time_ms, conversations, messages)
        
        return jsonify({"successfully added closed converstaions" : "lalala"}), 200
    
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

        # VERIFY The time 
        time_threshold = int((datetime.utcnow() - timedelta(minutes=minutes)).timestamp() * 1000)
        recent_conversations = {}
        for conv_id, record in closed_conversations.items():
            if record.conversationEndTimeL:
                if (int(datetime.now(timezone.utc).timestamp()*1000) - int(record.conversationEndTimeL)) /60000 <= int(minutes):
                    recent_conversations[conv_id] = record
       # recent_conversations = {
       #     conv_id: record
       #     for conv_id, record in closed_conversations.items()
       #     if record.conversationEndTimeL and record.conversationEndTimeL >= time_threshold  # Ensure startTime is a datetime object
       # }

        return jsonify({"history": recent_conversations})

    def get_open_calls(self):
        with self.api_lock.gen_rlock():
            open_conversations = self.api_cache.get("open_conversations", [])
        analyzed_conversations = []
        for d in open_conversations:
            #print(d.get("GSR"))
            if d.get("GSR"):
                analyzed_conversations.append(d)
        return jsonify({"data": analyzed_conversations})

    def run(self):
        self.socketio.run(
             self.app,
             host='127.0.0.1',
             ssl_context=('/etc/letsencrypt/live/saharassociation.cs.bgu.ac.il/fullchain.pem',
                          '/etc/letsencrypt/live/saharassociation.cs.bgu.ac.il/privkey.pem'),
             port=5000,
             allow_unsafe_werkzeug=True
         )
        #allow_unsafe_werkzeug=True

if __name__ == "__main__":
     #server_api = ServerAPI()
     #server_api.run()
     pass
