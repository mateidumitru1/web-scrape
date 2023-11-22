import mysql.connector
import uuid

db_config = {
  "host": 'localhost',
  "user": 'root',
  "password": 'pass',
  "database": 'project'
}



def insert_data_into_table(table_name, data):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(buffered = True)

    try:
      if table_name == 'events':
        if len(data['description']) > 11000:
          data['short_description'] += data['description'][:4500 - len(data['short_description']) - 1]
          data['description'] = data['description'][:4500]

      where_clause = ' AND '.join(f"{key} = %s" for key in data.keys())

      select_sql = f"SELECT id FROM {table_name} WHERE {where_clause}"
      cursor.execute(select_sql, tuple(data.values()))
      existing_record = cursor.fetchone()

      if existing_record:
        return existing_record[0]

      data['id'] = uuid.uuid4().bytes

      columns = ', '.join(data.keys())
      placeholders = ', '.join(['%s'] * len(data))

      insert_sql = "INSERT INTO %s (%s) VALUES (%s)" % (table_name, columns, placeholders)

      cursor.execute(insert_sql, list(data.values()))
      conn.commit()

      return data['id']

    except mysql.connector.Error as error:
      print("Failed to insert record into table {}".format(error))

    finally:
      cursor.close()
      conn.close()

