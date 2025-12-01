unit VeriModulu;

interface

uses
  System.SysUtils,
  System.Classes,
  FireDAC.Stan.Intf,
  FireDAC.Stan.Option,
  FireDAC.Stan.Error,
  FireDAC.UI.Intf,
  FireDAC.Phys.Intf,
  FireDAC.Stan.Def,
  FireDAC.Stan.Pool,
  FireDAC.Stan.Async,
  FireDAC.Phys,
  FireDAC.Phys.SQLite,
  FireDAC.Phys.SQLiteDef,
  FireDAC.VCLUI.Wait,
  Data.DB,
  FireDAC.Comp.Client,
  FireDAC.Comp.DataSet,
  System.IOUtils;

type
  TModulVeri = class(TDataModule)
    Baglanti: TFDConnection;
    SurucuLinki: TFDPhysSQLiteDriverLink;
    SorguKategoriler: TFDQuery;
    SorguNotlar: TFDQuery;
    SorguEtiketler: TFDQuery;
    KomutNotGuncelle: TFDCommand;
    SorguNotEtiketler: TFDQuery;
    procedure DataModuleCreate(Sender: TObject);
  private
    procedure VeritabaniniKur;
  public
    { Genel bildirimler }
  end;

var
  ModulVeri: TModulVeri;

implementation

{%CLASSGROUP 'Vcl.Controls.TControl'}

{$R *.dfm}

procedure TModulVeri.DataModuleCreate(Sender: TObject);
begin
  Baglanti.Params.Values['Database'] := TPath.Combine(TPath.GetDocumentsPath, 'ProfesyonelNotDefteri', 'notlar.db');
  Baglanti.Connected := True;
  VeritabaniniKur;
  SorguKategoriler.Open;
  SorguEtiketler.Open;
end;

procedure TModulVeri.VeritabaniniKur;
var
  VeritabaniYolu: string;
begin
  VeritabaniYolu := Baglanti.Params.Values['Database'];
  if not TFile.Exists(VeritabaniYolu) then
  begin
    TDirectory.CreateDirectory(TPath.GetDirectoryName(VeritabaniYolu));

    // Tabloları oluştur
    Baglanti.ExecSQL('CREATE TABLE Kategoriler (' +
                         'ID INTEGER PRIMARY KEY AUTOINCREMENT, ' +
                         'KategoriAdi VARCHAR(50) NOT NULL UNIQUE)');

    Baglanti.ExecSQL('CREATE TABLE Etiketler (' +
                         'ID INTEGER PRIMARY KEY AUTOINCREMENT, ' +
                         'EtiketAdi VARCHAR(50) NOT NULL UNIQUE)');

    Baglanti.ExecSQL('CREATE TABLE Notlar (' +
                         'ID INTEGER PRIMARY KEY AUTOINCREMENT, ' +
                         'KategoriID INTEGER, ' +
                         'Baslik VARCHAR(100), ' +
                         'Icerik BLOB, ' +
                         'Icerik_Metin TEXT, ' + // Aranabilir düz metin için
                         'OlusturmaTarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP, ' +
                         'GuncellemeTarihi TIMESTAMP, ' +
                         'FOREIGN KEY(KategoriID) REFERENCES Kategoriler(ID))');

    Baglanti.ExecSQL('CREATE TABLE Not_Etiketler (' +
                         'NotID INTEGER, ' +
                         'EtiketID INTEGER, ' +
                         'PRIMARY KEY (NotID, EtiketID), ' +
                         'FOREIGN KEY(NotID) REFERENCES Notlar(ID) ON DELETE CASCADE, ' +
                         'FOREIGN KEY(EtiketID) REFERENCES Etiketler(ID) ON DELETE CASCADE)');

    // Varsayılan verileri ekle
    Baglanti.ExecSQL('INSERT INTO Kategoriler (KategoriAdi) VALUES ("Genel")');
    Baglanti.ExecSQL('INSERT INTO Kategoriler (KategoriAdi) VALUES ("İş")');
    Baglanti.ExecSQL('INSERT INTO Etiketler (EtiketAdi) VALUES ("Önemli")');
    Baglanti.ExecSQL('INSERT INTO Etiketler (EtiketAdi) VALUES ("Proje X")');
  end;
end;

end.
