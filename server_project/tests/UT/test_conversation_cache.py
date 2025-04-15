from datetime import date, datetime
import pytest
from unittest.mock import patch, MagicMock, call
from openpyxl import Workbook
from server_project.objects.conversation_cache import ConversationCache


# Test for ConversationCache initialization
@patch('server_project.objects.conversation_cache.rwlock.RWLockFair')
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
@patch('server_project.objects.conversation_cache.ConversationCache._start_log_thread')
@patch('server_project.objects.conversation_cache.ConversationCache._start_cleanup_thread')
@patch('server_project.objects.conversation_cache.ConfigUtil')
def test_update_open_conversations(mock_config_util, mock_start_cleanup_thread, mock_start_log_thread):
    cache = ConversationCache()
    mock_current_time = 123456789
    mock_conversation = {'conv1': MagicMock()}
    mock_messages = {'conv1': {MagicMock()}}
    with patch.object(cache, '_lock', MagicMock()):
        cache.update_conversations(mock_current_time, mock_conversation, mock_messages)
    assert cache.open_conversations == mock_conversation
    assert cache.messages == mock_messages


# Test for moving conversation to closed conversations
@patch('server_project.objects.conversation_cache.LpUtils')
def test_move_conv_to_close(mock_lp_utils):
    cache = ConversationCache()
    mock_now = 123456789
    mock_conversations_ids = ['conv1', 'conv2']
    mock_response = MagicMock()
    mock_conversations_records = {
        'conv1': MagicMock(),
        'conv2': MagicMock()
    }
    mock_messages_records = {
        'conv1': [MagicMock()],
        'conv2': [MagicMock()]
    }
    mock_lp_utils().get_conversations_by_conv_id.return_value = mock_response
    mock_lp_utils.extract_conversations.return_value = mock_conversations_records
    mock_lp_utils.extract_messages.return_value = mock_messages_records
    cache.open_conversations = {
        'conv1': MagicMock(),
        'conv2': MagicMock()
    }
    cache._move_conv_to_close(mock_now, mock_conversations_ids)
    assert 'conv1' in cache.closed_conversations
    assert 'conv2' in cache.closed_conversations
    cache.closed_conversations['conv1'].update.assert_called_with(mock_conversations_records['conv1'])
    cache.closed_conversations['conv2'].update.assert_called_with(mock_conversations_records['conv2'])
    assert 'conv1' not in cache.open_conversations
    assert 'conv2' not in cache.open_conversations
    assert cache.messages['conv1'] == mock_messages_records['conv1']
    assert cache.messages['conv2'] == mock_messages_records['conv2']
    cache.closed_conversations['conv1'].update_field.assert_any_call("need_analyze", True)
    cache.closed_conversations['conv1'].update_field.assert_any_call("lastUpdateTime", mock_now)


# Test for getting all conversations
@patch('server_project.objects.conversation_cache.LpUtils')
def test_get_all_conversations(mock_rwlock):
    cache = ConversationCache()
    mock_lock = MagicMock()
    mock_rwlock.return_value = mock_lock
    mock_lock.gen_rlock.return_value.__enter__.return_value = mock_lock
    mock_lock.gen_rlock.return_value.__exit__.return_value = False
    mock_open_conversations = {
        'conv1': MagicMock(),
        'conv2': MagicMock()
    }
    mock_closed_conversations = {
        'conv3': MagicMock(),
        'conv4': MagicMock()
    }
    cache.open_conversations = mock_open_conversations
    cache.closed_conversations = mock_closed_conversations
    all_conversations = cache.get_all_conversations()
    expected_conversations = set(mock_open_conversations.values()) | set(mock_closed_conversations.values())
    assert all_conversations == expected_conversations


# Test for getting closed conversations
@patch('server_project.objects.conversation_cache.LpUtils')
def test_get_closed_conversations(mock_rwlock):
    cache = ConversationCache()
    mock_lock = MagicMock()
    mock_rwlock.return_value = mock_lock
    mock_rlock = MagicMock()
    mock_lock.gen_rlock.return_value = mock_rlock
    mock_closed_conversations = {
        'conv1': MagicMock(),
        'conv2': MagicMock(),
    }
    cache.closed_conversations = mock_closed_conversations
    result = cache.get_closed_conversations()
    assert result == mock_closed_conversations


# Test for getting closed to enrich
@patch('server_project.objects.conversation_cache.ConfigUtil')
def test_get_conversations_to_enrich(mock_lp_utils):
    cache = ConversationCache()
    mock_lock = MagicMock()
    mock_gen_rlock = MagicMock()
    mock_gen_rlock.__enter__.return_value = mock_lock
    mock_gen_rlock.__exit__.return_value = False
    cache._lock.gen_rlock = mock_gen_rlock
    mock_open_conversations = {
        'conv1': MagicMock(),
        'conv2': MagicMock()
    }
    mock_closed_conversations = {
        'conv3': MagicMock(need_analyze=True),
        'conv4': MagicMock(need_analyze=False)
    }
    cache.open_conversations = mock_open_conversations
    cache.closed_conversations = mock_closed_conversations
    mock_messages = {
        'conv1': [MagicMock()],
        'conv2': [MagicMock()],
        'conv3': [MagicMock()],
        'conv4': [MagicMock()]
    }
    cache.messages = mock_messages
    result = cache.get_conversations_to_enrich()
    assert 'conv1' in result
    assert 'conv2' in result
    assert 'conv3' in result
    assert 'conv4' not in result
    assert result['conv1'] == mock_messages['conv1']
    assert result['conv2'] == mock_messages['conv2']
    assert result['conv3'] == mock_messages['conv3']

# Test for getting open conversations
@patch('server_project.objects.conversation_cache.ConfigUtil')
def test_get_open_conversations(mock_config_util):
    cache = ConversationCache()
    mock_open_conversations = {
        'conv1': MagicMock(),
        'conv2': MagicMock()
    }
    cache.open_conversations = mock_open_conversations
    result = cache.get_open_conversations()
    assert result == mock_open_conversations
    assert 'conv1' in result
    assert 'conv2' in result
    assert isinstance(result['conv1'], MagicMock)
    assert isinstance(result['conv2'], MagicMock)


#Test for getting enrich conversation
@patch('server_project.objects.conversation_cache.ConfigUtil')
def test_enrich_conversation(mock_config_util):
    cache = ConversationCache()
    mock_lock = MagicMock()
    cache._lock.gen_wlock = MagicMock()
    cache._lock.gen_wlock.return_value.__enter__.return_value = mock_lock
    cache._lock.gen_wlock.return_value.__exit__.return_value = False
    mock_open_conv_record = MagicMock()
    mock_closed_conv_record = MagicMock()
    cache.open_conversations = {'open_conv': mock_open_conv_record}
    cache.closed_conversations = {'closed_conv': mock_closed_conv_record}
    conv_id_open = 'open_conv'
    conv_id_closed = 'closed_conv'
    conv_id_nonexistent = 'nonexistent_conv'
    json_str = '{"key1": "value1", "key2": "value2"}'
    last_message_id = 'msg123'
    cache.enrich_conversation(conv_id_open, json_str, last_message_id)
    mock_open_conv_record.update_field.assert_any_call('key1', 'value1')
    mock_open_conv_record.update_field.assert_any_call('key2', 'value2')
    mock_open_conv_record.update_field.assert_any_call('last_effected_message_id', last_message_id)
    assert cache.open_conversations[conv_id_open] == mock_open_conv_record
    cache.enrich_conversation(conv_id_closed, json_str, last_message_id)
    mock_closed_conv_record.update_field.assert_any_call('key1', 'value1')
    mock_closed_conv_record.update_field.assert_any_call('key2', 'value2')
    mock_closed_conv_record.update_field.assert_any_call('last_effected_message_id', last_message_id)
    mock_closed_conv_record.update_field.assert_any_call('need_analyze', False)
    assert cache.closed_conversations[conv_id_closed] == mock_closed_conv_record
    cache.enrich_conversation(conv_id_nonexistent, json_str, last_message_id)
    assert conv_id_nonexistent not in cache.open_conversations
    assert conv_id_nonexistent not in cache.closed_conversations
    invalid_json_str = '{"key1": "value1", "key2":'
    with patch('logging.error') as mock_logging_error:
        cache.enrich_conversation(conv_id_open, invalid_json_str, last_message_id)
        mock_logging_error.assert_called_with("Error decoding JSON: Expecting value: line 1 column 27 (char 26)")

# Testing for log data
@patch('server_project.objects.conversation_cache.time.sleep', return_value=None)
@patch('server_project.objects.conversation_cache.ConfigUtil')
@patch('server_project.objects.conversation_cache.ConversationCache._start_cleanup_thread')
@patch('server_project.objects.conversation_cache.ConversationCache._start_log_thread')
@patch('server_project.objects.conversation_cache.rwlock.RWLockFair')
def test_log_data(
        mock_rwlock, mock_start_log_thread, mock_start_cleanup_thread, mock_config_util, mock_sleep
):
    mock_config = MagicMock()
    mock_config.get_config_attribute.side_effect = lambda key: {"logCacheInterval": 1}[key]
    mock_config_util.return_value = mock_config
    mock_lock = MagicMock()
    mock_rwlock.return_value.gen_rlock.return_value.__enter__.return_value = mock_lock
    mock_rwlock.return_value.gen_rlock.return_value.__exit__.return_value = False
    cache = ConversationCache()
    counter = {"iterations": 0}

    def stop_after_two_iterations(*args, **kwargs):
        if counter["iterations"] >= 2:
            raise KeyboardInterrupt
        counter["iterations"] += 1

    with patch.object(cache, 'log_summary_line') as mock_log_summary, \
            patch.object(cache, 'log_conversation_info') as mock_log_info:
        with patch('logging.debug'), patch('logging.error'):
            mock_sleep.side_effect = stop_after_two_iterations
            try:
                cache.log_data()
            except KeyboardInterrupt:
                pass
            expected_path = f"logs/cache_log_{date.today().strftime('%m_%d_%y')}.xlsx"
            assert mock_log_summary.call_count == 2
            assert mock_log_info.call_count == 2
            assert mock_log_summary.call_args_list == [call(expected_path), call(expected_path)]
            assert mock_log_info.call_args_list == [call(expected_path), call(expected_path)]


#Tests for DR Cache files
@patch('server_project.objects.conversation_cache.ConfigUtil')
@patch('openpyxl.workbook.Workbook')
@patch('os.rename')
def test_DR_cache_file(mock_rename, mock_workbook, mock_config_util):
    mock_file_path = "test_file.xlsx"
    mock_new_file_path = f"{mock_file_path}_{datetime.now().strftime('%Y%m%d%H%M%S')}.bak"
    mock_wb = MagicMock(spec=Workbook)
    mock_workbook.return_value = mock_wb
    mock_rename.return_value = None
    cache = ConversationCache()
    result = cache.DR_cache_file(mock_file_path)
    assert isinstance(result, Workbook)
    mock_rename.assert_called_once_with(mock_file_path, mock_new_file_path)


@patch('server_project.objects.conversation_cache.ConfigUtil')
@patch('os.rename')
@patch('openpyxl.workbook.Workbook')
def test_DR_cache_file_file_not_found(mock_workbook, mock_rename, mock_config_util):
    mock_file_path = "test_file.xlsx"
    mock_wb = MagicMock(spec=Workbook)
    mock_workbook.return_value = mock_wb
    mock_rename.side_effect = FileNotFoundError
    cache = ConversationCache()
    result = cache.DR_cache_file(mock_file_path)
    mock_rename.assert_called_once_with(mock_file_path,
                                        f"{mock_file_path}_{datetime.now().strftime('%Y%m%d%H%M%S')}.bak")
    assert isinstance(result, Workbook)


@patch('server_project.objects.conversation_cache.ConfigUtil')
@patch('os.rename')
@patch('openpyxl.workbook.Workbook')
def test_DR_cache_file_rename_error(mock_workbook, mock_rename, mock_config_util):
    mock_file_path = "test_file.xlsx"
    mock_wb = MagicMock(spec=Workbook)
    mock_workbook.return_value = mock_wb
    mock_rename.side_effect = Exception("Some error")
    cache = ConversationCache()
    result = cache.DR_cache_file(mock_file_path)
    mock_rename.assert_called_once_with(mock_file_path,
                                        f"{mock_file_path}_{datetime.now().strftime('%Y%m%d%H%M%S')}.bak")
    assert isinstance(result, Workbook)


if __name__ == '__main__':
    pytest.main()
