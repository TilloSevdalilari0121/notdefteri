object DM: TDM
  OldCreateOrder = False
  OnCreate = DataModuleCreate
  Height = 231
  Width = 373
  object FDConnection: TFDConnection
    Params.Strings = (
      'Database=$(DOC)\NoteApp\notes.db'
      'DriverID=SQLite')
    LoginPrompt = False
    Left = 48
    Top = 24
  end
  object FDPhysSQLiteDriverLink: TFDPhysSQLiteDriverLink
    Left = 184
    Top = 24
  end
  object QryKategoriler: TFDQuery
    Connection = FDConnection
    SQL.Strings = (
      'SELECT * FROM Kategoriler ORDER BY KategoriAdi')
    Left = 48
    Top = 88
  end
  object QryNotlar: TFDQuery
    Connection = FDConnection
    SQL.Strings = (
      'SELECT * FROM Notlar WHERE KategoriID = :KategoriID ORDER BY Baslik')
    Left = 48
    Top = 152
    ParamData = <
      item
        Name = 'KATEGORIID'
        DataType = ftInteger
        ParamType = ptInput
        Value = 0
      end>
  end
  object CmdUpdateNote: TFDCommand
    Connection = FDConnection
    CommandText.Strings = (
      'UPDATE Notlar SET'
      '  Baslik = :Baslik,'
      '  Icerik = :Icerik,'
      '  Icerik_PlainText = :Icerik_PlainText,'
      '  GuncellemeTarihi = :Time'
      'WHERE'
      '  ID = :ID')
    Params = <
      item
        Name = 'BASLIK'
        DataType = ftString
        ParamType = ptInput
        Size = 100
      end
      item
        Name = 'ICERIK'
        DataType = ftBlob
        ParamType = ptInput
      end
      item
        Name = 'ICERIK_PLAINTEXT'
        DataType = ftMemo
        ParamType = ptInput
      end
      item
        Name = 'TIME'
        DataType = ftDateTime
        ParamType = ptInput
      end
      item
        Name = 'ID'
        DataType = ftInteger
        ParamType = ptInput
      end>
    Left = 184
    Top = 88
  end
end
