!include "MUI.nsh"
!define ASSETS_DIR "assets"
!define GUI_DIR "GUI"
!define PYTHON_DIR "python"
!define GENERATED_FILES_DIR "generated"
!define FFMPEG_DIR "FFmpeg"

!define ICON_FILE_NAME "setup.ico"
!define ICON_PATH "${ASSETS_DIR}\${ICON_FILE_NAME}"
!define MUI_ICON "${ICON_PATH}"
!define HEADER_IMAGE "${ASSETS_DIR}\land.bmp"

!define MAIN "main.py"
!define LICENSE "LICENSE.txt"
!define PROGRAM "tpmania"
!define TARGET "tpmania.bat"
!define INSTALLER "Install.exe"
!define UNINSTALLER "Uninstall.exe"
!define PUBLISHER "engg2800-g7"
Var SMDir

Name "${PROGRAM}"
InstallDir "$PROGRAMFILES\${PROGRAM}"
OutFile "${INSTALLER}"
BrandingText "${PUBLISHER}"

!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "${HEADER_IMAGE}"
!define MUI_WELCOMEFINISHPAGE_BITMAP "${HEADER_IMAGE}"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "${LICENSE}"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_STARTMENU "${PROGRAM}" $SMDir
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_DIRECTORY
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"


Section ""
    SetOutPath $INSTDIR

    File "${MAIN}"
    File "${TARGET}"
    File "${LICENSE}"

    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROGRAM}" "DisplayName" "${PROGRAM}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROGRAM}" "DisplayVersion" "1.4.3"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROGRAM}" "Publisher" "${PUBLISHER}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROGRAM}" "DisplayIcon" "$INSTDIR\${ICON_PATH}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROGRAM}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROGRAM}" "NoRepair" 1
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROGRAM}" "UninstallString" "$INSTDIR\${UNINSTALLER}"

    !insertmacro MUI_STARTMENU_WRITE_BEGIN "${PROGRAM}"
    CreateShortCut "$SMPROGRAMS\$SMDir\${PROGRAM}.lnk" "$INSTDIR\${TARGET}" "" "$INSTDIR\${ICON_PATH}" 0
    CreateShortCut "$SMPROGRAMS\$SMDir\Uninstall ${PROGRAM}.lnk" "$INSTDIR\${UNINSTALLER}"
    !insertmacro MUI_STARTMENU_WRITE_END

    CreateShortCut "$DESKTOP\${PROGRAM}.lnk" "$INSTDIR\${TARGET}" "" "$INSTDIR\${ICON_PATH}" 0

    SetOutPath "$INSTDIR\${ASSETS_DIR}" 
    File /r "${ASSETS_DIR}\*.*"

    SetOutPath "$INSTDIR\${PYTHON_DIR}"
    File /r "${PYTHON_DIR}\*.*"

    SetOutPath "$INSTDIR\${FFMPEG_DIR}"
    File /r "${FFMPEG_DIR}\*.*"

    SetOutPath "$INSTDIR\${GUI_DIR}"
    File /r "${GUI_DIR}\*.*"

    SetOutPath "$INSTDIR\${GENERATED_FILES_DIR}"
    CreateDirectory "$INSTDIR\${GENERATED_FILES_DIR}"

    WriteUninstaller "$INSTDIR\${UNINSTALLER}"
SectionEnd


Section "Uninstall"
    !insertmacro MUI_STARTMENU_GETFOLDER "${PROGRAM}" $SMDir
    Delete "$SMPROGRAMS\$SMDir\${PROGRAM}.lnk"
    Delete "$SMPROGRAMS\$SMDir\Uninstall ${PROGRAM}.lnk"
    RMDir "$SMPROGRAMS\$SMDir"

    Delete "$DESKTOP\${PROGRAM}.lnk"
    Delete "$INSTDIR\${MAIN}"
    Delete "$INSTDIR\${TARGET}"
    Delete "$INSTDIR\${LICENSE}"
    Delete "$INSTDIR\${UNINSTALLER}"

    RMDir /r "$INSTDIR\${ASSETS_DIR}"
    RMDir /r "$INSTDIR\${GUI_DIR}"
    RMDir /r "$INSTDIR\${PYTHON_DIR}"
    RMDir /r "$INSTDIR\${GENERATED_FILES_DIR}"
    RMDir /r "$INSTDIR\${FFMPEG_DIR}"

    SetOutPath $PROGRAMFILES
    RMDir $INSTDIR

    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROGRAM}"
SectionEnd
