unit UDataModule;

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
  FireDAC.Comp.DataSet;

uses
  System.IOUtils;

type
  TDM = class(TDataModule)
    FDConnection: TFDConnection;
    FDPhysSQLiteDriverLink: TFDPhysSQLiteDriverLink;
    QryKategoriler: TFDQuery;
    QryNotlar: TFDQuery;
    procedure DataModuleCreate(Sender: TObject);
  private
    procedure SetupDatabase;
  public
    { Public declarations }
  end;

var
  DM: TDM;

implementation

{%CLASSGROUP 'Vcl.Controls.TControl'}

{$R *.dfm}

procedure TDM.DataModuleCreate(Sender: TObject);
begin
  FDConnection.Params.Values['Database'] := TPath.Combine(TPath.GetDocumentsPath, 'NoteApp', 'notes.db');
  SetupDatabase;
  FDConnection.Connected := True;
  QryKategoriler.Open;
end;

procedure TDM.SetupDatabase;
var
  DBPath: string;
begin
  DBPath := FDConnection.Params.Values['Database'];
  if not TFile.Exists(DBPath) then
  begin
    TDirectory.CreateDirectory(TPath.GetDirectoryName(DBPath));
    // NOTE: Connection is established before this method is called.
    // Create Tables
    FDConnection.ExecSQL('CREATE TABLE Kategoriler (' +
                         'ID INTEGER PRIMARY KEY AUTOINCREMENT, ' +
                         'KategoriAdi VARCHAR(50) NOT NULL UNIQUE)');
    FDConnection.ExecSQL('CREATE TABLE Notlar (' +
                         'ID INTEGER PRIMARY KEY AUTOINCREMENT, ' +
                         'KategoriID INTEGER, ' +
                         'Baslik VARCHAR(100), ' +
                         'Icerik BLOB, ' + // Rich text will be stored as a blob
                         'Icerik_PlainText TEXT, ' + // For full-text search
                         'OlusturmaTarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP, ' +
                         'GuncellemeTarihi TIMESTAMP, ' +
                         'FOREIGN KEY(KategoriID) REFERENCES Kategoriler(ID))');
    // Add a default category
    FDConnection.ExecSQL('INSERT INTO Kategoriler (KategoriAdi) VALUES ("Genel")');
  end;
end;

end.
