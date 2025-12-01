unit Cerceve_Gezgin;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.ComCtrls, Vcl.CheckLst, Vcl.ExtCtrls,
  System.Generics.Collections;

type
  TFiltreDegistiOlayi = procedure(Gonderen: TObject) of object;

  TCerceveGezgin = class(TFrame)
    grpKategoriler: TGroupBox;
    tvKategoriler: TTreeView;
    Splitter: TSplitter;
    grpEtiketler: TGroupBox;
    clbEtiketler: TCheckListBox;
    procedure tvKategorilerChange(Sender: TObject; Node: TTreeNode);
    procedure clbEtiketlerClickCheck(Sender: TObject);
  private
    FOnFiltreDegisti: TFiltreDegistiOlayi;
  public
    procedure VerileriYukle;
    function GetSeciliKategoriID: Integer;
    procedure GetSeciliEtiketIDleri(EtiketIDleri: TList<Integer>);
    property OnFiltreDegisti: TFiltreDegistiOlayi read FOnFiltreDegisti write FOnFiltreDegisti;
  end;

implementation

uses VeriModulu;

{$R *.dfm}

{ TCerceveGezgin }

procedure TCerceveGezgin.VerileriYukle;
var
  Dugum: TTreeNode;
begin
  // Kategorileri Yükle
  tvKategoriler.Items.BeginUpdate;
  try
    tvKategoriler.Items.Clear;
    Dugum := tvKategoriler.Items.Add(nil, 'Tüm Notlar');
    Dugum.Data := Pointer(-1); // Bütün notlar için kök düğüm

    ModulVeri.SorguKategoriler.First;
    while not ModulVeri.SorguKategoriler.Eof do
    begin
      Dugum := tvKategoriler.Items.Add(nil, ModulVeri.SorguKategoriler.FieldByName('KategoriAdi').AsString);
      Dugum.Data := Pointer(ModulVeri.SorguKategoriler.FieldByName('ID').AsInteger);
      ModulVeri.SorguKategoriler.Next;
    end;
  finally
    tvKategoriler.Items.EndUpdate;
    if tvKategoriler.Items.Count > 0 then
      tvKategoriler.Selected := tvKategoriler.Items[0];
  end;

  // Etiketleri Yükle
  clbEtiketler.Items.BeginUpdate;
  try
    clbEtiketler.Items.Clear;
    ModulVeri.SorguEtiketler.First;
    while not ModulVeri.SorguEtiketler.Eof do
    begin
      clbEtiketler.Items.AddObject(ModulVeri.SorguEtiketler.FieldByName('EtiketAdi').AsString, TObject(ModulVeri.SorguEtiketler.FieldByName('ID').AsInteger));
      ModulVeri.SorguEtiketler.Next;
    end;
  finally
    clbEtiketler.Items.EndUpdate;
  end;
end;

function TCerceveGezgin.GetSeciliKategoriID: Integer;
begin
  Result := -1; // Varsayılan: Tümü
  if Assigned(tvKategoriler.Selected) then
    Result := Integer(tvKategoriler.Selected.Data);
end;

procedure TCerceveGezgin.GetSeciliEtiketIDleri(EtiketIDleri: TList<Integer>);
var
  i: Integer;
begin
  EtiketIDleri.Clear;
  for i := 0 to clbEtiketler.Items.Count - 1 do
  begin
    if clbEtiketler.Checked[i] then
      EtiketIDleri.Add(Integer(clbEtiketler.Items.Objects[i]));
  end;
end;

procedure TCerceveGezgin.tvKategorilerChange(Sender: TObject; Node: TTreeNode);
begin
  if Assigned(FOnFiltreDegisti) then
    FOnFiltreDegisti(Self);
end;

procedure TCerceveGezgin.clbEtiketlerClickCheck(Sender: TObject);
begin
  if Assigned(FOnFiltreDegisti) then
    FOnFiltreDegisti(Self);
end;

end.
