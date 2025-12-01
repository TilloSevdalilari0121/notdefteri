unit Cerceve_NotListesi;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.ComCtrls, Vcl.StdCtrls,
  System.Generics.Collections;

type
  TNotAcmaIstegiOlayi = procedure(Gonderen: TObject; NotID: Integer) of object;
  TFiltreDegistiOlayi = procedure(Gonderen: TObject) of object;

  TCerceveNotListesi = class(TFrame)
    AramaKutusu: TSearchBox;
    lvNotlar: TListView;
    procedure AramaKutusuInvokeSearch(Sender: TObject);
    procedure lvNotlarDblClick(Sender: TObject);
  private
    FOnNotAcmaIstegi: TNotAcmaIstegiOlayi;
    FOnFiltreDegisti: TFiltreDegistiOlayi; // Arama metni değiştiğinde bildirmek için
  public
    procedure NotlariYukle(KategoriID: Integer; EtiketIDleri: TList<Integer>);
    function GetSeciliNotID: Integer;
    property OnNotAcmaIstegi: TNotAcmaIstegiOlayi read FOnNotAcmaIstegi write FOnNotAcmaIstegi;
    property OnFiltreDegisti: TFiltreDegistiOlayi read FOnFiltreDegisti write FOnFiltreDegisti;
  end;

implementation

uses VeriModulu, FireDAC.Comp.Client;

{$R *.dfm}

{ TCerceveNotListesi }

procedure TCerceveNotListesi.NotlariYukle(KategoriID: Integer; EtiketIDleri: TList<Integer>);
var
  Sorgu: TFDQuery;
  ListItem: TListItem;
  SQL: TStrings;
  EtiketIDString: String;
begin
  Sorgu := TFDQuery.Create(nil);
  SQL := TStringList.Create;
  try
    Sorgu.Connection := ModulVeri.Baglanti;

    SQL.Add('SELECT DISTINCT n.ID, n.Baslik, n.GuncellemeTarihi FROM Notlar n');

    if EtiketIDleri.Count > 0 then
    begin
      EtiketIDString := '';
      for var EtiketID in EtiketIDleri do
        EtiketIDString := EtiketIDString + IntToStr(EtiketID) + ',';
      SetLength(EtiketIDString, Length(EtiketIDString) - 1);
      SQL.Add('INNER JOIN Not_Etiketler ne ON n.ID = ne.NotID');
      SQL.Add('WHERE ne.EtiketID IN (' + EtiketIDString + ')'); // IN clause is safe for integers
    end
    else
    begin
      SQL.Add('WHERE 1=1');
    end;

    if KategoriID > -1 then
    begin
      SQL.Add('AND n.KategoriID = :KategoriID');
      Sorgu.ParamByName('KategoriID').AsInteger := KategoriID;
    end;

    if not AramaKutusu.Text.IsEmpty then
    begin
      SQL.Add('AND (n.Baslik LIKE :AramaMetni OR n.Icerik_Metin LIKE :AramaMetni)');
      Sorgu.ParamByName('AramaMetni').AsString := '%' + AramaKutusu.Text + '%';
    end;

    Sorgu.SQL.Text := SQL.Text;
    Sorgu.Open;

    lvNotlar.Items.BeginUpdate;
    try
      lvNotlar.Items.Clear;
      while not Sorgu.Eof do
      begin
        ListItem := lvNotlar.Items.Add;
        ListItem.Caption := Sorgu.FieldByName('Baslik').AsString;
        ListItem.SubItems.Add(FormatDateTime('yyyy-mm-dd hh:nn', Sorgu.FieldByName('GuncellemeTarihi').AsDateTime));
        ListItem.Data := Pointer(Sorgu.FieldByName('ID').AsInteger);
        Sorgu.Next;
      end;
    finally
      lvNotlar.Items.EndUpdate;
    end;
  finally
    Sorgu.Free;
    SQL.Free;
  end;
end;

function TCerceveNotListesi.GetSeciliNotID: Integer;
begin
  Result := -1;
  if Assigned(lvNotlar.Selected) then
    Result := Integer(lvNotlar.Selected.Data);
end;

procedure TCerceveNotListesi.AramaKutusuInvokeSearch(Sender: TObject);
begin
  if Assigned(FOnFiltreDegisti) then
    FOnFiltreDegisti(Self);
end;

procedure TCerceveNotListesi.lvNotlarDblClick(Sender: TObject);
var
  NotID: Integer;
begin
  NotID := GetSeciliNotID;
  if (NotID > 0) and Assigned(FOnNotAcmaIstegi) then
    FOnNotAcmaIstegi(Self, NotID);
end;

end.
