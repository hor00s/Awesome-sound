from types import MappingProxyType
from itertools import combinations
from actions import Language
from typing import (
    Literal,
    Tuple,
    Any
)


class LanguageError(Exception):
    ...


LANGUAGE = MappingProxyType({
    # ENGLISH
    'en': MappingProxyType({
        'init_app_msg': 'Initializing application',
        'init_media_msg': 'Setting up media devices',
        'init_complete_msg': 'Ui setup is completed',
        'app_terminated_msg': 'Application terminated',
        'invalid_timestamp': 'Invalid timestamp',
        'clear_logs': 'Clear logs',
        'clear_logs_prompt': 'Are you sure you want to clear the logs?',
        'logs_cleared': 'Logs have been cleared',
        'restore_settings': 'Restore settings',
        'restore_settings_prompt': 'Are you sure you want to restore your settings?',
        'settings_restored': 'Settings have been restored',
        'song_exported': 'A song has been exported',
        'rename_song': 'Rename',
        'choose_name': 'Choose a new name',
        'renamed_popup': 'Song renamed successfully',
        'download_target_dir': 'Choose target directory',
        'download_dir_changed': 'Download directory has been changed',
        'download_dir_canceled': 'Change download directory has been canceled',
        'lyrics_edit': 'Lyrics edit',
        'lyrics_line': 'Add line:',
        'trim_mode': 'Trim mode',
        'trim_song': 'Trim song',
        'trim_confirm': 'Do you confirm you want to trim this song?',
        'trim_success': 'Song has been trimmed',
        'trim_abort': 'Trim has been aborted',
        'delete_lyrics': 'Delete lyrics',
        'delete_prompt': 'Are you sure you want to delete the lyrics for ',  # song name
        'lyrics_deleted': 'Lyrics has been removed for ',  # song name
        'delay_deleted': 'Delay has been unser for ',  # song name
        'lyrics_not_found': 'No lyrics found for ',  # song name
        'lyrics_aborted': 'Lyrics deletion has been aborted',
        'set_frame_rate': 'Set your frame rate between ',  # min_framerate -> max_framerate
        'frame_edit': 'Frame rate has been changed. Restart the app for the changed to be applied',
        'frame_invalid': 'Invalid value for frame rate ',  # `x`
        'logs': 'Logs',
        'shortcuts': 'Shortcuts',
        'delete_song': 'Delete song',
        'delete_song_prompt': 'Are you sure you want to delete ',  # song name
        'song_deleted': 'Song has been deleted ',  # song name
        'delay_unset': 'Delay has been unset for ',  # song name
        'delete_aborted': 'Delete action has been aborted',
        'lyrics_delay': 'Lyrics delay',
        'lyrics_delay_prompt': 'Set your delay',
        'delay_changed': 'Delay was changed for ',  # song name
        'delay_set': 'Delay has been set for',
        'delay_invalid': 'Invalid value for delay',
        'import_lyrics': 'Lyrics has been imported from ',  # src directory
        'language_changed': 'App\'s language has been changed',
        'general_error': 'an error has occurred',
        'edit_lyrics_prompt': 'Edit lyrics for ',  # song name
        'edit_lyrics': 'Edit lyrics',
        'lyrics_saved': 'Lyrics have been saved successfully for ',  # song name
    }),

    # GREEK
    'gr': MappingProxyType({
        'init_app_msg': 'Εκκίνηση εφαρμογής',
        'init_media_msg': 'Ρύθμιση πολυμέσων',
        'init_complete_msg': 'Η ρύθμιση του UI ολοκληρώθηκε',
        'app_terminated_msg': 'Η εφαρμογή τερματίστηκε',
        'invalid_timestamp': 'Μη έγκυρη χρονική σήμανση',
        'clear_logs': 'Εκκαθάριση αρχείων καταγραφής',
        'clear_logs_prompt': 'Είσαι σίγουρος ότι θέλεις να διαγράψεις τα αρχεία καταγραφής;',
        'logs_cleared': 'Τα αρχεία καταγραφής έχουν διαγραφεί',
        'restore_settings': 'Επαναφορά ρυθμίσεων',
        'restore_settings_prompt': 'Είστε βέβαιοι ότι θέλετε να επαναφέρετε τις ρυθμίσεις σας',
        'settings_restored': 'Οι ρυθμίσεις έχουν αποκατασταθεί',
        'song_exported': 'Έγινε εξαγωγή ενός τραγουδιού',
        'rename_song': 'Μετονομασία',
        'choose_name': 'Διάλεξε καινούριο όνομα',
        'renamed_popup': 'Το τραγούδι μετονομάστηκε με επιτυχία',
        'download_target_dir': 'Επιλέξτε προορισμό λήψεων',
        'download_dir_changed': 'Ο προορισμός λήψεων άλλαγε',
        'download_dir_canceled': 'Η αλλαγή προορισμού λήψεων ακυρώθηκε',
        'lyrics_edit': 'Επεξεργασία στίχων',
        'lyrics_line': 'Προσθήκη γραμμής:',
        'trim_mode': 'Λειτουργία περικοπής',
        'trim_song': 'Περικοπή τραγουδιού',
        'trim_confirm': 'Επιβεβαιώνετε ότι θέλετε να περικόψετε αυτό το τραγούδι;',
        'trim_success': 'Το τραγούδι έχει κοπεί',
        'trim_abort': 'Η περικοπή έχει ματαιωθεί',
        'delete_lyrics': 'Διαγραφή στίχων',
        'delete_prompt': 'Είστε βέβαιοι ότι θέλετε να διαγράψετε τους στίχους για το τραγούδι ',
        'lyrics_deleted': 'Οι στίχοι έχουν αφαιρεθεί για το τραγούδι ',
        'delay_deleted': 'Η καθυστέρηση αφαιρέθηκε για το τραγούδι ',
        'lyrics_not_found': 'Δεν βρέθηκαν στίχοι για το τραγούδι ',
        'lyrics_aborted': 'Η διαγραφή στίχων ματαιώθηκε',
        'set_frame_rate': 'Ρυθμίστε το framerate ',
        'frame_edit': 'Το framerate άλλαξε. Επανεκκινήστε την εφαρμογή για να εφαρμοστεί η αλλαγή',
        'frame_invalid': 'Μη έγκυρη τιμή για framerate ',
        'logs': 'Αρχεία καταγραφής',
        'shortcuts': 'Shortcuts',
        'delete_song': 'Διαγραφή τραφουδιού',
        'delete_song_prompt': 'Είστε βέβαιοι ότι θέλετε να διαγράψετε το ',
        'song_deleted': 'Το τραγούδι έχει διαγραφεί ',
        'delay_unset': 'Η καθυστέρηση αφαιρέθηκε για ',
        'delete_aborted': 'Η ενέργεια διαγραφής ματαιώθηκε',
        'lyrics_delay': 'Καθυστέρηση στίχων',
        'lyrics_delay_prompt': 'Ρυθμίστε την καθυστέρηση για τους στίχους',
        'delay_changed': 'Η καθυστέρηση στίχων άλλαξε για το ',
        'delay_set': 'Η καθυστέρηση στίχων ορίστηκε για το ',
        'delay_invalid': 'Μη έγκυρη τιμή',
        'import_lyrics': 'Οι στίχοι έχουν εισαχθεί από ',
        'language_changed': 'Η γλώσσα της εφαρμογής άλλαξε',
        'general_error': 'Παρουσιάστηκε σφάλμα',
        'edit_lyrics_prompt': 'Επεξεργασία στίχων για το ',
        'edit_lyrics': 'Επεξεργασία στίχων',
        'lyrics_saved': 'Οι στίχοι αποθηκεύτηκαν με επιτυχία για το ',
    }),
})


def get_available_languages() -> Tuple[str, ...]:
    return tuple(LANGUAGE.keys())


def find_diff() -> str:
    """In case of language inequality error, find the differences
    between all the assigned languages for quicker fix
    """
    text = ""
    df = []
    data = tuple(combinations(LANGUAGE, 2))
    for d1, d2 in data:
        get_dif = set(LANGUAGE[d1].keys()) ^ set(LANGUAGE[d2].keys())
        if get_dif:
            form = {'between': (d1, d2), 'values': get_dif}
            df.append(form)

    for diff in df:
        text += "\n\nDiff:\n"
        text += f"- {diff}\n"
    return text


count = set(len(v) for (_, v) in LANGUAGE.items())
if len(count) > 1:
    raise LanguageError(f"Inequality found between languages {find_diff()}")


Field = Literal[
    'init_app_msg',
    'init_media_msg',
    'init_complete_msg',
    'app_terminated_msg',
    'invalid_timestamp',
    'clear_logs',
    'clear_logs_prompt',
    'logs_cleared',
    'restore_settings',
    'restore_settings_prompt',
    'settings_restored',
    'song_exported',
    'rename_song',
    'choose_name',
    'renamed_popup',
    'download_target_dir',
    'download_dir_changed',
    'download_dir_canceled',
    'lyrics_edit',
    'lyrics_line',
    'trim_mode',
    'trim_song',
    'trim_confirm',
    'trim_success',
    'trim_abort',
    'delete_lyrics',
    'delete_prompt',
    'lyrics_deleted',
    'delay_deleted',
    'lyrics_not_found',
    'lyrics_aborted',
    'set_frame_rate',
    'frame_edit',
    'frame_invalid',
    'logs',
    'shortcuts',
    'delete_song',
    'delete_song_prompt',
    'song_deleted',
    'delay_unset',
    'delete_aborted',
    'lyrics_delay',
    'lyrics_delay_prompt',
    'delay_changed',
    'delay_set',
    'delay_invalid',
    'import_lyrics',
    'language_changed',
    'general_error',
    'edit_lyrics_prompt',
    'edit_lyrics',
    'lyrics_saved',
]


def get_message(selected_lang: Language, field: Field, *args: Any) -> str:
    return f"{LANGUAGE[selected_lang][field]} {' '.join(map(str, args))}"
