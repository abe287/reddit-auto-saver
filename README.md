## Description
This is a tool that automatically downloads images, videos, and text posts from your saved posts on your Reddit account. It checks every minute to see if you saved any new posts by fetching your private RSS feed from Reddit. I made this tool for archiving purposes, since posts can be taken down by Reddit.

## Supported Reddit Embeds
- imgur
- gfycat
- reddit (native)

## Setup
#### Part 1
For this to work, you will have to get your Private RSS Feed URI for your reddit account, you can find it at the link below. Select the JSON box next to the "your saved links" option (look at the image below for reference).
https://ssl.reddit.com/prefs/feeds/
![alt text](https://i.ibb.co/j8QQfjP/Screenshot-2022-02-06-224649.png)
Once you have the URI to your RSS Feed, paste it inside the settings.json file

#### Part 2
Install all the requirements
```
pip install -r requirements.txt
```

## Usage
```
python app.py
```
All the downloads will be saved to their respective subreddit folder inside a downloads folder.