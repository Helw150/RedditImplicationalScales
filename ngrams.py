#!/usr/bin/env python3

"""
	This script takes a list of subreddits and for each:
		* Identifies the time frame we have data for
		* Downloads a samples of random reddit comments from the same time frame
		* Compares our banned subreddit to overall reddit to identify unique
		  vernacular
		* Saves the unique words to "shift_graph.png" and "unique_words.txt"

	Prerequisites: Must have downloaded the banned-subreddit history via
	Data_collection_banned_subreddits.py (or downloaded that history from Dropbox)
"""

import json, csv, time, random, nltk, sys, math, os, re
from glob import glob
import numpy as np
import datetime as dt
from tqdm import tqdm
from shifterator import shifts as sh
import sys
import resource
import heapq

# Punkt English-language tokenizer
# Wordnet corpus for lemmatization
try:
    nltk.data.find("tokenizers/punkt")
    nltk.data.find("corpora/wordnet")
    nltk.data.find("corpora/stopwords")
except:
    nltk.download("stopwords")
    nltk.download("punkt")
    nltk.download("wordnet")
    nltk.download("omw-1.4")
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

# Global constants
save_folder = sys.argv[1]
shifterator_file = "shift_graph.png"
unique_words = "unique_words.txt"
number_unique_words = 100
ignoreUsers = set(
    [
        "[deleted]",
        "AutoModerator",
        "WikiTextBot",
        "converter-bot",
        "tweettranscriberbot",
        "CommonMisspellingBot",
        "NFL_Warning",
        "NFLConverterV2",
        "nflcomparebot",
    ]
)

roster_file = save_folder + "rosters.csv"
draft_file = save_folder + "draft_picks.csv"
all_players_file = save_folder + "all_players.json"
team_file = save_folder + "teams.csv"
game_file = save_folder + "games.csv"
staff_file = save_folder + "management.txt"
scrabble_file = save_folder + "scrabble.txt"
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
    "49ers",
    "cowboys",
    "eagles",
    "GreenBayPackers",
    "LosAngelesRams",
    "Patriots",
]
wordnet_lemmatizer = WordNetLemmatizer()


def memory_limit():
    rsrc = resource.RLIMIT_DATA
    soft, hard = resource.getrlimit(rsrc)
    soft /= 2
    resource.setrlimit(rsrc, (soft, hard))


def load_stop_lists():
    players_set = set()
    with open(all_players_file, "r") as f:
        for line in f.readlines():
            line = line.strip()
            line = json.loads(line)
            line = line["results"]
            for player in line:
                players_set.update(player["name"].lower().split(" "))
    with open(roster_file, "r") as f:
        players = csv.reader(f)
        players = list(players)
        index = {key: players[0].index(key) for key in players[0]}
        for player in players[1:]:
            players_set.update(player[index["full_name"]].lower().split(" "))
    with open(draft_file, "r") as f:
        players = csv.reader(f)
        players = list(players)
        index = {key: players[0].index(key) for key in players[0]}
        for player in players[1:]:
            players_set.update(player[index["pfr_name"]].lower().split(" "))
    with open(game_file, "r") as f:
        games = csv.reader(f)
        games = list(games)
        index = {key: games[0].index(key) for key in games[0]}
        coaches = set()
        for game in games[1:]:
            coaches.update(game[index["home_coach"]].lower().split(" "))
            coaches.update(game[index["away_coach"]].lower().split(" "))
    with open(team_file, "r") as f:
        teams = csv.reader(f)
        teams = list(teams)
        index = {key: teams[0].index(key) for key in teams[0]}
        teams_set = set()
        for team in teams[1:]:
            teams_set.update(team[index["nickname"]].lower().split(" "))
            teams_set.update(team[index["full"]].lower().split(" "))
    with open(scrabble_file, "r") as f:
        scrabble = set(word.lower().strip() for word in f.readlines())
    staff = set()
    with open(staff_file, "r") as f:
        staff_names = f.readlines()
        for name in staff_names:
            name = name.strip()
            staff.update(name.lower().split(" "))
    return (coaches, teams_set, players_set, staff, scrabble)


coaches, teams, players, staff, scrabble = load_stop_lists()
invalid_words = (
    set(stopwords.words("english"))
    | set(["dont", "nbsp", ".", "!", ";", "&", ",", "|", "%", "*", ":", "#", "?", '"'])
    | coaches
    | players
    | teams
    | staff
    | scrabble
)
invalid_words = set(
    [wordnet_lemmatizer.lemmatize(word.lower()) for word in invalid_words]
)

# Returns a list of all comment strings that aren't from users we're ignoring
# WARNING: Could be quite large!
def getAllComments(subreddit):
    files = glob(save_folder + "/" + subreddit + "*_comments.csv")
    commentText = []
    for commentfile in tqdm(
        files, total=len(files), desc="Reading comments for " + subreddit
    ):
        with open(commentfile, "r") as f:
            try:
                comments = csv.reader(f)
                comments = list(comments)
                index = {key: comments[0].index(key) for key in comments[0]}
                for comment in comments[1:]:
                    if comment[index["author"]] in ignoreUsers:
                        continue
                    if "RemindMe" in comment[index["body"]]:
                        continue
                    if (
                        "this comment was written by a bot"
                        in comment[index["body"]].lower()
                    ):
                        continue
                    if "opt out of replies" in comment[index["body"]].lower():
                        continue
                    commentText.append(comment[index["body"]])
            except KeyError:
                pass  # No comments that day
    print(len(commentText))
    print(commentText[0])
    return commentText


# Generates a word count from a list of comments
def getFrequencyDistribution(comments, hideProgress=False, use_bigram=False):
    counts = dict()
    for body in tqdm(
        comments,
        total=len(comments),
        desc="Calculating frequencies",
        disable=hideProgress,
    ):
        seen = set()
        stem = None
        max_count = 0
        if not use_bigram:
            for word in word_tokenize(body):
                if word.startswith("&"):
                    continue
                w = re.sub(r"[^\w\d]", "", word.lower(), flags=re.MULTILINE)
                stem = wordnet_lemmatizer.lemmatize(w)
                if (
                    stem in seen
                    or stem in invalid_words
                    or (
                        len(stem) > 0 and stem[-1] == "s" and stem[:-1] in invalid_words
                    )
                    or stem.isnumeric()
                    or len(stem) < 3
                    or stem.startswith("www")
                    or word.startswith("r/")
                ):
                    stem = None
                    continue
                seen.add(stem)
                if stem in counts:
                    counts[stem] += 1
                else:
                    counts[stem] = 1
        else:
            for bigram in nltk.bigrams(word_tokenize(body)):
                bi_word = []
                for word in bigram:
                    w = word.lower()
                    bi_word.append(w)
                stem = " ".join(bi_word).strip()
                if stem in seen or any([word in invalid_words for word in bi_word]):
                    stem = None
                    continue
                seen.add(stem)
                if stem in counts:
                    counts[stem] += 1
                else:
                    counts[stem] = 1
        if stem and counts[stem] > max_count:
            max_count = counts[stem]
            max_stem = stem
    print(max_count)
    print(max_stem)
    return counts


# Change to Heap (Don't Sort To Get Top-K >:( )
def findCommonWordsInDistribution(corpus, n=10000):
    return set(heapq.nlargest(3, corpus.keys(), key=lambda k: corpus[k]))


# Uses corpus to identify common words to reddit as a whole
# Then removes those words from "comments" distribution and returns result
def removeCommonWordsFromDistributions(corpus, common):
    good_corpus = dict()
    for word in corpus:
        if word not in common:
            good_corpus[word] = corpus[word]
    return good_corpus


# Icky function, reaches into the internals of shifterator
# to extract the unique words from our sample and saves them to
# 'filename', one term per line
def saveUniqueWords(comparison, filename):
    scoredTerms = []
    for term in comparison.type2s_diff:
        p2Diff = comparison.type2p_diff[term]
        # s2Diff = comparison.type2s_diff[term]
        # p2Avg  = comparison.type2p_avg[term]
        # s2Ref  = comparison.type2s_ref_diff[term]
        score = comparison.type2shift_score[term]
        # Shift scores are always positive, so we multiply them by (2sDiff/2sDiff)
        # to make them positive if it's a term for our sample, and negative if
        # it's a term for the corpus
        signed_score = score * (p2Diff / abs(p2Diff))
        scoredTerms.append([term, signed_score])
        # type_scores.append([term, 2pDiff, 2sDiff, 2pAvg, 2sRef, score, signed_score])
    sortedTerms = sorted(scoredTerms, key=lambda t: t[-1], reverse=False)[
        0:number_unique_words
    ]
    with open(filename, "w") as f:
        for term in sortedTerms:
            f.write(str(term[0]) + "," + str(term[-1]) + "\n")


if __name__ == "__main__":
    memory_limit()
    subs = subreddits
    subs_plus = subreddits + ["nfl"]
    for sub in tqdm(subs, total=len(subs), desc="Processing subreddits"):
        mainComments = getFrequencyDistribution(
            [
                comment
                for sub_add in subs
                if not sub_add == sub
                for comment in getAllComments(sub_add)
            ]
        )
        common = findCommonWordsInDistribution(mainComments)
        sampleMinusCommon = removeCommonWordsFromDistributions(mainComments, common)
        # First get the base distributions
        subComments = getFrequencyDistribution(getAllComments(sub))
        subCommon = set()  # findCommonWordsInDistribution(subComments)

        # Then remove common words
        subCommentsMinusCommon = removeCommonWordsFromDistributions(
            removeCommonWordsFromDistributions(subComments, common), subCommon
        )
        sampleMinusCommonSpec = removeCommonWordsFromDistributions(
            sampleMinusCommon, subCommon
        )

        # Now use shifterator to find the unique terms and save them
        comparisonJSD = sh.JSDivergenceShift(
            type2freq_1=subCommentsMinusCommon, type2freq_2=sampleMinusCommon
        )
        graphFilename = save_folder + sub + "_" + shifterator_file
        wordsFilename = save_folder + sub + "_" + unique_words
        comparisonJSD.get_shift_graph(
            top_n=10,
            title="Word shift for r/" + sub,
            system_names=["r/" + sub, "Main"],
            filename=graphFilename,
        )
        saveUniqueWords(comparisonJSD, wordsFilename)
