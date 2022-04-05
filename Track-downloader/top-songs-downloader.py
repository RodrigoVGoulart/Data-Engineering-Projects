import requests
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
    '''Returns a list of 50 most popular songs by artist, requires Id and limit as integers.'''
    
    url_songs = f'artist/{str(Id)}/top?limit={str(limit)}'
    response = requests.get(url_base + url_songs)
    
    return [i['title_short'] for i in response.json()['data']]

def downloadSong(artist, title):
    '''Gets artist and song title, downloads and saves file.'''
    
    url_youtube = 'https://www.youtube.com/results?search_query='
    pathToSave = f'./Songs/{artist}/'
    
    if '/' in title:
        temp_list = title.split('/')
        for item in temp_list:
            downloadSong(artist, item.strip())
    else:
        searchUrl = url_youtube + artist.replace(' ', '+') + '+' + title.replace(' ', '+') + '+lyrics'

        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        
        driver = webdriver.Chrome(options=op)        
        driver.get(searchUrl)
        
        wait = WebDriverWait(driver, 5)
        
        video_loaded = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="video-title"]')))        
        video_url = [link.get_attribute('href') for link in video_loaded][0]
        
        if type(video_url) == str:
            print("Downloading " + title + " from " + video_url)
        
            system("youtube-dl -x --audio-format mp3 -q -o \'" + pathToSave + title +\
                ".%(ext)s\' \'" + video_url + "\'")
            print("Downloaded " + title + "\n")
        else:
            print("Unable to download file")
        
if __name__=='__main__':
    
    choice = int(input("Escolha 1 para buscar músicas por cantor ou 2\
 para buscar uma música específica: "))
    
    if choice == 1:
        artist = input("Nome do cantor: ")
        limit = int(input("Número de músicas desejadas: "))
    
        songs = getSongs(getID(artist), limit)
        
        for title in songs:
            if title.strip() != '':
                downloadSong(artist, title)
            else:
                print("Missed one song.")
                
    elif choice == 2:
        title = input("Digite o título da música: ")
        artist = input("Digite o nome do cantor: ")
        
        try:
            downloadSong(artist, title)
        except:
            print("Música não encontrada.")
            
    else:
        print("Opção não suportada.")