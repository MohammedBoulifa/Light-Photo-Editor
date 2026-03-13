; Light - Photo Editor
; Inno Setup Script
; By Mohammed Boulifa

#define MyAppName "Light - Photo Editor"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Mohammed Boulifa"
#define MyAppExeName "Light - Photo Editor.exe"
#define MyAppIconFile "Icon.png"

[Setup]
AppId={{A3F2B1C4-7E8D-4F2A-9B3C-1D5E6F7A8B9C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL=https://github.com/MohammedBoulifa
AppSupportURL=https://github.com/MohammedBoulifa
AppUpdatesURL=https://github.com/MohammedBoulifa
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; Output settings
OutputDir=Installer_Output
OutputBaseFilename=Light-PhotoEditor-Setup-v1.0.0
Compression=lzma2/ultra64
SolidCompression=yes
; Modern wizard style
WizardStyle=modern
; Minimum Windows version: Windows 10 (required for dark-mode API used in Light.py)
MinVersion=10.0
; 64-bit only
ArchitecturesInstallIn64BitMode=x64
; Uninstaller
UninstallDisplayName={#MyAppName}

WizardImageFile=installer_sidebar.bmp
WizardSmallImageFile=installer_banner.bmp

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: checkedonce

[Files]
; Main executable (built by PyInstaller)
Source: "dist\Light - Photo Editor.exe"; DestDir: "{app}"; Flags: ignoreversion
; App icon — bundled alongside the exe (also used by iconphoto in Light.py)
Source: "Icon.png"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu shortcut
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
; Desktop shortcut (if user chose it)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Offer to launch the app at end of install
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up any files created by the app on uninstall
Type: filesandordirs; Name: "{app}"
