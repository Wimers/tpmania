# Import Required Modules
import ffmpeg
import itertools
import math
import os
import wave
import winreg
import shutil
import warnings

# Used for type hinting
from typing import Iterator

# Imports pygame, and blocks its printed launch messages
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from pygame import mixer  # For playing audio

# FFmpeg Exe location
FFMPEG_DIR = "FFmpeg"
FFMPEG_PATH = f"{FFMPEG_DIR}/ffmpeg.exe"

# String Constants
EMPTY_STRING = ""
SLASH = "/"
DOT = "."

# Time Constants
MS_PER_SEC = 1000
SECS_PER_MIN = 60

# Reading Mode
WAVE_READ_ONLY = "rb"

# Audio Player Config
MIXER_VOLUME = 0.3
DEFAULT_VOLUME_SCALE = MIXER_VOLUME * 100
DEFAULT_CHANNEL_MODE = 1  # Mono


def enumerate_serial_ports() -> Iterator[tuple[str, str]]:
    '''
    Uses the Win32 registry to return a iterator of serial
    (COM) ports existing on this computer.

    Reference:
        This code is in the public domain
        Eli Bendersky (eliben@gmail.com)
        https://eli.thegreenplace.net/2009/07/31/listing-all-serial-ports-on-windows-with-python
    '''
    path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
    except FileNotFoundError:
        raise RuntimeError("Unable to enumerate serial ports")

    for i in itertools.count():
        try:
            val = winreg.EnumValue(key, i)
            yield (str(val[1]), str(val[0]))
        except EnvironmentError:
            break


def combine_with_beep(
    file1: str,
    file2: str,
    output_file: str,
) -> None:
    '''
    Place file2 after file1, it is assumed file1 is mono.
    Both files must be .WAV files.

    Parameters:
        file1: path to first input file
        file2: path to second input file
        output_file: path to save result
    '''
    # First file
    stream1 = ffmpeg.input(file1)

    # Second file, down mixed to mono
    stream2 = (
        ffmpeg
        .input(file2)
        .filter("aformat", channel_layouts="mono")
    )

    # Mix both streams
    mixed = ffmpeg.filter([stream1, stream2], "amix")

    # Saving the file, overwriting it if it already exists
    (
        ffmpeg
        .output(mixed, output_file)
        .overwrite_output()
        .run_async(
            FFMPEG_PATH,
            quiet=True,
        )
    )


def ms_to_time(ms: int) -> str:
    '''
    Converts milliseconds into a string in the format "MM:SS".

    Parameters:
        ms (int): Time input in milliseconds.

    Returns:
        (int): Duration formatted as "MM:SS".
    '''
    secs = (ms / MS_PER_SEC)
    minutes = math.floor(secs / SECS_PER_MIN)
    secs = secs - (minutes * SECS_PER_MIN)

    # Round seconds to nearest integer
    if ((secs - math.floor(secs)) >= 0.5):
        seconds = math.ceil(secs)
    else:
        seconds = math.floor(secs)

    # If seconds is 60, increase number of minutes and reset
    # seconds to zero.
    if (seconds == SECS_PER_MIN):
        minutes += 1
        seconds = 0

    seconds_clock = str(seconds)
    minutes_clock = str(minutes)

    # If seconds/minutes is a single digit
    if (len(seconds_clock) == 1):
        seconds_clock = f"0{seconds_clock}"
    if (len(minutes_clock) == 1):
        minutes_clock = f"0{minutes_clock}"

    return f"{minutes_clock}:{seconds_clock}"


def get_wav_length(filename: str) -> float:
    '''
    Determines the duration of a .wav file in ms.

    Parameters:
        filename (str): Path to the .wav file

    Returns:
        (float): duration of file in ms
    '''
    with wave.open(filename, WAVE_READ_ONLY) as wav_file:
        frames = wav_file.getnframes()
        framerate = wav_file.getframerate()
        duration = frames / float(framerate)
        return duration


def strip_path(path: str) -> str:
    '''
    Extracts the filename of a file, from a the files
    entire path address.

    Parameters:
        path (str): Full file path address.

    Returns:
        (str): extracted filename

    Example:
        'C:/Users/Example/Y.E.A.H.tsq' -> 'Y.E.A.H.tsq'
    '''
    return path.split(SLASH)[-1]


def strip_file(filename: str) -> str:
    '''
    Removes the filetype from a filename

    Parameters:
        filename (str): filename of file

    Returns:
        (str): filename without file type

    Example:
        'Y.E.A.H.tsq' -> 'Y.E.A.H'
    '''
    return DOT.join(filename.split(DOT)[:-1])


def copy_file(source: str, destination: str) -> None:
    '''
    THIS FUNCTION IS NO LONGER USED WITHIN THE GUI

    Copies the file located at source to the destination path

    Parameters:
        source (str): source path
        destination (str): destination path

    Returns:
        (int): process status
    '''
    if (source is EMPTY_STRING) or (destination is EMPTY_STRING):
        print("Invalid path provided ! ")  # debugging
        return
    try:
        if (os.path.samefile(source, destination)):
            print("Error: Same file !")  # debugging
            return
        shutil.copyfile(source, destination)
        return
    except FileNotFoundError:
        shutil.copyfile(source, destination)
        print("File copied !")  # debugging


def initialise_mixer(audio_path: str) -> None:
    '''
    Initialises the audio mixer with a mono channel,
    and loads the selected audio file.
    '''
    if (mixer.get_init() is None):
        mixer.init(channels=DEFAULT_CHANNEL_MODE)

    mixer.music.load(audio_path)


def configure_mixer_volume(value: float) -> None:
    ''' Sets the volume of the audio mixer to the value provided '''
    if (value != DEFAULT_VOLUME_SCALE):
        mixer.music.set_volume(value)
    else:
        mixer.music.set_volume(MIXER_VOLUME)


def calc_error_from_timing_window(window: int) -> int:
    ''' Calculates timing window error '''
    if (window % 2):  # If value is odd, round to one decimal digit
        error = round(window / 2, 1)
    else:  # If timing window is even, convert error to integer
        error = int(window / 2)
    return error
