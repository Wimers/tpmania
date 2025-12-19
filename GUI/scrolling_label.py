# Import Pyside6 Modules
from PySide6.QtWidgets import (
    QLabel,
)
from PySide6.QtGui import (
    QFont,
    QPainter,
)

# Assorted Constants
ACTIVE = True
INACTIVE = False
EMPTY_STRING = ""
TEXT_BUFFER = "   "
PIXLES_PER_TICK = 1  # pixels per frame
MAGIC_NUMBER = 17
BREAK_POINT = 64


class ScrollingLabel(QLabel):
    '''
    A class to create and control Scrolling text labels.

    Inherits from QLabel
    '''
    def __init__(
            self,
            parent=None,
            text=EMPTY_STRING,
            font=QFont("Consolas", 9),
    ):
        ''' Initialises the label with the specified text and font '''
        super().__init__(parent)
        self._active = INACTIVE
        self.offset = 0
        self.setText(text)
        self.setFont(font)

    def get_active(self) -> bool:
        ''' Returns True is scrolling is active, else false '''
        return self._active

    def set_active(self, state: bool) -> None:
        '''
        Sets the scrolling state of lable, if set to INACTIVE
        repaints the label in default way.

        Parameters:
            state (bool): activity state
        '''
        self._active = state
        if (state is INACTIVE):
            self.offset = 0
            self.repaint()

    def tick(self) -> None:
        ''' Repaints the label, scrolling if active '''
        if (len(self.text()) <= MAGIC_NUMBER):
            self.set_active(INACTIVE)
        else:
            # Calculates text width with a buffer
            text_width = (
                self
                .fontMetrics()
                .horizontalAdvance(
                    self.text() + TEXT_BUFFER
                )
            )

            self.offset += PIXLES_PER_TICK
            if (text_width < self.offset):
                self.offset = 0

        # Trigger repaint
        self.repaint()

    def paintEvent(self, event):
        ''' Overwrites default paintEvent, enabling text scrolling effect '''
        # Use default paintEvent if INACTIVE
        if (self.get_active() is INACTIVE):
            super().paintEvent(event)
            return

        painter = QPainter(self)

        x_pos = -self.offset
        y_pos = 12

        counter = 0

        while (x_pos < self.width()):

            # Ensure loop will eventually break
            if (counter > BREAK_POINT):
                break

            # Repaint
            painter.drawText(x_pos, y_pos, self.text())

            # Calculate text width
            text_width = (
                self
                .fontMetrics()
                .horizontalAdvance(
                    self.text() + TEXT_BUFFER
                )
            )

            # Update position and counter
            x_pos += text_width
            counter += 1
