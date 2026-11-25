"""
Student Scores CRUD Pipeline
CSV -> Pandas -> SQLAlchemy -> MySQL -> Pandas (read) -> mysql.connector (update/delete)
"""

import logging
import os
import sys

import mysql.connector
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# ---------- Settings (change these) ----------
CSV_FILE = "student_scores.csv"
TABLE_NAME = "student_scores"

DB_CONFIG = {
    "user": "root",
    "password": os.environ.get("DB_PASSWORD", "YOUR PASSWORD"),  
    "host": "localhost",
    "database": "school",
    "port": 3306,
}

UPDATE_ID, NEW_MATH_SCORE = 2, 90   # student whose math_score will be updated
DELETE_ID = 3                       # student to delete (must exist in your CSV)

EXPECTED_COLUMNS = ["id", "name", "math_score", "english_score", "science_score"]

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("pipeline.log")],
)
log = logging.getLogger(__name__)


# ---------- Helpers ----------
def get_engine():
    url = URL.create(
        "mysql+mysqlconnector",
        username=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        database=DB_CONFIG["database"],
    )
    return create_engine(url)


def load_csv(path):
    """Read the CSV and validate it."""
    df = pd.read_csv(path)
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"CSV is missing columns: {missing}")
    if df["id"].duplicated().any():
        raise ValueError("CSV has duplicate ids")
    if df[EXPECTED_COLUMNS].isnull().any().any():
        log.warning("CSV contains empty values")
    log.info("Read %d rows from %s", len(df), path)
    return df


# ---------- CREATE ----------
def create_and_insert(engine, df):
    with engine.begin() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {TABLE_NAME}"))  # makes script re-runnable
        conn.execute(text(f"""
            CREATE TABLE {TABLE_NAME} (
                id INT PRIMARY KEY,
                name VARCHAR(100),
                math_score INT,
                english_score INT,
                science_score INT
            )
        """))
    df[EXPECTED_COLUMNS].to_sql(TABLE_NAME, engine, if_exists="append", index=False)
    log.info("Inserted %d rows into %s", len(df), TABLE_NAME)


# ---------- READ ----------
def read_table(engine):
    return pd.read_sql(f"SELECT * FROM {TABLE_NAME}", engine)


# ---------- UPDATE ----------
def update_math_score(conn, student_id, new_score):
    cur = conn.cursor()
    cur.execute(
        f"UPDATE {TABLE_NAME} SET math_score = %s WHERE id = %s",
        (new_score, student_id),
    )
    conn.commit()
    log.info("Updated %d row(s) (id=%s, math_score=%s)", cur.rowcount, student_id, new_score)
    cur.close()


# ---------- DELETE ----------
def delete_student(conn, student_id):
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {TABLE_NAME} WHERE id = %s", (student_id,))
    conn.commit()
    if cur.rowcount == 0:
        log.warning("No row found with id=%s, nothing deleted", student_id)
    else:
        log.info("Deleted %d row(s) (id=%s)", cur.rowcount, student_id)
    cur.close()


# ---------- Main ----------
def main():
    conn = None
    try:
        engine = get_engine()

        df = load_csv(CSV_FILE)
        create_and_insert(engine, df)

        after_insert = read_table(engine)
        print("\nAfter insert:\n", after_insert)
        log.info("Rows in CSV: %d | Rows in DB: %d", len(df), len(after_insert))

        conn = mysql.connector.connect(**DB_CONFIG)
        update_math_score(conn, UPDATE_ID, NEW_MATH_SCORE)
        delete_student(conn, DELETE_ID)

        print("\nFinal data:\n", read_table(engine))
        log.info("Pipeline finished successfully")

    except FileNotFoundError:
        log.error("CSV file '%s' not found. Put it in the same folder as pipeline.py", CSV_FILE)
        sys.exit(1)
    except mysql.connector.Error as e:
        log.error("MySQL error: %s", e)
        sys.exit(1)
    except Exception as e:
        log.error("Pipeline failed: %s", e)
        sys.exit(1)
    finally:
        if conn is not None and conn.is_connected():
            conn.close()
            log.info("Database connection closed")


if __name__ == "__main__":
    main()