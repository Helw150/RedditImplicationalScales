cd $1
running_users=""
for FILE in *;
do
    if [ $$FILE == "nfl_comments.csv" ]; then
	continue
    else
	if [[ $FILE == nfl*_comments.csv ]]; then
	    user_column=`sed -n $'1s/,/\\\n/gp' $FILE | grep -nx 'author_fullname' | cut -d: -f1`
	    uniq_users=`csvtool -t ',' col "$user_column" - < $FILE | sort | uniq`
	    running_users=`(echo "$running_users"; echo "$uniq_users") | sort | uniq`
	fi
    fi
done
echo "$running_users"
