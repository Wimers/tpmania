# Sequence file constants
EMPTY_STRING = ""
BUFFER = "---"
BAR_DIVIDER = ","
FILE_END = ";"
NAME_FLAG = "Name: "
ARTIST_FLAG = "Artist: "
BPM_FLAG = "BPM: "
DIFFICULTY_FLAG = "Difficulty: "
OFFSET_FLAG = "Offset: "
LENGTH_FLAG = "Length: "

# Sequence file restrictions
MAX_BEATS = 300
FULL_BEATS = 4  # Four full beats per bar
HALF_BEATS = 8  # Eight Half beats per bar

# Default Parameters
DEFAULT_NAME = EMPTY_STRING
DEFAULT_ARTIST = EMPTY_STRING
DEFAULT_BPM = "0"
DEFAULT_OFFSET = "0"
DEFAULT_DIFFICULTY = "N/A"
DEFAULT_BEATS_PER_BAR = 0
DEFAULT_NUM_BEATS = 0

# Other Constants
READ_MODE = 'r'


class Sequence:
    ''' A class to manage and sequences files and store metadata '''
    def __init__(self) -> None:
        ''' Initialises sequence parameters '''
        # Sequence file path
        self._sequence_path = EMPTY_STRING

        # Parameters parsed from sequence file
        self._name = DEFAULT_NAME
        self._artist = DEFAULT_ARTIST
        self._bpm = DEFAULT_BPM
        self._offset = DEFAULT_OFFSET
        self._difficulty = DEFAULT_DIFFICULTY

        # Parameters computed
        self._beats_per_bar = DEFAULT_BEATS_PER_BAR
        self._beats = DEFAULT_NUM_BEATS

    def get_sequence_path(self) -> str:
        ''' Returns the configured sequence file's path '''
        return self._sequence_path

    def get_name(self) -> str:
        ''' Returns sequence Name '''
        return self._name

    def get_artist(self) -> str:
        ''' Returns sequence Artist '''
        return self._artist

    def get_bpm(self) -> str:
        ''' Returns sequence BPM '''
        return self._bpm

    def get_offset(self) -> str:
        ''' Returns sequence Offset '''
        return self._offset

    def get_difficulty(self) -> str:
        ''' Returns sequence Difficulty '''
        return self._difficulty

    def get_beats(self) -> int:
        ''' Returns number of beats in sequence '''
        return self._beats

    def get_beats_per_bar(self) -> int:
        ''' Returns number of beats per bar in sequence '''
        return self._beats_per_bar

    def set_sequence_path(self, path: str) -> None:
        ''' Sets the path of the .tsq sequence file '''
        self._sequence_path = path

    def set_name(self, name: str) -> None:
        ''' Sets the sequence Name '''
        self._name = name

    def set_artist(self, artist: str) -> None:
        ''' Sets the sequence Artist '''
        self._artist = artist

    def set_bpm(self, bpm: str) -> None:
        ''' Sets the sequence BPM '''
        self._bpm = bpm

    def set_offset(self, offset: str) -> None:
        ''' Sets the sequence offset '''
        self._offset = offset

    def set_difficulty(self, difficulty: str) -> None:
        ''' Sets the sequence Difficulty '''
        self._difficulty = difficulty

    def set_beats_per_bar(self, beats: int) -> None:
        ''' Sets the number of beats per bar in sequence '''
        self._beats_per_bar = beats

    def set_beats(self, beats: int) -> None:
        ''' Sets the number of bars in the sequence '''
        self._beats = beats

    def parse_sequence(self) -> None:
        '''
        Parses the currently loaded sequence file and updates sequence
        metadata.
        '''
        # Initialise tracked parameters
        buffer_reached = False
        beats = 0
        beats_per_bar_known = False
        beats_per_bar = 0

        # Opens sequence file
        with open(self.get_sequence_path(), READ_MODE) as file:
            line_number = -1

            # Reads the file line by line
            for line in file:
                line_number += 1

                # Removes "\n" from end of each line
                line = line[:-1]

                if (line == BUFFER):
                    buffer_reached = True
                    continue

                # Determines beats per bar
                if (buffer_reached) and (beats_per_bar_known is False):
                    if (line != BAR_DIVIDER):
                        beats_per_bar += 1
                        beats += 1
                    else:
                        beats_per_bar_known = True
                        self.set_beats_per_bar(beats_per_bar)
                    continue

                # Count number of beats in sequence file,
                # breaking if 300 beats read.
                if (buffer_reached and (line not in (BAR_DIVIDER, FILE_END))):

                    # Check conditions
                    c1 = (
                        (
                            beats_per_bar == FULL_BEATS
                        ) and (
                            beats == MAX_BEATS
                        )
                    )

                    c2 = (
                        (
                            beats_per_bar == HALF_BEATS
                        ) and (
                            beats == (MAX_BEATS * 2)
                        )
                    )

                    if (c1 or c2):
                        break

                    beats += 1
                    continue

                # Stop reading lines once file end indicator reached
                if (line == FILE_END):
                    break

                # Extract metadata before the buffer:
                # name, artist, BPM, offset, difficulty
                if (not buffer_reached):
                    if line.startswith(NAME_FLAG):
                        self.set_name(line[len(NAME_FLAG):])

                    elif line.startswith(ARTIST_FLAG):
                        self.set_artist(line[len(ARTIST_FLAG):])

                    elif line.startswith(BPM_FLAG):
                        self.set_bpm(line[len(BPM_FLAG):])

                    elif line.startswith(OFFSET_FLAG):
                        self.set_offset(line[len(OFFSET_FLAG):])

                    elif line.startswith(DIFFICULTY_FLAG):
                        self.set_difficulty(line[len(DIFFICULTY_FLAG):])
                    else:
                        continue

            # Halve beats if sequence features half beats
            if (beats_per_bar == HALF_BEATS):
                beats = round(beats / 2)

        print(beats_per_bar)  # debugging
        self.set_beats(beats)
        print(beats)  # debugging
