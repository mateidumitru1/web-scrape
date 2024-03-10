from setup import setup

setup()

from requests import get
from bs4 import BeautifulSoup
from PIL import Image
from unidecode import unidecode
import json
import io
import re
from format_artist_list import remove_artists
from upload_image import upload_blob
from insert_to_database import *
from spotify import get_artist_details


iabilet_url = 'https://www.iabilet.ro'

locations_urls = [
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

artists_url = 'https://www.iabilet.ro/artist'

all_artists = []

events = []
locations = []
tickets = []

for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
    response = get(artists_url + '/' + char)
    html_soup = BeautifulSoup(response.text, 'html.parser')
    
    artists_list_element = html_soup.find('ul', class_ = 'artist-list')
    artist_list = artists_list_element.find_all('li')
    for item in artist_list:
        artist = item.find('a')
        if artist:
            artist = unidecode(artist.text)
            all_artists.append(artist)

all_artists = remove_artists(all_artists)

chars_to_remove = r'\\/:*?"<>|'

for url in locations_urls:
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

    name_location_image = re.sub('[' + re.escape(chars_to_remove) + ']', '', location)

    rgb_location_image.save('location-images/' + name_location_image.strip() + '.jpg', 'JPEG')

    locations.append({
        'name': location,
        'address': address
    })

    event_list = html_soup.find_all('div', class_ = 'event-list-venue-item')

    for event in event_list:
        tickets = []

        try:
            event_url = iabilet_url + event.find('a')['href']
            event_response = get(event_url)

            event_soup = BeautifulSoup(event_response.text, 'html.parser')

            main_content = event_soup.find('div', class_ = 'col-xs-7')

            if not main_content:
                main_content = event_soup.find('div', class_ = 'col-xs-9')


            title_element = main_content.find('h1')

            title_element_text = title_element.text.strip()
        
            date = main_content.find('meta')['content']
     

            short_description = main_content.find('div', class_ = 'short-desc').text.strip()
            short_description = short_description.replace('Mai multe detalii', '')

            description = main_content.find('div', class_ = 'event-detail').text.strip()

            try:
                image = event.find('img')
                image_response = get(image['src'], stream=True, headers={})
                image_data = image_response.content
                image_to_save = Image.open(io.BytesIO(image_data))
                rgb_image = image_to_save.convert('RGB')

                chars_to_remove = r'\\/:*?"<>|'
                title = re.sub('[' + re.escape(chars_to_remove) + ']', '', title_element_text)

                rgb_image.save('event-images/' + title.strip() + '.jpg', 'JPEG')
            except:
                print('No image found for event: ' + title_element_text)

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

            title_lower = ' ' + title.lower() + ' '
            title_lower.replace(',', ' ')
            title_lower.replace('\'', ' ')
            title_lower.replace('\u2019', ' ')
            title_lower.replace(' - ', ' ')
            title_lower = unidecode(title_lower)

            found_artists = set()

            for artist in all_artists:
                artist_lower = ' ' + artist.lower() + ' '

                if artist_lower in title_lower:
                    longer_versions = [other_artist for other_artist in all_artists if other_artist.lower().startswith(artist_lower.strip()) and len(other_artist) > len(artist)]
                    if not longer_versions:
                        found_artists.add(artist)
                        title_lower = title_lower.replace(artist_lower, ' ')

                    else:
                        for longer_artist in longer_versions:
                            if longer_artist.lower() in title_lower:
                                found_artists.add(longer_artist)
                                title_lower = title_lower.replace(longer_artist.lower(), ' ')
                                break

                        found_artists.add(artist)
                        title_lower = title_lower.replace(artist_lower, ' ')

            if not found_artists:
                print(f"No artist found in event title: {title}")


            events.append({
                    'title': title.strip(),
                    'date': date,
                    'short_description': short_description.strip(),
                    'description': description.strip(),
                    'location': location.strip(),
                    'ticket_types': tickets,
                    'artists': list(found_artists)
            })

        except Exception as e:
            print(e)
            pass


for location in locations:
    location['image_url'] = upload_blob('location-images/' + location['name'] + '.jpg', 'location-images/' + location['name'] + '.jpg')
    location['id'] = insert_location_into_table(location)

location_map = {
    location['name']: location['id'] for location in locations
}


for event in events:
    try:
        event['image_url'] = upload_blob('event-images/' + event['title'] + '.jpg', 'event-images/' + event['title'] + '.jpg')
    except:
        print('No image found for event: ' + event['title'])

    event['location_id'] = location_map[event['location']]

    if event['date'] == '':
        event.pop('date')
    event_location = event.pop('location')
    ticket_types = event.pop('ticket_types')

    event_to_add = event

    event_id = insert_event_into_table(event_to_add)

    for artist in event['artists']:
        if event_location == 'The Fool' or event_location == 'Club 99':
            artist_details = {
                'name': artist,
                'image_url': '',
                'genre': ['stand up comedy']
            }
        else:
            artist_details = get_artist_details(artist)

            if artist_details['image_url'] != '':
                artist_details['image_url'] = upload_blob(artist_details['image_url'], 'artist-images/' + artist + '.jpg')

        artist_id = insert_artist_into_table(artist_details)
        insert_event_artist_into_table(event_id, artist_id)

        for genre in artist_details['genre']:
            genre_id = insert_genre_into_table(genre)
            insert_genre_artist_into_table(genre_id, artist_id)

    for ticket_type in ticket_types:
        ticket_type['event_id'] = event_id
        insert_ticket_type_into_table(ticket_type)

