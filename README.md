# tpmania - Build Instructions & User Manual

**ENGG2800 | Team 7**

This document provides the installation steps, and user manual for the **tpmania** PC software.

---

## 1. Software Installation (GUI)

To install the desktop application:

1.  Launch `Install.exe`.
2.  Follow the on-screen instructions to install the application.
3.  Once installed, open the application using the desktop icon or by searching for "tpmania" in the Windows start menu.

---


## 2. User Manual

### Main Menu
The Main Menu appears upon opening the application.
* **Select Serial Port:** Click the dropdown menu to select the correct port (e.g., COM3) and click **Save**.
* **Reset:** Use the **Reset** button to refresh the menu if the port is not visible.

### File Selection Page

This page allows you to select audio and sequence files to save to the device.
1.  **Select Files:** Click the folder icons next to **Audio** (`.wav`) and **Sequence** (`.tsq`) to select files.
    * *Note:* The selected files must have matching names preceding the file extension.
2.  **Save Selection:** Click **Save** to confirm (or **Reset** to clear).
3.  **Upload to Device:**
    * Select the **Save Location** (RAM or EEPROM).
    * Click **Save** to send the content to the device.
    > **IMPORTANT:** The device must be in the **Main Menu state** (OLED displaying "Start Game!") to save successfully. Attempting to save outside of this state will raise an error.
4.  **Read Device Settings:** Click the icons next to EEPROM or RAM under "View Device Settings" to read the sequence stored on the device (this creates an equivalent `.tsq` file on the PC).

### Metadata Display Page

* **View Info:** Displays metadata (Artist, Name, BPM, Difficulty) for the selected sequence.
* **Audio Controls:** Use the **Play** button to start/pause audio and **Reset** to restart the track.

### Timing Windows Page

Configure the difficulty timing settings.
1.  **Select Level:** Click a scoring row (Perfect, Good, OK, Poor, Miss) in the table.
2.  **Adjust Duration:** Use the slider to set the duration in milliseconds.
3.  **Apply (Local):** Click **Apply** to save changes locally.
4.  **Save (Device):** Click **Save All** to push settings to the device.
    > **IMPORTANT:** The device must be in the **Main Menu state** (Start Game screen) to save settings. Otherwise, an error will occur.
5.  **Read Settings:** Click **Reset** to read the current settings from the device.

---

## 3. Uninstallation

1.  Locate the installation folder by right-clicking the `tpmania` desktop icon and selecting **Open File Location**.
2. Ensure the app is not running.
3.  Run `Uninstall.exe` and follow the on-screen instructions.

---

## 4. Developer Notes

### Editing the GUI
1.  Ensure the `PySide6` python module is installed.
2.  Open a command prompt in the `/GUI` directory and run:
    ```bash
    pyside6-designer
    ```
3.  Open `tpmania_gui.ui` within PySide6 Designer to make edits and save.
4.  Compile the Python file by running the following command in the `/GUI` directory:
    ```bash
    pyside6-uic tpmania_gui.ui -o tpmania_gui.py
    ```

### Compiling Portable Installer
1.  Install **NSIS** from [nsis.sourceforge.io](https://nsis.sourceforge.io/Download).
2.  Right-click on `script.nsi`.
3.  Select **Show more options** > **Compile NSIS Script**.
4.  This generates the portable installer `Install.exe`.
