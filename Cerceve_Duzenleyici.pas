unit Cerceve_Duzenleyici;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.ComCtrls;

type
  TDurumDegistiOlayi = procedure(Gonderen: TObject; Kaydedebilir, Silebilir: Boolean) of object;

  // Helper function to find RichEdit in a tab
  function GetMevcutZenginMetinEditoru(ASekme: TTabSheet): TRichEdit;

  TCerceveDuzenleyici = class(TFrame)
    SekmeKontrolu: TPageControl;
    tsKarsilama: TTabSheet;
    Label1: TLabel;
    Label2: TLabel;
    procedure SekmeKontroluDegisim(Sender: TObject);
    procedure SekmeKontroluSekmeKapat(Sender: TObject; var ASekme: TTabSheet);
  private
    FOnDurumDegisti: TDurumDegistiOlayi;
    function NotSekmesiniBul(NotID: Integer): TTabSheet;
    procedure ZenginMetinEditoruDegisim(Sender: TObject);
    procedure DurumuGuncelle;
  public
    function NotuSekmedeAc(NotID: Integer): Boolean;
    procedure MevcutNotuKaydet;
    procedure MevcutNotuSil;
    function KaydedilmemisDegisiklikVar: Boolean;
    function KaydedilmemisDegisiklikleriKontrolEt(Sekme: TTabSheet): Boolean;
    property OnDurumDegisti: TDurumDegistiOlayi read FOnDurumDegisti write FOnDurumDegisti;
  end;

implementation

uses VeriModulu, System.IOUtils;

{$R *.dfm}

function GetMevcutZenginMetinEditoru(ASekme: TTabSheet): TRichEdit;
begin
  Result := nil;
  if (ASekme <> nil) and (ASekme.ControlCount > 0) and (ASekme.Controls[0] is TRichEdit) then
    Result := TRichEdit(ASekme.Controls[0]);
end;

{ TCerceveDuzenleyici }

function TCerceveDuzenleyici.NotSekmesiniBul(NotID: Integer): TTabSheet;
var
  i: Integer;
begin
  Result := nil;
  for i := 0 to SekmeKontrolu.PageCount - 1 do
  begin
    if SekmeKontrolu.Pages[i].Tag = NotID then
    begin
      Result := SekmeKontrolu.Pages[i];
      Break;
    end;
  end;
end;

procedure TCerceveDuzenleyici.DurumuGuncelle;
var
  Kaydedebilir, Silebilir: Boolean;
begin
  Kaydedebilir := False;
  Silebilir := False;
  if (SekmeKontrolu.ActivePage <> nil) and (SekmeKontrolu.ActivePage <> tsKarsilama) then
  begin
    Silebilir := True;
    if SekmeKontrolu.ActivePage.Caption.EndsWith('*') then
      Kaydedebilir := True;
  end;

  if Assigned(FOnDurumDegisti) then
    FOnDurumDegisti(Self, Kaydedebilir, Silebilir);
end;

procedure TCerceveDuzenleyici.ZenginMetinEditoruDegisim(Sender: TObject);
var
  Sekme: TTabSheet;
begin
  if GetMevcutZenginMetinEditoru(SekmeKontrolu.ActivePage) = Sender as TRichEdit then
  begin
    Sekme := SekmeKontrolu.ActivePage;
    if not Sekme.Caption.EndsWith('*') then
      Sekme.Caption := Sekme.Caption + '*';
    DurumuGuncelle;
  end;
end;

function TCerceveDuzenleyici.NotuSekmedeAc(NotID: Integer): Boolean;
var
  Sekme: TTabSheet;
  ZenginMetinEditoru: TRichEdit;
  Sorgu: TFDQuery;
  Akis: TStream;
begin
  Result := False;
  Sekme := NotSekmesiniBul(NotID);
  if Assigned(Sekme) then
  begin
    SekmeKontrolu.ActivePage := Sekme;
    Result := True;
    Exit;
  end;

  Sorgu := TFDQuery.Create(nil);
  try
    Sorgu.Connection := ModulVeri.Baglanti;
    Sorgu.SQL.Text := 'SELECT * FROM Notlar WHERE ID = :ID';
    Sorgu.ParamByName('ID').AsInteger := NotID;
    Sorgu.Open;

    if not Sorgu.IsEmpty then
    begin
      Sekme := TTabSheet.Create(SekmeKontrolu);
      Sekme.PageControl := SekmeKontrolu;
      Sekme.Caption := Sorgu.FieldByName('Baslik').AsString;
      Sekme.Tag := NotID;

      ZenginMetinEditoru := TRichEdit.Create(Sekme);
      ZenginMetinEditoru.Parent := Sekme;
      ZenginMetinEditoru.Align := alClient;
      ZenginMetinEditoru.ScrollBars := ssVertical;
      ZenginMetinEditoru.Font.Name := 'Segoe UI';
      ZenginMetinEditoru.Font.Size := 10;
      ZenginMetinEditoru.OnChange := ZenginMetinEditoruDegisim;

      Akis := Sorgu.CreateBlobStream(Sorgu.FieldByName('Icerik'), bmRead);
      try
        if Akis.Size > 0 then
          ZenginMetinEditoru.Lines.LoadFromStream(Akis);
      finally
        Akis.Free;
      end;

      SekmeKontrolu.ActivePage := Sekme;
      Result := True;
    end;
  finally
    Sorgu.Free;
  end;
end;

procedure TCerceveDuzenleyici.MevcutNotuKaydet;
var
  ZenginMetinEditoru: TRichEdit;
  NotID: Integer;
  NotBasligi: string;
  Akis: TStream;
  Sekme: TTabSheet;
begin
  Sekme := SekmeKontrolu.ActivePage;
  ZenginMetinEditoru := GetMevcutZenginMetinEditoru(Sekme);
  if (Sekme = nil) or (ZenginMetinEditoru = nil) then Exit;

  NotID := Sekme.Tag;
  if NotID > 0 then
  begin
    if ZenginMetinEditoru.Lines.Count > 0 then
      NotBasligi := ZenginMetinEditoru.Lines[0]
    else
      NotBasligi := 'Başlıksız Not';
    if Length(NotBasligi) > 100 then NotBasligi := Copy(NotBasligi, 1, 100);

    Akis := TMemoryStream.Create;
    try
      ZenginMetinEditoru.Lines.SaveToStream(Akis);
      Akis.Position := 0;
      ModulVeri.KomutNotGuncelle.ParamByName('Baslik').AsString := NotBasligi;
      ModulVeri.KomutNotGuncelle.ParamByName('Icerik').LoadFromStream(Akis, ftBlob);
      ModulVeri.KomutNotGuncelle.ParamByName('Icerik_Metin').AsString := ZenginMetinEditoru.Lines.Text;
      ModulVeri.KomutNotGuncelle.ParamByName('Tarih').AsDateTime := Now;
      ModulVeri.KomutNotGuncelle.ParamByName('ID').AsInteger := NotID;
      ModulVeri.KomutNotGuncelle.Execute;
    finally
      Akis.Free;
    end;
    Sekme.Caption := NotBasligi;
    DurumuGuncelle;
  end;
end;

procedure TCerceveDuzenleyici.MevcutNotuSil;
var
  NotID: Integer;
  Sekme: TTabSheet;
begin
  Sekme := SekmeKontrolu.ActivePage;
  if (Sekme <> nil) and (Sekme <> tsKarsilama) then
  begin
    if MessageDlg('Bu notu silmek istediğinizden emin misiniz?', mtConfirmation, [mbYes, mbNo], 0) = mrYes then
    begin
      NotID := Sekme.Tag;
      ModulVeri.Baglanti.ExecSQL('DELETE FROM Not_Etiketler WHERE NotID = :ID', [NotID]);
      ModulVeri.Baglanti.ExecSQL('DELETE FROM Notlar WHERE ID = :ID', [NotID]);
      Sekme.Free; // FreeOnRelease yerine Free daha uygun çünkü olay bitti.
    end;
  end;
end;

function TCerceveDuzenleyici.KaydedilmemisDegisiklikleriKontrolEt(Sekme: TTabSheet): Boolean;
var
  Cevap: Integer;
begin
  Result := True; // Kapatılabilir varsayalım
  if Sekme.Caption.EndsWith('*') then
  begin
    SekmeKontrolu.ActivePage := Sekme;
    Cevap := MessageDlg(StringReplace(Sekme.Caption, '*', '', []) + ' notundaki değişiklikleri kaydedilsin mi?',
      mtConfirmation, [mbYes, mbNo, mbCancel], 0);
    case Cevap of
      mrYes: MevcutNotuKaydet;
      mrNo:  { Hiçbir şey yapma, sadece kapat };
      mrCancel: Result := False; // Kapatma
    end;
  end;
end;

function TCerceveDuzenleyici.KaydedilmemisDegisiklikVar: Boolean;
var
  i: Integer;
begin
  Result := False;
  for i := 0 to SekmeKontrolu.PageCount - 1 do
  begin
    if SekmeKontrolu.Pages[i].Caption.EndsWith('*') then
    begin
      Result := True;
      Break;
    end;
  end;
end;

procedure TCerceveDuzenleyici.SekmeKontroluDegisim(Sender: TObject);
begin
  DurumuGuncelle;
end;

procedure TCerceveDuzenleyici.SekmeKontroluSekmeKapat(Sender: TObject; var ASekme: TTabSheet);
begin
  if not KaydedilmemisDegisiklikleriKontrolEt(ASekme) then
    Abort; // Sekme kapatma işlemini iptal et
end;

end.
