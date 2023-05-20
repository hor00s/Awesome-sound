# mypy: ignore-errors
import os
import pyglet
import random
import datetime
import webbrowser
from pydub import AudioSegment
from comps import MusicPlayer
from tinytag import TinyTag
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import QTimer
from PyQt5 import uic, QtGui
from .languages import (
    get_message,
    get_available_languages,
)
from .qstyles import (
    lineedit_style,
    popup_lbl,
    action_lbl_style,
)
from typing import (
    Iterable,
    Callable,
    Literal,
    Tuple,
    Union,
    Dict,
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
    search_song,
    time_to_total_seconds,
)
from lyricshandler import (
    Renderer,
    Creator,
)
from actions import (
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
    LYRICS_ICON,
    SOURCE_CODE,
    BACKWARD_ARR,
    PREVIOUS_BTN,
    SUPPORTED_SONG_FORMATS,
    SUPPORTED_LYRICS_FORMATS,
    get_song_list,
    get_active_language,
    logger,
    config,
)
from .customwidgets import (
    StatusBarTimeEdit,
    ScrollMessageBox,
    StatusBarButton,
    ComboboxDialog,
)
from PyQt5.QtWidgets import (
    QLabel,
    QSlider,
    QLineEdit,
    QShortcut,
    QStatusBar,
    QMainWindow,
    QListWidget,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QInputDialog,
    QApplication,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        uic.loadUi(PLAYERUI, self)
        self.window_title = f"{TITLE} {VERISONS[-1]}"
        self.setWindowIcon(QtGui.QIcon(LOGO))
        self.setFixedSize(self.width(), self.height())
        lang = get_active_language()
        logger.info(f"{get_datetime()} {get_message(lang, 'init_app_msg')}")
        self.player = MusicPlayer(get_disk(config, get_song_list(SONGS_DIR)),
                                  config.get('is_muted'), config.get('volume'))

        self.trim_mode = False
        self.lyrics_mode = False
        dt = datetime.timedelta(hours=0, minutes=0, seconds=0, milliseconds=0)
        self.timestamp_start = dt
        self.timestamp_stop = dt

        self.set_title()

        self.sound = pyglet.media.Player()
        self.current_song = pyglet.media.load(self.player.disk.song_path)
        self.lyrics = Renderer(get_lyrics_file(LYRICS_DIR, self.player, Renderer.EXTENSION))
        self.sound.queue(self.current_song)
        logger.info(f"{get_datetime()} {get_message(lang, 'init_media_msg')}")

        # Load components
        self._load_sliders()
        self._load_labels()
        self._load_lists()
        self._load_btns()
        self._load_status_bar()
        self._load_line_edits()

        # Set UI
        self.play_btn.setIcon(QtGui.QIcon(self.play_btn_switcher()))
        self.current_playing_lbl.setText(self.player.disk.song_name)
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
        self.lyrics_btn.clicked.connect(lambda: self.make_lyrics())
        self.forward_btn.clicked.connect(lambda: self.small_step(1))  # seconds
        self.backward_btn.clicked.connect(lambda: self.small_step(- 1))  # seconds
        self.search_ln.textChanged.connect(lambda: self.search_song())

        last_song = config.get('last_song')
        if last_song:
            self.move_song(last_song['timestamp'])

        # Key binds
        self.mute_shortcut = QShortcut(QKeySequence(SHORTCUTS['MUTE']), self)
        self.next_shortcut = QShortcut(QKeySequence(SHORTCUTS['NEXT SONG']), self)
        self.prev_shortcut = QShortcut(QKeySequence(SHORTCUTS['PREV SONG']), self)
        self.play_shortcut = QShortcut(QKeySequence(SHORTCUTS['PLAY-PAUSE']), self)
        self.trim_shortcut = QShortcut(QKeySequence(SHORTCUTS['TRIM TRIGGER']), self)
        self.lyrics_shortcut = QShortcut(QKeySequence(SHORTCUTS['LYRICS TRIGGER']), self)
        self.delete_song_shortcut = QShortcut(QKeySequence(SHORTCUTS['DELETE SONG']), self)
        self.select_song_shortcut = QShortcut(QKeySequence(SHORTCUTS['SELECT SONG']), self)
        self.main_focus_shortcut = QShortcut(QKeySequence(SHORTCUTS['MAIN WINDOW FOCUS']), self)

        self.play_shortcut.activated.connect(lambda: self.play_btn_switcher())
        self.next_shortcut.activated.connect(lambda: self.next_song())
        self.prev_shortcut.activated.connect(lambda: self.prev_song())
        self.mute_shortcut.activated.connect(lambda: self.mute_player())
        self.delete_song_shortcut.activated.connect(lambda: self.delete_song())
        self.trim_shortcut.activated.connect(lambda: self.trim_song())
        self.lyrics_shortcut.activated.connect(lambda: self.make_lyrics())
        self.select_song_shortcut.activated.connect(lambda: self.manual_pick(self.music_container))
        self.main_focus_shortcut.activated.connect(
            lambda: QApplication.activeWindow().setFocus()
        )

        # Menu actions
        self.actionChoose_file.triggered.connect(lambda: self.save_lyric_file())
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
        self.actionMax_frame_rate.triggered.connect(lambda: self.set_frame_rate())
        self.actionShuffle.triggered.connect(lambda: self.order_by('shuffle'))
        self.actionAlphaberical.triggered.connect(lambda: self.order_by('alphabetical'))
        self.actionLength_increasing.triggered.connect(lambda: self.order_by('length', False))
        self.actionLength_decreasing.triggered.connect(lambda: self.order_by('length', True))
        self.actionOriginal.triggered.connect(lambda: self.order_by('original'))
        self.actionLanguage.triggered.connect(lambda: self.select_language())

        # Dynamic updating
        self.timer = QTimer(self.total_time_lbl)
        self.timer.timeout.connect(self.update)
        self.timer.start(config.get('max_frame_rate'))
        logger.info(f"{get_datetime()} {get_message(lang, 'init_complete_msg')}")

    def closeEvent(self, event: Any) -> None:
        # When player closes, the current timestamp of
        # the song (- set_behind seconds) is saved
        lang = get_active_language()
        set_behind = 2
        timestamp = float(f"{self.sound.time:.2f}")
        timestamp -= set_behind
        config.edit('last_song', {'song': self.player.disk.song_mp3, 'timestamp': timestamp})
        logger.info(f"{get_datetime()} {get_message(lang, 'app_terminated_msg')}")

    def _load_btns(self) -> None:
        self.prev_btn = self.findChild(QPushButton, 'prev_btn')
        self.next_btn = self.findChild(QPushButton, 'next_btn')
        self.play_btn = self.findChild(QPushButton, 'play_btn')
        self.mute_btn = self.findChild(QPushButton, 'mute_btn')
        self.rec_btn = self.findChild(QPushButton, 'rec_btn')
        self.backward_btn = self.findChild(QPushButton, 'backward_btn')
        self.forward_btn = self.findChild(QPushButton, 'forward_btn')
        self.lyrics_btn = self.findChild(QPushButton, 'lyrics_btn')

        self.prev_btn.setIcon(QtGui.QIcon(PREVIOUS_BTN))
        self.rec_btn.setIcon(QtGui.QIcon(RECORD_BTN))
        self.next_btn.setIcon(QtGui.QIcon(NEXT_BTN))
        self.play_btn.setIcon(QtGui.QIcon(PLAY_BTN))
        self.mute_btn.setIcon(QtGui.QIcon(MUTE_BTN))
        self.backward_btn.setIcon(QtGui.QIcon(BACKWARD_ARR))
        self.forward_btn.setIcon(QtGui.QIcon(FORWARD_ARR))
        self.lyrics_btn.setIcon(QtGui.QIcon(LYRICS_ICON))

        self.rec_btn.setStyleSheet(f'background-color: {THEMECLR}; border-radius: 10%;')
        self.prev_btn.setStyleSheet(f'background-color: {THEMECLR}; border-radius: 10%;')
        self.next_btn.setStyleSheet(f'background-color: {THEMECLR}; border-radius: 10%;')
        self.play_btn.setStyleSheet(f'background-color: {THEMECLR}; border-radius: 10%;')
        self.mute_btn.setStyleSheet(f'background-color: {THEMECLR}; border-radius: 10%;')
        self.lyrics_btn.setStyleSheet(f'background-color: {THEMECLR}; border-radius: 10%;')
        self.forward_btn.setStyleSheet(f'background-color: {THEMECLR}; border-radius: 10%;')
        self.backward_btn.setStyleSheet(f'background-color: {THEMECLR}; border-radius: 10%;')

    def _load_line_edits(self) -> None:
        self.search_ln = self.findChild(QLineEdit, 'search_query_ln')
        self.search_ln.setPlaceholderText("Search song...")
        self.search_ln.setStyleSheet(lineedit_style)

    def _load_sliders(self) -> None:
        self.song_slider = self.findChild(QSlider, 'music_prog_bar')
        self.volume_bar = self.findChild(QSlider, 'volume_bar')

    def _load_labels(self) -> None:
        self.current_playing_lbl = self.findChild(QLabel, 'current_playing_lbl')
        self.current_time_lbl = self.findChild(QLabel, 'current_time_lbl')
        self.total_time_lbl = self.findChild(QLabel, 'total_time_lbl')
        self.volume_lbl = self.findChild(QLabel, 'volume_lbl')
        self.lyrics_lbl = self.findChild(QLabel, 'lyrics_lbl')
        self.popup_lbl = self.findChild(QLabel, 'pop_up_lbl')
        self.bg_lbl = self.findChild(QLabel, 'bg_lbl')

        self.lyrics_lbl.setStyleSheet(
            'color: white; font-weight: bold;\
            font-size: 20px; background-color: rgba(255, 255, 255, 0);'
        )
        self.popup_lbl.setStyleSheet("background-color: gray;")
        self.bg_lbl.setStyleSheet(f"background-image : url({BACKGROUND})")
        self.current_playing_lbl.setStyleSheet(f'color: {THEMECLR};')
        self.current_time_lbl.setStyleSheet((f'color: {THEMECLR};'))
        self.total_time_lbl.setStyleSheet((f'color: {THEMECLR};'))
        self.volume_lbl.setStyleSheet((f'color: {THEMECLR};'))
        self.popup_lbl.setStyleSheet(popup_lbl)

        self.current_playing_lbl.setWordWrap(True)
        self.popup_lbl.hide()

    def _show_popup(self, msg: str, seconds: int = 3) -> None:
        """Show the popup label at the bottom right of the window

        :param msg: The message that will be displayed
        :type msg: str
        :param seconds: The time the popup will be active for, defaults to 3
        :type seconds: int, optional
        """
        self.popup_lbl.setText(msg)
        self.popup_lbl.show()
        QTimer.singleShot(seconds * 1000, self.popup_lbl.hide)

    def _slider_pressed(self) -> None:
        """Set the self.is_pressed to `True` if the music slider is pressed
        """
        self.is_pressed = True

    def move_song(self, seconds: float) -> None:
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
        self.time1_inp = StatusBarTimeEdit(self, str(self.timestamp_start))
        self.time2_inp = StatusBarTimeEdit(self, str(self.timestamp_start))
        self.arrow_lbl = QLabel(self)
        self.action_lbl = QLabel(self)

        self.go_start_timestamp = StatusBarButton(self, 'Start', tooltip_text="Jump to start point")
        self.go_end_timestamp = StatusBarButton(self, 'Stop', tooltip_text="Jump to endpoint")
        self.cancel_btn = StatusBarButton(self, 'X', tooltip_text="Cancel any activated mode")

        self.arrow_lbl.setText('~>')
        self.action_lbl.setText('')
        self.action_lbl.hide()

        self.status_bar.addWidget(self.time1_inp)
        self.status_bar.addWidget(self.arrow_lbl)
        self.status_bar.addWidget(self.time2_inp)
        self.status_bar.addWidget(self.go_start_timestamp)
        self.status_bar.addWidget(self.go_end_timestamp)
        self.status_bar.addWidget(self.cancel_btn)
        self.status_bar.addWidget(self.action_lbl)

        self.action_lbl.setStyleSheet(action_lbl_style)

        self.go_start_timestamp.clicked.connect(
            lambda: self.move_song(self._time_to_seconds(self.time1_inp.text()))
        )
        self.go_end_timestamp.clicked.connect(
            lambda: self.move_song(self._time_to_seconds(self.time2_inp.text(), 0.5))
        )
        self.cancel_btn.clicked.connect(lambda: self.edit_modes_off())

    def _time_to_seconds(self, time: str, subtract: float = 0) -> float:
        lang = get_active_language()
        try:
            seconds = time_to_total_seconds(time) / 60 - subtract
        except ValueError:
            seconds = self.sound.time
            self._show_popup(get_message(lang, 'invalid_timestamp'))
        finally:
            return seconds

    def _fill_list_widget(self) -> None:
        """Fill the list widget where all the songs are listed with
        the content of `self.player.disk`
        """
        self.music_container.clear()
        for song in self.player.disk:
            self.music_container.addItem(song)
        self.music_container.setCurrentRow(self.player.disk.song_index)

    def select_language(self) -> None:
        text = f"Select your language. (Current {get_active_language().title()}.)"

        d = ComboboxDialog(self, self.window_title, text,
                           *get_available_languages(), height=150)

        q, lang_option = d.get_option()
        if q:
            config.edit('language', lang_option)
            lang = get_active_language()
            msg = get_message(lang, 'language_changed')
            logger.success(f"{get_datetime()} {msg}")
            self._show_popup(msg)

    def small_step(self, step: int) -> None:
        current_seconds = self.song_slider.value() / 60
        self.sound.seek(current_seconds + step)

    def valid_timestamps(self, time1: datetime.timedelta, time2: datetime.timedelta) -> bool:
        return time1 < time2

    def clear_logs(self) -> None:
        lang = get_active_language()
        title, prompt = get_message(lang, 'clear_logs'), get_message(lang, 'clear_logs_prompt')
        q = self.askyesno(title, prompt)
        if q:
            logger.clear()
            self._show_popup(get_message(lang, 'logs_cleared'))

    def restore_settings(self) -> None:
        lang = get_active_language()
        title, prompt = (
            get_message(lang, 'restore_settings'), get_message(lang, 'restore_settings_prompt')
        )

        q = self.askyesno(title, prompt)
        if q:
            config.restore_default()
            logger.info(f"{get_datetime()} {get_message(lang, 'settings_restored')}")
            self._show_popup(get_message(lang, 'settings_restored'))

    def export_song(self) -> None:
        lang = get_active_language()
        message = get_message(lang, 'song_exported', SONGS_DIR, '->', config['download_dir'])
        logger.debug(message)
        export_song(SONGS_DIR, self.player.disk.song_mp3, config['download_dir'])
        self._show_popup(get_message(lang, 'song_exported'))

    def rename_song(self) -> None:
        lang = get_active_language()
        title, prompt = get_message(lang, 'rename_song'), get_message(lang, 'choose_name')
        song_name = self.player.disk.song_name
        new_name, q = QInputDialog.getText(self, title, prompt, text=song_name)

        lyrics_file = f"{song_name}.srt"
        if new_name and q:
            rename(SONGS_DIR, song_name, new_name, '.mp3')
            rename_info = get_message(lang, 'rename_song', song_name, '->', new_name)
            logger.info(rename_info)
            if os.path.exists(os.path.join(LYRICS_DIR, lyrics_file)):
                rename(LYRICS_DIR, song_name, new_name, '.srt')

                if (key := get_delay_key(self.player.disk)) in config:
                    value = config[key]
                    config.remove_key(key)
                    config.add(key, value)

            self.update_song_list(get_song_list(SONGS_DIR), deletion=True)
            self._show_popup(get_message(lang, 'renamed_popup'))
            self.prev_song()

    def change_download_dir(self) -> None:
        prev_dir = config['download_dir']
        lang = get_active_language()

        new_dir = QFileDialog.getExistingDirectory(self, get_message(lang, 'download_target_dir'))
        if new_dir:
            config.edit('download_dir', new_dir)
            info = get_message(lang, 'download_dir_changed', prev_dir, '->', new_dir)
            logger.info(info)
            self._show_popup(get_message(lang, 'download_dir_changed'))
        else:
            logger.warning(get_message(lang, 'download_dir_canceled'))

    def make_lyrics(self):
        lang = get_active_language()
        self.trim_mode = False
        slider_position = self.song_slider.value()
        if not self.lyrics_mode:
            self.timestamp_start = datetime.timedelta(seconds=slider_position)
            self.time1_inp.setText(str(self.timestamp_start))
            self.lyrics_mode = True
            self.action_lbl.show()
            self.action_lbl.setText('Lyrics mode')
        elif self.lyrics_mode:
            self.timestamp_stop = datetime.timedelta(seconds=slider_position)
            self.time2_inp.setText(str(self.timestamp_stop))
            self.lyrics_mode = False
            self.action_lbl.setText('')
            self.action_lbl.hide()
            if self.valid_timestamps(self.timestamp_start, self.timestamp_stop):
                lyrics_creator = Creator(self.player, LYRICS_DIR)
                lyrics_creator.init()
                title, prompt = get_message(lang, 'lyrics_edit'), get_message(lang, 'lyrics_line')
                line, accepted = QInputDialog.getText(self, title, prompt)
                if accepted:
                    lyrics_creator.write_line(line, self.time1_inp.text(), self.time2_inp.text())
                    self.lyrics = Renderer(get_lyrics_file(LYRICS_DIR, self.player,
                                                           Renderer.EXTENSION))

    def trim_song(self) -> None:
        lang = get_active_language()
        self.lyrics_mode = False
        slider_position = self.song_slider.value()
        if not self.trim_mode:
            self.timestamp_start = datetime.timedelta(seconds=slider_position)
            self.time1_inp.setText(str(self.timestamp_start))
            self.trim_mode = True
            self.action_lbl.show()
            self.action_lbl.setText(get_message(lang, 'trim_mode'))
        elif self.trim_mode:
            self.timestamp_stop = datetime.timedelta(seconds=slider_position)
            self.time2_inp.setText(str(self.timestamp_stop))
            self.trim_mode = False
            self.action_lbl.setText('')
            self.action_lbl.hide()
            if self.valid_timestamps(self.timestamp_start, self.timestamp_stop):
                title, prompt = get_message(lang, 'trim_song'), get_message(lang, 'trim_confirm')
                q = self.askyesno(title, prompt)
                if q:
                    start = (self.timestamp_start.seconds / 60) * 1000  # To milliseconds
                    stop = (self.timestamp_stop.seconds / 60) * 1000  # To milliseconds
                    audio = AudioSegment.from_file(self.player.disk.song_path, format='mp3')
                    extract = audio[start:stop]
                    trimmed_name = f'{self.player.disk.song_name}-trimmed.mp3'
                    export_dir = os.path.join(config['download_dir'], trimmed_name)
                    extract.export(export_dir)
                    import_songs([export_dir], SONGS_DIR)
                    self.update_song_list(get_song_list(SONGS_DIR))
                    # FIXME: This crashes if a song can't be trimmed. Show popup (self._show_popup)
                    time_start, time_stop = f"{start / 1000:.3f}", f"{stop / 1000:.3f}"
                    msg = get_message(lang, 'trim_success', time_start, '-', time_stop)
                    logger.success(msg)
        else:
            msg = get_message(lang, 'trim_abort')
            logger.warning(msg)

    def delete_lyrics(self) -> None:
        song = self.player.disk.song_name
        lang = get_active_language()
        key = get_delay_key(self.player.disk)
        path = os.path.join(LYRICS_DIR, f"{song}.srt")
        title, msg = get_message(lang, 'delete_lyrics'), get_message(lang, 'delete_prompt', song)
        q = self.askyesno(title, msg)

        if q:
            if os.path.exists(path):
                os.remove(path)
                log = f"Lyrics for {song} was removed"
                log = get_message(lang, 'lyrics_deleted', song)
                logger.success(log)
                self._show_popup(log)
                if key in config:
                    logger.success(get_message(lang, 'delay_deleted'), song)
                    config.remove_key(key)
            else:
                log = get_message(lang, 'lyrics_not_found', song)
                logger.info(log)
                self._show_popup(log)
        else:
            logger.info(get_message(lang, 'lyrics_aborted'))

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
            log = f"Lyrics for {self.player.disk.song_name} has been set"
            logger.success(log)
            self._show_popup(log)
            self.lyrics = Renderer(get_lyrics_file(LYRICS_DIR, self.player, Renderer.EXTENSION))
        except FileNotFoundError:
            pass
            # The file explorer was probably closed
        else:
            self.update_song()

    def set_frame_rate(self) -> None:
        lang = get_active_language()
        current_frames = config.get('max_frame_rate')
        min_frame_rate, max_frame_rate = 10, 120
        msg = get_message(lang, 'set_frame_rate', min_frame_rate, '-', max_frame_rate)
        frames, _ = QInputDialog.getText(self, "Set frame rate", msg, text=str(current_frames))
        dt = get_datetime()
        if frames.isnumeric():
            int_frames = int(frames)
            if min_frame_rate <= int_frames <= max_frame_rate:
                config.edit('max_frame_rate', int_frames)
                info = get_message(lang, 'frame_edit')
                logger.success(f"{dt} {info}")
                self._show_popup(info)
            else:
                msg = get_message(lang, 'frame_invalid', frames)
                log = f"{dt} {msg}"
                logger.warning(log)
                self._show_popup(msg)
        else:
            msg = get_message(lang, 'frame_invalid', frames)
            log = f"{dt} {msg}"
            logger.warning(log)
            self._show_popup(msg)

    def _file_explorer_one_file(self, file_types: Iterable[str]) -> str:
        types = make_file_types(file_types)
        path, _ = QFileDialog.getOpenFileName(self, "Choose file", "", types)
        return path

    def _file_explorer_many_files(self, file_types: Iterable[str]) -> List[str]:
        types = make_file_types(file_types)
        paths, _ = QFileDialog.getOpenFileNames(self, "Choose files", "", types)
        return paths

    def search_song(self) -> None:
        text = self.search_ln.text()
        if text:
            songs = self.player.disk.full_song_list
            current_index = self.player.disk.song_index
            found_index = search_song(songs, text, current_index)

            self.music_container.setCurrentRow(found_index)

    def askyesno(self, title: str, msg: str) -> bool:
        replies = {
            16384: True,
            65536: False,
        }
        reply = QMessageBox.question(self, title, msg,
                                     QMessageBox.Yes | QMessageBox.No)
        return replies[reply]

    def check_logs(self) -> None:
        w_width, w_height = 500, 600
        if logger.log_path is not None:
            with open(logger.log_path, mode='r') as f:
                logs = f.read()

            lang = get_active_language()
            res = ScrollMessageBox(get_message(lang, 'logs'), logs,
                                   w_width, w_height, QtGui.QIcon(LOGO))
            res.exec_()
        else:
            raise FileNotFoundError("There is no file assigned for logging or is deleted")

    def shortcuts_help(self) -> None:
        w_width, w_height = 150, 300
        msg = ""
        for bind, key in SHORTCUTS.items():
            msg += f"{bind} ~> {key}\n"
        lang = get_active_language()
        res = ScrollMessageBox(get_message(lang, 'shortcuts'), msg,
                               w_width, w_height, QtGui.QIcon(LOGO))
        res.exec_()

    def update_song_list(self, song_list: Tuple[str, ...], deletion: bool = False) -> None:
        config.edit('last_song', {})
        self.player.change_disk(get_disk(config, song_list), deletion)
        self._fill_list_widget()
        # Set 'last_song' to `{}` after importing new and changing the `disk` for safety

    def import_songs(self) -> None:
        paths = self._file_explorer_many_files(SUPPORTED_SONG_FORMATS)
        import_songs(paths, SONGS_DIR)
        self.update_song_list(get_song_list(SONGS_DIR))

    def _order_shuffle_playlist(self) -> None:
        songs = list(get_song_list(SONGS_DIR))
        random.shuffle(songs)
        self.update_song_list(tuple(songs))

    def _order_alphabetical(self) -> None:
        songs = tuple(sorted(get_song_list(SONGS_DIR), key=lambda i: i[0]))
        self.update_song_list(songs)

    def _order_length(self, reverse: bool) -> None:
        songs = get_song_list(SONGS_DIR)

        song_objs: List[Tuple[TinyTag, str]] = []
        for song in songs:
            path = os.path.join(SONGS_DIR, song)
            song_objs.append((TinyTag.get(path), song))

        sorted_songs = sorted(song_objs, key=lambda i: i[0].duration, reverse=reverse)
        self.update_song_list(tuple(map(lambda i: i[1], sorted_songs)))

    def order_by(self, option: Literal['shuffle', 'alphabetical', 'length', 'original'],
                 *args: Any, **kwargs: Any) -> None:
        options: Dict[str, Callable[..., None]] = {
            'shuffle': self._order_shuffle_playlist,
            'alphabetical': self._order_alphabetical,
            'length': self._order_length,
            'original': lambda: self.update_song_list(get_song_list(SONGS_DIR))
        }
        options[option](*args, **kwargs)

    def delete_song(self) -> None:
        lang = get_active_language()
        dt = get_datetime()

        song = self.player.disk.song_name
        lang = get_active_language()
        prompt = f"Are you sure you want to delete {song}?"
        title = "Delete song"
        title, prompt = (get_message(lang, 'delete_song'),
                         get_message(lang, 'delete_song_prompt', song))

        reply = self.askyesno(title, prompt)
        if reply and len(os.listdir(SONGS_DIR)) > 2:
            to_delete = self.player.disk.song_mp3
            delete_song(SONGS_DIR, to_delete)
            self.update_song_list(get_song_list(SONGS_DIR), deletion=True)
            self.next_song()
            log = get_message(lang, 'song_deleted', f"`{song}`")
            logger.success(log)
            self._show_popup(log)
            key = get_delay_key(self.player.disk)
            if key in config:
                config.remove_key(key)
                log = f"{dt} {get_message('language', 'delay_unset', song)}"
                logger.info(log)
        else:
            logger.debug(f"{dt} {get_message(lang, 'delete_aborted')}")

    def display_lyric(self, line: Union[str, None]) -> None:
        if line is not None:
            self.lyrics_lbl.setText(line)
        else:
            self.lyrics_lbl.setText("")

    def update_song(self) -> None:
        self.current_playing_lbl.setText(self.player.disk.song_name)
        self.music_container.setCurrentRow(self.player.disk.song_index)

        self.sound = pyglet.media.Player()
        self.current_song = pyglet.media.load(self.player.disk.song_path)

        self.lyrics = Renderer(get_lyrics_file(LYRICS_DIR, self.player, Renderer.EXTENSION))

        self.sound.queue(self.current_song)

        self.sound.play() if self.player else self.sound.pause()

    def set_lyrics_delay(self) -> None:
        lang = get_active_language()
        title, prompt = get_message(lang, 'lyrics_delay'), get_message(lang, 'lyrics_delay_prompt')
        delay, _ = QInputDialog.getText(self, title, prompt)
        key = get_delay_key(self.player.disk)
        set_lyrics_delay(key, delay, config)

    def edit_modes_off(self) -> None:
        self.trim_mode = False
        self.lyrics_mode = False
        self.time1_inp.setText('0:00:00')
        self.time2_inp.setText('0:00:00')
        self.action_lbl.setText('')
        self.action_lbl.hide()

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
        slider.sliderPosition = x
        slider.update()
        slider.repaint()

    def update(self) -> None:
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
