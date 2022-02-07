import requests
import time, calendar
import datetime as dt
import os
import subprocess

#Custom console print
def console_log(message):
    currentDT = calendar.timegm(time.gmtime())
    currentDT = dt.datetime.fromtimestamp(currentDT).strftime('%m/%d/%Y - %H:%M:%S')

    print(f"[{currentDT}] [{message}]")

#Get saved posts from user's reddit rss feed
def get_posts():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'}
    saved_data = requests.get(rss_url, headers=headers).json()
    posts = saved_data['data']['children']
    return posts

#Get file names from subreddit folder
def get_files(subreddit):
    os.makedirs(subreddit, exist_ok = True)
    files = [f for f in os.listdir(subreddit) if os.path.isfile(os.path.join(subreddit, f))]
    files = [x.split(".")[0] for x in files]
    files = [x.split("_")[0] for x in files]

    return files

def download_file(media_url, filename):
    try:
        media = requests.get(media_url, timeout=5)
    except Timeout:
        return download_file(media_url, filename)
    if media.status_code == 200:
        open(filename, 'wb').write(media.content)

def process_download(media_url, post_id, source, subreddit, selftext, gallery_data):
    if source == 'i.imgur.com':
        media_url = media_url.replace('.gifv', '.mp4')
        file_extension = media_url.split(".")[-1]
        file_name = f'{subreddit}/{post_id}.{file_extension}'
        download_file(media_url, file_name)

    elif source == 'i.redd.it':
        file_extension = media_url.split(".")[-1]
        file_name = f'{subreddit}/{post_id}.{file_extension}'
        download_file(media_url, file_name)
    
    elif source == 'gfycat.com':
        file_name = f'{subreddit}/{post_id}.mp4'
        gfycat_id = media_url.split("/")[-1]
        media_url = f"https://giant.gfycat.com/{gfycat_id}.mp4"
        download_file(media_url, file_name)
    
    elif source == f"self.{subreddit}":
        f = open(f"{subreddit}/{post_id}.txt", "w")
        f.write(selftext)
        f.close()
    
    elif source == 'v.redd.it':
        subprocess.call('youtube-dl "'+media_url+'" -o "/'+subreddit+'/'+post_id+'.mp4" --quiet', shell=False)
    
    elif source == 'reddit.com':
        index = 1
        for image in gallery_data:
            file_extension = "jpg" if image['image_type'] == "image/jpg" else "png"
            download_file(f"https://i.redd.it/{image['media_id']}.{file_extension}", f"{subreddit}/{post_id}_{index}.{file_extension}")
            index = index + 1
    
    time.sleep(0.20)

#Run main process
def main():
    while True:
        console_log("Getting saved posts...")
        posts = get_posts()
        console_log("Downloading posts...")

        for post in posts:
            #If post is a link then continue (not comment, account, subreddit, etc.)
            if post['kind'] == 't3':
                source = post['data']['domain']
                media_url = post['data']['url']
                post_id = post['data']['id']
                subreddit = post['data']['subreddit']
                selftext = post['data']['selftext']

                if "gallery_data" in post['data']:
                    gallery_data = []
                    images = post['data']['gallery_data']['items']
                    for image in images:
                        gallery_data.append({"media_id": image['media_id'], "image_type": post['data']['media_metadata'][image['media_id']]['m']})
                else:
                    gallery_data = None

                #get previously downloaded file names (so we don't re-download the same posts)
                files = get_files(subreddit)

                if not post_id in files:
                    console_log(f"Downloading - Post ID : {post_id}")
                    process_download(media_url, post_id, source, subreddit, selftext, gallery_data)
        
        console_log(f"Next check in {delay} seconds")
        print()
        time.sleep(delay)

if __name__ == "__main__":
    #Get your RSS feed here: https://ssl.reddit.com/prefs/feeds/
    rss_url = "YOUR_RSS_URL"
    delay = 300 #5 minutes
    main()