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

def delete_all_tables():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(buffered = True)
    try:
      cursor.execute("DELETE FROM ticket_types")
      cursor.execute("DELETE FROM events")
      cursor.execute("DELETE FROM locations")
      conn.commit()
    
    except mysql.connector.Error as error:
      print("Failed to delete records from table {}".format(error))
    
    finally:
      cursor.close()
      conn.close()