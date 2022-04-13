SCRAPED_FOLDER=$1
RESULTS_FOLDER=$2

bash uniq_users.sh $SCRAPED_FOLDER > $RESULTS_FOLDER/user_counts.txt
bash word_count.sh $SCRAPED_FOLDER > $RESULTS_FOLDER/word_count.txt

$MAIN_REDDIT_USERS=$RESULTS_FOLDER/main_reddit_users.txt
bash uniq_users_nfl.sh $SCRAPED_FOLDER > $MAIN_REDDIT_USERS

bash multi_team_users.sh $SCRAPED_FOLDER > $RESULTS_FOLDER/multi_team_users.txt

bash overlap.sh $SCRAPED_FOLDER $MAIN_REDDIT_USERS > $RESULTS_FOLDER/overlap_with_main.txt
