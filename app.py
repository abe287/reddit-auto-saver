import requests
import time, calendar
import datetime as dt
import os
import subprocess
import json
import threading
import jinja2
import markdown

#Custom console print
def console_log(message: str) -> None:
    currentDT = calendar.timegm(time.gmtime())
    currentDT = dt.datetime.fromtimestamp(currentDT).strftime('%m/%d/%Y - %H:%M:%S')

    print(f"[{currentDT}] [{message}]")

#Get saved posts from user's reddit rss feed
def get_posts() -> list:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'}
    saved_data = requests.get(rss_url, headers=headers).json()
    posts = saved_data['data']['children']
    return posts

#Get file names from subreddit folder
def get_files(subreddit: str) -> list:
    path = f"downloads/{subreddit}"
    os.makedirs(path, exist_ok = True)
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    files = [x.split(".")[0] for x in files]
    files = [x.split("_")[0] for x in files]

    return files

def download_file(media_url: str, filename: str) -> None:
    try:
        media = requests.get(media_url, timeout=5)
    except Timeout:
        return download_file(media_url, filename)
    if media.status_code == 200:
        open(filename, 'wb').write(media.content)

# Render template with jinja2
def render_template(file_name: str, **context) -> object:
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader('templates/')
    ).get_template(file_name).render(context)

def process_download(post: dict, gallery_data: list) -> None:
    title = post['data']['title']
    source = post['data']['domain']
    media_url = post['data']['url']
    post_id = post['data']['id']
    subreddit = post['data']['subreddit']
    selftext = post['data']['selftext']

    if source == 'i.imgur.com':
        media_url = media_url.replace('.gifv', '.mp4')
        file_extension = media_url.split(".")[-1]
        file_name = f'downloads/{subreddit}/{post_id}.{file_extension}'
        download_file(media_url, file_name)

    elif source == 'i.redd.it':
        file_extension = media_url.split(".")[-1]
        file_name = f'downloads/{subreddit}/{post_id}.{file_extension}'
        download_file(media_url, file_name)
    
    elif source == 'gfycat.com':
        file_name = f'downloads/{subreddit}/{post_id}.mp4'
        gfycat_id = media_url.split("/")[-1]
        media_url = f"https://giant.gfycat.com/{gfycat_id}.mp4"
        download_file(media_url, file_name)
    
    elif source == f"self.{subreddit}":
        post_html = markdown.markdown(selftext)

        # Get date created (OP)
        timestamp = post['data']['created']
        date_time = dt.datetime.fromtimestamp(timestamp)
        op_time_string = date_time.strftime("%d %B, %Y | %H:%M:%S")

        html = render_template('post_template.html', post = post, post_html = post_html, op_time_string = op_time_string)
        with open(f"downloads/{subreddit}/{post_id}.html","w", encoding='utf-8') as f:
            f.write(html)
    
    elif source == 'reddit.com':
        index = 1
        for image in gallery_data:
            file_extension = "jpg" if image['image_type'] == "image/jpg" else "png"
            download_file(f"https://i.redd.it/{image['media_id']}.{file_extension}", f"downloads/{subreddit}/{post_id}_{index}.{file_extension}")
            index = index + 1
    
    else:
        subprocess.call('yt-dlp "'+media_url+'" -o "/downloads/'+subreddit+'/'+post_id+'.mp4" --quiet', shell=False)

#Run main process
def main(f_stop: object) -> None:
    console_log("Getting saved posts...")
    posts = get_posts()
    
    console_log("Downloading posts...")
    for post in posts:
        #If post is a link (not comment, account, subreddit, etc.)
        if post['kind'] == 't3':
            gallery_data = []
            if "gallery_data" in post['data']:
                images = post['data']['gallery_data']['items']
                for image in images:
                    gallery_data.append({"media_id": image['media_id'], "image_type": post['data']['media_metadata'][image['media_id']]['m']})

            #get previously downloaded file names (so we don't re-download the same posts)
            subreddit = post['data']['subreddit']
            files = get_files(subreddit)

            post_id = post['data']['id']
            if not post_id in files:
                console_log(f"Downloading - Post ID : {post_id}")
                process_download(post, gallery_data)
    
    console_log(f"Next check in {delay} seconds")
    print()
    if not f_stop.is_set():
        threading.Timer(delay, main, [f_stop]).start()

if __name__ == "__main__":
    with open("settings.json") as f:
        settings = json.load(f)
    rss_url = settings['rss_uri']
    delay = settings['delay']
    
    threading.Thread(target=main, args=(threading.Event(),)).start()