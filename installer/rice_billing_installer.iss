; Rice Billing System - Inno Setup Installer Script
; Windows 7+ Compatible Installer
;
; Build this installer:
;   1. Build executable first: python build_executable.py --clean
;   2. Install Inno Setup 6: https://jrsoftware.org/isinfo.php
;   3. Compile: Right-click this file -> Compile (or use ISCC.exe)
;
; Output: RiceBillingSystem_Setup.exe

#define MyAppName "Rice Billing System"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "AYOP BIN ARSHAD"
#define MyAppURL "https://github.com/littlecharlie/program_beli_padi"
#define MyAppExeName "RiceBillingSystem.exe"
#define MyAppDescription "Rice Purchase & Delivery Management System"

[Setup]
; Application Information
AppId={{8F4E6C9A-1B2D-4E3F-9A8B-7C6D5E4F3A2B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppCopyright=Copyright (C) 2024 {#MyAppPublisher}
AppComments={#MyAppDescription}

; Installation Directories
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output
OutputDir=..\installer_output
OutputBaseFilename=RiceBillingSystem_Setup_v{#MyAppVersion}
SetupIconFile=..\resources\app_icon.ico

; Compression
Compression=lzma2/max
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMANumBlockThreads=2

; Windows Version Compatibility
MinVersion=6.1sp1
; 6.1sp1 = Windows 7 SP1
; Also compatible with: Windows 8, 8.1, 10, 11

; Privileges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; UI Configuration
WizardStyle=modern
WizardImageFile=compiler:WizModernImage-IS.bmp
WizardSmallImageFile=compiler:WizModernSmallImage-IS.bmp

; Uninstall
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

; Misc
ArchitecturesInstallIn64BitMode=x64
DisableWelcomePage=no
LicenseFile=LICENSE.txt
InfoBeforeFile=INSTALL_INFO.txt

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Types]
Name: "full"; Description: "Full Installation (Recommended)"
Name: "minimal"; Description: "Minimal Installation"
Name: "custom"; Description: "Custom Installation"; Flags: iscustom

[Components]
Name: "core"; Description: "Core Application Files"; Types: full minimal custom; Flags: fixed
Name: "shortcuts"; Description: "Desktop and Start Menu Shortcuts"; Types: full custom
Name: "config"; Description: "Configuration Files"; Types: full minimal custom; Flags: fixed
Name: "docs"; Description: "Documentation (README)"; Types: full custom

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Components: shortcuts
Name: "quicklaunchicon"; Description: "Create a &Quick Launch icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
; Core Application Files
Source: "..\dist\RiceBillingSystem\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core

; Configuration Files
Source: "config_templates\.env.template"; DestDir: "{app}"; DestName: ".env.example"; Flags: ignoreversion; Components: config
Source: "config_templates\config.ini.template"; DestDir: "{app}"; DestName: "config.ini"; Flags: onlyifdoesntexist; Components: config

; Documentation
Source: "..\README.md"; DestDir: "{app}"; DestName: "README.txt"; Flags: ignoreversion isreadme; Components: docs
Source: "INSTALL_INFO.txt"; DestDir: "{app}"; Flags: ignoreversion; Components: docs

; License
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion; Components: core

; Post-installation scripts
Source: "scripts\first_run_setup.py"; DestDir: "{app}\scripts"; Flags: ignoreversion; Components: core
Source: "scripts\check_database.py"; DestDir: "{app}\scripts"; Flags: ignoreversion; Components: core

; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
; Start Menu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\resources\app_icon.ico"
Name: "{group}\Configure Database"; Filename: "notepad.exe"; Parameters: "{app}\.env"; Comment: "Configure database connection"
Name: "{group}\User Guide"; Filename: "{app}\README.txt"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop Icon
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\resources\app_icon.ico"

; Quick Launch
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon; IconFilename: "{app}\resources\app_icon.ico"

[Registry]
; File associations (optional - for future use with .rbs files)
; Add application path to registry
Root: HKLM; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; Flags: uninsdeletekeyifempty
Root: HKLM; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"
Root: HKLM; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"

[Run]
; First-time configuration wizard (optional)
Filename: "{app}\scripts\first_run_setup.py"; Description: "Run first-time configuration"; Flags: postinstall skipifsilent nowait; Check: HasPython

; Launch application
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

; Open README
Filename: "{app}\README.txt"; Description: "View README file"; Flags: postinstall shellexec skipifsilent unchecked

[UninstallRun]
; Cleanup tasks before uninstall
Filename: "{app}\scripts\cleanup.bat"; Flags: runhidden; RunOnceId: "cleanup"

[UninstallDelete]
; Delete user-created files
Type: files; Name: "{app}\.env"
Type: files; Name: "{app}\*.log"
Type: filesandordirs; Name: "{app}\exports"
Type: filesandordirs; Name: "{app}\backups"
Type: dirifempty; Name: "{app}"

[Code]
var
  DatabaseConfigPage: TInputQueryWizardPage;
  DemoModePage: TInputOptionWizardPage;

function HasPython: Boolean;
var
  ResultCode: Integer;
begin
  // Check if Python is installed
  Result := Exec('python', '--version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

procedure InitializeWizard;
begin
  // Create demo mode selection page
  DemoModePage := CreateInputOptionPage(wpSelectComponents,
    'Database Configuration', 'How would you like to run the application?',
    'Please select whether to use a database or run in demo mode.',
    True, False);
  DemoModePage.Add('Use PostgreSQL Database (Recommended for production)');
  DemoModePage.Add('Demo Mode (No database required - for testing only)');
  DemoModePage.Values[0] := True;

  // Create database configuration page (only shown if database mode selected)
  DatabaseConfigPage := CreateInputQueryPage(DemoModePage.ID,
    'Database Connection', 'Enter your PostgreSQL database connection details',
    'The application will use these settings to connect to your database.');
  DatabaseConfigPage.Add('Database Host:', False);
  DatabaseConfigPage.Add('Database Port:', False);
  DatabaseConfigPage.Add('Database Name:', False);
  DatabaseConfigPage.Add('Database User:', False);
  DatabaseConfigPage.Add('Database Password:', True);

  // Default values
  DatabaseConfigPage.Values[0] := 'localhost';
  DatabaseConfigPage.Values[1] := '5432';
  DatabaseConfigPage.Values[2] := 'rice_billing_db';
  DatabaseConfigPage.Values[3] := 'postgres';
  DatabaseConfigPage.Values[4] := '';
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  // Skip database config page if demo mode selected
  if (PageID = DatabaseConfigPage.ID) and DemoModePage.Values[1] then
    Result := True
  else
    Result := False;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  EnvFile: string;
  EnvContent: TArrayOfString;
  I: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    EnvFile := ExpandConstant('{app}\.env');

    // Create .env file with user's configuration
    SetArrayLength(EnvContent, 0);

    if DemoModePage.Values[1] then
    begin
      // Demo mode
      SetArrayLength(EnvContent, GetArrayLength(EnvContent) + 1);
      EnvContent[High(EnvContent)] := '# Rice Billing System Configuration - DEMO MODE';
      SetArrayLength(EnvContent, GetArrayLength(EnvContent) + 1);
      EnvContent[High(EnvContent)] := '';
      SetArrayLength(EnvContent, GetArrayLength(EnvContent) + 1);
      EnvContent[High(EnvContent)] := 'DEMO_MODE=true';
      SetArrayLength(EnvContent, GetArrayLength(EnvContent) + 1);
      EnvContent[High(EnvContent)] := '';
      SetArrayLength(EnvContent, GetArrayLength(EnvContent) + 1);
      EnvContent[High(EnvContent)] := '# Database configuration (not used in demo mode)';
      SetArrayLength(EnvContent, GetArrayLength(EnvContent) + 1);
      EnvContent[High(EnvContent)] := 'DB_HOST=localhost';
      SetArrayLength(EnvContent, GetArrayLength(EnvContent) + 1);
      EnvContent[High(EnvContent)] := 'DB_PORT=5432';
      SetArrayLength(EnvContent, GetArrayLength(EnvContent) + 1);
      EnvContent[High(EnvContent)] := 'DB_NAME=rice_billing_db';
      SetArrayLength(EnvContent, GetArrayLength(EnvContent) + 1);
      EnvContent[High(EnvContent)] := 'DB_USER=postgres';
      SetArrayLength(EnvContent, GetArrayLength(EnvContent) + 1);
      EnvContent[High(EnvContent)] := 'DB_PASSWORD=';
    end
    else
    begin
      // Database mode
      SetArrayLength(EnvContent, GetArrayLength(EnvContent) + 1);
      EnvContent[High(EnvContent)] := '# Rice Billing System Configuration';
      SetArrayLength(EnvContent, GetArrayLength(EnvContent) + 1);
      EnvContent[High(EnvContent)] := '';
      SetArrayLength(EnvContent, GetArrayLength(EnvContent) + 1);
      EnvContent[High(EnvContent)] := 'DEMO_MODE=false';
      SetArrayLength(EnvContent, GetArrayLength(EnvContent) + 1);
      EnvContent[High(EnvContent)] := '';
      SetArrayLength(EnvContent, GetArrayLength(EnvContent) + 1);
      EnvContent[High(EnvContent)] := '# Database Configuration';
      SetArrayLength(EnvContent, GetArrayLength(EnvContent) + 1);
      EnvContent[High(EnvContent)] := 'DB_HOST=' + DatabaseConfigPage.Values[0];
      SetArrayLength(EnvContent, GetArrayLength(EnvContent) + 1);
      EnvContent[High(EnvContent)] := 'DB_PORT=' + DatabaseConfigPage.Values[1];
      SetArrayLength(EnvContent, GetArrayLength(EnvContent) + 1);
      EnvContent[High(EnvContent)] := 'DB_NAME=' + DatabaseConfigPage.Values[2];
      SetArrayLength(EnvContent, GetArrayLength(EnvContent) + 1);
      EnvContent[High(EnvContent)] := 'DB_USER=' + DatabaseConfigPage.Values[3];
      SetArrayLength(EnvContent, GetArrayLength(EnvContent) + 1);
      EnvContent[High(EnvContent)] := 'DB_PASSWORD=' + DatabaseConfigPage.Values[4];
    end;

    // Add common configuration
    SetArrayLength(EnvContent, GetArrayLength(EnvContent) + 1);
    EnvContent[High(EnvContent)] := '';
    SetArrayLength(EnvContent, GetArrayLength(EnvContent) + 1);
    EnvContent[High(EnvContent)] := '# Printer Configuration';
    SetArrayLength(EnvContent, GetArrayLength(EnvContent) + 1);
    EnvContent[High(EnvContent)] := 'PRINTER_NAME=EPSON LQ-310';
    SetArrayLength(EnvContent, GetArrayLength(EnvContent) + 1);
    EnvContent[High(EnvContent)] := 'PRINTER_INTERFACE=usb';
    SetArrayLength(EnvContent, GetArrayLength(EnvContent) + 1);
    EnvContent[High(EnvContent)] := '';
    SetArrayLength(EnvContent, GetArrayLength(EnvContent) + 1);
    EnvContent[High(EnvContent)] := '# Logging';
    SetArrayLength(EnvContent, GetArrayLength(EnvContent) + 1);
    EnvContent[High(EnvContent)] := 'LOG_LEVEL=INFO';

    // Save .env file
    SaveStringsToFile(EnvFile, EnvContent, False);
  end;
end;

[Messages]
WelcomeLabel2=This will install [name/ver] on your computer.%n%nThe Rice Billing System helps manage rice purchase transactions and delivery invoices for AYOP BIN ARSHAD rice business.%n%nRecommended: Close all other applications before continuing.
FinishedHeadingLabel=Completing the [name] Setup Wizard
FinishedLabelNoIcons=Setup has finished installing [name] on your computer.%n%nIMPORTANT NEXT STEPS:%n1. If using database mode, ensure PostgreSQL is installed and running%n2. Configure the database connection in the .env file if needed%n3. Install Epson LQ-310 printer driver if not already installed%n4. Launch the application from your desktop or Start Menu
