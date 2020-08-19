import psutil
from win32con import SW_HIDE
from win32gui import ShowWindow, IsWindowVisible, IsWindowEnabled, EnumWindows
from win32process import GetWindowThreadProcessId
from skimage.io import imread, imsave
from skimage.transform import resize
from skimage.util import img_as_ubyte
from base64 import b64encode
from spotipy import Spotify, oauth2, util
from os import remove
from GUI import *
from re import finditer
import json
from spotipy.exceptions import SpotifyException
from requests.exceptions import HTTPError
from keyboard import is_pressed
from time import sleep

# TODO optimize the progression of the progress bar
# TODO try to change the slider's colours to match spotify colours
# TODO get the volume icon closer to the slider
# TODO possibly add a search bar
# TODO make the spotify button send the user back to spotify app

toggle_visibility_key = "shift"


def authentication():
    USERNAME = "YOUR USERNAME HERE"
    scope = "streaming user-library-read user-modify-playback-state user-read-playback-state user-library-modify " \
            "playlist-read-private playlist-read-private"
    redirect_uri = 'http://google.com/'
    CLIENT_ID, CLIENT_SECRET = "YOUR CLIEND ID HERE", "YOUR CLIENT SECRET HERE"

    sp_oauth = oauth2.SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=redirect_uri,
                                   scope=scope, username=USERNAME)
    token_info = sp_oauth.get_cached_token()
    if not token_info:
        token = util.prompt_for_user_token(USERNAME, scope=scope, client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                                           redirect_uri=redirect_uri)
        token_info = sp_oauth.get_cached_token()
    else:
        token = token_info["access_token"]

    try:
        sp = Spotify(auth=token)
        return sp
    except:
        print("User token could not be created")
        exit()


def updateVisibility(key, visibility, *false_elements):
    overlayW[key].update(visible=visibility)
    for elem in false_elements:                                 # This function updates the visibility of elements
        overlayW[elem].update(visible=False)
    overlayW.Refresh()


def updateSound(volume):
    if volume >= 70:
        updateVisibility("-soundmax-", True, "-soundmuted-", "-sound1-")

    if 70 > volume > 0:
        updateVisibility("-sound1-", True, "-soundmuted-", "-soundmax-")

    if volume == 0:
        updateVisibility("-soundmuted-", True, "-sound1-", "-soundmax-")


def updateText(key=str, text=str):
    overlayW[key].update(text)


def updateProgressBar(song_seconds, bar_progress):          # this is the function that updates the progress bar
    increment_val = 100 / song_seconds                      # it's very crappy atm, I'll look into it more

    overlayW["progress"].UpdateBar((bar_progress + increment_val) * increment_val)
    overlayW.Refresh()


def slider(values_variable):
    volume = values_variable['volumeslider']

    return volume


def songImage(url):                 # takes the song image and modifies it in order to be added on the program
    imsave("pic.png", img_as_ubyte(resize(imread(url, as_gray=False), (50, 50))))
    with open("pic.png", "rb") as saved:
        saved = saved.read()

    b64img = b64encode(saved)
    remove("pic.png")

    overlayW["songimage"].update(data_base64=b64img)

    return b64img


def updateSongName(track):                  # This function updates the song name, and formats it to fit on the screen
    name = str(track['item']['name'])       # in case the song name is too long.

    if len(name) >= 20:
        space_occurences = [m.start() for m in finditer(' ', name)]
        occ = space_occurences[1]

        final = name[:occ] + "\n" + name[occ + 1:]
        return str(final)

    else:
        return name


def getLikedSongs(sp):                                          # Gets the liked songs of the user
    playlists = sp.current_user_saved_tracks(limit=50)
    liked_uris = []
    for item in playlists["items"]:
        liked_uris.append(item["track"]["uri"])

    return liked_uris


def playlistsToJSON(sp):                                # Writes the playlist names and URI on a json to be read later
    playlists = sp.current_user_playlists()

    playlist_names = []
    playlist_uris = []

    for item in playlists["items"]:             # name of playlists
        playlist_names.append(item["name"])
        playlist_uris.append(item["uri"])

    playlist_name_and_uri = {"Liked songs": getLikedSongs(sp)}

    for name in playlist_names:
        for uri in playlist_uris:
            playlist_name_and_uri[name] = uri
            playlist_uris.remove(uri)
            break

    with open("playlists.json", "w") as write_file:
        json.dump(playlist_name_and_uri, write_file)

    return playlist_name_and_uri


def readPlJson():
    with open("playlists.json", "r") as read_file:
        data = json.load(read_file)
        pl_names = []
        for e in data:
            pl_names.append(e)
        read_file.close()
        return pl_names


def writeChosenPlaylists(chosen_playlists):
    with open("chosen_playlists.json", "w") as playlists_file:
        json.dump(chosen_playlists, playlists_file)
        playlists_file.close()


def readChosenPlaylists():
    try:
        with open("chosen_playlists.json", "r") as read_file:
            data = json.load(read_file)
            pl_names = []
            for e in data:
                pl_names.append(e)
            read_file.close()
            return pl_names
    except FileNotFoundError:
        pass


def playUserChosenPlaylist(sp, window_values_varname):
    try:
        song = window_values_varname["chosenplaylists"][0]          # reads the selected playlist from the program
        with open("chosen_playlists.json", "r") as read_file:
            data = json.load(read_file)                             # reads the playlists chosen by user from the json
            read_file.close()

        for key in data.keys():
            try:
                if "Liked songs" in key:                            # checks if Liked songs was selected
                    sp.start_playback(uris=data["Liked songs"])
                else:
                    sp.start_playback(context_uri=data[song])       # plays the playlist selected by user
            except (HTTPError, SpotifyException):                   # still returns 400 for some reason but liked songs
                pass                                                # playlist is able to play with no problem

    except (IndexError, TypeError):
        pass


def checkIfCurrentSongIsLiked(sp):
    try:
        is_liked = sp.current_user_saved_tracks_contains([sp.currently_playing()["item"]["id"]])[0]

        if is_liked:
            updateVisibility("liked", True, "notliked")
        if not is_liked:
            updateVisibility("notliked", True, "liked")

        return is_liked
    except TypeError:
        updateVisibility("notliked", True, "liked")


def addOrRemoveLikedSong(sp):
    currently_playing_id = sp.currently_playing()["item"]["id"]
    is_liked = checkIfCurrentSongIsLiked(sp)

    if not is_liked:
        sp.current_user_saved_tracks_add([currently_playing_id])

    if is_liked:
        sp.current_user_saved_tracks_delete([currently_playing_id])


def updatePlayButton(track, sp):
    is_playing = sp.currently_playing()["is_playing"]

    if is_playing:
        updateVisibility("-pause-", True, "-play-")

    else:
        updateVisibility("-play-", True, "-pause-")


def toggleWindowVisibility(visibility):
    if is_pressed(toggle_visibility_key) and visibility:
        overlayW.Hide()
        visibility = False
        sleep(1)                                                    # Toggles the window visibility using shift
                                                                    # the key can be changed to anything
    if is_pressed(toggle_visibility_key) and not visibility:
        overlayW.UnHide()
        visibility = True
        sleep(1)


def hideSpotify():                                                  # This function is for sure confusing, as it was for
    def get_hwnds_for_pid(pid):                                     # me, but it gets the hwnd of spotify from the pid
        def callback(hwnd, hwnds):                                  # in order to minimize it to the SystemTray later
            if IsWindowVisible(hwnd) and IsWindowEnabled(hwnd):
                _, found_pid = GetWindowThreadProcessId(hwnd)
                if found_pid == pid:
                    hwnds.append(hwnd)
            return True

        hwnds = []
        EnumWindows(callback, hwnds)
        return hwnds

    processes_names = {}

    for proc in psutil.process_iter(['pid', 'name']):
        processes_names[proc.name()] = proc

    if 'Spotify.exe' in processes_names:
        main = processes_names["Spotify.exe"].pid
        parent = processes_names["Spotify.exe"].parent().pid

        if parent is None:
            spotify_handles = get_hwnds_for_pid(main)

        else:
            spotify_handles = get_hwnds_for_pid(parent)

        for handle in spotify_handles:
            ShowWindow(handle, SW_HIDE)
                                                # Spotify has to be running in order for spotibar to work, so if it's
    if "Spotify.exe" not in processes_names:    # not running an error popup window will appear.
        sg.PopupError("Spotify has to be running\nin order to use this program\n", no_titlebar=True,
                      background_color="#212121", font="ProximaNova 15", grab_anywhere=True, text_color="#b3b3b3",
                      keep_on_top=True)

        exit()
