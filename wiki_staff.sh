cat ./staff_wiki.html | grep " – " | sed -e 's/<[^>]*>//g' | sed -e 's/.*–//g' | sed 's/^ //g' | sed 's/and /\n/g'
