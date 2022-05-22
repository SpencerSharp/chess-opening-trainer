import requests
from pathlib import Path
import time

# Assume about 5 MB/s down or so
# 

master_url = "https://database.lichess.org/standard/list.txt"

dl_dir = Path.cwd() / 'resources'

response = requests.get(master_url)

txt = response.text



fils = txt.split("\n")

def extract_name(url):
    ind = url.index("rated")+6
    return url[ind:]

def convert_to_filepath(url):
    return dl_dir / extract_name(url)

def dl_file(url):
    global prev

    cnt = 0

    filpath = convert_to_filepath(url)

    if filpath.exists():
        return
    else:
        if prev != None:
            prev_fil = convert_to_filepath(prev)
            prev_fil.unlink()
            # unlink prev
            tmp = prev
            prev = None
            dl_file(tmp)

    r = requests.get(url, stream=True)
    with filpath.open('wb') as fd:
        for chunk in r.iter_content(chunk_size=4000):
            fd.write(chunk)
            time.sleep(0.001)
    
    prev = url



for url in fils:
    dl_file(url)
    prev = url
