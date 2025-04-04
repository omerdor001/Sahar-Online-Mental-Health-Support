import pytest
from unittest.mock import patch, MagicMock, ANY
from AI.analyzer import Analyzer

# Test for Analyzer initialization
@patch('AI.analyzer.ConfigUtil')
@patch('AI.analyzer.ConversationCache')
@patch('AI.analyzer.BasicAlgorithmAdapter')
def test_analyzer_init(mock_basic_algorithm, mock_conversation_cache, mock_config_util):
    analyzer = Analyzer()
    assert isinstance(analyzer, Analyzer)
    assert analyzer.cache == mock_conversation_cache.return_value

# Test for _start_analyze_thread method
@patch('AI.analyzer.ConfigUtil')
@patch('AI.analyzer.ConversationCache')
@patch('AI.analyzer.BasicAlgorithmAdapter')
@patch('threading.Thread')
def test_start_analyze_thread(mock_thread, mock_basic_algorithm, mock_conversation_cache, mock_config_util):
    analyzer = Analyzer()
    analyzer._start_analyze_thread()
    mock_thread.assert_called_once_with(target=analyzer.analyze)
    mock_thread.return_value.start.assert_called_once()


# Test for get_algorithms method
@patch('AI.analyzer.ConfigUtil')
@patch('AI.analyzer.ConversationCache')
@patch('AI.analyzer.BasicAlgorithmAdapter')
def test_get_algorithms(mock_basic_algorithm, mock_conversation_cache, mock_config_util):
    mock_config_util.return_value.get_config_attribute.return_value = ['basic_algorithm']

    analyzer = Analyzer()
    analyzer.get_algorithms()

    assert mock_basic_algorithm.return_value in analyzer.algorithms_adapters

# Test for convert_str_to_adapter method
@patch('AI.analyzer.BasicAlgorithmAdapter')
def test_convert_str_to_adapter(mock_basic_algorithm):
    adapter = Analyzer().convert_str_to_adapter('basic_algorithm')
    assert adapter == mock_basic_algorithm.return_value

    adapter = Analyzer().convert_str_to_adapter('non_existent_algorithm')
    assert adapter is None

if __name__ == '__main__':
    pytest.main()