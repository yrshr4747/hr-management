import oracledb

# Step 1: Try connecting to Oracle
try:
    connection = oracledb.connect(
        user="system",
        password="123Cs0076",
        dsn="localhost:1521/XEPDB1"  # or "localhost:1521/XE" depending on your container
    )
    print("✅ Successfully connected to Oracle Database!")

    # Step 2: Run a simple query
    cursor = connection.cursor()
    cursor.execute("SELECT sysdate FROM dual")
    result = cursor.fetchone()
    print("Current date/time in Oracle:", result[0])

except Exception as e:
    print("❌ Connection failed:")
    print(e)

finally:
    try:
        cursor.close()
        connection.close()
    except:
        pass