# Module Imports
import mariadb
import sys

# Connect to MariaDB Platform
db = None
try:
    db = mariadb.connect(
        user="root",
        password="",
        host="localhost",
        port=3306,
        database="database_tst"

    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)
