
; The name of the installer
Name "SaiyanQuest"

; Set the icon for the installer
Icon "../mods/SaiyanQuest/gfx/icon.ico"

; The file to write
OutFile "SaiyanQuest-installer.exe"

; Request application privileges for Windows Vista and higher
RequestExecutionLevel admin

; Build Unicode installer
Unicode True

; The default installation directory
InstallDir $PROGRAMFILES\SaiyanQuest

; Registry key to check for directory (so if you install again, it will 
; overwrite the old one automatically)
InstallDirRegKey HKLM "Software\SaiyanQuest" "Install_Dir"

;--------------------------------

; Include Modern UI
!include "MUI2.nsh"

; MUI Settings
!define MUI_ABORTWARNING

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "$%TXMNBuildDir%\LICENSE"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "English"

;--------------------------------
LicenseData "$%TXMNBuildDir%\LICENSE"

!define VERSION "0.4.35.0"
VIProductVersion "${VERSION}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "ProductName" "SaiyanQuest"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileVersion" "${VERSION}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileDescription" "SaiyanQuest is a free, open source monster-fighting RPG."
VIAddVersionKey /LANG=${LANG_ENGLISH} "LegalCopyright" "GNU GPL v3"

; The stuff to install
Section "SaiyanQuest (required)"

  SectionIn RO

  ; Set output path to the installation directory.
  SetOutPath $INSTDIR

  ; Put file there
  File "$%TXMNBuildDir%\run_SaiyanQuest.exe"
  File /r "$%TXMNBuildDir%\*"

  ; Write the installation path into the registry
  WriteRegStr HKLM SOFTWARE\SaiyanQuest "Install_Dir" "$INSTDIR"

  ; Write the uninstall keys for Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SaiyanQuest" "DisplayName" "SaiyanQuest"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SaiyanQuest" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SaiyanQuest" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SaiyanQuest" "NoRepair" 1
  WriteUninstaller "$INSTDIR\uninstall.exe"

SectionEnd

; Optional section (can be disabled by the user)
Section "Start Menu Shortcuts"

  CreateDirectory "$SMPROGRAMS\SaiyanQuest"
  CreateShortcut "$SMPROGRAMS\SaiyanQuest\SaiyanQuest.lnk" "$INSTDIR\SaiyanQuest.nsi"

SectionEnd

;--------------------------------

; Uninstaller

Section "Uninstall"

  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SaiyanQuest"
  DeleteRegKey HKLM SOFTWARE\NSIS_SaiyanQuest

  ; Remove files and uninstaller
  Delete $INSTDIR\run_SaiyanQuest.exe
  Delete $INSTDIR\uninstall.exe
  Delete $INSTDIR\*

  ; Remove shortcuts, if any
  Delete "$SMPROGRAMS\SaiyanQuest\*.lnk"

  ; Remove directories
  RMDir "$SMPROGRAMS\SaiyanQuest"
  RMDir "$INSTDIR"

SectionEnd
