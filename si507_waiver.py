#################################
##### Name: Duanmu Mingliang
##### Uniqname: Duanmu Mingliang
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key


class NationalSite:
    def __init__(self, category, name, address, zipcode, phone):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone

    def info(self):
        return self.name+' ('+self.category+'): '+self.address+' ' + self.zipcode
    pass


def build_state_url_dict():
    url = 'https://www.nps.gov/index.htm'
    print('Fetching')
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    result = soup.find_all('ul', class_='dropdown-menu SearchBar-keywordSearch')[0].findChildren('a')
    dic = {res.text.lower(): 'https://www.nps.gov' + res['href'] for res in result}
    return dic
    pass
       

def get_site_instance(site_url):
    html = requests.get(site_url)
    soup = BeautifulSoup(html.text, 'html.parser')
    name = soup.find(class_='Hero-titleContainer clearfix').find_all('a')[0].text
    category = soup.find(class_='Hero-designation').text
    address = 'no address'
    zipcode = 'no zipcode'
    phone = 'no phone'
    if soup.find(class_='adr') is not None:
      address = soup.find(class_='adr').find('span', itemprop='addressLocality').text.strip() + ', '
      address += soup.find(class_='adr').find('span', itemprop='addressRegion').text
      zipcode = soup.find(class_='adr').find('span', itemprop='postalCode').text.strip()
    if soup.find(class_='tel') is not None:
        phone = soup.find(class_='tel').text.strip()
    return NationalSite(category, name, address, zipcode, phone)
    pass


def get_sites_for_state(state_url):
    html = requests.get(state_url)
    soup = BeautifulSoup(html.text, 'html.parser')
    sites = []
    for res in soup.find('ul', attrs={'id': 'list_parks'}).find_all(class_='clearfix'):
        information = get_site_instance('https://www.nps.gov' + res.find('a')['href'])
        sites.append(information)
    return sites
    pass


def get_nearby_places(site_object):
    url = 'http://www.mapquestapi.com/search/v2/radius?'
    key = 'key=' + secrets.API_KEY
    origin = 'origin=' + site_object.zipcode
    radius = 'radius=10'
    maxMatches = 'maxMatches=10'
    ambiguities = 'ambiguities=ignore'
    outFormat = 'outFormat=json'
    url += key + '&' + origin + '&' + radius + '&' + maxMatches + '&' + ambiguities + '&' + outFormat
    html = requests.get(url)
    return json.loads(html.text)
    pass
    

if __name__ == "__main__":
    state_list = []
    park_list = []
    states = build_state_url_dict()
    while True:
        print('Enter a state name (e.g. Michigan, michigan) or "exit"')
        url = input(': ')
        if url == 'exit':
            exit(0)
        elif url.lower() in states.keys():
            result = get_sites_for_state(states[url.lower()])
            for element in result:
                if url.lower() in state_list:
                    print('Using cache')
                else:
                    print('Fetching')
            head_state = 'List of national sites in ' + url.lower()
            line = ''
            for i in range(0, len(head_state)):
                line += '-'
            print(line)
            print(head_state)
            print(line)
            count = 1
            for element in result:
                print('[' + str(count) + '] ' + element.info())
                count += 1
            state_list.append(url.lower())
            while True:
                print('Choose the number for detail search or "exit" or "back"')
                number = input(': ')
                if number == 'exit':
                    exit(0)
                elif number == 'back':
                    break
                elif number.isdigit() and 1 <= int(number) <= len(result):
                    park_name = result[int(number)-1].name
                    if result[int(number)-1].zipcode == 'no zipcode':
                        print('[Error] No zipcode, cannot search for nearby places')
                        continue
                    else:
                        places = get_nearby_places(result[int(number) - 1])
                        if park_name in park_list:
                            print('Using cache')
                        else:
                            print('Fetching')
                        head_park = "Places near " + park_name
                        line = ''
                        for i in range(0, len(head_park)):
                            line += '-'
                        print(line)
                        print(head_park)
                        print(line)
                        for item in places['searchResults']:
                            name = item['name']
                            if item['fields']['group_sic_code_name'] == '':
                                category = 'no category'
                            else:
                                category = item['fields']['group_sic_code_name']
                            if item['fields']['address'] == '':
                                address = 'no address'
                            else:
                                address = item['fields']['address']
                            if item['fields']['city'] == '':
                                city = 'no city'
                            else:
                                city = item['fields']['city']
                            if name and category and address and city:
                                print('- ' + name + ' (' + category + '): ' + address + ', ' + city)
                        park_list.append(park_name)
                else:
                    print('[Error] Invalid input')
        else:
            print('[Error] Enter proper state name')
            continue
    pass
