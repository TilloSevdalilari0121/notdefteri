unit UMainForm;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.ComCtrls, Vcl.StdCtrls, Vcl.ExtCtrls,
  Vcl.ToolWin, Vcl.ActnList, Data.DB, System.IOUtils, Vcl.Samples.Spin, Vcl.Imaging.pngimage;

type
  TMainForm = class(TForm)
    ToolBar: TToolBar;
    StatusBar: TStatusBar;
    pnlLeft: TPanel;
    tvCategories: TTreeView;
    Splitter1: TSplitter;
    pnlRight: TPanel;
    pnlNoteListHeader: TPanel;
    SearchBox: TSearchBox;
    lvNotes: TListView;
    Splitter2: TSplitter;
    reNoteContent: TRichEdit;
    ActionList: TActionList;
    actAddCategory: TAction;
    actAddNote: TAction;
    actDelete: TAction;
    actSaveNote: TAction;
    btnNewCategory: TToolButton;
    btnNewNote: TToolButton;
    btnDelete: TToolButton;
    ToolButton4: TToolButton;
    btnSave: TToolButton;
    ImageList: TImageList;
    procedure FormCreate(Sender: TObject);
    procedure FormShow(Sender: TObject);
    procedure actAddCategoryExecute(Sender: TObject);
    procedure tvCategoriesChange(Sender: TObject; Node: TTreeNode);
    procedure actAddNoteExecute(Sender: TObject);
    procedure lvNotesItemClick(Sender: TObject; const AItem: TListItem);
    procedure actSaveNoteExecute(Sender: TObject);
    procedure actDeleteExecute(Sender: TObject);
    procedure SearchBoxInvokeSearch(Sender: TObject);
  private
    FCurrentNoteID: Integer;
    procedure LoadCategories;
    procedure LoadNotes;
    procedure ClearNoteView;
    function GetSelectedCategoryID: Integer;
    function GetSelectedNoteID: Integer;
  public
    { Public declarations }
  end;

var
  MainForm: TMainForm;

implementation

uses UDataModule;

{$R *.dfm}

{ TMainForm }

procedure TMainForm.FormCreate(Sender: TObject);
begin
  FCurrentNoteID := -1;
end;

procedure TMainForm.FormShow(Sender: TObject);
begin
  LoadCategories;
  if tvCategories.Items.Count > 0 then
    tvCategories.Selected := tvCategories.Items[0];
end;

procedure TMainForm.LoadCategories;
var
  Node: TTreeNode;
begin
  tvCategories.Items.BeginUpdate;
  try
    tvCategories.Items.Clear;
    DM.QryKategoriler.First;
    while not DM.QryKategoriler.Eof do
    begin
      Node := tvCategories.Items.Add(nil, DM.QryKategoriler.FieldByName('KategoriAdi').AsString);
      Node.Data := Pointer(DM.QryKategoriler.FieldByName('ID').AsInteger);
      DM.QryKategoriler.Next;
    end;
  finally
    tvCategories.Items.EndUpdate;
  end;
end;

function TMainForm.GetSelectedCategoryID: Integer;
begin
  Result := -1;
  if Assigned(tvCategories.Selected) then
    Result := Integer(tvCategories.Selected.Data);
end;

function TMainForm.GetSelectedNoteID: Integer;
begin
  Result := -1;
  if Assigned(lvNotes.Selected) then
    Result := lvNotes.Selected.Data;
end;

procedure TMainForm.tvCategoriesChange(Sender: TObject; Node: TTreeNode);
begin
  LoadNotes;
  ClearNoteView;
end;

procedure TMainForm.LoadNotes;
var
  CategoryID: Integer;
  ListItem: TListItem;
begin
  CategoryID := GetSelectedCategoryID;
  lvNotes.Items.BeginUpdate;
  try
    lvNotes.Items.Clear;
    ClearNoteView;
    DM.QryNotlar.Close;
    DM.QryNotlar.ParamByName('KategoriID').AsInteger := CategoryID;
    DM.QryNotlar.Open;

    if not SearchBox.Text.IsEmpty then
    begin
       DM.QryNotlar.Filter := 'Baslik LIKE ' + QuotedStr('%' + SearchBox.Text + '%') +
                             ' OR Icerik_PlainText LIKE ' + QuotedStr('%' + SearchBox.Text + '%');
       DM.QryNotlar.Filtered := True;
    end
    else
    begin
       DM.QryNotlar.Filtered := False;
    end;

    DM.QryNotlar.First;
    while not DM.QryNotlar.Eof do
    begin
      ListItem := lvNotes.Items.Add;
      ListItem.Caption := DM.QryNotlar.FieldByName('Baslik').AsString;
      ListItem.SubItems.Add(FormatDateTime('yyyy-mm-dd hh:nn', DM.QryNotlar.FieldByName('GuncellemeTarihi').AsDateTime));
      ListItem.Data := Pointer(DM.QryNotlar.FieldByName('ID').AsInteger);
      DM.QryNotlar.Next;
    end;
  finally
    lvNotes.Items.EndUpdate;
  end;
end;

procedure TMainForm.ClearNoteView;
begin
  reNoteContent.Lines.Clear;
  FCurrentNoteID := -1;
end;

procedure TMainForm.lvNotesItemClick(Sender: TObject; const AItem: TListItem);
var
  Stream: TStream;
begin
  FCurrentNoteID := GetSelectedNoteID;
  if FCurrentNoteID > 0 then
  begin
    if DM.QryNotlar.Locate('ID', FCurrentNoteID, []) then
    begin
      Stream := DM.QryNotlar.CreateBlobStream(DM.QryNotlar.FieldByName('Icerik'), bmRead);
      try
        reNoteContent.Lines.LoadFromStream(Stream);
      finally
        Stream.Free;
      end;
    end;
  end;
end;

procedure TMainForm.actAddCategoryExecute(Sender: TObject);
var
  CategoryName: string;
begin
  if InputQuery('New Category', 'Category Name:', CategoryName) and (Trim(CategoryName) <> '') then
  begin
    try
      DM.FDConnection.ExecSQL('INSERT INTO Kategoriler (KategoriAdi) VALUES (:Name)', [CategoryName]);
      LoadCategories;
    except
      on E: Exception do
        MessageDlg('Error creating category: ' + E.Message, mtError, [mbOK], 0);
    end;
  end;
end;

procedure TMainForm.actAddNoteExecute(Sender: TObject);
var
  CategoryID: Integer;
  NewNoteID: Integer;
begin
  CategoryID := GetSelectedCategoryID;
  if CategoryID > 0 then
  begin
    DM.FDConnection.ExecSQL('INSERT INTO Notlar (KategoriID, Baslik, GuncellemeTarihi) VALUES (:CatID, :Title, :Time)',
                           [CategoryID, 'New Note', Now]);
    NewNoteID := DM.FDConnection.GetLastAutoGenValue('Notlar');
    LoadNotes;
    // Select the new note in the list view
    var i := 0;
    while i < lvNotes.Items.Count do
    begin
      if Integer(lvNotes.Items[i].Data) = NewNoteID then
      begin
        lvNotes.Items[i].Selected := True;
        lvNotes.SetFocus;
        break;
      end;
      Inc(i);
    end;
  end
  else
  begin
    MessageDlg('Please select a category first.', mtInformation, [mbOK], 0);
  end;
end;

procedure TMainForm.actDeleteExecute(Sender: TObject);
var
  CategoryID, NoteID: Integer;
begin
  NoteID := GetSelectedNoteID;
  CategoryID := GetSelectedCategoryID;

  if NoteID > 0 then
  begin
    if MessageDlg('Are you sure you want to delete this note?', mtConfirmation, [mbYes, mbNo], 0) = mrYes then
    begin
      DM.FDConnection.ExecSQL('DELETE FROM Notlar WHERE ID = :ID', [NoteID]);
      LoadNotes;
    end;
  end
  else if CategoryID > 0 then
  begin
     if MessageDlg('Are you sure you want to delete this category and all its notes?', mtConfirmation, [mbYes, mbNo], 0) = mrYes then
     begin
       DM.FDConnection.ExecSQL('DELETE FROM Notlar WHERE KategoriID = :ID', [CategoryID]);
       DM.FDConnection.ExecSQL('DELETE FROM Kategoriler WHERE ID = :ID', [CategoryID]);
       LoadCategories;
       if tvCategories.Items.Count > 0 then
         tvCategories.Selected := tvCategories.Items[0];
     end;
  end;
end;


procedure TMainForm.actSaveNoteExecute(Sender: TObject);
var
  Stream: TStream;
  NoteTitle: string;
begin
  if FCurrentNoteID > 0 then
  begin
    // Extract first line as title
    if reNoteContent.Lines.Count > 0 then
      NoteTitle := reNoteContent.Lines[0]
    else
      NoteTitle := 'Untitled Note';

    if Length(NoteTitle) > 100 then
      NoteTitle := Copy(NoteTitle, 1, 100);

    Stream := TMemoryStream.Create;
    try
      reNoteContent.Lines.SaveToStream(Stream);
      Stream.Position := 0;

      DM.CmdUpdateNote.ParamByName('Baslik').AsString := NoteTitle;
      DM.CmdUpdateNote.ParamByName('Icerik').LoadFromStream(Stream, ftBlob);
      DM.CmdUpdateNote.ParamByName('Icerik_PlainText').AsString := reNoteContent.Lines.Text;
      DM.CmdUpdateNote.ParamByName('Time').AsDateTime := Now;
      DM.CmdUpdateNote.ParamByName('ID').AsInteger := FCurrentNoteID;
      DM.CmdUpdateNote.Execute;
    finally
      Stream.Free;
    end;
    LoadNotes; // Refresh note list to show updated title/time
  end;
end;

procedure TMainForm.SearchBoxInvokeSearch(Sender: TObject);
begin
  LoadNotes;
end;

end.
