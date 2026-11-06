; Inno Setup script for the unofficial Windows port of Metadata Cleaner.
; Requires Inno Setup 6.3 or newer (ArchitecturesAllowed=x64compatible is not
; available in older versions).
;
; Build the payload first (see docs/BUILD.md and installer/README.md), then:
;   iscc installer\metadatacleaner.iss
;
; The script expects this layout:
;   dist\payload\MetadataCleaner.exe
;   dist\payload\runtime\...
;   dist\payload\share\...
;   dist\payload\tools\exiftool\...
;   dist\payload\tools\ffmpeg\...

#define AppName "Metadata Cleaner"
#define AppVersion "4.0.1"
#define AppPublisher "Ronny Visa"
#define AppURL "https://github.com/rvisas/metadatacleaner-windows"
#define AppExeName "MetadataCleaner.exe"
#define PayloadDir "..\dist\payload"

[Setup]
AppId={{65A32700-214A-44C6-AA24-3D74B64BC43A}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion} (Windows port)
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}/issues
AppUpdatesURL={#AppURL}/releases
AppCopyright=GPL-3.0-or-later
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE
OutputDir=..\dist\installer
OutputBaseFilename=MetadataCleaner-Setup-{#AppVersion}
SetupIconFile=branding\metadatacleaner-windows.ico
UninstallDisplayIcon={app}\{#AppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.19041
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
CloseApplications=yes
RestartApplications=no
VersionInfoVersion=4.0.1.0
VersionInfoCompany={#AppPublisher}
VersionInfoDescription={#AppName} installer
VersionInfoProductName={#AppName}
VersionInfoProductVersion={#AppVersion}

; Code signing is configured once SignPath Foundation approves the project.
; Uncomment and point SignTool at the signing command or the Inno Setup IDE
; tool entry. Never commit a certificate or private key.
; SignTool=signtool
; SignedUninstaller=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#PayloadDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
