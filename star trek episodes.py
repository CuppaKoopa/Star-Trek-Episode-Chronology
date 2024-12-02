import requests
from bs4 import BeautifulSoup
import csv

def fetch_series_links():
    url = 'https://en.wikipedia.org/wiki/List_of_Star_Trek_lists'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    series_links = []
    for link in soup.select('a[href^="/wiki/List_of_Star_Trek"]'):
        href = link.get('href')
        if 'episodes' in href:
            full_url = f"https://en.wikipedia.org{href}"
            series_links.append(full_url)
    
    return series_links

def fetch_episode_list(series_url):
    response = requests.get(series_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    episodes = []
    tables = soup.find_all('table', class_='wikitable')
    print(f"Found {len(tables)} tables in {series_url}")

    for table in tables:
        headers = [header.get_text(strip=True).lower() for header in table.find_all('th')]
        print(f"Headers: {headers}")
        
        title_index = None
        release_date_index = None
        
        for i, header in enumerate(headers):
            if 'title' in header:
                title_index = i
            if 'original air date' in header or 'airdate' in header:
                release_date_index = i
        
        if title_index is None or release_date_index is None:
            continue
        
        rows = table.find_all('tr')[1:]  # Skip header row
        print(f"Found {len(rows)} rows in table")
        for row in rows:
            cols = row.find_all(['th', 'td'])
            print(f"Found {len(cols)} columns in row")
            if len(cols) > max(title_index, release_date_index):
                title = cols[title_index].get_text(strip=True)
                release_date = cols[release_date_index].get_text(strip=True)
                print(f"Title: {title}, Release Date: {release_date}")  # Debugging output
                episodes.append((title, release_date))
            else:
                print(f"Skipping row with insufficient columns: {cols}")
    
    return episodes

def save_to_csv(episodes, filename='star_trek_episodes.csv'):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Release Date'])
        for episode in episodes:
            writer.writerow(episode)

def main():
    print("Fetching series links...")
    series_links = fetch_series_links()
    all_episodes = []
    
    for link in series_links:
        print(f"Fetching episodes from {link}...")
        episodes = fetch_episode_list(link)
        all_episodes.extend(episodes)
    
    all_episodes.sort(key=lambda x: x[1])  # Sort by release date
    save_to_csv(all_episodes)
    print("Episodes saved to star_trek_episodes.csv")

if __name__ == '__main__':
    main()