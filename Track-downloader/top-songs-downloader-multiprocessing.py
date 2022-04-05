import multiprocessing
import requests
import multiprocessing.dummy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os import system


url_base = 'https://api.deezer.com/'


def getID(artist):
    '''Returns an int of the Id number related to a certain artist, requires name as a string.'''
    
    url_search = "search/artist?"
    params = {'q': artist}
    response = requests.get(url_base + url_search, params=params)
    
    return response.json()['data'][0]['id']

def getSongs(Id, limit = 20):
    '''Returns a list of most popular songs by artist, requires Id and limit as integers.'''
    
    url_songs = f'artist/{str(Id)}/top?limit={str(limit)}'
    response = requests.get(url_base + url_songs)
    
    return [i['title_short'] for i in response.json()['data']]

def getURLs(artist, songs):
    '''Gets artist and title, returning a list of urls of the videos.'''
    
    url_youtube = 'https://www.youtube.com/results?search_query='
    
    arr = []
    
    count = 0
    
    for title in songs:
        if '/' in title:
            temp_list = title.split('/')
            for item in temp_list:
                getURLs(artist, item.strip())
        else:
            searchUrl = url_youtube + artist.replace(' ', '+') + '+' + title.replace(' ', '+') + '+lyrics'

            op = webdriver.ChromeOptions()
            op.add_argument('headless')
            driver = webdriver.Chrome(options=op)
            driver.get(searchUrl)
            wait = WebDriverWait(driver, 15)
            video_loaded = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="video-title"]')))

            video_url = [link.get_attribute('href') for link in video_loaded][0]
            
            arr.append({'artist': artist, 'title': title, 'url': video_url})
            
            count += 1
            
            print(f"Getting {count} of {len(songs)}...")
    
    print("Done! Starting to download.")

    return arr

def downloadSongs(arr):
    '''Gets artist, title and urls, downloads and saves file.'''
    
    pathToSave = './Songs/'       
    
    if arr['url'] and arr['title'] != None:
        system("youtube-dl -x --audio-format mp3 -q -o \'" + pathToSave + arr['artist'] +\
            '/' + arr['title'] + ".%(ext)s\' \'" + arr['url'] + "\'")
    else:
        print('Missed one song.')

        
if __name__=='__main__':
    
    choice = int(input("Escolha 1 para buscar músicas por cantor ou 2\
 para buscar uma música específica: "))
    
    if choice == 1:
        artist = input("Nome do cantor: ")
        limit = int(input("Número de músicas desejadas: "))
    
        songs = getSongs(getID(artist), limit)
        
        arr = getURLs(artist, songs)
        
        p = multiprocessing.dummy.Pool(8)
        p.map(downloadSongs, arr)

                
    elif choice == 2:
        title = input("Digite o título da música: ")
        artist = input("Digite o nome do cantor: ")
        
        arr = getURLs(artist, [title])
        
        try:
            p = multiprocessing.dummy.Pool(8)
            p.map(downloadSongs, arr)
        except:
            print("Música não encontrada.")
            
    else:
        print("Opção não suportada.")