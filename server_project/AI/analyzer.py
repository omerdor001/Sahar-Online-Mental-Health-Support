import logging
import threading
import time

from AI.ai_adapters import aialgorithm
from AI.ai_adapters.GSR_algorithm_adapter import GSRAlgorithmAdapter
from AI.ai_adapters.aialgorithm import AIAlgorithm
from AI.ai_adapters.basic_algorithm_adapter import BasicAlgorithmAdapter
from objects.message_record import MessageRecord
from utils.config_util import ConfigUtil
from objects.conversation_cache import ConversationCache
#from concurrent.futures import ThreadPoolExecutor


class Analyzer:
    _instance = None
    algorithms_adapters: set[AIAlgorithm]

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.algorithms_adapters = set()
            cls._instance.cache = ConversationCache()
            cls._instance.get_algorithms()
            cls._instance._start_analyze_thread()
        return cls._instance

    def _start_analyze_thread(self):
        self.analyz_thread = threading.Thread(target=self.analyze)
        self.analyz_thread.daemon = True
        self.analyz_thread.start()

    def analyze(self):
        while True:
            try:
                time_to_sleep: int = ConfigUtil().get_config_attribute("analyzer_interval")
                print("start Analyze")
                logging.info("Start analyze")
                data: dict[str, [MessageRecord]] = self.cache.get_conversations_to_enrich()
                #print(f"there are {len(data)} converstation to enrich")
                if len(data) != 0:
                    for adapter in self.algorithms_adapters:
                        #print(f"Start analyze {adapter.get_name()}")
                        logging.info(f"Start analyzing {adapter.get_name()}")
                        #executor = ThreadPoolExecutor(max_workers=min(50,len(data)))
                        #print("initialized exector")
                        #futures = [executor.submit(adapter.reference_to_analyze, {key: value}) for key, value in data.items()]
                        #print("done futures")
                        #results = [f.result() for f in futures]
                        #print(results)
                        #print(f"analyze {len(data)} conversations")
                        results = adapter.reference_to_analyze(data)
                        #print(f"results is {results}")
                        for conv_id, json_data in results.items():
                            messages = data[conv_id]
                            last_message_id = max(messages, key=lambda msg: msg.timeL if msg.timeL else 0).messageId
                            #print(f"analyzed converstaion id {conv_id} with last_message_id {last_message_id}")
                            self.cache.enrich_conversation(conv_id, json_data, last_message_id)
                    self.cache.update_need_analyze(data)
                
                logging.info("End analyzing successfully")
            except Exception as e:
                print(f"error in analyze process{e}")
                logging.error(f"Error in analyze process {e}")
            print("End Analyze")
            time.sleep(time_to_sleep)

    def get_algorithms(self):
        """
        Retrieves AI algorithm names from the configuration file and initializes corresponding algorithm adapters.
        """
        config = ConfigUtil()
        algorithms: [str] = config.get_config_attribute("AI-algorithms")
        for algorithm_name in algorithms:
            adapter = self.convert_str_to_adapter(algorithm_name)
            if adapter is not None:
                self.algorithms_adapters.add(adapter)

    def convert_str_to_adapter(self, algorithm_name):
        adapter: AIAlgorithm
        switcher = {"basic_algorithm": BasicAlgorithmAdapter(),
                    "GSR_algorithm": GSRAlgorithmAdapter()}
        return switcher.get(algorithm_name, None)

