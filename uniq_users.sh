cd $1
running_users=""
for FILE in *;
do
    user_column=`sed -n $'1s/,/\\\n/gp' $FILE | grep -nx 'author_fullname' | cut -d: -f1`
    uniq_users=`csvtool -t ',' col "$user_column" - < $FILE | sort | uniq`
    running_users=`(echo "$running_users"; echo "$uniq_users") | sort | uniq`
    uniq_users_count=`wc -w <(echo "$uniq_users") | cut -d" " -f1`
    echo $FILE
    echo $uniq_users_count
done
uniq_users_count=`wc -l <(echo "$running_users") | cut -d" " -f1`
echo "Total Unique Users"
echo $uniq_users_count
