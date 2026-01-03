; Inno Setup Script for STT Keyboard (Windows)
; https://jrsoftware.org/isinfo.php

#define MyAppName "STT Keyboard"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "STT Keyboard Team"
#define MyAppURL "https://github.com/yourusername/stt-keyboard"
#define MyAppExeName "STTKeyboard.exe"

[Setup]
; Application information
AppId={{E3F9A8B4-2C5D-4E6F-9A8B-1C3D5E7F9A0B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Installation directories
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output
OutputDir=dist
OutputBaseFilename=STTKeyboard-Setup-{#MyAppVersion}

; Compression
Compression=lzma
SolidCompression=yes

; Visual
WizardStyle=modern
SetupIconFile=resources\icon.ico

; Privileges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Architecture
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main executable and files
Source: "dist\STTKeyboard\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\STTKeyboard\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Documentation
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "QUICKSTART.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion;

; Helper scripts
Source: "dist\download_model.py"; DestDir: "{app}"; Flags: ignoreversion

; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Optionally run the application after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;

  // Check if Visual C++ Redistributable is installed
  if not RegKeyExists(HKLM, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64') then
  begin
    if MsgBox('This application requires Microsoft Visual C++ Redistributable.' + #13#10 +
              'Would you like to download it now?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      ShellExec('open', 'https://aka.ms/vs/17/release/vc_redist.x64.exe', '', '', SW_SHOW, ewNoWait, ResultCode);
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Create models directory
    CreateDir(ExpandConstant('{app}\models'));

    // Show message about downloading models
    MsgBox('Installation complete!' + #13#10 + #13#10 +
           'Before using STT Keyboard, you need to download a speech recognition model.' + #13#10 + #13#10 +
           'Please run: python download_model.py --language en-us --size small' + #13#10 + #13#10 +
           'Or see the QUICKSTART.md file for detailed instructions.',
           mbInformation, MB_OK);
  end;
end;
