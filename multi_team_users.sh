cd $1
for FILE in *;
do
    running_users=""
    echo $FILE
    for FILE2 in *;
    do
	if [[ $FILE == nfl*_comments.csv ]] || [[ $FILE2 == nfl*_comments.csv ]]; then
	    continue
	else
	    if [[ $FILE == *comments.csv ]] && [[ $FILE2 == *comments.csv ]] && [ "$FILE" != "$FILE2" ]; then
		user_column=`sed -n $'1s/,/\\\n/gp' $FILE | grep -nx 'author_fullname' | cut -d: -f1`
		uniq_users=`csvtool -t ',' col "$user_column" - < $FILE | sort | uniq`
		user_column2=`sed -n $'1s/,/\\\n/gp' $FILE2 | grep -nx 'author_fullname' | cut -d: -f1`
		uniq_users2=`csvtool -t ',' col "$user_column" - < $FILE2 | sort | uniq`
		uniq_overlap_users=`comm -12 <(echo "$uniq_users") <(echo "$uniq_users2")`
		running_users=`(echo "$running_users"; echo "$uniq_overlap_users") | sort | uniq`
		uniq_users_count=`wc -w <(echo "$uniq_overlap_users") | cut -d" " -f1`
		uniq_users_count=`wc -l <(echo "$running_users") | cut -d" " -f1`
	    fi
	fi
    done
    uniq_users_count=`wc -l <(echo "$running_users") | cut -d" " -f1`
    echo $uniq_users_count
done


