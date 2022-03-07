function myserver () {
    python scrape_comments.py
}
until myserver; do     echo "Server 'myserver' crashed with exit code $?.  Respawning.." >&2;     sleep 20; done
