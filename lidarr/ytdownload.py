#!/usr/bin/python3
import time
import sys
import os
import subprocess
from ytmusicapi import YTMusic

if len(sys.argv) < 5:
    exit()

album_year = str(sys.argv[1])
album_title = str(sys.argv[2])
artist_name = str(sys.argv[3])
audio_path = sys.argv[4]
# album_year = "2022"
# album_title = "I HAD TO DIE TO SURVIVE"
# artist_name = "ghost and pals"
# audio_path = "/home/hugh/Music/arr-scripts/lidarr/"
print("date:", album_year)
print("title:", album_title)
print("artist:", artist_name)
print("audio_path:", audio_path)

def downloadAlbum(playlistId):
    global audio_path

    url = f"https://music.youtube.com/playlist?list={playlistId}"
    subprocess.call(['env', '-C', audio_path, 'yt-dlp', '-if', 'bestaudio', '-o%(title)s.%(ext)s', '--add-metadata', url])

    print("url:", url)

    for filename in os.listdir(audio_path):
        path = os.path.join(audio_path, filename)
        name, ext = os.path.splitext(path)
        output_format = '.opus' if ext == '.webm' else '.aac' if ext == '.m4a' else None
        
        if output_format:
            print("converting file:", filename)
            if subprocess.call(['ffmpeg', '-hide_banner', '-i', path, '-acodec', 'copy', name + output_format]) != 0:
                print("Error extracting audio from:", filename)
            os.remove(path)

yt = YTMusic()
search_results = yt.search(artist_name, "artists")

for i, result in enumerate(search_results):
    artistId = search_results[i]["browseId"]
    artist = yt.get_artist(artistId)
    time.sleep(0.5)

    albums = []
    singles = []

    if ("albums" in artist):
        if ("params" in artist["albums"]):
            albums = yt.get_artist_albums(channelId=artist["albums"]["browseId"], params=artist["albums"]["params"])
        else:
            albums = artist["albums"]["results"]

    if ("singles" in artist):
        if ("params" in artist["singles"]):
            singles = yt.get_artist_albums(channelId=artist["singles"]["browseId"], params=artist["singles"]["params"])
        else:
            singles = artist["singles"]["results"]

    for release in (albums + singles):
        if (album_title == release["title"] and album_year == release["year"]):
            print(album_title, "found!")

            albumDetails = yt.get_album(release["browseId"])
            playlistId = albumDetails["audioPlaylistId"]
            downloadAlbum(playlistId)
            
            exit()
    
    time.sleep(0.5)
