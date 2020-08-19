import PySimpleGUIQt as sg
from b64imgs import *
import PySimpleGUI as ps
from ast import literal_eval

sg.theme("DarkAmber")
sg.theme_background_color("42, 42, 42")
size = (500, 300)
font = "ProximaNova 11"
sg.theme_border_width(0)
sg.theme_text_color("white")


controls = [[sg.Button('', image_data=previous, button_color=(sg.theme_background_color(), sg.theme_background_color()),
                       border_width=0, key='-previous-', tooltip="Previous song"),
            sg.Button('', image_data=paused, button_color=(sg.theme_background_color(), sg.theme_background_color()),
                      border_width=0, key='-pause-', tooltip="Play or pause playback"),
            sg.Button('', image_data=play, button_color=(sg.theme_background_color(), sg.theme_background_color()),
                      border_width=0, key='-play-', tooltip="Play or pause playback", visible=False),
            sg.Button('', image_data=next, button_color=(sg.theme_background_color(), sg.theme_background_color()),
                      border_width=0, key='-next-', tooltip="Next song")]]

sound = [[sg.Text(" ", background_color="transparent", font="Proximanova 2")],

         [sg.Button('', image_data=muted, button_color=(sg.theme_background_color(), sg.theme_background_color()),
                    border_width=0, key='-soundmuted-', tooltip="Mute", visible=False),
         sg.Button('', image_data=sound1, button_color=(sg.theme_background_color(), sg.theme_background_color()),
                   border_width=0, key='-sound1-', tooltip="Mute", visible=True),
         sg.Button('', image_data=soundmax, button_color=(sg.theme_background_color(), sg.theme_background_color()),
                   border_width=0, key='-soundmax-', tooltip="Mute", visible=False),
         sg.Slider(orientation="h", size_px=(70, 8), default_value=50, range=(1, 100), tooltip="Adjust sound volume",
                   key="volumeslider")]]

header = [[sg.Text("Currently playing", font="proximanova 16", justification="l", background_color="transparent",
                   text_color="#b3b3b3", size=(30, 1))],

          [sg.Text("", justification="c", background_color="transparent", font="Proximanova 13",
                   key="songname", size=(15, 3)),
           sg.Image(data_base64="", key="songimage")]]

playlist = [[sg.Button('', image_data=spotifyicon, button_color=(sg.theme_background_color(), sg.theme_background_color()),
                       border_width=0, key='-spotify-', tooltip="Opens spotify main program")],

            [sg.Text("Playlists", font="proximanova 16", background_color="transparent",
                     text_color="#b3b3b3"),
             sg.Button('', image_data=settings, button_color=(sg.theme_background_color(), sg.theme_background_color()),
                       border_width=0, key='settings', tooltip="Choose playlists to display below.")],

            [sg.Listbox(values=[" "], key="chosenplaylists",
                        font="ProximaNova 13", size_px=(136, 90), select_mode='single', background_color="transparent",
                        text_color=sg.theme_text_color())]]

overlay = [[sg.Column(playlist, element_justification="l"),
            sg.Column(header, element_justification="l")],

           [sg.Button('', image_data=notliked, button_color=(sg.theme_background_color(), sg.theme_background_color()),
                      key='notliked', pad=(20, 0), tooltip="Add current song to liked songs"),
            sg.Button('', image_data=liked, button_color=(sg.theme_background_color(), sg.theme_background_color()),
                      key='liked', pad=(20, 0), tooltip="Remove current song from liked songs", visible=False),
            sg.Text(" ", background_color="transparent", margins=(10, 50, 0, 0)),
            sg.Column(controls),
            sg.Column(sound, size=(20, 1))],

           [sg.Text("0:00", key="-start-", font=font, justification="c", background_color="transparent", size_px=(50, 15),
                    margins=(15, 0, 0, 0)),
            sg.ProgressBar(100, size_px=(370, 5), bar_color=("#535353", "#b3b3b3"), start_value=0, key="progress"),
            sg.Text("0:00", key="-end-", font=font, justification="c", background_color="transparent", size_px=(40, 15))]]


overlayW = sg.Window("", overlay, keep_on_top=True,
                     no_titlebar=True, size=size,
                     alpha_channel=0.95,
                     background_image="Resources/spotify.png",
                     element_justification="l",
                     grab_anywhere=True)


def playlistWin(playlist_names):                    # this is the window where playlists are chosen
    ps.theme_background_color("#212121")
    ps.theme_border_width(0)
    ps.theme_button_color(('#b3b3b3', '#212121'))
    playwindow = [[ps.Text("Choose four playlists you\nwant to see on the left",
                           justification="c", background_color=ps.theme_background_color(), text_color="#b3b3b3")],

                  [ps.Listbox(playlist_names, key="listselection", background_color=ps.theme_background_color(),
                              select_mode="multiple", no_scrollbar=True, size=(360, 7), text_color="#b3b3b3", enable_events=True)],

                  [ps.InputText(background_color="#b3b3b3", key="return_playlist")],

                  [ps.Button("Submit", tooltip="Add the selected playlists to the main menu"),
                   ps.Button("Cancel", tooltip="Cancel and go back to the program")]]

    playwindowW = ps.Window("", playwindow,
                            no_titlebar=True,
                            size=(400, 310),
                            element_justification="c",
                            alpha_channel=0.95,
                            font=("Proxima Nova", 14),
                            keep_on_top=True).Finalize()

    while True:
        ev2, vals2 = playwindowW.Read(timeout=10000)
        if ev2 == "Cancel":
            playwindowW.Close()
            break

        if ev2 == "listselection":
            playwindowW["return_playlist"].update(vals2["listselection"])

        if ev2 == "Submit":
            playwindowW.Close()
            chosen = literal_eval(vals2["return_playlist"])

            return chosen
