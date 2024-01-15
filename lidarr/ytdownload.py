#!/usr/bin/python3
import time
import sys
import os
import subprocess
from ytmusicapi import YTMusic

if len(sys.argv) < 6:
    exit()

album_year = int(sys.argv[1])
album_years = [str(album_year), str(album_year+1), str(album_year-1)] # sometimes the album year is off

deezer_album_title = str(sys.argv[2])
lidarr_album_title = str(sys.argv[3])
album_titles = [lidarr_album_title, deezer_album_title]

artist_name = str(sys.argv[4])
audio_path = sys.argv[5]
# album_year = "2022"
# album_title = "I HAD TO DIE TO SURVIVE"
# artist_name = "ghost and pals"
# audio_path = "/home/hugh/Music/arr-scripts/lidarr/"
print("date:", album_year)
print("titles:", album_titles)
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
        if (release["title"] in album_titles) and (release["year"] in album_years):
            albumDetails = yt.get_album(release["browseId"])
            downloadAlbum(albumDetails["audioPlaylistId"])
            exit()
    
    time.sleep(0.5)

# If this fails, do a search with artist + album name and pray:
time.sleep(1)
print("python failed finding album:", lidarr_album_title, "trying alt method..")

search_results = yt.search(artist_name + " " + album_titles[0], "albums")
if search_results:
    albumDetails = yt.get_album(search_results[0]["browseId"])
    downloadAlbum(albumDetails["audioPlaylistId"])
