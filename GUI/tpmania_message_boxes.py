# Import Pyside6 Modules
from PySide6.QtWidgets import QMessageBox  # QWidget
from PySide6.QtGui import QFont, QIcon

# Media Directories
ASSETS_DIR = "assets"
WINDOW_ICON_PATH = f"{ASSETS_DIR}/setup.ico"

# Assorted Constants
TPMANIA_TITLE = "tpmania"
DEFAULT_FONT_TYPE = "Segoe UI"
EMPTY_STRING = ""


class TPManiaMessageBox(QMessageBox):
    ''' A class for modeling message boxes customised for TPMANIA '''
    def __init__(
            self,
            message_type: QMessageBox.Icon,
            text: str,
            title: str = TPMANIA_TITLE,
            font: QFont | None = None,
            icon: QIcon | None = None,
    ) -> None:
        '''
        Displays a message box with the specified text, title, and icon.
        Message type can include: Information, Warning, or Critical.

        Parameters:
            message_type (QMessageBox.Icon): The alert icon to display
            text (str): The message to display
            title (str): Title of the message box window
            font (QFont): Message box font
            icon (QIcon): Window icon
        '''
        super().__init__()

        if (font is None):
            font = QFont(DEFAULT_FONT_TYPE, pointSize=9)

        if (icon is None):
            icon = QIcon(WINDOW_ICON_PATH)

        self.setIcon(message_type)
        self.setText(text)
        self.setWindowTitle(title)
        self.setFont(font)
        self.setWindowIcon(icon)
        self.setFixedSize(200, 100)  # (w , h)
        self.exec()


def timing_window_selection_error_box() -> None:
    '''
    Displays an error message box informing the user that timing windows
    must be in strictly increasing order.
    '''
    TPManiaMessageBox(
        QMessageBox.Icon.Critical,
        (
            "Timing windows must be in "
            "<b>stricly increasing</b> order!<br><br>"
            "Perfect! &lt; Good! &lt; OK &lt; Poor &lt; Miss"
        ),
        "Usage Error",
    )


def files_confirmed_message_box() -> None:
    '''
    Displays an information message box informing the user that the
    files they selected have been confirmed.
    '''
    TPManiaMessageBox(
        QMessageBox.Icon.Information,
        (
            "Files have been selected successfully"
        ),
        "Success",
    )


def serial_connection_error_box(port: str) -> None:
    '''
    Displays an error message box informing the user that the serial
    connection to the given port could not be established or was lost.

    Parameters:
        port (str): Configured serial port
    '''
    if (port is not None) and (port != EMPTY_STRING):
        text = (
            f"Unable to connect to: <b>{port}</b><br>"
            "Please try again!"
        )
    else:
        text = (
            "Connection has disconnected, "
            "or no connection was established."
        )

    TPManiaMessageBox(
        QMessageBox.Icon.Critical,
        text,
        "Serial Connection Error",
    )


def save_to_device_successful() -> None:
    '''
    Displays an information message box confirming that data
    was successfully saved to the device.
    '''
    TPManiaMessageBox(
        QMessageBox.Icon.Information,
        "Successfully saved to device",
        "Save Successful",
    )


def unknown_error_message_box() -> None:
    '''
    Displays an error message box confirming that an unknown
    error has occured during a process.
    '''
    TPManiaMessageBox(
        QMessageBox.Icon.Critical,
        "An unknown error has occured!",
        "Unknown Error",
    )


def sequence_save_location_unspecified() -> None:
    '''
    Displays an error message box informing the user to select
    a save location on the micro-controller for the sequence file.
    '''
    TPManiaMessageBox(
        QMessageBox.Icon.Critical,
        "Please select a location on device to save to",
        "Save Error",
    )


def no_serial_communication_message_box() -> None:
    '''
    Displays an error message box informing the user that the device
    is not connected and no serial communication is available.
    '''
    TPManiaMessageBox(
        QMessageBox.Icon.Critical,
        (
            "Device is not connected!<br>"
            "Please select a serial communication port "
            "before attempting to save files"
        ),
        "Device not connected",
    )


def timeout_message_box() -> None:
    '''
    Displays an error message box indicating that function
    call has timed out, due to some error.
    '''
    TPManiaMessageBox(
        QMessageBox.Icon.Critical,
        (
            "Process has timed out!<br>"
            "Please check device mode, and connections."
        ),
        "Process Timeout",
    )


def reset_files_message_box() -> None:
    '''
    Displays an info message box indicating that file selection
    has been reset.
    '''
    TPManiaMessageBox(
        QMessageBox.Icon.Information,
        "Files successfully reset",
        "Success",
    )


def no_file_on_ram_message_box() -> None:
    '''
    Displays an error message box indicating that no sequence
    file is currently saved to the device RAM.
    '''
    TPManiaMessageBox(
        QMessageBox.Icon.Critical,
        (
            "No sequence is loaded to RAM!<br>"
            "Please save a sequence, and try again."
        ),
        "No File Saved",
    )


def no_sequence_file_selected() -> None:
    '''
    Displays an error message box informing the user that they
    have not selected a sequence.
    '''
    TPManiaMessageBox(
        QMessageBox.Icon.Critical,
        (
            "No Sequence file has been selected!<br>"
            "Please select a file and try again."
        ),
        "No Sequence File Selected",
    )


def no_audio_file_selected() -> None:
    '''
    Displays an error message box informing the user that they
    have not selected an audio file.
    '''
    TPManiaMessageBox(
        QMessageBox.Icon.Critical,
        (
            "No Audio file has been selected!<br>"
            "Please select a file and try again."
        ),
        "No Audio File Selected",
    )


def no_files_selected() -> None:
    '''
    Displays an error message box informing the user that they
    have not selected an any file.
    '''
    TPManiaMessageBox(
        QMessageBox.Icon.Critical,
        (
            "No Files have been selected!<br>"
            "Please select all files and try again."
        ),
        "No Files Selected",
    )


def received_sequence_from_device(location: str, path: str) -> None:
    '''
    Displays a message box confirming that a sequence file was retrieved
    from the device (RAM or EEPROM), and shows the path where it was saved.

    Parameters:
        location (str): Code indicating the memory location (RAM/EEPROM)
        path (str): Path where the sequence file was saved
    '''
    TPManiaMessageBox(
        QMessageBox.Icon.Information,
        (
            "Successfully retrieved sequence file stored in "
            f"<b>{location}</b> from device!<br>"
            "To view contents please open:<br><br>"
            f"<b>{path}</b>"
        ),
        "File Retrieved",
    )


def found_the_secret_key() -> None:
    ''' My Key ! '''
    TPManiaMessageBox(
        QMessageBox.Icon.NoIcon,
        (
            "You've found a Secret Key ! <br>"
            "...you are no longer alone..."
        ),
        "⟡ SECRET 🗝️ ⟡",
    )
