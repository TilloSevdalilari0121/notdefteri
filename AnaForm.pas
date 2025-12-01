unit AnaForm;

interface

uses
  Winapi.Windows,
  Winapi.Messages,
  System.SysUtils,
  System.Variants,
  System.Classes,
  Vcl.Graphics,
  Vcl.Controls,
  Vcl.Forms,
  Vcl.Dialogs,
  Vcl.Themes,
  Vcl.Menus,
  Cerceve_Gezgin, Cerceve_NotListesi, Cerceve_Duzenleyici,
  System.Generics.Collections;

type
  TFrmAna = class(TForm)
    Splitter1: TSplitter;
    Splitter2: TSplitter;
    AnaMenu: TMainMenu;
    Dosya1: TMenuItem;
    YeniNot1: TMenuItem;
    N1: TMenuItem;
    Cikis1: TMenuItem;
    Gorunum1: TMenuItem;
    Temalar1: TMenuItem;
    AcikTema1: TMenuItem;
    KoyuTema1: TMenuItem;
    EylemListesi: TActionList;
    EylemYeniNot: TAction;
    EylemNotuKaydet: TAction;
    EylemNotuSil: TAction;
    ResimListesi: TImageList;
    StilYoneticisi: TStyleManager;
    CerceveGezgin1: TCerceveGezgin;
    CerceveNotListesi1: TCerceveNotListesi;
    CerceveDuzenleyici1: TCerceveDuzenleyici;
    AracCubugu: TToolBar;
    btnYeniNot: TToolButton;
    btnNotuKaydet: TToolButton;
    btnNotuSil: TToolButton;
    procedure FormCreate(Sender: TObject);
    procedure FormShow(Sender: TObject);
    procedure FormCloseQuery(Sender: TObject; var CanClose: Boolean);
    procedure Cikis1Click(Sender: TObject);
    procedure TemaMenuItemClick(Sender: TObject);
    procedure EylemYeniNotExecute(Sender: TObject);
    procedure EylemNotuKaydetExecute(Sender: TObject);
    procedure EylemNotuSilExecute(Sender: TObject);
  private
    // Frame'ler arası iletişim için olay yöneticileri
    procedure FiltreDegisti(Gonderen: TObject);
    procedure NotAcmaIstegi(Gonderen: TObject; NotID: Integer);
    procedure DuzenleyiciDurumuDegisti(Gonderen: TObject; Kaydedebilir, Silebilir: Boolean);
  public
    { Genel bildirimler }
  end;

var
  FrmAna: TFrmAna;

implementation

uses VeriModulu;

{$R *.dfm}

procedure TFrmAna.FormCreate(Sender: TObject);
begin
  // Varsayılan temayı ayarla
  AcikTema1.IsChecked := True;
  TStyleManager.TrySetStyle('Windows10');

  // Frame'ler arasındaki olayları birbirine bağla
  CerceveGezgin1.OnFiltreDegisti := FiltreDegisti;
  CerceveNotListesi1.OnNotAcmaIstegi := NotAcmaIstegi;
  CerceveNotListesi1.OnFiltreDegisti := FiltreDegisti; // Arama kutusu değişiklikleri için
  CerceveDuzenleyici1.OnDurumDegisti := DuzenleyiciDurumuDegisti;
end;

procedure TFrmAna.FormShow(Sender: TObject);
begin
  // Başlangıçta verileri yükle
  CerceveGezgin1.VerileriYukle;
end;

procedure TFrmAna.FormCloseQuery(Sender: TObject; var CanClose: Boolean);
var
  i: integer;
  Sekme: TTabSheet;
begin
  CanClose := True;
  for i := CerceveDuzenleyici1.SekmeKontrolu.PageCount - 1 downto 0 do
  begin
    Sekme := CerceveDuzenleyici1.SekmeKontrolu.Pages[i];
    if Sekme <> CerceveDuzenleyici1.tsKarsilama then
    begin
       if not CerceveDuzenleyici1.KaydedilmemisDegisiklikleriKontrolEt(Sekme) then
       begin
         CanClose := False;
         Exit;
       end;
    end;
  end;
end;

procedure TFrmAna.Cikis1Click(Sender: TObject);
begin
  Close;
end;

procedure TFrmAna.TemaMenuItemClick(Sender: TObject);
var
  MenuItem: TMenuItem;
begin
  MenuItem := Sender as TMenuItem;
  if MenuItem.Caption = 'Koyu' then
    TStyleManager.TrySetStyle('Windows10 Dark')
  else
    TStyleManager.TrySetStyle('Windows10');
end;

// Orkestrasyon Metodları (Olay Yöneticileri)

procedure TFrmAna.FiltreDegisti(Gonderen: TObject);
var
  KategoriID: Integer;
  EtiketIDleri: TList<Integer>;
begin
  EtiketIDleri := TList<Integer>.Create;
  try
    KategoriID := CerceveGezgin1.GetSeciliKategoriID;
    CerceveGezgin1.GetSeciliEtiketIDleri(EtiketIDleri);
    CerceveNotListesi1.NotlariYukle(KategoriID, EtiketIDleri);
  finally
    EtiketIDleri.Free;
  end;
end;

procedure TFrmAna.NotAcmaIstegi(Gonderen: TObject; NotID: Integer);
begin
  CerceveDuzenleyici1.NotuSekmedeAc(NotID);
end;

procedure TFrmAna.DuzenleyiciDurumuDegisti(Gonderen: TObject; Kaydedebilir, Silebilir: Boolean);
begin
  EylemNotuKaydet.Enabled := Kaydedebilir;
  EylemNotuSil.Enabled := Silebilir;
end;

// Eylemler

procedure TFrmAna.EylemYeniNotExecute(Sender: TObject);
var
  KategoriID, YeniNotID: Integer;
begin
  KategoriID := CerceveGezgin1.GetSeciliKategoriID;
  if KategoriID = -1 then
  begin
    if ModulVeri.SorguKategoriler.RecordCount > 0 then
      KategoriID := ModulVeri.SorguKategoriler.Fields[0].AsInteger
    else
    begin
      MessageDlg('Lütfen önce bir kategori oluşturun.', mtInformation, [mbOK], 0);
      Exit;
    end;
  end;

  ModulVeri.Baglanti.ExecSQL('INSERT INTO Notlar (KategoriID, Baslik, GuncellemeTarihi) VALUES (:CatID, :Title, :Time)',
                         [KategoriID, 'Yeni Not', Now]);
  YeniNotID := ModulVeri.Baglanti.GetLastAutoGenValue('Notlar');

  FiltreDegisti(Self); // Not listesini yenile
  CerceveDuzenleyici1.NotuSekmedeAc(YeniNotID);
end;

procedure TFrmAna.EylemNotuKaydetExecute(Sender: TObject);
begin
  CerceveDuzenleyici1.MevcutNotuKaydet;
  FiltreDegisti(Self); // Yeni başlığı/tarihi göstermek için listeyi yenile
end;

procedure TFrmAna.EylemNotuSilExecute(Sender: TObject);
begin
  CerceveDuzenleyici1.MevcutNotuSil;
  FiltreDegisti(Self); // Not listesini yenile
end;

end.
