from requests_oauthlib import OAuth1Session
import json

import os
import time
import requests

with open('keys.json','r') as keys_raw:
    keys = json.load(keys_raw)
    twitter = OAuth1Session(keys['CK'],keys['CS'],keys['AT'],keys['AS'])

url = "https://api.twitter.com/1.1/search/tweets.json"

save_dir = 'Images'

idnum = ''

if os.path.exists(save_dir) == False:
    os.mkdir(save_dir)

for _ in range(5):
    params ={
        'q' : u'#Splatoon2 #SplatNet2',
        'count' : 100,
        'max_id' : idnum
    }

    req = twitter.get(url,params = params)

    if req.status_code == 200:
        result = json.loads(req.text)

        for data in result['statuses']:
            if 'media' not in data['entities']:
                continue
            
            urls = data['entities']['media']
            media_urls = urls[0]['media_url']

            name = os.path.basename(media_urls)
            with open(os.path.join(save_dir,name),'wb') as f:
                content = requests.get(media_urls).content
                f.write(content)
        
        idnum = data['id']
    else:
        print("Error: {}".format(req.status_code))

    time.sleep(1)