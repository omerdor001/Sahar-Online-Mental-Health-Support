import pytest
from unittest.mock import patch, MagicMock, call
from objects.conversation_cache import ConversationCache
from datetime import datetime, timedelta

# Test for ConversationCache initialization
@patch('objects.conversation_cache.rwlock.RWLockFair')
@patch('threading.Thread')
def test_conversation_cache_init(mock_thread, mock_rwlock):
    cache = ConversationCache()
    assert isinstance(cache, ConversationCache)
    assert cache.closed_conversations == {}
    assert cache.messages == {}
    assert cache.open_conversations == {}
    mock_rwlock.assert_called_once()
    mock_thread.assert_any_call(target=cache.cleanup_old_data)
    mock_thread.assert_any_call(target=cache.log_data)

# Test for starting cleanup thread
@patch('threading.Thread')
def test_start_cleanup_thread(mock_thread):
    cache = ConversationCache()
    cache._start_cleanup_thread()
    mock_thread.assert_called_with(target=cache.cleanup_old_data)
    mock_thread.return_value.start.assert_called_once()

# Test for starting log thread
@patch('threading.Thread')
def test_start_log_thread(mock_thread):
    cache = ConversationCache()
    cache._start_log_thread()
    mock_thread.assert_called_with(target=cache.log_data)
    mock_thread.return_value.start.assert_called_once()

# Test for updating open conversations
@patch('objects.conversation_cache.ConversationCache._start_log_thread')
@patch('objects.conversation_cache.ConversationCache._start_cleanup_thread')
@patch('objects.conversation_cache.ConfigUtil')
def test_update_open_conversations(mock_config_util, mock_start_cleanup_thread, mock_start_log_thread):
    cache = ConversationCache()
    mock_current_time = 123456789
    mock_conversation = {'conv1': MagicMock()}
    mock_messages = {'conv1': {MagicMock()}}

    with patch.object(cache, '_lock', MagicMock()):
        cache.update_conversations(mock_current_time, mock_conversation, mock_messages)
    
    assert cache.open_conversations == mock_conversation
    assert cache.messages == mock_messages

if __name__ == '__main__':
    pytest.main()