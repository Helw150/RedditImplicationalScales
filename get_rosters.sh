for i in {1..24}
do
    curl 'https://api.lineups.com/nfl/fetch/players?page='$i \
	 -H 'x-hash: MTMzMDAyNjA1OQ==' \
	 -H 'Accept: application/json, text/plain, */*' \
	 -H 'Referer: https://www.lineups.com/' \
	 -H 'sec-ch-ua-mobile: ?0' \
	 -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36' \
	 -H 'sec-ch-ua: " Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"' \
	 -H 'sec-ch-ua-platform: "Linux"' \
	 --compressed
    echo
done
