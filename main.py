from functions import *
from GUI import *
from math import floor
from datetime import timedelta

sp = authentication()
visibility = True      # visibility of the window


def spotiBar():
    def songDuration():
        durationms = int(track["item"]["duration_ms"])

        return str(timedelta(0, 0, 0, durationms))[2:].split(".")[0]

    def progressTime():                                                        # These functions convert time from ms to
        progress = int(track["progress_ms"])                                   # M:S format to be shown on the start and
                                                                                # end labels
        return str(timedelta(0, 0, 0, progress))[2:].split(".")[0]

    def barProgress():
        song_seconds = floor(int(track["item"]["duration_ms"]) / 1000)
        current_seconds = floor(int(track["progress_ms"]) / 1000)               # This function updates the progress bar
                                                                                # but it is crappy so i'll look for
        updateProgressBar(song_seconds, current_seconds)                        # better ways

    while True:
        event, values = overlayW.read(timeout=500, timeout_key="update")
        toggleWindowVisibility(visibility)
        try:
            track = sp.currently_playing()
            imageurl = track["item"]["album"]["images"][1]["url"]               # variables about currently playing song
            songImage(imageurl)
            songname, artistname = updateSongName(track), track['item']['album']['artists'][0]['name']

        except TypeError:
            pass

        if event in "update":
            try:
                barProgress()
                updateText("songname", songname + "\n" + artistname)            # All these update the elements on the
                updateText("-start-", progressTime())                           # screen
                updateText("-end-", songDuration())
                updateSound(sp.current_playback()["device"]["volume_percent"])
                sp.volume(slider(values))
                overlayW["chosenplaylists"].update(values=readChosenPlaylists())
                playUserChosenPlaylist(sp, values)
                is_liked = checkIfCurrentSongIsLiked(sp)
                updatePlayButton(track, sp)
            except TypeError:
                updateText("songname", "Start a song on\nSpotify to start.")

        if event == "-next-":
            sp.next_track()
            updateText("songname", songname + "\n" + artistname)
            updateText("-end-", songDuration())

        if event == "-previous-":
            sp.previous_track()
            updateText("songname", songname + "\n" + artistname)

        if event == "-play-":
            sp.start_playback()

        if event == "-pause-":
            sp.pause_playback()

        if event == "-sound1-" or event == "-soundmax-":
            current_volume = sp.current_playback()["device"]["volume_percent"]
            sp.volume(0)

            updateVisibility("-soundmuted-", True, "-sound1-", "-soundmax-")

        if event == "-soundmuted-":
            sp.volume(current_volume)

            if current_volume >= 70:
                updateVisibility("-soundmax-", True)
            else:
                updateVisibility("-sound1-", True, "-soundmax-")
            updateVisibility("-soundmuted-", False)

        if event == "settings":
            uris = playlistsToJSON(sp)
            playlist_names = readPlJson()
            names_chosen = playlistWin(playlist_names)                          # This updates the playlist names
            chosen_playlists = {}

            for item in names_chosen:
                if item in playlist_names:
                    chosen_playlists[item] = uris[item]

            writeChosenPlaylists(chosen_playlists)

        if event == "liked":
            addOrRemoveLikedSong(sp)

        if event == "notliked":
            addOrRemoveLikedSong(sp)


hideSpotify()

spotiBar()