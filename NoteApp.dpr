program NoteApp;

uses
  Vcl.Forms,
  UMainForm in 'UMainForm.pas' {MainForm},
  UDataModule in 'UDataModule.pas' {DM: TDataModule};

{$R *.res}

begin
  Application.Initialize;
  Application.MainFormOnTaskbar := True;
  Application.CreateForm(TMainForm, MainForm);
  Application.CreateForm(TDM, DM);
  Application.Run;
end.
