; Huntarr-2 Windows Installer Script
; NSIS Modern User Interface

!include "MUI2.nsh"
!include "FileFunc.nsh"

; General
Name "Huntarr-2"
!define PRODUCT_NAME "Huntarr-2"
!define PRODUCT_PUBLISHER "Huntarr-2"
!define PRODUCT_WEB_SITE "https://github.com/xtamtamx/huntarr-2"

; Read version from file
!searchparse /file "${VERSIONFILE}" "" VERSION
OutFile "installer\${PRODUCT_NAME}-${VERSION}-win.exe"
InstallDir "$PROGRAMFILES64\${PRODUCT_NAME}"
InstallDirRegKey HKLM "Software\${PRODUCT_NAME}" "InstallDir"
RequestExecutionLevel admin

; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${PROJECT_ROOT}\frontend\static\logo\huntarr.ico"
!define MUI_UNICON "${PROJECT_ROOT}\frontend\static\logo\huntarr.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "${PROJECT_ROOT}\LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installer Sections
Section "Install"
    SetOutPath "$INSTDIR"
    
    ; Copy all files from PyInstaller dist
    File /r "${PROJECT_ROOT}\dist\Huntarr-2\*.*"
    
    ; Create config directory in AppData
    CreateDirectory "$APPDATA\Huntarr-2\config"
    CreateDirectory "$APPDATA\Huntarr-2\config\logs"
    
    ; Create Start Menu shortcuts
    CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
    CreateShortcut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk" "$INSTDIR\Huntarr-2.exe"
    CreateShortcut "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
    
    ; Create Desktop shortcut
    CreateShortcut "$DESKTOP\${PRODUCT_NAME}.lnk" "$INSTDIR\Huntarr-2.exe"
    
    ; Write uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; Write registry keys for Add/Remove Programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "DisplayName" "${PRODUCT_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "DisplayIcon" "$INSTDIR\Huntarr-2.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "Publisher" "${PRODUCT_PUBLISHER}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "DisplayVersion" "${VERSION}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "NoRepair" 1
    
    ; Get installed size
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "EstimatedSize" "$0"
SectionEnd

; Uninstaller Section
Section "Uninstall"
    ; Remove files
    RMDir /r "$INSTDIR"
    
    ; Remove Start Menu shortcuts
    RMDir /r "$SMPROGRAMS\${PRODUCT_NAME}"
    
    ; Remove Desktop shortcut
    Delete "$DESKTOP\${PRODUCT_NAME}.lnk"
    
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
    DeleteRegKey HKLM "Software\${PRODUCT_NAME}"
    
    ; Note: We don't remove AppData config to preserve user settings
SectionEnd
