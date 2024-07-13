# Populate Database tables with dummy data

This folder contains SQL scripts that populate the database tables with dummy data.

It will create a virtual environment and install the necessary dependencies to run the script.

The db credentials and connection details are stored in the python script, change them if needed.

# Requirements
1. Python 3.12 or higher

## How to use

1. Ensure you have the database running on your machine.
2. Ensure you have the database schema and tables created.
3. Run the populate_db.sh script on the root of this folder.

````bash
./populate_db.sh
````

4. The script will try to populate the database with dummy data.
5. If the script fails, psycopg2 will raise an error with the reason for the failure.gi