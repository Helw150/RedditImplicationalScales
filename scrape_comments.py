import csv
import requests
from collections import defaultdict
from datetime import datetime, timedelta
import time
import os
import json

subreddits = [
    "raiders",
    "Jaguars",
    "Chargers",
    "Tennesseetitans",
    "Colts",
    "Texans",
    "AZCardinals",
    "panthers",
    "nyjets",
    "miamidolphins",
    "buccaneers",
    "Saints",
    "Commanders",
    "NYGiants",
    "DenverBroncos",
    "buffalobills",
    "detroitlions",
    "falcons",
    "ravens",
    "browns",
    "KansasCityChiefs",
    "CHIBears",
    "minnesotavikings",
    "Seahawks",
    "bengals",
    "steelers",
    "49er",
    "cowboys",
    "eagles",
    "GreenBayPackers",
    "LosAngelesRams",
    "Patriots",
    "nfl",
]
ignored_users = ["[deleted]", "automoderator"]
lookback_days = 30
min_comments_per_sub = 1

url = "https://api.pushshift.io/reddit/comment/search?&limit=1000&sort=desc&subreddit={}&before="

startTime = datetime.utcnow()
startEpoch = int(startTime.timestamp())
endTime = startTime - timedelta(days=lookback_days)
endEpoch = int(endTime.timestamp())
totalSeconds = startEpoch - endEpoch


if not os.path.exists("/data/wheld3/reddit_data"):
    os.makedirs("/data/wheld3/reddit_data")


def scrapeComments(subreddit):
    previousEpoch = startEpoch
    print(f"Scraping: {subreddit}")
    first = True
    count = 0
    if os.path.exists(f"/data/wheld3/reddit_data/{subreddit}_comments.csv"):
        with open(f"/data/wheld3/reddit_data/{subreddit}_comments.csv", "r") as csvfile:
            comment_reader = csv.reader(csvfile)
            comment_reader = list(comment_reader)
            if len(comment_reader) != 0:
                first = False
                keys = comment_reader[0]
                a_file = open(f"/data/wheld3/reddit_data/{subreddit}_comments.csv", "a")
                dict_writer = csv.DictWriter(a_file, keys)
                count = len(comment_reader) - 1
                previousEpoch = int(comment_reader[-1][keys.index("created_utc")]) - 1
                print(previousEpoch)
    while True:
        if previousEpoch < endEpoch:
            print(endEpoch)
            print(previousEpoch)
            break
        newUrl = url.format(subreddit) + str(previousEpoch)
        try:
            response = requests.get(
                newUrl,
                headers={
                    "User-Agent": "Computational Social Science scraper by wheld3@gatech.edu"
                },
            )
        except requests.exceptions.ReadTimeout:
            print(
                f"Pushshift timeout, this usually means pushshift is down. Waiting 5 seconds and trying again: {newUrl}"
            )
            time.sleep(5)
            continue
        try:
            objects = response.json()["data"]
        except json.decoder.JSONDecodeError:
            print(
                f"Decoding error, this usually means pushshift is down. Waiting 5 seconds and trying again: {newUrl}"
            )
            time.sleep(5)
            continue

        time.sleep(1)  # pushshift is ratelimited. If we go too fast we'll get errors

        if len(objects) == 0:
            break
        if first:
            keys = set([key for object in objects for key in object.keys()]).union(
                set(
                    [
                        "author_cakeday",
                        "edited",
                        "awarders",
                        "retrieved_on",
                        "media_metadata",
                        "editable",
                    ]
                )
            )
            a_file = open(f"/data/wheld3/reddit_data/{subreddit}_comments.csv", "w")
            dict_writer = csv.DictWriter(a_file, keys)
            dict_writer.writeheader()
            first = False
        dict_writer.writerows(objects)
        object = objects[-1]
        count += len(objects)
        print(count)
        previousEpoch = object["created_utc"] - 1
    a_file.close()
    print(f"Total Comments for {subreddit}: {count}")
    return count


totalCount = 0
for subreddit in subreddits:
    subredditCount = scrapeComments(subreddit)
    totalCount += subredditCount

print(f"{totalCount} comments across {len(subreddits)} subreddits.")
