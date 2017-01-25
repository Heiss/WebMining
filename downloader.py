import ssl, os, urllib.request, xml, time
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import pandas as pd

sites = []
files = []

def loadSites():
    global sites
    
    fname = "./sites"
    with open(fname) as f:
        sites = f.readlines()
    
    print(sites)
    
def downloadXML():
    global sites, files
    
    ssl._create_default_https_context = ssl._create_unverified_context
    
    for i, val in list(enumerate(sites)):
        parse = urlparse(val)
        site = parse.netloc
        
        wp = urllib.request.urlopen(val)
        pw = wp.read().decode('utf-8')
        
        filename = os.getcwd() + "/" + urlparse(val).hostname + ".txt"
        target = open(filename, 'w')
        target.truncate()
        target.write(pw)
        target.close()
        files.append(filename)
    
    print(files)
    
def downloadArticles():
    store = pd.HDFStore('store.h5')
    
    for i, val in list(enumerate(files)):
        
        col = ["timestamp", "url", "content"]
        
        if sites[i] in store:
            df = store[sites[i]]
        else:
            df = pd.DataFrame(columns=col)
        
        root = ET.parse(val).getroot()
        
        for child in root[0]:
            if(child.tag != "item"):
                continue
            
            link = child[1].text
        
            wp = urllib.request.urlopen(link)
            pw = wp.read().decode('utf-8')
            
            data = {"timestamp" : {int(round(time.time() * 1000))},  
                     "url" : {link},
                     "content" : {pw}}
            tempDF = pd.DataFrame(data, columns=col)
            
            df = df.append(tempDF, ignore_index=True)
        
        hostname = urlparse(sites[i]).hostname
        print("Fertig: " + hostname) 
        store[hostname] = df
    store.close()
            
def showArticles():
    store = pd.HDFStore('store.h5')
    print(store.keys())
    for i, val in list(enumerate(sites)):
        hostname = urlparse(sites[i]).hostname
        print(store[hostname])

def execute():
    print("Lade Seiten aus Datei...")
    loadSites()
    print("Lade XML aller Seiten herunter...")
    downloadXML()
    print("Lade Artikel herunter...")
    downloadArticles()
    print("Zeige Artikel an...")
    showArticles()
    
execute()