import unittest
from unittest.mock import patch, MagicMock, ANY
from datetime import datetime, timedelta
import logging

# Path to the module to test - adjust if your project structure is different
# This assumes 'server_project' is in your PYTHONPATH or tests are run from a level where it can be imported.
from services.db_cleanup_service import delete_old_conversation_predictions, RECORDS_OLDER_THAN_WEEKS
from dao_object.conversation_prediction_object import ConversationPredictionDAO # For type checking if needed

class TestDBCleanupService(unittest.TestCase):

    @patch('services.db_cleanup_service.db.session')
    @patch('services.db_cleanup_service.db.app') # Mock the source of app_context
    def test_delete_old_records_success(self, mock_db_app, mock_db_session):
        # --- Arrange ---
        # Mock app_context to be a context manager
        mock_app_context_manager = MagicMock()
        mock_db_app.app_context.return_value = mock_app_context_manager
        
        # Mock the query chain
        mock_query = MagicMock()
        mock_filtered_query = MagicMock()
        
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filtered_query
        mock_filtered_query.delete.return_value = 5 # Simulate 5 records deleted
        
        logging.disable(logging.CRITICAL) # Disable logging for cleaner test output

        # --- Act ---
        # Pass the mock_db_app as the app_context_source
        num_deleted = delete_old_conversation_predictions(app_context_source=mock_db_app)

        # --- Assert ---
        self.assertEqual(num_deleted, 5)
        mock_db_app.app_context.assert_called_once() # Check context was used
        mock_db_session.query.assert_called_once_with(ConversationPredictionDAO)
        
        # Check that filter was called. ANY is used for the cutoff_date as it's tricky to match exactly.
        # A more precise check would involve capturing the argument and verifying its range.
        mock_query.filter.assert_called_once_with(ANY) 
        # Example of how to check the filter condition more precisely:
        # args, _ = mock_query.filter.call_args
        # self.assertIsInstance(args[0].left, sqlalchemy.orm.attributes.InstrumentedAttribute) # LHS is DAO.created_at
        # self.assertEqual(args[0].operator.__name__, 'lt') # Operator is <
        # self.assertIsInstance(args[0].right.value, datetime) # RHS is a datetime object

        mock_filtered_query.delete.assert_called_once_with(synchronize_session=False)
        mock_db_session.commit.assert_called_once()
        mock_db_session.rollback.assert_not_called()
        
        logging.disable(logging.NOTSET) # Re-enable logging

    @patch('services.db_cleanup_service.db.session')
    @patch('services.db_cleanup_service.db.app')
    def test_delete_old_records_exception_during_delete(self, mock_db_app, mock_db_session):
        # --- Arrange ---
        mock_app_context_manager = MagicMock()
        mock_db_app.app_context.return_value = mock_app_context_manager
        
        mock_query = MagicMock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.side_effect = Exception("Simulated DB error during delete")
        
        logging.disable(logging.CRITICAL)

        # --- Act ---
        num_deleted = delete_old_conversation_predictions(app_context_source=mock_db_app)

        # --- Assert ---
        self.assertEqual(num_deleted, 0)
        mock_db_app.app_context.assert_called() # Called for operation and possibly for rollback
        mock_db_session.query.assert_called_once_with(ConversationPredictionDAO)
        mock_query.filter.assert_called_once()
        mock_db_session.commit.assert_not_called()
        mock_db_session.rollback.assert_called_once() # Rollback should be called
        
        logging.disable(logging.NOTSET)

    @patch('services.db_cleanup_service.db.session')
    @patch('services.db_cleanup_service.db.app')
    def test_delete_old_records_no_app_context_source(self, mock_db_app, mock_db_session):
        # --- Arrange ---
        # Simulate db.app being None if not explicitly passed and not found
        # This requires the db_cleanup_service.db.app to be patchable or the logic to allow None
        # For this test, we explicitly pass None as app_context_source
        logging.disable(logging.CRITICAL)

        # --- Act ---
        # To truly test the internal fallback `app_context_source = db.app` being None,
        # you'd need to patch `services.db_cleanup_service.db.app` itself if `delete_old_conversation_predictions`
        # is called with app_context_source=None by default in the scheduler.
        # Here, we directly test the path where app_context_source results in None.
        with patch('services.db_cleanup_service.db.app', None): # Patch db.app to be None for this test
             num_deleted = delete_old_conversation_predictions(app_context_source=None)

        # --- Assert ---
        self.assertEqual(num_deleted, 0)
        mock_db_session.query.assert_not_called()
        mock_db_session.commit.assert_not_called()
        mock_db_session.rollback.assert_not_called()
        # Logging for "Application context source not available" should have occurred.

        logging.disable(logging.NOTSET)

if __name__ == '__main__':
    unittest.main() 