from requests import get
from bs4 import BeautifulSoup
from PIL import Image
import json
import io
import re
from upload_image import upload_blob
from insert_to_database import insert_data_into_table, delete_all_tables

iabilet_url = 'https://www.iabilet.ro'

urls = [
            iabilet_url + '/bilete-sala-palatului-venue-876/', 
            iabilet_url + '/bilete-hard-rock-cafe-venue-560/',
            iabilet_url + '/bilete-arenele-romane-venue-25/',
            iabilet_url + '/bilete-romexpo-venue-1461/',
            iabilet_url + '/bilete-club-fabrica-venue-264/',
            iabilet_url + '/bilete-quantic-venue-1705/',
            iabilet_url + '/bilete-expirat-halele-carol-venue-1845/',
            iabilet_url + '/bilete-club-99-venue-1409/',
            iabilet_url + '/bilete-the-fool-venue-3205/'
        ]

events = []
locations = []
tickets = []

for url in urls:
    response = get(url)
    html_soup = BeautifulSoup(response.text, 'html.parser')

    location_soup = html_soup.find('div', class_ = 'wrap likable-image-container').find('h1')
    location = location_soup.text.strip()
    location = location.replace('Bilete', '').strip()

    address = html_soup.find('span', class_ = 'address').text.strip()
    address = address.replace('\n', ', ').strip()

    location_image = html_soup.find('div', class_ = 'wrap likable-image-container').find('img')
    location_image_response = get(location_image['src'], stream=True, headers={})
    location_image_data = location_image_response.content
    location_image_to_save = Image.open(io.BytesIO(location_image_data))
    rgb_location_image = location_image_to_save.convert('RGB')

    chars_to_remove = r'\\/:*?"<>|'
    name_location_image = re.sub('[' + re.escape(chars_to_remove) + ']', '', location)

    rgb_location_image.save('location-images/' + name_location_image.strip() + '.jpg', 'JPEG')

    locations.append({
        'name': location,
        'address': address
    })

    event_list = html_soup.find_all('div', class_ = 'event-list-venue-item')

    for event in event_list:
        tickets = []

        event_url = iabilet_url + event.find('a')['href']
        event_response = get(event_url)

        event_soup = BeautifulSoup(event_response.text, 'html.parser')

        main_content = event_soup.find('div', class_ = 'col-xs-7')

        title = main_content.find('h1').text.strip()
        date = ''
        try:
            date = main_content.find('meta')['content']
        except:
            print('No date found for event: ' + title)

        short_description = main_content.find('div', class_ = 'short-desc').text.strip()
        short_description = short_description.replace('Mai multe detalii', '')

        description = main_content.find('div', class_ = 'event-detail').text.strip()

        image = event.find('img')
        image_response = get(image['src'], stream=True, headers={})
        image_data = image_response.content
        image_to_save = Image.open(io.BytesIO(image_data))
        rgb_image = image_to_save.convert('RGB')

        chars_to_remove = r'\\/:*?"<>|'
        title_image = re.sub('[' + re.escape(chars_to_remove) + ']', '', title)

        rgb_image.save('event-images/' + title_image.strip() + '.jpg', 'JPEG')

        ticket_soup = BeautifulSoup(event_response.text, 'html.parser')

        ticket_table = None
        try:
            ticket_table = ticket_soup.find('div', class_ = 'table-flex form-zone')

            ticket_types = ticket_table.find_all('div', class_ = 'table-flex-row')
            ticket_types.pop(ticket_types.__len__() - 1)

            for ticket_type in ticket_types:
                ticket_type_name = ticket_type.find('div', class_='ticket-categ').find('div', class_='ticket-info').find('span').get_text(strip=True)
                
                ticket_type_price_div = ticket_type.find('div', class_='ticket-price')
                ticket_type_price = None
                
                if ticket_type_price_div:
                    current_price_span = ticket_type_price_div.find('span', class_=lambda x: x != 'old-price')
                    
                    if not current_price_span:
                        current_price_anchor = ticket_type_price_div.find('a')
                    
                    if current_price_span:
                        ticket_type_price = current_price_span.get_text(strip=True, separator='.')
                    elif current_price_anchor:
                        ticket_type_price = current_price_anchor.get_text(strip=True, separator='.')
                tickets.append({
                    'name': ticket_type_name,
                    'price': float(ticket_type_price[:-4]),
                    'quantity': 100
                })
            
        except:
            print('No tickets found for event: ' + event_url)

        events.append({
                'title': title_image.strip(),
                'date': date,
                'short_description': short_description.strip(),
                'description': description.strip(),
                'location': location.strip(),
                'ticket_types': tickets
        })

delete_all_tables()

for location in locations:
    location['image_url'] = upload_blob('location-images/' + location['name'] + '.jpg', 'location-images/' + location['name'] + '.jpg')
    location['id'] = insert_data_into_table('locations', location)

location_map = {
    location['name']: location['id'] for location in locations
}


for event in events:
    event['image_url'] = upload_blob('event-images/' + event['title'] + '.jpg', 'event-images/' + event['title'] + '.jpg')

    event['location_id'] = location_map[event['location']]

    if event['date'] == '':
        event.pop('date')
    event.pop('location')

    event_to_add = {
        'title': event['title'],
        'short_description': event['short_description'],
        'description': event['description'],
        'image_url': event['image_url'],
        'location_id': event['location_id']
    }

    event_id = insert_data_into_table('events', event_to_add)

    for ticket_type in event['ticket_types']:
        ticket_type['event_id'] = event_id
        insert_data_into_table('ticket_types', ticket_type)

