from flask import current_app
from db import db  # Replace 'your_project_name' with the actual name of your project

class DatabaseHelper:
    @staticmethod
    def add_instance(instance):
        """Add and commit an instance to the database."""
        #print("starting to add instance")
        with current_app.app_context():
            #print("inside with current_app")
            db.session.add(instance)
            try:
                db.session.commit()
                #print(f"Successfully added: {instance}")
            except Exception as e:
                db.session.rollback()
                #print(f"Error committing to the database: {e}")
        #print("done with current_app")


    @staticmethod
    def update_instance():
        """Commit updates to the database."""
        with current_app.app_context():
            try:
                db.session.commit()
                #print("Update committed successfully!")
            except Exception as e:
                db.session.rollback()
                #print(f"Error committing update to the database: {e}")

    @staticmethod
    def delete_instance(instance):
        """Delete an instance from the database."""
        with current_app.app_context():
            db.session.delete(instance)
            try:
                db.session.commit()
                #print(f"Successfully deleted: {instance}")
            except Exception as e:
                db.session.rollback()
                #print(f"Error deleting from the database: {e}")
