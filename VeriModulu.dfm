object ModulVeri: TModulVeri
  OldCreateOrder = False
  OnCreate = DataModuleCreate
  Height = 271
  Width = 434
  object Baglanti: TFDConnection
    Params.Strings = (
      'Database=$(DOC)\ProfesyonelNotDefteri\notlar.db'
      'DriverID=SQLite')
    LoginPrompt = False
    Left = 48
    Top = 24
  end
  object SurucuLinki: TFDPhysSQLiteDriverLink
    Left = 184
    Top = 24
  end
  object SorguKategoriler: TFDQuery
    Connection = Baglanti
    SQL.Strings = (
      'SELECT * FROM Kategoriler ORDER BY KategoriAdi')
    Left = 48
    Top = 88
  end
  object SorguNotlar: TFDQuery
    Connection = Baglanti
    SQL.Strings = (
      'SELECT * FROM Notlar WHERE KategoriID = :KategoriID ORDER BY Baslik')
    Left = 144
    Top = 88
    ParamData = <
      item
        Name = 'KATEGORIID'
        DataType = ftInteger
        ParamType = ptInput
        Value = 0
      end>
  end
  object SorguEtiketler: TFDQuery
    Connection = Baglanti
    SQL.Strings = (
      'SELECT * FROM Etiketler ORDER BY EtiketAdi')
    Left = 240
    Top = 88
  end
  object KomutNotGuncelle: TFDCommand
    Connection = Baglanti
    CommandText.Strings = (
      'UPDATE Notlar SET'
      '  Baslik = :Baslik,'
      '  Icerik = :Icerik,'
      '  Icerik_Metin = :Icerik_Metin,'
      '  GuncellemeTarihi = :Tarih'
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
        Name = 'ICERIK_METIN'
        DataType = ftMemo
        ParamType = ptInput
      end
      item
        Name = 'TARIH'
        DataType = ftDateTime
        ParamType = ptInput
      end
      item
        Name = 'ID'
        DataType = ftInteger
        ParamType = ptInput
      end>
    Left = 48
    Top = 152
  end
  object SorguNotEtiketler: TFDQuery
    Connection = Baglanti
    SQL.Strings = (
      'SELECT EtiketID FROM Not_Etiketler WHERE NotID = :NotID')
    Left = 336
    Top = 88
    ParamData = <
      item
        Name = 'NOTID'
        DataType = ftInteger
        ParamType = ptInput
      end>
  end
end
