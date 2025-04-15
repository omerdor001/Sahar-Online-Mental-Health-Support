import threading
import unittest
from unittest.mock import patch, MagicMock

from server_project.AI.ai_adapters.GSR_algorithm_adapter import GSRAlgorithmAdapter
from server_project.AI.ai_adapters.basic_algorithm_adapter import BasicAlgorithmAdapter
from server_project.AI.analyzer import Analyzer
from server_project.objects.message_record import MessageRecord
from server_project.utils.config_util import ConfigUtil


class System_tests(unittest.TestCase):
    @patch.object(Analyzer, 'get_algorithms')
    @patch.object(Analyzer, '_start_analyze_thread')
    @patch.object(ConfigUtil, 'load_config')
    @patch('server_project.objects.conversation_cache.ConversationCache')
    def test_analyze(self, MockConversationCache, mock_load_config, mock_start_analyze_thread, mock_get_algorithms):
        mock_config_instance = MagicMock(spec=ConfigUtil)
        mock_load_config.return_value = None
        mock_config_instance.return_value.get_config_attribute = lambda attribute: {
            "analyzer_interval": 15,
        }.get(attribute)
        with patch.object(ConfigUtil, '_instance', mock_config_instance):
            mock_cache = MagicMock()
            MockConversationCache.return_value = mock_cache
            mock_cache.get_conversations_to_enrich.return_value = {
                "conv_id_1": [
                    MessageRecord(
                        type="TEXT_PLAIN",
                        messageData={"msg": {"text": "היי"}},
                        messageId="ms::dialog:47b21186-4501-4363-8752-27bc8bd212b7::msg:0",
                        audience="ALL",
                        seq=0,
                        dialogId="47b21186-4501-4363-8752-27bc8bd212b7",
                        participantId="afae94dfe29ab73ff32e45d760068b6b1bb368ecb7fe3f039d59d6cf30bd3bc9",
                        source="SHARK",
                        time="2024-04-29 16:10:19.187+0000",
                        timeL=1714407019187,
                        device="DESKTOP",
                        sentBy="Consumer"
                    )
                ],
                "conv_id_2": [
                    MessageRecord(
                        type="TEXT_PLAIN",
                        messageData={"msg": {"text": "שלום"}},
                        messageId="ms::dialog:47b21186-4501-4363-8752-27bc8bd212b7::msg:1",
                        audience="ALL",
                        seq=1,
                        dialogId="47b21186-4501-4363-8752-27bc8bd212b7",
                        participantId="afae94dfe29ab73ff32e45d760068b6b1bb368ecb7fe3f039d59d6cf30bd3bc9",
                        source="SHARK",
                        time="2024-04-29 16:15:19.187+0000",
                        timeL=1714407019188,
                        device="DESKTOP",
                        sentBy="Consumer"
                    )
                ]
            }
            mock_basic_adapter = MagicMock(spec=BasicAlgorithmAdapter)
            mock_gsr_adapter = MagicMock(spec=GSRAlgorithmAdapter)
            analyzer = Analyzer()
            analyzer.cache = mock_cache
            analyzer.algorithms_adapters.add(mock_basic_adapter)
            analyzer.algorithms_adapters.add(mock_gsr_adapter)
            mock_basic_adapter.reference_to_analyze.return_value = {
                "conv_id_1": {"result": "data1"},
                "conv_id_2": {"result": "data2"}
            }
            mock_gsr_adapter.reference_to_analyze.return_value = {
                "conv_id_1": {"result": "gsr_data1"},
                "conv_id_2": {"result": "gsr_data2"}
            }
            with patch('time.sleep', return_value=None):
                analyzer.analyze_for_testing()
                mock_cache.get_conversations_to_enrich.assert_called()
                mock_basic_adapter.reference_to_analyze.assert_called()
                mock_gsr_adapter.reference_to_analyze.assert_called()
                self.assertTrue(mock_basic_adapter.reference_to_analyze.called)
                self.assertTrue(mock_gsr_adapter.reference_to_analyze.called)

    @patch.object(Analyzer, 'get_algorithms')
    @patch.object(Analyzer, '_start_analyze_thread')
    @patch.object(ConfigUtil, 'load_config')
    @patch('server_project.objects.conversation_cache.ConversationCache')
    def test_analyze_with_threads(self, MockConversationCache, mock_load_config, mock_start_analyze_thread,
                                  mock_get_algorithms):
        mock_config_instance = MagicMock(spec=ConfigUtil)
        mock_load_config.return_value = None
        mock_config_instance.return_value.get_config_attribute = lambda attribute: {
            "analyzer_interval": 15,
        }.get(attribute)
        with patch.object(ConfigUtil, '_instance', mock_config_instance):
            mock_cache = MagicMock()
            MockConversationCache.return_value = mock_cache
            mock_cache.get_conversations_to_enrich.return_value = {
                "conv_id_1": [
                    MessageRecord(
                        type="TEXT_PLAIN",
                        messageData={"msg": {"text": "היי"}},
                        messageId="ms::dialog:47b21186-4501-4363-8752-27bc8bd212b7::msg:0",
                        audience="ALL",
                        seq=0,
                        dialogId="47b21186-4501-4363-8752-27bc8bd212b7",
                        participantId="afae94dfe29ab73ff32e45d760068b6b1bb368ecb7fe3f039d59d6cf30bd3bc9",
                        source="SHARK",
                        time="2024-04-29 16:10:19.187+0000",
                        timeL=1714407019187,
                        device="DESKTOP",
                        sentBy="Consumer"
                    )
                ],
                "conv_id_2": [
                    MessageRecord(
                        type="TEXT_PLAIN",
                        messageData={"msg": {"text": "שלום"}},
                        messageId="ms::dialog:47b21186-4501-4363-8752-27bc8bd212b7::msg:1",
                        audience="ALL",
                        seq=1,
                        dialogId="47b21186-4501-4363-8752-27bc8bd212b7",
                        participantId="afae94dfe29ab73ff32e45d760068b6b1bb368ecb7fe3f039d59d6cf30bd3bc9",
                        source="SHARK",
                        time="2024-04-29 16:15:19.187+0000",
                        timeL=1714407019188,
                        device="DESKTOP",
                        sentBy="Consumer"
                    )
                ]
            }
            mock_basic_adapter = MagicMock(spec=BasicAlgorithmAdapter)
            mock_gsr_adapter = MagicMock(spec=GSRAlgorithmAdapter)
            analyzer = Analyzer()
            analyzer.cache = mock_cache
            analyzer.algorithms_adapters.add(mock_basic_adapter)
            analyzer.algorithms_adapters.add(mock_gsr_adapter)
            mock_basic_adapter.reference_to_analyze.return_value = {
                "conv_id_1": {"result": "data1"},
                "conv_id_2": {"result": "data2"}
            }
            mock_gsr_adapter.reference_to_analyze.return_value = {
                "conv_id_1": {"result": "gsr_data1"},
                "conv_id_2": {"result": "gsr_data2"}
            }
            def run_analysis():
                with patch('time.sleep', return_value=None):
                    analyzer.analyze_for_testing()
            threads = []
            for _ in range(5):
                thread = threading.Thread(target=run_analysis)
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join()
            mock_cache.get_conversations_to_enrich.assert_called()
            mock_basic_adapter.reference_to_analyze.assert_called()
            mock_gsr_adapter.reference_to_analyze.assert_called()
            self.assertEqual(mock_basic_adapter.reference_to_analyze.call_count, 5)
            self.assertEqual(mock_gsr_adapter.reference_to_analyze.call_count, 5)
            self.assertTrue(mock_basic_adapter.reference_to_analyze.called)
            self.assertTrue(mock_gsr_adapter.reference_to_analyze.called)


if __name__ == '__main__':
    unittest.main()
