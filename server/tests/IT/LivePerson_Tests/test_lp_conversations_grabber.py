import pytest
from unittest.mock import patch, MagicMock
from lp_api_manager.lp_conversations_grabber import LpConversationGrabber
from datetime import datetime

# Test for LpConversationGrabber initialization
@patch('lp_api_manager.lp_conversations_grabber.LpUtils')
def test_lp_conversation_grabber_init(mock_lp_utils):
    mock_lp_utils.return_value.bearer_token = 'dummy_token'
    mock_lp_utils.return_value.messageHistDomain = 'dummy_domain'
    mock_lp_utils.return_value.account_id = 'dummy_account'

    grabber = LpConversationGrabber()
    assert isinstance(grabber, LpConversationGrabber)
    assert grabber.bearer_token == 'dummy_token'
    assert grabber.message_hist_domain == 'dummy_domain'
    assert grabber.account_id == 'dummy_account'
    assert grabber.last_grab_time <= int(datetime.now().timestamp() * 1000)

if __name__ == '__main__':
    pytest.main()