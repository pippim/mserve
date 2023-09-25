#!/bin/bash
#  https://www.pippim.com/programs/mserve.html#pickled-youtube-playlists

#    Follow instructions and note "Copy Button" below:

#        STEP 1: Use CTRL+I in web browser
#        STEP 2: Click Button 1 to copy to clipboard "youPlayListScroll()"
#        STEP 3: Go to web browser and use CTRL+V then Enter
#        STEP 3A: Type "allow pasting" (without the quotes) if requested by browser
#        STEP 3B: Wait for web browser to stop scrolling, 1 second per song
#        STEP 4: Click Button 2 to copy to clipboard "youPlaylistCopy()"
#        STEP 5: Go to web browser and use Ctrl+V then Enter
#        STEP 6: Click Button 3 to copy to clipboard "youPlaylistSave()"
#        STEP 7: Go to web browser and use Ctrl+V then Enter
#        STEP 8: Run this bash script youPlaylistMoveCSV.sh
#        STEP 9: Use "View Playlists", select Playlist, View Button

if [ "$#" -ne 1 ]; then
    printf 'ERROR! You must provide the "Playlist Name" in quotes!\n' >&2
    exit 1
fi

if [ ! -f ~/Downloads/my_data.csv ]; then
    printf "ERROR! File ~/Downloads/my_data.csv not found!\n" >&2
    exit 1
fi

cd ~/Downloads
mv -v my_data.csv "$1".csv
cp -v "$1".csv ~/.local/share/mserve/YouTubePlaylists
rm -v ~/.local/share/mserve/YouTubePlaylists/"$1".pickle
echo "Ready for mserve: View Playlists, Select $1, then View Button"
