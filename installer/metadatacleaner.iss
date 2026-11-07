; Inno Setup script for the unofficial Windows port of Metadata Cleaner.
; Requires Inno Setup 6.3 or newer (ArchitecturesAllowed=x64compatible is not
; available in older versions).
;
; Build the payload first (see docs/BUILD.md and installer/README.md). The
; build script writes to a temporary directory outside this repository.
; Then compile with explicit input and output directories:
;   iscc /DAppVersion=4.0.2 /DPayloadDir=<build>\payload /DOutputDir=<build>\installer installer\metadatacleaner.iss
;
; The payload layout is:
;   payload\MetadataCleaner.exe
;   payload\runtime\...
;   payload\share\...
;   payload\tools\exiftool\...
;   payload\tools\ffmpeg\...

#define AppName "Metadata Cleaner"
#ifndef AppVersion
#define AppVersion "4.0.2"
#endif
#define AppPublisher "Ronny Visa"
#define AppURL "https://github.com/rvisas/metadatacleaner-windows"
#define AppExeName "MetadataCleaner.exe"
#define AppUserModelID "io.gitlab.metadatacleaner.metadatacleaner"
#ifndef PayloadDir
  #error Define PayloadDir (the directory containing MetadataCleaner.exe)
#endif
#ifndef OutputDir
  #error Define OutputDir (the installer output directory)
#endif

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
OutputDir={#OutputDir}
OutputBaseFilename=MetadataCleaner-{#AppVersion}-windows-x64-setup
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
UsePreviousAppDir=yes
UsePreviousGroup=yes
UsePreviousTasks=yes
VersionInfoVersion={#AppVersion}.0
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

[InstallDelete]
; Only English and Spanish are shipped. Remove translations left by an older
; build so an upgrade matches a fresh installation.
Type: filesandordirs; Name: "{app}\share\locale"

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#AppExeName}"; IconIndex: 0; AppUserModelID: "{#AppUserModelID}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#AppExeName}"; IconIndex: 0; AppUserModelID: "{#AppUserModelID}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[CustomMessages]
english.UpgradeWelcome=Setup will update Metadata Cleaner from version %1 to %2. Your settings and file list will be kept.
spanish.UpgradeWelcome=El instalador actualizará Metadata Cleaner de la versión %1 a la %2. Tus ajustes y la lista de archivos se conservarán.

[Code]
var
  PreviousVersion: String;

function GetPreviousVersion: String;
var
  Key: String;
  Value: String;
begin
  Result := '';
  Key := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\' +
    '{#SetupSetting("AppId")}' + '_is1';
  if RegQueryStringValue(HKCU, Key, 'DisplayVersion', Value) then
    Result := Value
  else if RegQueryStringValue(HKLM, Key, 'DisplayVersion', Value) then
    Result := Value;
end;

procedure InitializeWizard;
var
  Welcome: String;
begin
  PreviousVersion := GetPreviousVersion;
  if (PreviousVersion <> '') and not WizardSilent then
  begin
    Welcome := ExpandConstant('{cm:UpgradeWelcome}');
    StringChangeEx(Welcome, '%1', PreviousVersion, True);
    StringChangeEx(Welcome, '%2', '{#AppVersion}', True);
    WizardForm.WelcomeLabel2.Caption := Welcome;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  Language: String;
begin
  if CurStep = ssPostInstall then
  begin
    Language := ActiveLanguage;
    if (Language <> 'english') and (Language <> 'spanish') then
      Language := 'english';
    RegWriteStringValue(
      HKCU, 'Software\Metadata Cleaner', 'Language', Language);
  end;
end;
