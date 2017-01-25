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
    
    
def downloadXML():
    global sites, files
    
    ssl._create_default_https_context = ssl._create_unverified_context
    
    for i, val in list(enumerate(sites)):
        parse = urlparse(val)
        site = parse.netloc
        
        wp = urllib.request.urlopen(val)
        pw = wp.read().decode('utf-8')
        
        filename = os.getcwd() + "/" + urlparse(val).hostname + ".xml"
        target = open(filename, 'w')
        target.truncate()
        target.write(pw)
        target.close()
        
        if filename not in files:
            files.append(filename)

    
def downloadArticles():
    global sites, files

    for i, val in list(enumerate(files)):
        hostname = urlparse(sites[i]).hostname
        filecsv = os.getcwd() + "/dataStore/" + hostname + ".csv"
        filelinks = os.getcwd() + "/links_" + hostname + ".csv"
        links = [line.rstrip('\n') for line in open(filelinks)]
        
        print("Starte: " + hostname)
        
        col = ["timestamp", "url", "content"]
        df = pd.DataFrame(columns=col)
        
        for link in links:
            wp = urllib.request.urlopen(link)
            pw = wp.read().decode('utf-8')
            
            data = {"timestamp" : {int(round(time.time() * 1000))}, "url" : {link}, "content" : {pw}}
            tempDF = pd.DataFrame(data, columns=col)
            
            df = df.append(tempDF, ignore_index=True)
        
        print("Fertig: " + hostname)
        
        with open(filecsv, "a") as f:
            df.to_csv(f, sep='\t', encoding='utf-8', header=False)
        
        print("In Datei geschrieben...")
        
def downloadArticleLinks():
    global sites, files
    
    for i, val in list(enumerate(files)):
        hostname = urlparse(sites[i]).hostname
        root = ET.parse(val).getroot()
        filecsv = os.getcwd() + "/links_" + hostname + ".csv"
        
        if os.path.isfile(filecsv):
            links = [line.rstrip('\n') for line in open(filecsv)]
        else:
            links = []
        
        print("Starte: " + hostname)
        
        for child in root[0]:
            if(child.tag != "item"):
                continue
            
            link = child[1].text
            
            if link not in links:
                with open(filecsv, "a") as f:
                    f.write(link)
                    f.write("\n")
        
        print("Fertig: " + hostname) 
        

def execute():
    print("Lade Seiten aus Datei...")
    loadSites()
    print("Lade XML aller Seiten herunter...")
    downloadXML()
    print("Sammle neue Artikellinks...")
    downloadArticleLinks()
    print("Lade Artikel herunter...")
    downloadArticles()

while True:
    startTime = int(time.time())
    execute()
    diffTime = int(time.time()) - startTime
    waitTime = int(20 * 60 - diffTime / 1000)
    
    if waitTime > 0:
        print("Warte %smin ab %s" % (int(waitTime / 60), time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())))
    time.sleep(waitTime)
        