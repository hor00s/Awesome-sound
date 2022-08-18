import os

SONGSFILE:    tuple[str]  = tuple(filter(lambda i: i != '.gitignore', os.listdir('songs')))
PREVIOUS_BTN: str         = os.path.join('images', 'previous-button.png')
PAUSE_BTN:    str         = os.path.join('images', 'pause-button.png')
PLAY_BTN:     str         = os.path.join('images', 'play-button.png')
NEXT_BTN:     str         = os.path.join('images', 'next-button.png')
BACKGROUND:   str         = os.path.join('images', 'background.jpg')
LOGO:         str         = os.path.join('images', 'applogo.png')
PLAYERUI:     str         = os.path.join('window', 'player.ui')
THEMECLR:     str         = 'rgb(0, 188, 255)'
THEMECLR:     str         = 'rgb(144,238,144)'
TITLE:        str         = 'Awesome sound'
VERISONS:     tuple       = ('v.0.5', )
HEIGHT:       int         = 473
WIDTH:        int         = 539

SHORTCUTS: dict = {
    'PLAY-PAUSE': 'Space',
    'PREV SONG': '+',
    'NEXT SONG': '-',
}
