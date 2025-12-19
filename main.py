# POWER SHELL COMMAND TO GENERATE .py file FROM .ui file
# ======================================================
# pyside6-uic tpmania_gui.ui -o tpmania_gui.py
#
#
# POWER SHELL COMMAND TO LAUNCH Pyside6 Designer
# pyside6-designer
# ======================================================

# Import the generated UI class, and backend functions
from GUI.tpmania_gui import Ui_MainWindow
from GUI.generic_worker import GenericWorker
from GUI.scrolling_label import ScrollingLabel
from GUI.sequence_class import Sequence
from GUI.tpmania_message_boxes import (
    TPManiaMessageBox,
    timing_window_selection_error_box,
    files_confirmed_message_box,
    serial_connection_error_box,
    save_to_device_successful,
    unknown_error_message_box,
    sequence_save_location_unspecified,
    no_serial_communication_message_box,
    timeout_message_box,
    reset_files_message_box,
    no_file_on_ram_message_box,
    no_sequence_file_selected,
    no_audio_file_selected,
    found_the_secret_key,
    received_sequence_from_device,
    no_files_selected,
)
from GUI.helper import (
    enumerate_serial_ports,
    combine_with_beep,
    ms_to_time,
    get_wav_length,
    strip_path,
    strip_file,
    initialise_mixer,
    configure_mixer_volume,
    calc_error_from_timing_window,
)

# Import Pyside6 Modules
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QDialogButtonBox,
    QFileDialog,
    QMessageBox,
    QHeaderView,
)
from PySide6.QtGui import (
    QIcon,
    QFont,
    QCloseEvent,
    QPixmap,
)
from PySide6.QtCore import (
    QSize,
    QTimer,
    QThread,
    QRect,
    Qt,
    QStandardPaths,
)

# Import Additional Modules
import math
import os
import serial
import sys
import time
import warnings
from pathlib import Path

# Used for type hinting
from typing import Any, Callable

# Imports pygame, and blocks its printed launch messages
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from pygame import mixer  # For playing audio

# Assorted String Constants
EMPTY_STRING = ""
BACK_SLASH = "\\"
SLASH = "/"
EEPROM = "EEPROM"
RAM = "RAM"

# Media Directories
ASSETS_DIR = "assets"
DEFAULT_SAVE_DIR = "generated"

# Determine Users Download directory, and set save directory
# for generated files
downloads_path = str(Path.home() / "Downloads")
fixed_download_dir = list(downloads_path)

for i, char in enumerate(fixed_download_dir):
    if (char == BACK_SLASH):
        fixed_download_dir[i] = SLASH

USER_DOWNLOADS_DIR = f"{''.join(fixed_download_dir)}/{DEFAULT_SAVE_DIR}"
print(f"USER_DOWNLOADS_DIR: {USER_DOWNLOADS_DIR}")

# Create the directory if it doesn't exist
directory = Path(f"{USER_DOWNLOADS_DIR}")
directory.mkdir(parents=True, exist_ok=True)

# Essential Media Paths
WINDOW_ICON_PATH = f"{ASSETS_DIR}/setup.ico"
PLAY_ICON_PATH = f"{ASSETS_DIR}/play.png"
PAUSE_ICON_PATH = f"{ASSETS_DIR}/pause.png"
REPLAY_BUTTON_PATH = f"{ASSETS_DIR}/replay.png"
VOLUME_ICON_PATH = f"{ASSETS_DIR}/volume.png"
SYNC_BEEP_PATH = f"{ASSETS_DIR}/5khz_tone_1ms_mono.wav"
THREAD_INDICATOR_PATH = f"{ASSETS_DIR}/red_status.png"
READY_INDICATOR_PATH = f"{ASSETS_DIR}/green_status.png"
MYSTERY_PATH = f"{ASSETS_DIR}/eye.bmp"

# User generated file paths
AUDIO_TYPE = ".wav"
SEQUENCE_TYPE = ".tsq"
SYNCHRONISED_USER_AUDIO_PATH = f"{USER_DOWNLOADS_DIR}/delayed{AUDIO_TYPE}"

print(f" Synchronised user audio path: {SYNCHRONISED_USER_AUDIO_PATH}")

# Sequence file constants
BUFFER = "---"
BAR_DIVIDER = ","
FILE_END = ";"

# Default sequence parameters
DEFAULT_NAME = EMPTY_STRING
DEFAULT_ARTIST = EMPTY_STRING
DEFAULT_BPM = "0"
DEFAULT_OFFSET = "0"
DEFAULT_DIFFICULTY = "N/A"

# Sequence file restrictions
MAX_BEATS = 300
HALF_BEATS = 8

# GUI page indexs
HOME_PAGE = 0
SETTINGS_PAGE = 1
MAIN_PAGE = 2
TIMING_WINDOWS_PAGE = 3
MYSTERY_PAGE = 4

# File handling Modes
READ_MODE = 'r'
WRITE_MODE = 'w'

# GUI object settings
MAIN_WINDOW_WIDTH = 300
MAIN_WINDOW_HEIGHT = 450
TPMANIA_TITLE = "tpmania"
AUDIO_FILE = f"Audio files (*{AUDIO_TYPE})"
SEQUENCE_FILE = f"Sequence files (*{SEQUENCE_TYPE})"
NO_FILE_TEXT = "No File Selected"
SELECT_OPTION_TEXT = "--select"
UNKNOWN = "Unknown"
DEFAULT_FONT_TYPE = "Segoe UI"

# Audio Player Config
MIXER_VOLUME = 0.3
DEFAULT_VOLUME_SCALE = MIXER_VOLUME * 100
DEFAULT_AUDIO_LENGTH_TEXT = "00:00"
DEFAULT_ELAPSED = f"{DEFAULT_AUDIO_LENGTH_TEXT} / {DEFAULT_AUDIO_LENGTH_TEXT}"
DEFAULT_AUDIO_DURATION = 0  # ms

# Volume slider
MIN_VOLUME = 0
MAX_VOLUME = 100
VOLUME_STEP_RATE = 4

# Playback progress bar
DEFAULT_PROGRESS = 0
PROGRESS_MIN = 0
PROGRESS_MAX = 220
MS_PER_SEC = 1000

# Init GUI Variables
DEFAULT_SERIAL_CONNECTION = None
DEFAULT_AUDIO_PLAYING_FLAG = False
DEFAULT_AUDIO_NEVER_PLAYED_FLAG = True
DEFAULT_THREAD_RUNNING_FLAG = False
DEFAULT_THREAD = None
DEFAULT_WORKER = None
DEFAULT_RESPONSE_CODE = -1

# Timing window settings
MIN_TIMING_WINDOW = 1
MAX_TIMING_WINDOW = 500
TIMING_WINDOW_LENGTH = 4
DEFAULT_SLIDER_VALUE = 250
DEFAULT_TIMING_WINDOWS = (
    200,
    300,
    400,
    500,
)

# Serial communication indicator characters
SQ_TO_RAM_CHAR = 'S'
SQ_TO_EEPROM_CHAR = 'E'
SQ_TO_BOTH_CHAR = 'B'
TW_TO_EEPROM_CHAR = 'T'
LOAD_SQ_FROM_RAM_CODE = 'R'
LOAD_SQ_FROM_EEPROM_CODE = 'N'
REQUEST_TIMING_WINDOWS_CODE = 'W'
END_TRANSFER = 'X'

# New comm protocol
READY_CODE = "RDY"
NULL_CHAR = '\x00'

# Serial communication baud rate, and encoding type
BAUD_RATE = 9600
DATA_ENCODING_TYPE = "ascii"

# Serial communication and read/write timeout (in seconds).
# Function reading/writing will return an empty string after
# the timeout, this is to prevent blocking.
READ_TIMEOUT = 0.1
WRITE_TIMEOUT = 0.1

# Process Exit Codes
STATUS_TIMEOUT = -1
STATUS_SUCCESS = 0
STATUS_DEVICE_NOT_CONNECTED = 1
STATUS_SAVE_LOCATION_UNSPECIFIED = 2
STATUS_NO_SEQUENCE_FILE_SELECTED = 3
STATUS_RECEIVED_EEPROM_TSQ = 4
STATUS_RECEIVED_RAM_TSQ = 5
STATUS_NO_FILE_ON_RAM = 6
STATUS_TIMING_WINDOWS_USAGE_ERROR = 7
STATUS_UNKNOWN_ERROR = 8
STATUS_NO_PORT_SET = 9
STATUS_FILES_CONFIRMED = 10
STATUS_FILES_RESET = 11
STATUS_FILENAME_MISMATCH = 12
STATUS_NO_AUDIO_FILE = 13
STATUS_MITIGATE_AUDIO_DELAY = 14
STATUS_NO_FILES_SELECTED = 15

# Maximum time (in seconds) to wait
# on process before exiting thread
MAX_WAIT_TIME = 5

TINY_WAIT = 0.002  # 2ms
SMALL_WAIT = 0.01  # 10 ms
MEDIUM_WAIT = 0.025  # 25 ms
DECENT_WAIT = 0.1  # 100 ms
BIG_WAIT = 0.4  # 400 ms
EXTREME_WAIT = 1  # 1000 ms

# Timer interupt rates (all in milliseconds)
PERIODIC_CHECK_TIMER = 1000
MUSIC_TIMER = 100
SCROLL_INTERVAL_TIMER = 25  # ~40 FPS

# Scrolling Label Constants
ACTIVE = True
INACTIVE = False
MAGIC_NUMBER = 17
PIXLES_PER_TICK = 1  # Pixels scrolled per frame

# Status Bar Timeout
STATUS_ALERT_TIMEOUT = 3000


class MyWindow(QMainWindow):
    ''' Main application window for the GUI '''
    def __init__(self):
        '''
        Initialises the GUI, this includes setting:

        - Window titles
        - Window and button icons
        - Linking buttons to functions
        - Window geometry
        - Initialising timing windows
        - Refreshing serial ports
        - Configuring timers
        - Tracked GUI variables to default

        '''
        super(MyWindow, self).__init__()
        self.ui = Ui_MainWindow()  # Create an instance of the UI class
        self.ui.setupUi(self)  # Set up the UI in the main window

        # Initialise Threading
        self.thread_tracker = {}
        self.worker_tracker = {}
        self.thread_id = 0

        # Initialise GUI variables
        self._sequence = Sequence()
        self._current_timing_windows = DEFAULT_TIMING_WINDOWS
        self._serial_connection = DEFAULT_SERIAL_CONNECTION
        self._serial_port = EMPTY_STRING
        self._sequence_save_path = EMPTY_STRING
        self._ready_for_rendering = False
        self._block_scrolling = False

        # Flags
        self._thread_is_running = DEFAULT_THREAD_RUNNING_FLAG
        self._audio_playing = DEFAULT_AUDIO_PLAYING_FLAG
        self._audio_never_played = DEFAULT_AUDIO_NEVER_PLAYED_FLAG
        self._response_code = DEFAULT_RESPONSE_CODE

        # Temporary storage variables
        self._temp_timing_windows = DEFAULT_TIMING_WINDOWS
        self._temp_audio_path = EMPTY_STRING
        self._temp_sequence_path = EMPTY_STRING

        # Scrollable text labels list
        self._scrollable_labels: list[ScrollingLabel | None] = []

        # Users Selected Audio file
        self._audio_path = EMPTY_STRING

        # Audio File Lengths
        self._sync_beep_length = int(
            get_wav_length(SYNC_BEEP_PATH) * MS_PER_SEC
        )
        self._audio_file_duration = DEFAULT_AUDIO_DURATION
        self._audio_length_text = DEFAULT_AUDIO_LENGTH_TEXT

        # Set visual window settings
        self.setWindowIcon(QIcon(WINDOW_ICON_PATH))
        self.setWindowTitle(TPMANIA_TITLE)
        self.setFixedSize(MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)

        # Configure pages
        self.configure_home_page()
        self.configure_files_page()
        self.configure_metadata_page()
        self.configure_timing_windows_page()

        # Configure global features
        self.configure_audio_playback()
        self.configure_threading_indicators()

        # Mystery
        self._secret_found = False
        self.configure_mystery_page()

        # Configures timers, and starts global check timer
        self.configure_timers()

        # Disable additional features
        self.ui.volumeSlider.hide()
        self.ui.volumeIcon.hide()
        self.ui.AudioSynchronisation.setChecked(True)

    def configure_timers(self) -> None:
        ''' Configures the GUI's various timers '''
        # Timer for updating audio progress bar
        self.music_timer = QTimer(self)
        self.music_timer.timeout.connect(self.update_time_elapsed)

        # Timer for updating scrolling labels
        self.label_update_timer = QTimer(self)
        self.label_update_timer.timeout.connect(self.trigger_label_update)

        # Global constant timer, which checks for updates every second
        self.periodic_check_timer = QTimer(self)
        self.periodic_check_timer.timeout.connect(self.periodic_check)
        self.periodic_check_timer.start(PERIODIC_CHECK_TIMER)

    def inc_thread_id(self) -> None:
        ''' Incriments the global thread id number '''
        self.thread_id += 1

    def configure_scrollable_metadata_labels(self) -> None:
        ''' Creates the scrollable metadata labels for Name and Artist '''
        font = QFont("Segoe UI", 9)

        # Create Scrolling name label
        self.NameDisplay = (
            ScrollingLabel(
                parent=self.ui.MetadataLabelsWidget,
                text=UNKNOWN,
                font=font
            )
        )
        self.NameDisplay.setObjectName(u"NameDisplay")
        self.NameDisplay.setGeometry(QRect(10, 30, 130, 16))
        self._scrollable_labels.append(self.NameDisplay)

        # Create scrolling artist label
        self.ArtistDisplay = (
            ScrollingLabel(
                parent=self.ui.MetadataLabelsWidget,
                text=UNKNOWN,
                font=font,
            )
        )
        self.ArtistDisplay.setObjectName(u"ArtistDisplay")
        self.ArtistDisplay.setGeometry(QRect(10, 10, 130, 16))
        self._scrollable_labels.append(self.ArtistDisplay)

    def configure_filename_labels(self) -> None:
        '''
        Configures the scrollable audio/sequence filename labels
        '''
        self.AudioFilenameLabel = (
            ScrollingLabel(self.ui.FileSelectionFrame, NO_FILE_TEXT)
        )
        self.AudioFilenameLabel.setObjectName(u"AudioFilenameLabel")
        self.AudioFilenameLabel.setGeometry(QRect(90, 40, 110, 16))

        self.SequenceFilenameLabel = (
            ScrollingLabel(self.ui.FileSelectionFrame, NO_FILE_TEXT)
        )
        self.SequenceFilenameLabel.setObjectName(u"SequenceFilenameLabel")
        self.SequenceFilenameLabel.setGeometry(QRect(90, 60, 110, 16))

        self._scrollable_labels.append(self.AudioFilenameLabel)
        self._scrollable_labels.append(self.SequenceFilenameLabel)

    def configure_home_page(self) -> None:
        ''' Configures all interactive elements and tooltips on home page '''
        # Configure navigation buttons
        self.ui.fileSelection.clicked.connect(self.settings_page)
        self.ui.metadataDisplay.clicked.connect(self.metadata_page)
        self.ui.timingWindows.clicked.connect(self.timing_windows_page)

        # Configure serial port display and selection
        self.ui.ConfigurePort.button(QDialogButtonBox.Save).clicked.connect(
            self.handle_save_serial_port,
        )
        self.ui.ConfigurePort.button(QDialogButtonBox.Retry).clicked.connect(
            self.refresh_serial_port,
        )

        # Configure tool tips
        self.ui.ConfigurePort.button(QDialogButtonBox.Save).setToolTip(
            "Save the selected COM Port"
        )
        self.ui.ConfigurePort.button(QDialogButtonBox.Retry).setToolTip(
            "Reset the selected COM Port"
        )
        self.ui.timingWindows.setToolTip(
            "Update and view device timing windows"
        )
        self.ui.metadataDisplay.setToolTip(
            "View sequence metadata, and play audio"
        )
        self.ui.fileSelection.setToolTip("Save and update sequences")
        self.ui.SerialPorts.setToolTip("Select serial port")

        # Intialise available serial ports
        self.refresh_serial_port()

    def configure_files_page(self) -> None:
        ''' Configures all interactive elements and tooltips on files page '''
        # Configure scrolling filename labels
        self.configure_filename_labels()

        # Configure file selection/retrieval/saving buttons
        self.ui.homeFromFiles.clicked.connect(self.go_home)
        self.ui.SelectSequenceButton.clicked.connect(
            self.change_sequence_file_path,
        )
        self.ui.SelectAudioButton.clicked.connect(
            self.change_audio_file_path,
        )
        self.ui.SaveRamSequence.clicked.connect(
            self.get_ram_sequence,
        )
        self.ui.SaveEepromSequence.clicked.connect(
            self.get_eeprom_sequence,
        )
        self.ui.SaveSettingsButton.clicked.connect(
            self.save_sequence_to_device,
        )
        self.ui.ConfirmSelection.button(QDialogButtonBox.Save).clicked.connect(
            self.handle_file_selection_confirmation
        )
        (
            self
            .ui
            .ConfirmSelection
            .button(QDialogButtonBox.Reset)
            .clicked
            .connect(self.handle_file_resetting)
        )

        # Configure tool tips
        self.ui.ConfirmSelection.button(QDialogButtonBox.Save).setToolTip(
            "Save file preferences"
        )
        self.ui.ConfirmSelection.button(QDialogButtonBox.Reset).setToolTip(
            "Reset file preferences"
        )
        self.ui.SaveSettingsButton.setToolTip(
            "Save sequence to specified location(s)"
        )
        self.ui.SaveToDeviceEEPROM.setToolTip("Select EEPROM")
        self.ui.SaveToDeviceRAM.setToolTip("Select RAM")
        self.ui.SaveRamSequence.setToolTip(
            "Save the file stored on device RAM"
        )
        self.ui.SaveEepromSequence.setToolTip(
            "Save the file stored on device EEPROM"
        )
        self.ui.SelectSequenceButton.setToolTip("Select sequence file")
        self.ui.SelectAudioButton.setToolTip("Select audio file")
        self.ui.homeFromFiles.setToolTip("Return to Home Page")

    def configure_metadata_page(self) -> None:
        ''' Configures all interactive elements and tooltips on info page '''

        # Link home navigation button
        self.ui.homeFromInfo.clicked.connect(self.go_home)

        self.configure_volume_slider()
        self.configure_progress_bar()
        self.configure_scrollable_metadata_labels()

        # Configure tool tips
        self.ui.homeFromInfo.setToolTip("Return to Home Page")
        self.ui.volumeIcon.setToolTip("Adjust playback volume (within GUI)")
        self.ui.AudioSynchronisation.setToolTip(
            "Adds synchronisation beep at beginning of audio"
        )

    def configure_timing_windows_page(self) -> None:
        '''
        Configures all interactive elements and tooltips on timing
        windows page, and initialise timing windows to default values.
        '''
        # Link buttons to functions
        self.ui.homeFromTW.clicked.connect(self.go_home)
        self.ui.SaveChoice.button(QDialogButtonBox.Apply).clicked.connect(
            self.apply_score_selection,
        )
        self.ui.SaveChoice.button(QDialogButtonBox.SaveAll).clicked.connect(
            self.handle_saving_timing_windows,
        )
        self.ui.SaveChoice.button(QDialogButtonBox.Reset).clicked.connect(
            self.handle_reset_timing_window,
        )
        self.ui.resetDeviceToDefaults.clicked.connect(
            self.set_timing_windows_to_defaults
        )

        self.configure_timing_windows_slider()

        # Disable row/column dimension editing in timing window table
        (
            self.ui
            .TimingWindowTable
            .verticalHeader()
            .setSectionResizeMode(QHeaderView.Fixed)
        )
        (
            self.ui
            .TimingWindowTable
            .horizontalHeader()
            .setSectionResizeMode(QHeaderView.Fixed)
        )

        # Configure tool tips
        self.ui.SaveChoice.button(QDialogButtonBox.Apply).setToolTip(
            "Update selected window locally"
        )
        self.ui.SaveChoice.button(QDialogButtonBox.SaveAll).setToolTip(
            "Save all windows to device"
        )
        self.ui.SaveChoice.button(QDialogButtonBox.Reset).setToolTip(
            "Reset and display devices current windows"
        )
        self.ui.homeFromTW.setToolTip("Return to Home Page")

        # Initialise timing windows
        self.initialise_timing_window(DEFAULT_TIMING_WINDOWS)

    def configure_mystery_page(self) -> None:
        ''' Configures mystery page elements, buttons and tooltips '''
        # Connect buttons
        self.ui.homeFromMystery.clicked.connect(self.go_home)
        self.ui.secretButton.clicked.connect(self._secret)
        self.ui.mysteryButton.clicked.connect(self._mystery)

        # Add image
        self.ui.mysteryLabel.setPixmap(QPixmap(MYSTERY_PATH))
        self.ui.mysteryLabel.setScaledContents(True)

        # Configure tooltips
        self.ui.mysteryButton.setToolTip("...stay far away from here...")
        self.ui.homeFromMystery.setToolTip("Return to Home Page")

    def configure_timing_windows_slider(self) -> None:
        ''' Configures the timing window slider settings in the GUI '''
        self.ui.horizontalSlider.valueChanged.connect(self.on_slider_changed)
        self.ui.horizontalSlider.setMinimum(MIN_TIMING_WINDOW)
        self.ui.horizontalSlider.setMaximum(MAX_TIMING_WINDOW)
        self.ui.horizontalSlider.setValue(DEFAULT_SLIDER_VALUE)
        self.ui.horizontalSlider.setToolTip("Adjust timing window")

    def configure_audio_playback(self) -> None:
        ''' Configure audio playback functionality '''
        # Link play/pause and replay buttons
        self.ui.AudioPlayback.clicked.connect(self.play_audio)
        self.ui.ReplayAudio.clicked.connect(self.thread_replay_audio)

        # Configure Icons
        self.ui.ReplayAudio.setIcon(QIcon(REPLAY_BUTTON_PATH))
        self.ui.AudioPlayback.setIcon(QIcon(PLAY_ICON_PATH))
        self.ui.AudioPlayback.setIconSize(QSize(
            self.ui.AudioPlayback.size().width(),
            self.ui.AudioPlayback.size().height(),
        ))

        # Configure tooltips
        self.ui.AudioPlayback.setToolTip("Play / Pause")
        self.ui.ReplayAudio.setToolTip("Replay audio")

    def configure_progress_bar(self) -> None:
        ''' Configure audio playback progress bar '''
        # Set default progress, and min/max range
        self.ui.progressBar.setValue(DEFAULT_PROGRESS)
        self.ui.progressBar.setRange(PROGRESS_MIN, PROGRESS_MAX)

    def configure_volume_slider(self) -> None:
        ''' Configure Volume Slider '''
        # Link button
        self.ui.volumeSlider.valueChanged.connect(self.on_volume_changed)

        # Set min/max and default volume, as well as step size
        self.ui.volumeSlider.setMinimum(MIN_VOLUME)
        self.ui.volumeSlider.setMaximum(MAX_VOLUME)
        self.ui.volumeSlider.setSingleStep(VOLUME_STEP_RATE)
        self.ui.volumeSlider.setValue(DEFAULT_VOLUME_SCALE)

        # Configure Icon
        self.ui.volumeIcon.setPixmap(QPixmap(VOLUME_ICON_PATH))
        self.ui.volumeIcon.setScaledContents(True)

    def configure_threading_indicators(self) -> None:
        ''' Configures the thread indicator on GUI '''
        # Hides indicator by default
        self.ui.threadIndicator.hide()

        # Sets Icons
        self.ui.threadIndicator.setPixmap(QPixmap(THREAD_INDICATOR_PATH))
        self.ui.threadIndicator.setScaledContents(True)
        self.ui.readyIndicator.setPixmap(QPixmap(READY_INDICATOR_PATH))
        self.ui.readyIndicator.setScaledContents(True)

        # Configure tooltips
        self.ui.threadIndicator.setToolTip("Thread is active!")
        self.ui.readyIndicator.setToolTip("No active processes")

    def get_thread(self, id: int) -> QThread | None:
        '''
        Returns the QThread instance associated with the thread id,
        or None if none running.
        '''
        return self.thread_tracker.get(id, None)

    def get_worker(self, id: int) -> GenericWorker | None:
        '''
        Returns the GenericWorker instance associated with the thread id,
        which is responsible for communicating between background threads
        and the main GUI instance.
        '''
        return self.worker_tracker.get(id, None)

    def get_sequence(self) -> Sequence:
        ''' Returns the Sequence class stored in GUI '''
        return self._sequence

    def get_audio_playing(self) -> bool:
        ''' Returns the tracked state of audio playback as bool '''
        return self._audio_playing

    def get_temp_audio_path(self) -> str:
        ''' Returns the temporarilty stored audio file path '''
        return self._temp_audio_path

    def get_temp_sequence_path(self) -> str:
        ''' Returns the temporarilty stored sequence file path '''
        return self._temp_sequence_path

    def get_audio_path(self) -> str:
        ''' Returns the configured audio file's path '''
        return self._audio_path

    def get_serial_port(self) -> str:
        ''' Returns the serial port currently in use by GUI '''
        return self._serial_port

    def get_serial_connection(self) -> serial.Serial | None:
        '''
        Returns the serial connection to the micro-controller (if connected),
        else returns None.
        '''
        return self._serial_connection

    def get_audio_never_played(self) -> bool:
        '''
        Returns True if the audio file being played,
        has never been played since being selected.
        Else returns False.
        '''
        return self._audio_never_played

    def get_current_timing_windows(self) -> tuple:
        '''
        Returns tuple of current timing windows,
        these are the values stored on the micro-controller.
        '''
        return self._current_timing_windows

    def get_temp_timing_windows(self) -> tuple:
        '''
        Returns tuple of temporary timing windows,
        these are the values displayed when timing
        windows are being adjusted but have not yet
        been saved.
        '''
        return self._temp_timing_windows

    def get_response_code(self) -> int:
        ''' Returns the most recent response code '''
        return self._response_code

    def get_sequence_save_path(self) -> str:
        ''' Returns sequence save path '''
        return self._sequence_save_path

    def get_sync_beep_length(self) -> int:
        ''' Returns the duration in ms, of the sync beep '''
        return self._sync_beep_length

    def get_audio_file_duration(self) -> int:
        ''' Returns the duration in ms of users audio file '''
        return self._audio_file_duration

    def get_audio_length_text(self) -> str:
        ''' Returns audio file length, in "MM:SS" format '''
        return self._audio_length_text

    def set_audio_length_text(self, length: str) -> None:
        ''' Set audio file length, in "MM:SS" format '''
        self._audio_length_text = length

    def set_sequence(self, sequence: Sequence) -> None:
        ''' Sets the sequence within the GUI '''
        self._sequence = sequence

    def set_thread(self, thread: QThread, id: int) -> None:
        ''' Sets thread instance being run in background by GUI '''
        self.thread_tracker[id] = thread

    def set_thread_is_running(self) -> None:
        ''' Sets flag for whether any thread is currently running '''
        if (len(self.thread_tracker) == 0):
            if self.ui.threadIndicator.isVisible():
                self.ui.threadIndicator.hide()
                self.ui.readyIndicator.show()
        else:
            if (not self.ui.threadIndicator.isVisible()):
                self.ui.threadIndicator.show()
                self.ui.readyIndicator.hide()

    def set_worker(self, worker: GenericWorker, id: int) -> None:
        ''' Adds a worker to the worker tracker dictionary '''
        self.worker_tracker[id] = worker

    def set_temp_audio_path(self, path: str) -> None:
        ''' Sets the temporarilty stored audio file path '''
        self._temp_audio_path = path

    def set_temp_sequence_path(self, path: str) -> None:
        ''' Sets the temporarilty stored audio file path '''
        self._temp_sequence_path = path

    def set_audio_path(self, path: str) -> None:
        ''' Sets the path of the .wav audio file '''
        self._audio_path = path

    def set_audio_playing(self, state: bool) -> None:
        ''' Sets the tracked state of audio playback '''
        self._audio_playing = state

    def set_audio_never_played(self, state: bool) -> None:
        '''
        Sets state that tracks if an audio file has been
        played since being selected.
        '''
        self._audio_never_played = state

    def set_serial_port(self, port: str) -> None:
        ''' Sets the serial port currently in use by GUI '''
        self._serial_port = port

    def set_current_timing_windows(self, windows: tuple) -> None:
        ''' Sets the timing windows currently stored on device '''
        self._current_timing_windows = windows

    def set_temp_timing_windows(self, windows: tuple) -> None:
        ''' Sets the temporary timing windows currently stored on device '''
        self._temp_timing_windows = windows

    def set_serial_connection(self, connection: serial.Serial | None) -> None:
        ''' Sets the GUI Serial Connection '''
        self._serial_connection = connection

    def set_response_code(self, response: int) -> None:
        ''' Set most recent response code '''
        self._response_code = response

    def set_sequence_save_path(self, path: str) -> None:
        ''' Set the sequence save path '''
        self._sequence_save_path = path

    def set_audio_file_duration(self, duration: int) -> None:
        ''' Sets the tracked duration of the users audio file in ms '''
        self._audio_file_duration = duration

    def save_serial_connection(self) -> int | None:
        '''
        Attempts to establish a serial connection with the micro-controller
        using the currently selected serial port.

        Returns:
            (int): Exit status of process, or None if no status to report
        '''
        # If no port is selected, the connection is set to None.
        # Then an error message is prompted after exiting
        if (self.get_serial_port() == EMPTY_STRING):
            self.set_serial_connection(None)
            return STATUS_NO_PORT_SET

        # Establish connection
        connection = serial.Serial(
                self.get_serial_port(),
                BAUD_RATE,
                timeout=READ_TIMEOUT,
                write_timeout=WRITE_TIMEOUT,
            )

        # Set connection
        self.set_serial_connection(connection)

    def refresh_serial_port(self) -> None:
        '''
        Refreshes the list of available serial ports shown in GUI combo box,
        and closes any existing serial connection.
        '''
        self.ui.SerialPorts.clear()

        # Close previous serial connection
        if (self.get_serial_connection() is not None):
            self.get_serial_connection().close()

        # Find valid ports (if any) and add then to combo box
        try:
            for i, port in enumerate(enumerate_serial_ports()):
                self.ui.SerialPorts.addItem(EMPTY_STRING)
                self.ui.SerialPorts.setItemText(i, f"{port[0]}")
                self.set_serial_port(EMPTY_STRING)
        except RuntimeError:
            return

    def handle_save_serial_port(self) -> None:
        ''' Saves serial port with a threaded process '''
        self._start_threaded_task(self.save_serial_port)

    def save_serial_port(self) -> int | None:
        '''
        Saves the serial port selected in the combo box and establishes
        a new serial connection.

        If the selected port is the same as the currently set port,
        the function returns without making changes.

        Returns:
            (int): Exit status of process, or None if successful
        '''
        # Check if the serial port is already set
        if (self.ui.SerialPorts.currentText() == self.get_serial_port()):
            # Return if no serial port is set
            if (self.get_serial_port() != EMPTY_STRING):
                return

        # Save serial port and establish serial connection
        self.set_serial_port(self.ui.SerialPorts.currentText())
        return self.save_serial_connection()

    def metadata_page(self) -> None:
        '''
        Switches the GUI to the main page, which displays
        sequence metadata and audio playback controls.
        '''
        self.ui.stackedWidget.setCurrentIndex(MAIN_PAGE)

    def go_home(self) -> None:
        ''' Takes user back to home page of GUI '''
        self.ui.stackedWidget.setCurrentIndex(HOME_PAGE)

    def settings_page(self) -> None:
        '''
        Configures and displays the settings page by updating audio/sequence
        file labels, refreshing serial port if necessary, and initialising
        timing windows. If user had unsaved changes in settings, they be reset.
        '''
        # Resets sequence/audio file labels if unsaved changes were made
        audio_path = self.get_audio_path()
        sequence_path = self.get_sequence().get_sequence_path()
        if (audio_path == EMPTY_STRING):
            self.AudioFilenameLabel.setText(NO_FILE_TEXT)
        else:
            self.AudioFilenameLabel.setText(
                strip_path(self.get_audio_path())
            )
        if (sequence_path == EMPTY_STRING):
            self.SequenceFilenameLabel.setText(NO_FILE_TEXT)
        else:
            self.SequenceFilenameLabel.setText(
                strip_path(self.get_sequence().get_sequence_path())
            )

        # Refreshes serial port list, if no port is saved
        serial_port = self.get_serial_port()
        if (serial_port == EMPTY_STRING):
            self.refresh_serial_port()

        # Refresh timing windows
        self.initialise_timing_window(self.get_current_timing_windows())

        # Go to settings page
        self.ui.stackedWidget.setCurrentIndex(SETTINGS_PAGE)

    def timing_windows_page(self) -> None:
        ''' Sets GUI page to the timing windows settings page '''
        self.ui.stackedWidget.setCurrentIndex(TIMING_WINDOWS_PAGE)

    def change_file_path(self, file_type: str) -> str:
        '''
        Opens a file selection dialog for user to select a file,
        and returns the chosen file path.

        Parameters:
            file_type (str): File type filter for the selection dialog

        Returns:
            (str): The selected file path, or an empty string if cancelled
        '''
        path, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select File',
            dir=QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.DownloadLocation
            ),
            filter=file_type,
        )
        return path

    def change_sequence_file_path(self) -> None:
        '''
        Allows the user to change the sequence file path and updates the
        corresponding UI label and temporary storage.
        '''
        path = self.change_file_path(SEQUENCE_FILE)
        if (path != EMPTY_STRING):
            self.set_filename_labels_inactive()
            self.SequenceFilenameLabel.setText(strip_path(path))
        self.set_temp_sequence_path(path)

    def change_audio_file_path(self) -> None:
        '''
        Allows the user to change the audio file path and updates the
        corresponding UI label and temporary storage.
        '''
        path = self.change_file_path(AUDIO_FILE)
        if (path != EMPTY_STRING):
            self.set_filename_labels_inactive()
            self.AudioFilenameLabel.setText(strip_path(path))
        self.set_temp_audio_path(path)

    def load_sequence(self) -> None:
        '''
        Loads and parses the current sequence file, updating the GUI with
        metadata such as name, difficulty, BPM, artist, offset, and length.
        '''
        # Ignore if no sequence selected
        if (self.get_sequence().get_sequence_path() == EMPTY_STRING):
            return

        self.get_sequence().parse_sequence()

        # Name
        if (self.get_sequence().get_name() not in (EMPTY_STRING, UNKNOWN)):
            self.NameDisplay.setText(
                f"{self.get_sequence().get_name()}"
            )

        # Difficulty
        if (self.get_sequence().get_difficulty() != EMPTY_STRING):
            self.ui.DifficultyDisplay.setText(
                f"{self.get_sequence().get_difficulty()}"
            )

        # BPM
        if (self.get_sequence().get_bpm() != EMPTY_STRING):
            self.ui.BPMDisplay.setText(
                f"{self.get_sequence().get_bpm()}"
            )

        # Artist
        if (self.get_sequence().get_artist() not in (EMPTY_STRING, UNKNOWN)):
            self.ArtistDisplay.setText(
                f"{self.get_sequence().get_artist()}"
            )

        # Offset
        if (self.get_sequence().get_offset() != EMPTY_STRING):
            self.ui.OffsetDisplay.setText(
                f"{self.get_sequence().get_offset()}"
            )

    def update_time_elapsed(self) -> None:
        '''
        Updates the audio progress bar and elapsed time label to reflect
        the current audio playback position, and stops updating when playback
        ends.
        '''
        # If audio playing
        if (self.get_audio_playing() and mixer.music.get_busy()):
            synchronisation_active = self.ui.AudioSynchronisation.isChecked()
            offset = 0
            elapsed_ms = mixer.music.get_pos()

            if (synchronisation_active):
                # Shift elapsed time by beep offset and sequence offset
                offset = int(self.get_sequence().get_offset())
                elapsed_ms -= (offset + self.get_sync_beep_length())

            # Calculate proportion of song played, and update progress bar
            if (elapsed_ms >= 0):
                if (synchronisation_active):
                    # Shift wav length by beep offset and sequence offset
                    adjusted_wav_length = (
                        self.get_audio_file_duration() - (
                            offset + self.get_sync_beep_length()
                        )
                    )
                else:
                    adjusted_wav_length = self.get_audio_file_duration()

                # Only update progress once all offsets passed
                if (adjusted_wav_length >= 0):
                    progress = math.floor(
                        PROGRESS_MAX * (elapsed_ms / adjusted_wav_length)
                    )

                    # If music only one timer interval away from finish,
                    # update progress bar to 100%.
                    diff = adjusted_wav_length - elapsed_ms
                    if (diff < (MUSIC_TIMER * (3/2))):
                        progress = PROGRESS_MAX

                    self.ui.progressBar.setValue(progress)

                    # Update text tracker
                    self.ui.elapsed.setText(
                        f"{ms_to_time(elapsed_ms)} / "
                        f"{self.get_audio_length_text()}"
                    )
        else:
            if self.get_audio_playing():
                # Create function to handle end of file or reset
                self.set_audio_playing((not self.get_audio_playing()))

            # Stop updating when sound is finished
            self.music_timer.stop()

    def play_audio(self) -> None:
        '''
        Handles audio playback toggle functionality:

        Plays, pauses, or resumes the audio file depending on
        current playback state.
        '''
        # If mixer not set, do nothing
        if (mixer.get_init() is None):
            return

        # If no audio file is selected, do nothing
        if (self.get_audio_path() is EMPTY_STRING):
            return

        # If not playing, and song never played, play from beginning
        if ((not self.get_audio_playing()) and self.get_audio_never_played()):
            if self.ui.AudioSynchronisation.isChecked():
                mixer.music.load(SYNCHRONISED_USER_AUDIO_PATH)
            else:
                mixer.music.load(self.get_audio_path())
            self.music_timer.start(MUSIC_TIMER)
            mixer.music.play()
            self.set_audio_never_played(False)

            # Disable audio sync button, and change play button icon to pause
            self.ui.AudioSynchronisation.setEnabled(False)
            self.ui.AudioPlayback.setIcon(QIcon(PAUSE_ICON_PATH))

        # If music is paused, resume music
        elif (not self.get_audio_playing()):
            self.music_timer.start(MUSIC_TIMER)
            mixer.music.unpause()
            self.ui.AudioPlayback.setIcon(QIcon(PAUSE_ICON_PATH))

        # Pause music
        else:
            mixer.music.pause()
            self.ui.AudioPlayback.setIcon(QIcon(PLAY_ICON_PATH))
        self.set_audio_playing((not self.get_audio_playing()))

    def reset_audio_and_progress(self) -> None:
        '''
        Resets audio playback to default state by resetting the progress bar,
        playback state, button icons, and stopping the mixer.
        '''
        self.reset_progress_bar()
        self.set_audio_never_played(True)
        self.set_audio_playing(False)
        self.ui.AudioPlayback.setIcon(QIcon(PLAY_ICON_PATH))
        self.ui.AudioSynchronisation.setEnabled(True)

        # Stop mixer if initialised
        if (mixer.get_init() is not None):
            mixer.music.stop()

    def thread_replay_audio(self) -> None:
        ''' Handles the replay button action in a thread '''
        self._start_threaded_task(self.replay_audio)

    def replay_audio(self) -> None:
        '''
        Rewinds audio to start if a file is selected,
        and resets progress bars.
        '''
        self.reset_audio_and_progress()
        if (self.get_audio_path() != EMPTY_STRING):
            mixer.music.rewind()

    def handle_file_selection_confirmation(self) -> None:
        '''
        Confirms file selection using a threaded process,
        Blocks scrolling labels to prevent visual bugs.
        '''
        # Disable scrolling labels before starting
        self._block_scrolling = True
        self.set_filename_labels_inactive()
        self._start_threaded_task(self.confirm_file_selection)

    def mitigate_audio_rendering_blocking(self) -> int:
        '''
        Processess CPU intensive audio handling tasks,
        creating the synchronised audio file with delay,
        initialising audio mixer, and volume.

        Note:
            This function should be run in its own thread
            as it is quite intensive and will block the
            main GUI thread.

        Returns:
            (int): STATUS_MITIGATE_AUDIO_DELAY when finished

        '''
        print("Before combine_with_beep")  # debugging
        combine_with_beep(
            SYNC_BEEP_PATH,
            self.get_audio_path(),
            SYNCHRONISED_USER_AUDIO_PATH,
        )

        initialise_mixer(self.get_audio_path())
        configure_mixer_volume(
            round((self.ui.volumeSlider.value() / MAX_VOLUME), 2)
        )

        self.calc_sequence_audio_length()

        print("After combine_with_beep")  # debugging

        self.ui.elapsed.setText(
            f"{DEFAULT_AUDIO_LENGTH_TEXT} / "
            f"{self.get_audio_length_text()}"
        )
        return STATUS_MITIGATE_AUDIO_DELAY

    def confirm_file_selection(self) -> int:
        '''
        Confirms and saves the user's selected sequence and audio files,
        updates metadata in the GUI, and configures the audio mixer.

        Returns:
            (int): Exit status of process
        '''
        # Determine filenames of users temp set files, and new files (if any)
        current_sq_label = self.SequenceFilenameLabel.text()
        current_au_label = self.AudioFilenameLabel.text()

        # Check if any files selected
        if (current_sq_label == current_au_label):
            if (current_sq_label == NO_FILE_TEXT):
                return STATUS_NO_FILES_SELECTED
            self.reset_file_selection()
            return STATUS_UNKNOWN_ERROR

        # Check if sequence file selected
        if (current_sq_label == NO_FILE_TEXT):
            self.clear_temp_paths()
            self.AudioFilenameLabel.setText(NO_FILE_TEXT)
            return STATUS_NO_SEQUENCE_FILE_SELECTED

        # Check if audio file selected
        if (current_au_label == NO_FILE_TEXT):
            self.clear_temp_paths()
            self.SequenceFilenameLabel.setText(NO_FILE_TEXT)
            return STATUS_NO_AUDIO_FILE

        # Compare filenames against each other
        if (strip_file(current_sq_label) != strip_file(current_au_label)):
            self.clear_temp_paths()
            return STATUS_FILENAME_MISMATCH

        # If sequence filename matches, set temp path to current sequence path
        if self.get_sequence().get_sequence_path():
            if current_sq_label in self.get_sequence().get_sequence_path():
                self.set_temp_sequence_path(
                    self.get_sequence()
                    .get_sequence_path()
                )

        # If audio filename matches, set audio path to current audio path
        if self.get_audio_path():
            if current_au_label in self.get_audio_path():
                self.set_temp_audio_path(self.get_audio_path())

        # Reset stored sequence parameters to defaults
        self.set_sequence(Sequence())

        # Update audio and sequence paths
        self.set_audio_path(self.get_temp_audio_path())
        self.get_sequence().set_sequence_path(
            self.get_temp_sequence_path()
        )

        self.clear_temp_paths()

        # Load metadata from sequence into GUI
        self.load_sequence()

        return STATUS_FILES_CONFIRMED

    def calc_sequence_audio_length(self) -> None:
        '''
        Sets the sequence length to the length of the set WAV file
        in "MM:SS" string format.
        '''
        # Calculate wav file duration in ms
        self.set_audio_file_duration(
            get_wav_length(
                self.get_audio_path(),
            ) * MS_PER_SEC
        )

        # Convert to "MM:SS" string
        self.set_audio_length_text(
            ms_to_time(self.get_audio_file_duration())
        )

    def clear_temp_paths(self) -> None:
        ''' Clears any temporarily stored audio and sequence file paths '''
        self.set_temp_audio_path(EMPTY_STRING)
        self.set_temp_sequence_path(EMPTY_STRING)

    def handle_file_resetting(self) -> None:
        ''' Handles resetting selected files, using a threaded process '''
        self._start_threaded_task(self.reset_file_selection)

    def reset_file_selection(self) -> int:
        '''
        Resets all sequence and audio file selections to defaults, including:
        UI labels, stored parameters, audio playback state, audio mixers,
        and progress bars.

        Returns:
            (int): Exit status of process
        '''
        # Reset temporary file paths
        self.clear_temp_paths()

        # Reset audio duration
        self.set_audio_file_duration(DEFAULT_AUDIO_DURATION)

        # Reset UI labels for sequence file metadata display
        self.AudioFilenameLabel.setText(NO_FILE_TEXT)
        self.SequenceFilenameLabel.setText(NO_FILE_TEXT)
        self.NameDisplay.setText(UNKNOWN)
        self.ArtistDisplay.setText(UNKNOWN)
        self.ui.BPMDisplay.setText(DEFAULT_BPM)
        self.ui.DifficultyDisplay.setText(DEFAULT_DIFFICULTY)
        self.ui.OffsetDisplay.setText(DEFAULT_OFFSET)

        # Reset stored sequence parameters
        self.set_sequence(Sequence())

        # Reset the audio file selected
        self.set_audio_path(EMPTY_STRING)

        # Reset audio playback and mixer, and progress bar
        self.reset_audio_and_progress()

        return STATUS_FILES_RESET

    def reset_progress_bar(self) -> None:
        '''
        Resets the progress bar and elapsed time label to default values
        '''
        self.ui.progressBar.setValue(DEFAULT_PROGRESS)
        self.ui.elapsed.setText(
            f"{DEFAULT_AUDIO_LENGTH_TEXT} / "
            f"{self.get_audio_length_text()}"
        )

    def on_volume_changed(self) -> None:
        ''' Updates the playback volume of mixer based on slider '''
        if (mixer.get_init() is None):
            return
        value = round((self.ui.volumeSlider.value() / MAX_VOLUME), 2)
        mixer.music.set_volume(value)

    def on_slider_changed(self) -> None:
        '''
        Updates the displayed value in the GUI
        when the user moves the timing window slider.
        '''
        value = self.ui.horizontalSlider.value()
        self.ui.ValueFromSlider.setText(f"{value} ms")

    def apply_score_selection(self) -> None:
        '''
        Applies the current slider value to the selected timing window,
        updates the displayed error, then resets the slider.
        '''
        # Find the selected timing window, and list of
        # current temp timing windows
        selected = self.ui.TimingWindowTable.currentItem()
        array = list(self.get_temp_timing_windows())

        # If user selected a timing window
        if selected:
            # Update temporary timing windows
            row = self.ui.TimingWindowTable.row(selected)
            window = self.ui.horizontalSlider.value()
            if (row >= TIMING_WINDOW_LENGTH):
                return
            array[row] = window
            self.set_temp_timing_windows(tuple(array))
            error = calc_error_from_timing_window(window)

            # Update displayed timing window value (with error)
            self.ui.TimingWindowTable.currentItem().setText(
                f"{window} ms (+/- {error} ms)"
            )

        # Reset slider to default value
        self.ui.horizontalSlider.setValue(DEFAULT_SLIDER_VALUE)

    def set_timing_windows_to_defaults(self) -> None:
        ''' Sets the timing windows to default values in GUI and on device '''
        self.initialise_timing_window(DEFAULT_TIMING_WINDOWS)
        self.set_temp_timing_windows(DEFAULT_TIMING_WINDOWS)
        self.handle_saving_timing_windows()

    def handle_saving_timing_windows(self) -> None:
        ''' Handles saving timing windows, using a threaded process '''
        self._start_threaded_task(self.save_all_timing_windows)

    def save_all_timing_windows(self) -> int:
        '''
        Attempts to save the current timing windows to the device.
        Ensures timing window order is valid, prompts usage error box if not,
        and updates both the GUI and micro-controller on success.

        Returns:
            (int): Exit status of process
        '''
        if (self.get_serial_connection() is None):
            return STATUS_DEVICE_NOT_CONNECTED

        windows = self.get_temp_timing_windows()

        # For each timing window, check that the timing windows are
        # ordered in increasing order.
        for i, timing in enumerate(windows):
            if (i == 0):
                prev_time = timing
                continue
            elif (timing <= prev_time):
                # Prompt user with error message, and set GUI timing window
                # display to current device settings.
                return STATUS_TIMING_WINDOWS_USAGE_ERROR

            prev_time = timing

        # If usage is correct, set new timing windows in GUI
        print(windows)  # debugging
        self.set_current_timing_windows(windows)
        self.ui.TimingWindowTable.item(TIMING_WINDOW_LENGTH, 0).setText(
            f"+{self.get_current_timing_windows()[3]} ms"
        )

        # Save timing windows to device
        return self.transfer_windows()

    def initialise_timing_window(self, windows: list) -> None:
        '''
        Populates the timing window table in the GUI with provided values and
        their associated error margins, then resets the slider.

        Parameters:
            windows (list): List of timing window values in milliseconds
        '''
        # Reset temp timing windows
        self.set_temp_timing_windows(tuple(windows))

        for i, window in enumerate(windows):
            error = calc_error_from_timing_window(window)

            # Update window value in GUI
            self.ui.TimingWindowTable.item(i, 0).setText(
                f"{window} ms (+/- {error} ms)"
            )

            # Update "Miss" timing window label in GUI
            if (i == len(windows) - 1):
                self.ui.TimingWindowTable.item(i + 1, 0).setText(
                    f"+{window} ms"
                )

        print(f"Windows initialised: {windows}")  # debugging
        print(f"Temp timing windows: {self.get_temp_timing_windows()}")

        # Reset slider
        self.ui.horizontalSlider.setValue(DEFAULT_SLIDER_VALUE)

    def handle_reset_timing_window(self) -> None:
        ''' Handles resetting timing windows, using a threaded process '''
        self._start_threaded_task(self.request_device_timing_windows_settings)

    def set_timing_window(self, timing_windows: tuple) -> None:
        '''
        Updates the current and temporary timing windows, then initialises
        the GUI display with the new timing window values.

        Parameters:
            timing_windows (tuple): Timing window values in milliseconds
        '''
        self.set_current_timing_windows(timing_windows)
        self.set_temp_timing_windows(timing_windows)
        self.initialise_timing_window(timing_windows)

    def save_sequence_to_device(self) -> None:
        '''
        Initiates saving of the currently loaded sequence file to the
        microcontroller.
        '''
        self._start_threaded_task(self.transfer_sequence_file)

    def serial_readline(self) -> str:
        ''' Reads a line from the configured serial connection '''
        line = (
            self.get_serial_connection()
            .readline()
            .decode(DATA_ENCODING_TYPE, errors="ignore")
            .strip()
            .lstrip(NULL_CHAR)
            .rstrip(NULL_CHAR)
        )
        return line

    def wait_for_response(self, code: str) -> int:
        '''
        Wait for response code from device.

        Parameters:
            code (str): Code indicating the memory location

        Returns:
            (int): Exit status of process
        '''

        time_waited = 0
        while (time_waited < MAX_WAIT_TIME):
            line = self.serial_readline()

            print(f"Received: {repr(line)}")  # debugging

            # If no data read
            if (line is None) or (line == EMPTY_STRING):
                time.sleep(DECENT_WAIT)
                time_waited += (DECENT_WAIT + READ_TIMEOUT)
                print(f"Time waited: {time_waited}\n")  # debugging
                continue

            if (line != code):
                print(f"Waiting for {code}, got: {line}\n")  # debugging

                # Precaution
                time_waited += TINY_WAIT

            else:
                # No more data, code character reached
                self.set_response_code(STATUS_SUCCESS)
                return STATUS_SUCCESS

        self.set_response_code(STATUS_TIMEOUT)
        return STATUS_TIMEOUT

    def transfer_sequence_file(self) -> int:
        '''
        Sequences featuring half beats (8 beats per bar in file),
        or over 300 beats, are sent to the device modified.
        Beats past 300 are not sent, and every second half-beat is ignored.

        Upon successful transfer, user is prompted with Success message box.

        Returns:
            (int): Exit status of process
        '''
        if (self.get_serial_connection() is None):
            return STATUS_DEVICE_NOT_CONNECTED

        # Promt error box if user attempts to save file, when none is selected
        if (self.get_sequence().get_sequence_path() == EMPTY_STRING):
            return STATUS_NO_SEQUENCE_FILE_SELECTED

        # Check which location boxes are checked
        save_to_ram = self.ui.SaveToDeviceRAM.isChecked()
        save_to_eeprom = self.ui.SaveToDeviceEEPROM.isChecked()

        # Determine save mode, or prompt error box if none is selected
        flow_control_active = False
        if (save_to_ram and save_to_eeprom):
            code = SQ_TO_BOTH_CHAR
        elif (save_to_ram):
            code = SQ_TO_RAM_CHAR
        elif (save_to_eeprom):
            code = SQ_TO_EEPROM_CHAR
            flow_control_active = True
        else:
            return STATUS_SAVE_LOCATION_UNSPECIFIED

        # Transmit code char to micro-controller to
        # communicate that sequence file is being sent
        self.get_serial_connection().write(code.encode(DATA_ENCODING_TYPE))
        print(code)  # debugging

        self.wait_for_response(READY_CODE)
        if (self.get_response_code() == STATUS_TIMEOUT):
            return STATUS_TIMEOUT

        # Create list of metadata parameters to be sent
        parameters = [
            self.get_sequence().get_name(),
            self.get_sequence().get_artist(),
            self.get_sequence().get_bpm(),
            self.get_sequence().get_difficulty(),
            self.get_sequence().get_offset(),
            self.get_sequence().get_beats(),
            self.get_audio_length_text(),
        ]

        # Transmit sequence metadata line by line.
        # Each parameter is newline terminated.
        for param in parameters:
            print(param)  # debugging
            data = f"{param}\n"
            self.get_serial_connection().write(data.encode(DATA_ENCODING_TYPE))

        time.sleep(DECENT_WAIT)  # This helps

        # --- Transmit sequence beats ---
        # If file consists of half beats, only every second beat will be sent
        # Additionally only a maximum of 300 beats will be sent.
        buffer_reached = False
        beats = 0
        parity = True

        file_path = self.get_sequence().get_sequence_path()
        with open(file_path, READ_MODE) as file:
            for line in file:

                # Ignore lines before buffer
                if (buffer_reached is False) and (line != f"{BUFFER}\n"):
                    continue

                # Detect buffer has been reached, and continue parsing
                if (line == f"{BUFFER}\n"):
                    buffer_reached = True
                    continue

                # Ignore bar divider
                if (line == f"{BAR_DIVIDER}\n"):
                    continue

                # Stop transferring lines if End of file reached
                if (line == f"{FILE_END}\n"):
                    break

                # Skip every second beat if sequence features half-beats
                if (self.get_sequence().get_beats_per_bar() == HALF_BEATS):
                    if parity:
                        parity = not parity
                    else:
                        parity = not parity
                        continue

                # If EEPROM mode, wait for ready signal
                if (flow_control_active):
                    self.wait_for_response(READY_CODE)
                    if (self.get_response_code() == STATUS_TIMEOUT):
                        return STATUS_TIMEOUT

                # Use tiny delay for RAM modes
                else:
                    time.sleep(TINY_WAIT)

                # Transmit beat
                beats += 1
                self.get_serial_connection().write(
                    line.encode(DATA_ENCODING_TYPE),
                )
                print(f"Sent beat {beats}: {line[:-1]}")  # debugging

                # If 300 beats sent, stop parsing file
                if (beats == MAX_BEATS):
                    break

        # Decent delay between sending and waiting for data back
        # wait longer for files with more beats
        time.sleep(DECENT_WAIT + beats/1000)

        # Read responses back from micro-controller and print to terminal
        self.wait_for_response(END_TRANSFER)
        if (self.get_response_code() == STATUS_SUCCESS):

            # Prompt user with message box that data was successfully saved
            return STATUS_SUCCESS

        return STATUS_TIMEOUT

    def transfer_windows(self) -> int:
        '''
        Transfers the current timing window values to the micro-controller
        and prompts user with message box upon successful transfer.

        Returns:
            (int): Exit status of process
        '''
        if (self.get_serial_connection() is None):
            return STATUS_DEVICE_NOT_CONNECTED

        # Transmit code char to micro-controller to
        # communicate that timing windows are being sent
        code = TW_TO_EEPROM_CHAR
        self.get_serial_connection().write(code.encode(DATA_ENCODING_TYPE))

        # Check device ready
        self.wait_for_response(READY_CODE)
        if (self.get_response_code() == STATUS_TIMEOUT):
            return STATUS_TIMEOUT

        # Transmit all timing window values, all are newline terminated
        parameters = list(self.get_current_timing_windows())
        for param in parameters:
            print(param)  # debugging
            data = f"{param}\n"
            self.get_serial_connection().write(data.encode(DATA_ENCODING_TYPE))

        self.wait_for_response(END_TRANSFER)
        if (self.get_response_code() == STATUS_SUCCESS):
            # Prompt user with message box that data was successfully saved
            return STATUS_SUCCESS

        return STATUS_TIMEOUT

    def choose_save_location(self, caption: str, filter: str) -> str:
        '''
        Prompts window to select a path to save a file.
        Default save location is set to Downloads.

        Parameters:
            caption (str): Window title
            filter (str): File type filter

        Returns:
            (str): path to save location
        '''
        filepath, _ = QFileDialog.getSaveFileName(
            parent=self,
            caption=caption,
            dir=QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.DownloadLocation
            ),
            filter=filter,
        )
        return filepath

    def get_ram_sequence(self) -> None:
        '''
        Retrieves the sequence file stored in the micro-controllers
        RAM and saves it locally. Runs as a threaded process.

        Returns:
            (int): exit code of process, or None if no status to report
        '''
        path = self.choose_save_location(
            caption="Save Sequence",
            filter=SEQUENCE_FILE,
        )
        if (path == EMPTY_STRING):
            return
        self.set_sequence_save_path(path)
        self._start_threaded_task(
            self.get_file_from_device,
            LOAD_SQ_FROM_RAM_CODE,
            path,
        )

    def get_eeprom_sequence(self) -> None:
        '''
        Retrieves the sequence file stored in the micro-controllers
        EEPROM and saves it locally. Runs as a threaded process.
        '''
        path = self.choose_save_location(
            caption="Save Sequence",
            filter=SEQUENCE_FILE,
        )
        if (path == EMPTY_STRING):
            return
        self.set_sequence_save_path(path)
        self._start_threaded_task(
            self.get_file_from_device,
            LOAD_SQ_FROM_EEPROM_CODE,
            path,
        )

    def request_device_timing_windows_settings(self) -> int:
        '''
        Requests the current timing window settings from the micro-controller.

        Connects the "Reset" button on the timing windows page to
        the request_device_timing_windows_settings() function.
        For more details please refer to the above function.

        Returns:
            (int): Exit status of process
        '''
        if (self.get_serial_connection() is None):
            return STATUS_DEVICE_NOT_CONNECTED

        # Transmit code to micro-controller to communicate GUI
        # is requesting timing windows
        code = REQUEST_TIMING_WINDOWS_CODE
        self.get_serial_connection().write(code.encode(DATA_ENCODING_TYPE))

        # Read responses back from micro-controller, and records values.
        # If timing windows list is of non-zero length, then update
        # GUI with windows, else set to default.
        timing_windows = []

        time_waited = 0
        while (time_waited < MAX_WAIT_TIME):
            # Read line from serial port
            line = self.serial_readline()

            # Exit if connection timesout
            if (line == EMPTY_STRING):
                time.sleep(BIG_WAIT)
                time_waited += (BIG_WAIT + READ_TIMEOUT)
                print(f"Time waited: {time_waited}")  # debugging
                continue

            # Append each value to timing windows list
            if (line != END_TRANSFER):
                print(repr(line))  # debugging
                timing_windows.append(int(line))

            # End of Transfer reached
            else:
                print(timing_windows)  # debugging
                # If timing windows has values appended, set timing windows
                if (len(timing_windows) != 0):
                    self.set_timing_window(tuple(timing_windows))
                    return STATUS_SUCCESS

                # Error with reading, set windows to default
                else:
                    self.set_timing_window(DEFAULT_TIMING_WINDOWS)
                    return STATUS_UNKNOWN_ERROR

        return STATUS_TIMEOUT

    def get_file_from_device(self, code: str, path: str) -> int:
        '''
        Retrieves a sequence file stored on the micro-controllers
        RAM or EEPROM, saves it locally, and prompts a message box,
        to inform user of save location and success.

        The function sends a command code to the device, then reads back
        file contents line by line until the transfer terminates. Special
        markers (BUFFER, BAR_DIVIDER, END_TRANSFER) are inserted into the
        saved file as needed.

        The resulting file is formatted in the expected .tsq sequence file
        format, enabling it to be resent to the device in the future.

        Parameters:
            code (str): Code indicating the memory location

        Returns:
            (int): Exit status of process
        '''
        if (self.get_serial_connection() is None):
            return STATUS_DEVICE_NOT_CONNECTED

        # Transmit code to micro-controller to communicate
        # which sequence the GUI is requesting.
        self.get_serial_connection().write(code.encode(DATA_ENCODING_TYPE))
        print(code)  # dubugging

        time.sleep(DECENT_WAIT)

        # Read responses back from micro-controller, and format data
        # approapriately in the standard .tsq sequence file format.
        with open(path, WRITE_MODE) as file:
            beat_counter = 0
            buffer_reached = False
            read_next_line = True
            time_waited = 0
            while (time_waited < MAX_WAIT_TIME):

                # Checks if toggle is set to
                # allow next line to be read.
                if read_next_line:
                    # Read line
                    line = self.serial_readline()
                    print(repr(line))  # debugging
                else:
                    # Re-enable line reading
                    read_next_line = True

                if (line is None) or (line == EMPTY_STRING):
                    time.sleep(BIG_WAIT)
                    time_waited += (BIG_WAIT + READ_TIMEOUT)
                    print(f"Time waited: {time_waited}")  # debugging

                # Detect buffer has been reached,
                # and initialise beat counter.
                if (line == BUFFER):
                    file.write(f"{BUFFER}\n")
                    buffer_reached = True
                    beat_counter = 0
                    continue

                # Write all lines read prior to received buffer
                if (buffer_reached is False):
                    file.write(f"{line}\n")
                    continue

                # ---- Buffer has been reached ----

                beat_counter += 1
                if (line != END_TRANSFER):
                    file.write(f"{line}\n")

                # If line read is end of transfer, then write
                # FILE_END and exit.
                else:
                    file.write(f"{FILE_END}\n")
                    return self.file_from_device_exit_status(code)

                # Every fourth beat read the next upcoming line,
                # to check if it is an end of transfer.
                # If it is not, then write a bar divider to file.
                # Else write FILE_END and exit.
                if ((beat_counter % 4) == 0):
                    beat_counter = 0
                    line = self.serial_readline()

                    print(repr(line))  # debugging
                    if (line == END_TRANSFER):
                        file.write(f"{FILE_END}\n")
                        return self.file_from_device_exit_status(code)

                    file.write(f"{BAR_DIVIDER}\n")

                    # Toggle whether to read line on next iteration
                    read_next_line = False

            return STATUS_TIMEOUT
        return STATUS_UNKNOWN_ERROR

    def file_from_device_exit_status(self, code: str) -> int:
        '''
        Returns the exit code when getting a file from the device,
        upon successfully receiving data. This prompts user
        with message box to indicate sequence saved.

        Parameters:
            code (str): Code indicating the memory location

        Returns:
            (int): Exit status of process
        '''
        if (code == LOAD_SQ_FROM_EEPROM_CODE):
            return STATUS_RECEIVED_EEPROM_TSQ
        elif (code == LOAD_SQ_FROM_RAM_CODE):
            return STATUS_RECEIVED_RAM_TSQ
        else:
            print(f"Error, received code: {code}")  # debugging
            return STATUS_UNKNOWN_ERROR

    def file_mismatch_message(self) -> None:
        '''
        Displays an error message box informing the user
        of filename mismatch, and the error.
        '''
        current_sq_label = self.SequenceFilenameLabel.text()
        current_au_label = self.AudioFilenameLabel.text()
        self.AudioFilenameLabel.setText(NO_FILE_TEXT)
        self.SequenceFilenameLabel.setText(NO_FILE_TEXT)

        TPManiaMessageBox(
            QMessageBox.Icon.Critical,
            (
                "Selected filenames mismatch!<br><br>"
                f"<b>Sequence</b>: &nbsp;<b>{strip_file(current_sq_label)}"
                f"</b>{SEQUENCE_TYPE}<br>"
                f"<b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Audio</b>: &nbsp;<b>{
                    strip_file(current_au_label)
                }"
                f"</b>{AUDIO_TYPE}<br><br>"
                "Ensure filenames match, and try again."
            ),
            "File Mismatch",
        )

    def _start_threaded_task(
            self,
            function: Callable[..., Any],
            *args: Any,
    ) -> None:
        '''
        Helper function that sets up a thread with signals,
        allowing it to communicate with GUI thread.

        It takes the function to run and its arguments.
        '''
        id = self.thread_id
        self.inc_thread_id()  # Incriment global thread counter
        print(f"Thread created: {id}")
        self.set_thread_is_running()

        thread = QThread()
        self.set_thread(thread, id)
        self.set_worker(GenericWorker(function, *args, id=id), id)
        self.get_worker(id).moveToThread(thread)
        self.get_thread(id).started.connect(self.get_worker(id).run)

        # Remove thread from tracker when finished
        self.get_thread(id).finished.connect(
            lambda tid=id: self.thread_tracker.pop(tid, None)
        )
        self.get_thread(id).finished.connect(
            lambda tid=id: print(f"Thread Terminated: {tid}")
        )  # debugging

        self.get_worker(id).result.connect(self.handle_result)
        self.get_worker(id).error.connect(self.report_error)
        self.get_worker(id).finished.connect(self.get_thread(id).quit)
        self.get_worker(id).finished.connect(self.get_worker(id).deleteLater)

        # Remove thread from tracker when finished
        self.get_worker(id).finished.connect(
            lambda tid=id: self.worker_tracker.pop(tid, None)
        )
        self.get_worker(id).finished.connect(
            lambda tid=id: print(f"Worker Terminated: {tid}")
        )  # debugging

        self.get_thread(id).finished.connect(self.get_thread(id).deleteLater)

        # Start the thread
        self.get_thread(id).start()

    def handle_result(self, status: Any) -> None:
        '''
        Handles functionality after a thread exits, functionality
        depends on exit status.

        Parameters:
            status (Any): Exit status of the thread
        '''
        if (status is None):
            pass
        elif (status == STATUS_UNKNOWN_ERROR):
            unknown_error_message_box()
        elif (status == STATUS_SUCCESS):
            save_to_device_successful()
        elif (status == STATUS_SAVE_LOCATION_UNSPECIFIED):
            sequence_save_location_unspecified()
        elif (status == STATUS_NO_SEQUENCE_FILE_SELECTED):
            no_sequence_file_selected()
        elif (status == STATUS_DEVICE_NOT_CONNECTED):
            no_serial_communication_message_box()
        elif (status == STATUS_NO_FILE_ON_RAM):
            no_file_on_ram_message_box()
        elif (status == STATUS_TIMING_WINDOWS_USAGE_ERROR):
            timing_window_selection_error_box()
            self.initialise_timing_window(
                self.get_current_timing_windows(),
            )
        elif (status == STATUS_RECEIVED_EEPROM_TSQ):
            received_sequence_from_device(
                EEPROM,
                self.get_sequence_save_path(),
            )
        elif (status == STATUS_RECEIVED_RAM_TSQ):
            received_sequence_from_device(
                RAM,
                self.get_sequence_save_path(),
            )
        elif (status == STATUS_TIMEOUT):
            timeout_message_box()
        elif (status == STATUS_NO_PORT_SET):
            serial_connection_error_box(None)
        elif (status == STATUS_FILES_CONFIRMED):
            # Prompt user to select save location for the
            # audio with synchronisation beep added
            self.set_filename_labels_inactive()
            self._ready_for_rendering = True
            files_confirmed_message_box()
        elif (status == STATUS_MITIGATE_AUDIO_DELAY):
            self._block_scrolling = False
        elif (status == STATUS_FILES_RESET):
            reset_files_message_box()
        elif (status == STATUS_FILENAME_MISMATCH):
            self.file_mismatch_message()
        elif (status == STATUS_NO_AUDIO_FILE):
            no_audio_file_selected()
        elif (status == STATUS_NO_FILES_SELECTED):
            no_files_selected()
        else:
            unknown_error_message_box()

    def report_error(self, exception: Exception) -> None:
        '''
        Receives the exception object from the worker and prompts
        a corresponding error box, and prints error to terminal.

        Parameters:
            exception (Exception): exception caught
        '''
        print(f"{type(exception).__name__} - {exception}")  # debugging

        # On Serial failure, shows an error message, resets the selected port,
        # and refreshes the list of available ports.
        if isinstance(exception, (OSError, serial.SerialException)):
            serial_connection_error_box(self.get_serial_port())
            self.set_serial_port(EMPTY_STRING)
            self.refresh_serial_port()

        else:  # Prompt error message upon any other errors caught
            TPManiaMessageBox(
                str(exception),
                str(type(exception).__name__),
                QMessageBox.Icon.Critical,
            )

    def set_filename_labels_inactive(self) -> None:
        ''' Disables scrolling from filename labels '''
        self.AudioFilenameLabel.set_active(INACTIVE)
        self.SequenceFilenameLabel.set_active(INACTIVE)

    def periodic_check(self) -> None:
        '''
        Runs a periodic check to see if any threads are running,
        or if scrolling labels should continue to be updated again.

        Also checks if the heavy computational task of processing audio
        is queued, if so that is processes.
        '''
        # Checks if thread indicator needs to be updated
        self.set_thread_is_running()

        if (  # Audio file selected, and ready for rendering
            self.get_audio_path() != EMPTY_STRING
        ) and (self._ready_for_rendering):

            # Process audio and initialise mixer
            self._start_threaded_task(
                self.mitigate_audio_rendering_blocking
            )

            # Reset flag
            self._ready_for_rendering = False

        # If scrolling is blocked ignore
        if (self._block_scrolling is True):
            return

        # Check if any labels are active
        any_active = False
        for label in self._scrollable_labels:
            # Set label to active if size is large
            if (len(label.text()) > MAGIC_NUMBER):
                label.set_active(ACTIVE)
                any_active = True

        # Start update timer if any active
        if (any_active):
            self.label_update_timer.start(SCROLL_INTERVAL_TIMER)
        else:  # Disable timer
            self.label_update_timer.stop()

    def trigger_label_update(self) -> None:
        ''' Triggers the update of any scrolling labels active '''
        for label in (self._scrollable_labels):
            if (label.get_active() is ACTIVE):
                label.tick()

    def _secret(self) -> None:
        ''' Nothing to see here... '''
        if (self.ui.secretButton.text() == "🗝️"):
            self.ui.secretButton.setText(EMPTY_STRING)
            self.ui.secretButton.setCursor(Qt.ArrowCursor)
            self._secret_found = True
            found_the_secret_key()
        elif (self._secret_found is False):
            self.ui.secretButton.setText("🗝️")
        else:
            return

    def _mystery(self) -> None:
        ''' Surely let us have some fun with this ! '''
        if (self._secret_found is False):
            return
        elif (self.ui.mysteryButton.text() == "🔓"):
            self.ui.stackedWidget.setCurrentIndex(MYSTERY_PAGE)
        else:
            self.ui.mysteryButton.setText("🔓")

    def closeEvent(self, event: QCloseEvent) -> None:
        '''
        Cleanup temporary user-generated files upon program shutdown.
        Quits/terminates remaining threads, stops timers, and quits mixer.

        Note: this funciton is pre-named in QCloseEvent

        Parameters:
            event (QCloseEvent): Close event triggered when GUI is shutdown
        '''
        # Stop all timers
        self.music_timer.stop()
        self.label_update_timer.stop()
        self.periodic_check_timer.stop()

        # Quit mixer if active
        if (mixer.get_init() is not None):
            mixer.quit()

        print(f"Threads alive at close: {self.thread_tracker}")  # debugging

        # Stop all running threads
        for id in self.thread_tracker.keys():
            if self.get_thread(id).isRunning():
                self.get_thread(id).quit()  # Ask the thread to exit

        time.sleep(DECENT_WAIT)
        # Terminate any threads still active
        if (len(self.thread_tracker) != 0):
            for id in self.thread_tracker.keys():
                if self.get_thread(id).isRunning():
                    self.get_thread(id).terminate()
                    print(f"Thread TERMINATED: {id}")  # debugging

        print(f"After Cleanup: {self.thread_tracker}")  # debugging

        # Delete generated files in default save directory
        for file in os.listdir(DEFAULT_SAVE_DIR):
            path = os.path.join(DEFAULT_SAVE_DIR, file)
            if os.path.isfile(path):
                os.remove(path)
        return super().closeEvent(event)


def main() -> None:
    ''' Launches the application, starting the event loop '''
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
