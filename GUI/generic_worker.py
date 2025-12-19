# Import Pyside6 Modules
from PySide6.QtCore import (
    QObject,
    Signal,
)

# Used for type hinting
from typing import Any, Callable


class GenericWorker(QObject):
    '''
    The GenericWorker class handles processes by running
    them in a separate thread.

    It inherits from QObject to use signals and slots.
    '''
    # Signals for communicating with the main GUI thread
    result = Signal(object)
    error = Signal(Exception)
    finished = Signal()

    def __init__(
            self,
            function: Callable[..., Any],
            *args: Any,
            id: int,
    ) -> None:
        ''' Initializes the Worker with a function and its arguments '''
        super().__init__()
        self._function = function
        self._args = args
        self._id = id

    def get_function(self) -> Callable[..., Any]:
        ''' Returns the function callable '''
        return self._function

    def get_args(self) -> tuple[Any, ...]:
        ''' Returns tuple of input arguments '''
        return self._args

    def run(self) -> None:
        ''' Attempts to run input function '''
        try:
            return_value = self.get_function()(*self.get_args())
            self.result.emit(return_value)
        except Exception as error:
            self.error.emit(error)
            print(f"Error: {error}")  # debugging
        finally:
            self.finished.emit()
