import os
import pyglet  # type: ignore
import datetime
import webbrowser
from pydub import AudioSegment  # type: ignore
from comps import MusicPlayer
from tinytag import TinyTag  # type: ignore
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import QTimer
from PyQt5 import uic, QtGui
from typing import (
    Iterable,
    Union,
    List,
    Any,
)
from .uiactions import (
    get_delay_key,
    get_datetime,
    get_disk,
    get_lyrics_file,
    set_lyrics_delay,
    mute_setup,
    manual_save_lyrics,
    make_file_types,
    edit_volume,
    import_songs,
    delete_song,
    export_song,
    rename,
)
from lyricshandler import (
    Renderer,
)
from actions import (
    FPS,
    LOGO,
    TITLE,
    THEMECLR,
    VERISONS,
    PLAYERUI,
    NEXT_BTN,
    PLAY_BTN,
    MUTE_BTN,
    SHORTCUTS,
    SONGS_DIR,
    PAUSE_BTN,
    LYRICS_DIR,
    RECORD_BTN,
    BACKGROUND,
    FORWARD_ARR,
    SOURCE_CODE,
    BACKWARD_ARR,
    PREVIOUS_BTN,
    SUPPORTED_SONG_FORMATS,
    SUPPORTED_LYRICS_FORMATS,
    logger,
    config,
)
from .customwidgets import (
    ScrollMessageBox,
)
from PyQt5.QtWidgets import (
    QLabel,
    QSlider,
    QShortcut,
    QStatusBar,
    QMainWindow,
    QListWidget,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QInputDialog,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        uic.loadUi(PLAYERUI, self)   # type: ignore
        self.window_title = f"{TITLE} {VERISONS[-1]}"
        self.setWindowIcon(QtGui.QIcon(LOGO))
        self.setFixedSize(self.width(), self.height())
        logger.info(f"{get_datetime()} Initializing application")
        self.player = MusicPlayer(get_disk(config), config.get('is_muted'), config.get('volume'))

        self.trim_mode = False
        self.lyrics_mode = False
        self.timestamp_start = datetime.timedelta(hours=0, minutes=0, seconds=0, milliseconds=0)
        self.timestamp_stop = datetime.timedelta(hours=0, minutes=0, seconds=0, milliseconds=0)

        self.set_title()

        self.sound = pyglet.media.Player()
        self.current_song = pyglet.media.load(self.player.disk.song_path)
        self.lyrics = Renderer(get_lyrics_file(LYRICS_DIR, self.player, Renderer.EXTENSION))
        self.sound.queue(self.current_song)
        logger.info(f"{get_datetime()} Setting up media devices")

        # Load components
        self._load_sliders()
        self._load_labels()
        self._load_lists()
        self._load_btns()
        self._load_status_bar()

        # Set UI
        self.play_btn.setIcon(QtGui.QIcon(self.play_btn_switcher()))
        self.current_playing_lbl.setText(self.player.disk.title())
        self.music_container.setCurrentRow(self.player.disk.song_index)
        self.volume_lbl.setText(f"Vol: {self.player.volume}")
        self.volume_bar.setValue(self.player.volume)
        self.volume_bar.setTickPosition(10)
        self.volume_bar.setMaximum(100)
        self._fill_list_widget()

        # Set commands
        self.play_btn.clicked.connect(lambda: self.play_btn_switcher())
        self.music_container.itemDoubleClicked.connect(
            lambda: self.manual_pick(self.music_container)
        )
        self.volume_bar.valueChanged.connect(lambda: self.volume_control())
        self.next_btn.clicked.connect(lambda: self.next_song())
        self.prev_btn.clicked.connect(lambda: self.prev_song())
        self.mute_btn.clicked.connect(lambda: self.mute_player())

        self.is_pressed = False
        self.song_slider.sliderPressed.connect(lambda: self._slider_pressed())
        self.song_slider.sliderReleased.connect(
            lambda: self.move_song(self.song_slider.value() / 60)
        )
        self.rec_btn.clicked.connect(lambda: self.trim_song())
        self.forward_btn.clicked.connect(lambda: self.small_step(1))  # seconds
        self.backward_btn.clicked.connect(lambda: self.small_step(- 1))  # seconds

        last_song = config.get('last_song')
        if last_song:
            self.move_song(last_song['timestamp'])

        # Key binds
        self.play_shortcut = QShortcut(QKeySequence(SHORTCUTS['PLAY-PAUSE']), self)
        self.next_shortcut = QShortcut(QKeySequence(SHORTCUTS['NEXT SONG']), self)
        self.prev_shortcut = QShortcut(QKeySequence(SHORTCUTS['PREV SONG']), self)
        self.mute_shortcut = QShortcut(QKeySequence(SHORTCUTS['MUTE']), self)
        self.delete_song_shortcut = QShortcut(QKeySequence(SHORTCUTS['DELETE SONG']), self)
        self.trim_shortcut = QShortcut(QKeySequence(SHORTCUTS['TRIM TRIGGER']), self)

        self.play_shortcut.activated.connect(lambda: self.play_btn_switcher())  # type: ignore
        self.next_shortcut.activated.connect(lambda: self.next_song())  # type: ignore
        self.prev_shortcut.activated.connect(lambda: self.prev_song())  # type: ignore
        self.mute_shortcut.activated.connect(lambda: self.mute_player())  # type: ignore
        self.delete_song_shortcut.activated.connect(lambda: self.delete_song())  # type: ignore
        self.trim_shortcut.activated.connect(lambda: self.trim_song())  # type: ignore

        # Menu actions
        self.actionChoose_file.triggered.connect(lambda: self.save_lyric_file())
        self.actionCreate.triggered.connect(lambda: print('create'))
        self.actionShortcuts.triggered.connect(lambda: self.shortcuts_help())
        self.actionDelay.triggered.connect(lambda: self.set_lyrics_delay())
        self.actionImport_songs.triggered.connect(
            lambda: self.import_songs()
        )
        self.actionDelete_song.triggered.connect(lambda: self.delete_song())
        self.actionClear_logs.triggered.connect(lambda: self.clear_logs())
        self.actionReset.triggered.connect(lambda: self.restore_settings())
        self.actionDelete.triggered.connect(lambda: self.delete_lyrics())
        self.actionSee_logs.triggered.connect(lambda: self.check_logs())
        self.actionSource_code.triggered.connect(lambda: webbrowser.open(SOURCE_CODE))
        self.actionExport_song.triggered.connect(lambda: self.export_song())
        self.actionRename_song.triggered.connect(lambda: self.rename_song())
        self.actionChange_download_dir.triggered.connect(lambda: self.change_download_dir())

        # Dynamic updating
        timer = QTimer(self.total_time_lbl)
        timer.timeout.connect(self.update)  # type: ignore
        timer.start(FPS(20))
        logger.info(f"{get_datetime()} Ui set up is completed")

    def closeEvent(self, event: Any) -> None:
        # When player closes, the current timestamp of
        # the song (- set_behind seconds) is saved
        set_behind = 2
        timestamp = float(f"{self.sound.time:.2f}")
        timestamp -= set_behind
        config.edit('last_song', {'song': self.player.disk.song_mp3, 'timestamp': timestamp})
        logger.info(f"{get_datetime()} Application terminated")

    def _load_btns(self) -> None:
        self.prev_btn = self.findChild(QPushButton, 'prev_btn')
        self.next_btn = self.findChild(QPushButton, 'next_btn')
        self.play_btn = self.findChild(QPushButton, 'play_btn')
        self.mute_btn = self.findChild(QPushButton, 'mute_btn')
        self.rec_btn = self.findChild(QPushButton, 'rec_btn')
        self.backward_btn = self.findChild(QPushButton, 'backward_btn')
        self.forward_btn = self.findChild(QPushButton, 'forward_btn')

        self.prev_btn.setIcon(QtGui.QIcon(PREVIOUS_BTN))
        self.rec_btn.setIcon(QtGui.QIcon(RECORD_BTN))
        self.next_btn.setIcon(QtGui.QIcon(NEXT_BTN))
        self.play_btn.setIcon(QtGui.QIcon(PLAY_BTN))
        self.mute_btn.setIcon(QtGui.QIcon(MUTE_BTN))
        self.backward_btn.setIcon(QtGui.QIcon(BACKWARD_ARR))
        self.forward_btn.setIcon(QtGui.QIcon(FORWARD_ARR))

        self.rec_btn.setStyleSheet(f'background-color: {THEMECLR}; border-radius: 10%;')
        self.prev_btn.setStyleSheet(f'background-color: {THEMECLR}; border-radius: 10%;')
        self.next_btn.setStyleSheet(f'background-color: {THEMECLR}; border-radius: 10%;')
        self.play_btn.setStyleSheet(f'background-color: {THEMECLR}; border-radius: 10%;')
        self.mute_btn.setStyleSheet(f'background-color: {THEMECLR}; border-radius: 10%;')
        self.forward_btn.setStyleSheet(f'background-color: {THEMECLR}; border-radius: 10%;')
        self.backward_btn.setStyleSheet(f'background-color: {THEMECLR}; border-radius: 10%;')

    def _load_sliders(self) -> None:
        self.song_slider = self.findChild(QSlider, 'music_prog_bar')
        self.volume_bar = self.findChild(QSlider, 'volume_bar')

    def _load_labels(self) -> None:
        self.current_playing_lbl = self.findChild(QLabel, 'current_playing_lbl')
        self.current_time_lbl = self.findChild(QLabel, 'current_time_lbl')
        self.total_time_lbl = self.findChild(QLabel, 'total_time_lbl')
        self.volume_lbl = self.findChild(QLabel, 'volume_lbl')
        self.lyrics_lbl = self.findChild(QLabel, 'lyrics_lbl')
        self.bg_lbl = self.findChild(QLabel, 'bg_lbl')

        self.lyrics_lbl.setStyleSheet(
            'color: white; font-weight: bold;\
            font-size: 20px; background-color: rgba(255, 255, 255, 0);'
        )
        self.bg_lbl.setStyleSheet(f"background-image : url({BACKGROUND})")
        self.current_playing_lbl.setStyleSheet(f'color: {THEMECLR};')
        self.current_time_lbl.setStyleSheet((f'color: {THEMECLR};'))
        self.total_time_lbl.setStyleSheet((f'color: {THEMECLR};'))
        self.volume_lbl.setStyleSheet((f'color: {THEMECLR};'))
        self.current_playing_lbl.setWordWrap(True)

    def _slider_pressed(self) -> None:
        """Set the self.is_pressed to `True` if the music slider is pressed
        """
        self.is_pressed = True

    def move_song(self, seconds: int) -> None:
        """Move the music slider to a song's timestamp and upon release,
        set the song to that timestamp and reset the `self.is_pressed` to `False`

        :param seconds: The timestamp the the slider was left
        :type seconds: int
        """
        self.is_pressed = False
        self.sound.seek(seconds)

    def _load_lists(self) -> None:
        self.music_container = self.findChild(QListWidget, 'music_container')

        self.music_container.setStyleSheet(
            f"background-color: rgba(255, 255, 255, 0); color: {THEMECLR};"
        )
        self.music_container.setWordWrap(True)
        self.music_container.setSpacing(3)

    def _load_status_bar(self) -> None:
        self.status_bar = self.findChild(QStatusBar, 'statusbar')
        self.time1_lbl = QLabel(self)
        self.time2_lbl = QLabel(self)
        self.arrow_lbl = QLabel(self)
        self.action_lbl = QLabel(self)

        self.time1_lbl.setText(str(self.timestamp_start))
        self.time2_lbl.setText(str(self.timestamp_stop))
        self.arrow_lbl.setText('~>')
        self.action_lbl.setText('')

        self.status_bar.addWidget(self.time1_lbl)
        self.status_bar.addWidget(self.arrow_lbl)
        self.status_bar.addWidget(self.time2_lbl)
        self.status_bar.addWidget(self.action_lbl)

    def _fill_list_widget(self) -> None:
        """Fill the list widget where all the songs are listed with
        the content of `self.player.disk`
        """
        self.music_container.clear()
        for song in self.player.disk:
            self.music_container.addItem(song)
        self.music_container.setCurrentRow(self.player.disk.song_index)

    def refresh_status_bar(self, start: str, end: str, action: str) -> None:
        self.time1_lbl.setText(start)
        self.time2_lbl.setText(end)
        self.action_lbl.setText(action)

    def small_step(self, step: int) -> None:
        current_seconds = self.song_slider.value() / 60
        self.sound.seek(current_seconds + step)

    def valid_timestamps(self, time1: datetime.timedelta, time2: datetime.timedelta) -> bool:
        return time1 < time2

    def clear_logs(self) -> None:
        q = self.askyesno("Clear logs", "Are you sure you want to clear all app's logs?")
        if q:
            logger.clear()

    def restore_settings(self) -> None:
        q = self.askyesno("Restore settings", "Are you sure you want to restore app's settings?")
        if q:
            config.restore_default()

    def export_song(self) -> None:
        song = self.player.disk.title()
        logger.debug(f'Song {song} moved from {SONGS_DIR} -> {config["download_dir"]}')
        export_song(SONGS_DIR, self.player.disk.song_mp3, config['download_dir'])

    def rename_song(self) -> None:
        song_name = self.player.disk.title()
        new_name, q = QInputDialog.getText(self, 'Rename', 'Choose a new name', text=song_name)

        lyrics_file = f"{song_name}.srt"
        if new_name and q:
            rename(SONGS_DIR, song_name, new_name, '.mp3')
            logger.info(f"Rename {song_name} -> {new_name}")
            if os.path.exists(os.path.join(LYRICS_DIR, lyrics_file)):
                rename(LYRICS_DIR, song_name, new_name, '.srt')

                if (key := get_delay_key(self.player.disk)) in config:
                    value = config[key]
                    config.remove_key(key)
                    new_key = f"songs/{new_name}.mp3.delay"
                    config.add(new_key, value)

            self.update_song_list(deletion=True)
            self.next_song()

    def change_download_dir(self) -> None:
        prev_dir = config['download_dir']
        new_dir = QFileDialog.getExistingDirectory(self, "Choose target directory")
        if new_dir:
            config.edit('download_dir', new_dir)
            logger.info(f"Download directory {prev_dir} -> {new_dir}")
        else:
            logger.warning('Change download directory has been canceled')

    def trim_song(self) -> None:
        slider_position = self.song_slider.value()

        if not self.trim_mode:
            self.timestamp_start = datetime.timedelta(seconds=slider_position)
            self.time1_lbl.setText(str(self.timestamp_start))
            self.trim_mode = True
            self.action_lbl.setText('Trim mode')
            logger.info('Trim mode `On`')
        elif self.trim_mode:
            self.timestamp_stop = datetime.timedelta(seconds=slider_position)
            self.time2_lbl.setText(str(self.timestamp_stop))
            self.trim_mode = False
            self.action_lbl.setText('')
            if self.valid_timestamps(self.timestamp_start, self.timestamp_stop):
                start = (self.timestamp_start.seconds / 60) * 1000  # To milliseconds
                stop = (self.timestamp_stop.seconds / 60) * 1000  # To milliseconds
                audio = AudioSegment.from_file(self.player.disk.song_path, format='mp3')
                extract = audio[start:stop]  # type: ignore
                trimmed_name = f'{self.player.disk.title()}-trimmed.mp3'
                export_dir = os.path.join(config['download_dir'], trimmed_name)
                extract.export(export_dir)
                import_songs([export_dir], SONGS_DIR)
                self.update_song_list()
                # TODO: Reset status bar after x seconds
                # FIXME: This crashes if a song can't be trimmed
                # TODO: Use status bar to show such errors for x seconds
                song = self.player.disk.title()
                msg = f"Song {song} has been trimmed from `{start / 1000:.3f} - {stop / 1000:.3f}`"
                logger.info('Trim mode `Off`')
                logger.success(msg)
        else:
            logger.warning("Trim has been abborted")

    def delete_lyrics(self) -> None:
        key = get_delay_key(self.player.disk)
        path = os.path.join(LYRICS_DIR, f"{self.player.disk.title()}.srt")
        title = "Delete lyrics"
        msg = f"Are you sure you want to delete lyrics for {self.player.disk.title()}?"
        q = self.askyesno(title, msg)

        if q:
            if os.path.exists(path):
                os.remove(path)
                logger.success(f"Lyrics for {self.player.disk.title()} was removed")
                if key in config:
                    logger.success(f"Delay for {self.player.disk.title()} has been unset")
                    config.remove_key(key)
            else:
                logger.info(f"No lyrics found for song {self.player.disk.title()}")
        else:
            logger.info("Delete lyrics aborted")
        self.update_song()

    def set_title(self) -> None:
        if self.player.is_muted:
            self.setWindowTitle(self.window_title + " MUTED")
        else:
            self.setWindowTitle(self.window_title)

    def mute_player(self) -> None:
        mute_setup(self.player, config)
        self.set_title()

    def save_lyric_file(self) -> None:
        try:
            path = self._file_explorer_one_file(SUPPORTED_LYRICS_FORMATS)
            manual_save_lyrics(path, self.player, LYRICS_DIR)
        except FileNotFoundError:
            logger.warning(f"{get_datetime()} File manager closed unexpectedly")
            # The file explorer was probably closed
        else:
            self.update_song()

    def _file_explorer_one_file(self, file_types: Iterable[str]) -> str:
        types = make_file_types(file_types)
        path, _ = QFileDialog.getOpenFileName(self, "Choose file", "", types)
        return path

    def _file_explorer_many_files(self, file_types: Iterable[str]) -> List[str]:
        types = make_file_types(file_types)
        paths, _ = QFileDialog.getOpenFileNames(self, "Choose files", "", types)
        return paths

    def askyesno(self, title: str, msg: str) -> bool:
        replies = {
            16384: True,
            65536: False,
        }
        reply = QMessageBox.question(self, title, msg,
                                     QMessageBox.Yes | QMessageBox.No)  # type: ignore
        return replies[reply]

    def check_logs(self) -> None:
        w_width, w_height = 500, 600
        if logger.log_path is not None:
            with open(logger.log_path, mode='r') as f:
                logs = f.read()

            res = ScrollMessageBox('Logs', logs, w_width, w_height, QtGui.QIcon(LOGO))
            res.exec_()
        else:
            raise FileNotFoundError("There is no file assigned for logging or is deleted")

    def shortcuts_help(self) -> None:
        w_width, w_height = 150, 300
        msg = ""
        for bind, key in SHORTCUTS.items():
            msg += f"{bind} ~> {key}\n"
        res = ScrollMessageBox('Shortcuts', msg, w_width, w_height, QtGui.QIcon(LOGO))
        res.exec_()

    def update_song_list(self, deletion: bool = False) -> None:
        config.edit('last_song', {})
        self.player.change_disk(get_disk(config), deletion)
        self._fill_list_widget()
        # Set 'last_song' to `{}` after importing new and changing the `disk` for safety

    def import_songs(self) -> None:
        paths = self._file_explorer_many_files(SUPPORTED_SONG_FORMATS)
        import_songs(paths, SONGS_DIR)
        self.update_song_list()

    def delete_song(self) -> None:
        prompt = f"Are you sure you want to delete {self.player.disk.title()}?"
        title = "Delete song"
        reply = self.askyesno(title, prompt)
        if reply:
            to_delete = self.player.disk.song_mp3
            delete_song(SONGS_DIR, to_delete)
            self.update_song_list(deletion=True)
            self.next_song()
            logger.success(f"Song {to_delete} has been deleted")
            key = get_delay_key(self.player.disk)
            if key in config:
                config.remove_key(key)
                logger.success(f"Delay for {to_delete} has been unset")
        else:
            logger.debug("Delete song action was aborted")

    def display_lyric(self, line: Union[str, None]) -> None:
        if line is not None:
            self.lyrics_lbl.setText(line)
        else:
            self.lyrics_lbl.setText("")

    def update_song(self) -> None:
        self.current_playing_lbl.setText(self.player.disk.title())
        self.music_container.setCurrentRow(self.player.disk.song_index)

        self.sound = pyglet.media.Player()
        self.current_song = pyglet.media.load(self.player.disk.song_path)

        self.lyrics = Renderer(get_lyrics_file(LYRICS_DIR, self.player, Renderer.EXTENSION))

        self.sound.queue(self.current_song)

        self.sound.play() if self.player else self.sound.pause()

    def set_lyrics_delay(self) -> None:
        delay, _ = QInputDialog.getText(self, 'Lyrics delay', 'Set your lyrics delay')
        key = get_delay_key(self.player.disk)
        set_lyrics_delay(key, delay, config)

    def edit_modes_off(self) -> None:
        self.trim_mode = False
        self.lyrics_mode = False
        self.time1_lbl.setText('0.00.00')
        self.time2_lbl.setText('0.00.00')
        self.action_lbl.setText('')

    def next_song(self) -> None:
        self.edit_modes_off()
        self.player.disk.next()
        self.update_song()

    def prev_song(self) -> None:
        self.edit_modes_off()
        self.player.disk.prev()
        self.update_song()

    def manual_pick(self, music_container: QListWidget) -> None:
        self.edit_modes_off()
        self.player.disk.user_pick(music_container.currentRow())
        self.update_song()

    def play_btn_switcher(self) -> str:
        self.player.playing()
        img = PAUSE_BTN if self.player else PLAY_BTN

        self.sound.play() if self.player else self.sound.pause()
        self.play_btn.setIcon(QtGui.QIcon(img))
        return img

    def volume_control(self) -> None:
        edit_volume(config, self.player, self.volume_bar.value())

        self.volume_lbl.setText(f"Vol: {self.volume_bar.value()}")
        if not self.player.is_muted:
            self.sound.volume = self.player.volume / 100
        #                                          ^^^^^
        # This is because self.sound.volume accepts
        # values from 0.0 - 1.0 but I want to display 0 - 100
        # Example: displayed = 50; 50 / 100 = 0.5

    def helper_update_slider(self, slider: QSlider, x: int) -> None:
        # # Update slider's position every ms that ellapses
        slider.tracking = True
        slider.setValue(x)
        slider.sliderPosition = x  # type: ignore
        slider.update()
        slider.repaint()

    def update(self) -> None:  # type: ignore
        tag = TinyTag.get(self.player.disk.song_path)
        total_time = tag.duration
        total_seconds = total_time * 60
        self.song_slider.setRange(0, total_seconds)  # Set the total steps of the slider

        # Current time. Use this for the slider update
        current_time = self.sound.time
        current_seconds = current_time * 60

        if not self.is_pressed:
            # When the slider is pressed, stop updating the progres bar automaticaly so we can
            # set it where it will be released
            self.helper_update_slider(self.song_slider, current_seconds)

        if current_time >= total_time:
            self.next_song()

        seconds_to_minute_format = datetime.timedelta(seconds=current_time)
        # total_time_to_minute is used for the slider steps
        total_time_to_minute = str(datetime.timedelta(seconds=total_time))

        if not self.player.is_muted:
            self.volume_control()
        elif self.player.is_muted:
            self.sound.volume = 0

        delay_key = get_delay_key(self.player.disk)
        lyric_line = self.lyrics.get_line(seconds_to_minute_format, config.get(delay_key))
        self.display_lyric(lyric_line)

        self.total_time_lbl.setText(total_time_to_minute)

        current_time_text = str(seconds_to_minute_format)
        if '.' in current_time_text:
            current_time_text = current_time_text[:current_time_text.index('.') + 3]
            self.current_time_lbl.setText(current_time_text)
