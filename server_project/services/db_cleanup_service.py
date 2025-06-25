import logging
import threading
import time
from datetime import datetime, timedelta
from DataBase.database_helper import db # SQLAlchemy instance from DataBaseHelper
from dao_object.conversation_prediction_object import ConversationPredictionDAO

# Configuration for the cleanup task
CLEANUP_INTERVAL_SECONDS = 24 * 60 * 60  # 24 hours
RECORDS_OLDER_THAN_WEEKS = 2

def delete_old_conversation_predictions(app_context_source=None):
    """
    Deletes records from ConversationPredictionDAO table that are older than
    RECORDS_OLDER_THAN_WEEKS.
    Requires an application context to perform database operations.
    app_context_source: Typically the Flask app or db.app if available globally and configured.
    """
    if app_context_source is None:
        # This assumes 'db.app' is the configured Flask app instance or a proxy that provides context
        # This might need adjustment based on how your Flask app is structured and db is initialized
        logging.error("DB Cleanup: Application context source not available. Trying get from DB")

        app_context_source = db.app 

    if app_context_source is None:
        logging.error("DB Cleanup: Application context source not available. Cannot perform cleanup.")
        return 0

    try:
        with app_context_source.app_context():
            cutoff_date = datetime.utcnow() - timedelta(weeks=RECORDS_OLDER_THAN_WEEKS)
            
            logging.info(f"DB Cleanup: Starting cleanup of records older than {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')} UTC from 'conversation_predictions' table.")
            
            num_deleted = db.session.query(ConversationPredictionDAO).filter(
                ConversationPredictionDAO.created_at < cutoff_date
            ).delete(synchronize_session=False)
            
            db.session.commit()
            
            logging.info(f"DB Cleanup: Successfully deleted {num_deleted} old records from 'conversation_predictions'.")
            return num_deleted
    except Exception as e:
        # Ensure rollback happens within an app context if the session is tied to it.
        # If an error occurred before or during context acquisition, this might also fail
        # or db.session might not be valid.
        try:
            with app_context_source.app_context():
                db.session.rollback()
        except Exception as rollback_e:
            logging.error(f"DB Cleanup: Error during rollback after another error: {rollback_e}")
        logging.error(f"DB Cleanup: Error during database cleanup: {e}")
        return 0

def _daily_cleanup_task(app_context_source=None):
    """
    Internal function that runs in a loop to perform daily cleanup.
    """
    logging.info("Daily DB cleanup thread started.")
    while True:
        try:
            # Pass the app_context_source to the cleanup function
            delete_old_conversation_predictions(app_context_source)
        except Exception as e:
            logging.error(f"DB Cleanup: Unhandled exception in _daily_cleanup_task loop: {e}")
        
        logging.info(f"DB Cleanup: Task finished. Next run in {CLEANUP_INTERVAL_SECONDS / 3600:.2f} hours.")
        time.sleep(CLEANUP_INTERVAL_SECONDS)

_cleanup_thread = None
_cleanup_thread_lock = threading.Lock()
_flask_app_for_cleanup = None # Module-level variable to store the Flask app instance

def set_flask_app_for_cleanup(app):
    """Call this once during app initialization to provide the Flask app context for the cleanup thread."""
    global _flask_app_for_cleanup
    _flask_app_for_cleanup = app

def start_daily_cleanup_scheduler():
    """
    Starts the daily database cleanup scheduler in a separate thread.
    Ensures only one scheduler thread is running.
    The Flask app instance must be set via set_flask_app_for_cleanup() before calling this.
    """
    global _cleanup_thread
    if _flask_app_for_cleanup is None:
        logging.error("DB Cleanup: Flask app not set for cleanup scheduler. Call set_flask_app_for_cleanup() first.")
        return

    with _cleanup_thread_lock:
        if _cleanup_thread is None or not _cleanup_thread.is_alive():
            # Pass the Flask app to the target function so it can manage context
            _cleanup_thread = threading.Thread(target=_daily_cleanup_task, args=(_flask_app_for_cleanup,), daemon=True)
            _cleanup_thread.start()
            logging.info("Daily database cleanup scheduler started.")
        else:
            logging.info("Daily database cleanup scheduler is already running.")

# To stop the thread (e.g., during application shutdown or tests), you might need a mechanism.
# For a daemon thread, it will exit when the main program exits.
# If explicit stop is needed:
# _stop_event = threading.Event()
# And in _daily_cleanup_task: check _stop_event.is_set() in the loop and time.sleep(_stop_event.wait(timeout))
# And a function stop_daily_cleanup_scheduler() would call _stop_event.set() and _cleanup_thread.join() 