import csv
import sys
from tqdm import tqdm
from ngrams import getAllComments, subreddits, memory_limit, unique_words

save_folder = sys.argv[1]
keywords = {}
sizes = {}
overlaps = {}
with open("subreddit_features.csv", "r") as f:
    for line in f.readlines():
        subreddit, num_users, overlap = line.split(",")
        sizes[subreddit] = float(num_users)
        overlaps[subreddit] = float(overlap)

for sub in subreddits:
    with open(save_folder + sub + "_" + unique_words, "r") as f:
        keywords[sub] = set([line.split(",")[0] for line in f.readlines()])


def get_size(sub):
    return sizes[sub]


def get_overlap(sub):
    return overlaps[sub]


if __name__ == "__main__":
    memory_limit()
    a_file = open(f"/data/wheld3/reddit_data/dataset.csv", "w")
    keys = [
        "main_ratio",
        "size_percent",
        "overlap",
        "length",
        "reply",
        "media",
        "sub",
        "keyword",
    ]
    dict_writer = csv.DictWriter(a_file, keys)
    dict_writer.writeheader()
    subs = subreddits
    main_comments, main_counts = getAllComments("nfl", feature_builder=True)
    max_length = 0
    for comment, _, _, _ in main_comments:
        if len(comment) > max_length:
            max_length = len(comment)
    for sub in tqdm(subs, total=len(subs), desc="Processing subreddits"):
        comments, sub_counts = getAllComments(sub, feature_builder=True)
        features = []
        seen_authors = set()
        for comment, author, reply, media in comments:
            seen_authors.add(author)
            main_count = main_counts[author] if author in main_counts else 0
            sub_count = sub_counts[author] if author in sub_counts else 0
            main_ratio = float(main_count) / float(main_count + sub_count)
            size_percent = get_size(sub)
            overlap = get_overlap(sub)
            length = len(comment) / max_length
            keyword = any([keyword in comment for keyword in keywords[sub]])
            features.append(
                {
                    "main_ratio": main_ratio,
                    "size_percent": size_percent,
                    "overlap": overlap,
                    "length": length,
                    "reply": reply,
                    "media": media,
                    "sub": 1,
                    "keyword": keyword,
                }
            )
        dict_writer.writerows(features)
        features = []
        for comment, author, reply, media in main_comments:
            if author in seen_authors:
                main_count = main_counts[author] if author in main_counts else 0
                sub_count = sub_counts[author] if author in sub_counts else 0
                main_ratio = float(main_count) / float(main_count + sub_count)
                size_percent = get_size(sub)
                overlap = get_overlap(sub)
                length = len(comment) / max_length
                keyword = any([keyword in comment for keyword in keywords[sub]])
                features.append(
                    {
                        "main_ratio": main_ratio,
                        "size_percent": size_percent,
                        "overlap": overlap,
                        "length": length,
                        "reply": reply,
                        "media": media,
                        "sub": 0,
                        "keyword": keyword,
                    }
                )
        dict_writer.writerows(features)
