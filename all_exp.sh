SCRAPED_FOLDER=$1
RESULTS_FOLDER=$2

bash uniq_users.sh $SCRAPED_FOLDER > $RESULTS_FOLDER/user_counts.txt
bash word_count.sh $SCRAPED_FOLDER > $RESULTS_FOLDER/word_count.txt

$MAIN_REDDIT_USERS=$RESULTS_FOLDER/main_reddit_users.txt
bash uniq_users_nfl.sh $SCRAPED_FOLDER > $MAIN_REDDIT_USERS

bash multi_team_users.sh $SCRAPED_FOLDER > $RESULTS_FOLDER/multi_team_users.txt

bash overlap.sh $SCRAPED_FOLDER $MAIN_REDDIT_USERS > $RESULTS_FOLDER/overlap_with_main.txt

# Go to the website listed and copy the query using your browser then run the following script
# bash get_rosters.sh > $SCRAPED_FOLDER/all_players.json

wget https://raw.githubusercontent.com/nflverse/nfldata/master/data/rosters.csv
mv ./rosters.csv $SCRAPED_FOLDER/rosters.csv
wget https://raw.githubusercontent.com/nflverse/nfldata/master/data/draft_picks.csv
mv ./draft_picks.csv $SCRAPED_FOLDER/draft_picks.csv
wget https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv
mv ./games.csv $SCRAPED_FOLDER/games.csv
wget https://raw.githubusercontent.com/nflverse/nfldata/master/data/teams.csv
mv ./teams.csv $SCRAPED_FOLDER/teams.csv
wget https://raw.githubusercontent.com/zeisler/scrabble/master/db/dictionary.csv
mv ./dictionary.csv $SCRAPED_FOLDER/scrabble.txt
bash wiki_staff.sh > $SCRAPED_FOLDER/management.txt

python ngrams.py $SCRAPED_FOLDER
