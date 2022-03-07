cd $1
running_users=""
for FILE in *;
do
    if [[ $FILE == nfl*_comments.csv ]]; then
	continue
    else
	if [[ $FILE == *comments.csv ]]; then
	    user_column=`sed -n $'1s/,/\\\n/gp' $FILE | grep -nx 'author_fullname' | cut -d: -f1`
	    uniq_users=`csvtool -t ',' col "$user_column" - < $FILE | sort | uniq`
	    uniq_overlap_users=`comm -12 <(echo "$uniq_users") <(sort "$2")`
	    running_users=`(echo "$running_users"; echo "$uniq_overlap_users") | sort | uniq`
	    uniq_users_count=`wc -w <(echo "$uniq_overlap_users") | cut -d" " -f1`
	    echo $FILE
	    echo $uniq_users_count
	fi
    fi
done
uniq_users_count=`wc -l <(echo "$running_users") | cut -d" " -f1`
echo "Total Main & Subreddit Posting Users"
echo $uniq_users_count
