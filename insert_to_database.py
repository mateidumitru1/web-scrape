import mysql.connector
import uuid

db_config = {
  "host": 'localhost',
  "user": 'root',
  "password": 'pass',
  "database": 'project'
}

def insert_location_into_table(location):
  conn = mysql.connector.connect(**db_config)
  cursor = conn.cursor(buffered = True)

  try:
    select_sql = "SELECT id FROM locations WHERE name = %s"
    cursor.execute(select_sql, (location['name'],))
    existing_record = cursor.fetchone()

    if existing_record:
      return existing_record[0]
    
    location['id'] = uuid.uuid4().bytes

    insert_sql = "INSERT INTO locations (id, name, address, image_url) VALUES (%s, %s, %s, %s)"
    cursor.execute(insert_sql, (location['id'], location['name'], location['address'], location['image_url']))
  
    conn.commit()

    return location['id']
  
  except mysql.connector.Error as error:
    print("Failed to insert record into table {}".format(error))

  finally:
    cursor.close()
    conn.close()

def insert_event_into_table(event):
  conn = mysql.connector.connect(**db_config)
  cursor = conn.cursor(buffered = True)

  try:
    if len(event['description']) > 11000:
      event['short_description'] += event['description'][:4500 - len(event['short_description']) - 1]
      event['description'] = event['description'][:4500]

    select_sql = "SELECT id FROM events WHERE title = %s AND date = %s AND short_description = %s AND description = %s"
    cursor.execute(select_sql, (event['title'], event['date'], event['short_description'], event['description']))
    existing_record = cursor.fetchone()

    if existing_record:
      return existing_record[0]
    
    event['id'] = uuid.uuid4().bytes

    insert_sql = "INSERT INTO events (id, title, date, short_description, description, image_url, location_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(insert_sql, (event['id'], event['title'], event['date'], event['short_description'], event['description'], event['image_url'], event['location_id']))
  
    conn.commit()

    return event['id']
  
  except mysql.connector.Error as error:
    print("Failed to insert record into table {}".format(error))

  finally:
    cursor.close()
    conn.close()

def insert_artist_into_table(artist):
  conn = mysql.connector.connect(**db_config)
  cursor = conn.cursor(buffered = True)

  try:
    select_sql = "SELECT id FROM artists WHERE name = %s"
    cursor.execute(select_sql, (artist,))
    existing_record = cursor.fetchone()

    if existing_record:
      return existing_record[0]
    
    artist_id = uuid.uuid4().bytes

    insert_sql = "INSERT INTO artists (id, name) VALUES (%s, %s)"
    cursor.execute(insert_sql, (artist_id, artist))
  
    conn.commit()

    return artist_id
  
  except mysql.connector.Error as error:
    print("Failed to insert record into table {}".format(error))

  finally:
    cursor.close()
    conn.close()

def insert_event_artist_into_table(event_id, artist_id):
  conn = mysql.connector.connect(**db_config)
  cursor = conn.cursor(buffered = True)

  try:
    select_sql = "SELECT * FROM event_artists WHERE event_id = %s AND artist_id = %s"
    cursor.execute(select_sql, (event_id, artist_id))
    existing_record = cursor.fetchone()

    if existing_record:
      return existing_record[0]
    
    insert_sql = "INSERT INTO event_artists (event_id, artist_id) VALUES (%s, %s)"
    cursor.execute(insert_sql, (event_id, artist_id))
  
    conn.commit()

    return artist_id
  
  except mysql.connector.Error as error:
    print("Failed to insert record into table {}".format(error))

  finally:
    cursor.close()
    conn.close()

def insert_ticket_type_into_table(ticket_type):
  conn = mysql.connector.connect(**db_config)
  cursor = conn.cursor(buffered = True)

  try:
    select_sql = "SELECT id FROM ticket_types WHERE event_id = %s AND name = %s"
    cursor.execute(select_sql, (ticket_type['event_id'], ticket_type['name']))
    existing_record = cursor.fetchone()

    if existing_record:
      return existing_record[0]
    
    ticket_type_id = uuid.uuid4().bytes

    insert_sql = "INSERT INTO ticket_types (id, event_id, name, price) VALUES (%s, %s, %s, %s)"
    cursor.execute(insert_sql, (ticket_type_id, ticket_type['event_id'], ticket_type['name'], ticket_type['price']))
  
    conn.commit()

    return ticket_type_id
  
  except mysql.connector.Error as error:
    print("Failed to insert record into table {}".format(error))

  finally:
    cursor.close()
    conn.close()