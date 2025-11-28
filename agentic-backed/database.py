import os
import json
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from models.analysis_models import CallReportDB

# Load environment variables
load_dotenv()

class DatabaseManager:
    _instance = None
    _pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize_pool()
        return cls._instance

    def _initialize_pool(self):
        """Initialize the connection pool."""
        try:
            self._pool = psycopg2.pool.SimpleConnectionPool(
                1,  # minconn
                10, # maxconn
                user=os.getenv("user"),
                password=os.getenv("password"),
                host=os.getenv("host"),
                port=os.getenv("port"),
                dbname=os.getenv("dbname")
            )
            print("✅ Database connection pool created successfully.")
        except Exception as e:
            print(f"❌ Error creating database connection pool: {e}")
            self._pool = None

    def get_connection(self):
        """Get a connection from the pool."""
        if self._pool:
            return self._pool.getconn()
        else:
            # Try to re-initialize if pool is missing (e.g. startup failure)
            self._initialize_pool()
            if self._pool:
                return self._pool.getconn()
            raise Exception("Database connection pool is not initialized.")

    def return_connection(self, conn):
        """Return a connection to the pool."""
        if self._pool and conn:
            self._pool.putconn(conn)

    def close_all_connections(self):
        """Close all connections in the pool."""
        if self._pool:
            self._pool.closeall()
            print("Database connection pool closed.")

    def save_call_report(self, report_db: "CallReportDB") -> bool:
        """
        Save the call analysis report to the database.
        
        Args:
            report_db: CallReportDB model instance containing flattened data.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            insert_query = """
                INSERT INTO public.call_reports (
                    call_id,
                    call_duration_seconds,
                    stressed_detected,
                    sentiment_counts,
                    top_stressors,
                    common_blockers,
                    is_severe_case,
                    analysis_timestamp
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                RETURNING id;
            """
            
            cursor.execute(insert_query, (
                report_db.call_id,
                report_db.call_duration_seconds,
                report_db.stressed_detected,
                json.dumps(report_db.sentiment_counts),
                report_db.top_stressors,
                report_db.common_blockers,
                report_db.is_severe_case
            ))
            
            report_id = cursor.fetchone()[0]
            conn.commit()
            
            print(f"✅ Successfully saved report to database. ID: {report_id}")
            return True

        except Exception as e:
            print(f"❌ Failed to save report to database: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            self.return_connection(conn)

# Global instance
db_manager = DatabaseManager()

def save_call_report(data: "CallReportDB") -> bool:
    """Wrapper function to save call report using the singleton manager."""
    return db_manager.save_call_report(data)
