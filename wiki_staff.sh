cat List_of_current_National_Football_League_staffs | grep " – " | sed -e 's/<[^>]*>//g' | sed -e 's/.*–//g' | sed 's/^ //g' | sed 's/and /\n/g'
