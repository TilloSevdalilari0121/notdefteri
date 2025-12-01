program NotDefteri;

uses
  Vcl.Forms,
  AnaForm in 'AnaForm.pas' {FrmAna},
  VeriModulu in 'VeriModulu.pas' {ModulVeri: TDataModule},
  Cerceve_Gezgin in 'Cerceve_Gezgin.pas' {CerceveGezgin: TFrame},
  Cerceve_NotListesi in 'Cerceve_NotListesi.pas' {CerceveNotListesi: TFrame},
  Cerceve_Duzenleyici in 'Cerceve_Duzenleyici.pas' {CerceveDuzenleyici: TFrame};

{$R *.res}

begin
  Application.Initialize;
  Application.MainFormOnTaskbar := True;
  Application.CreateForm(TFrmAna, FrmAna);
  Application.CreateForm(TModulVeri, ModulVeri);
  Application.Run;
end.
