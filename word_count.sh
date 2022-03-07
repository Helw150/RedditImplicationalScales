cd $1
running_users=""
for FILE in *;
do
    if [ $$FILE == "nfl_comments.csv" ]; then
	continue
    else
	if [[ $FILE == *_comments.csv ]]; then
	    body_column=`sed -n $'1s/,/\\\n/gp' $FILE | grep -nx 'body' | cut -d: -f1`
	    unique_comments=`csvtool -t ',' col "$body_column" - < $FILE | sort | uniq -c | sort -nr | grep "^      1" | cut -c 9-`
	    no_urls=`(echo "$unique_comments") | grep -v "^https" | grep -v "^http"`
	    must_have_words=`(echo "$no_urls") | grep -E [a-Z]+`
	    remove_newlines=`(echo "$must_have_words") | awk -v RS='"' 'NR % 2 == 0 { gsub(/\n/, "_NEWLINE_") } { printf("%s%s", $0, RT) }'`
	    echo $FILE
	    echo "`(echo "$must_have_words") | sed -e 's/^"//' -e 's/"$//' | wc -l`"
	fi
    fi
done
