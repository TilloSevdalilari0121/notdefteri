object CerceveNotListesi: TCerceveNotListesi
  Width = 300
  Height = 600
  TabOrder = 0
  object AramaKutusu: TSearchBox
    Left = 0
    Top = 0
    Width = 300
    Height = 25
    Align = alTop
    TabOrder = 0
  end
  object lvNotlar: TListView
    Left = 0
    Top = 25
    Width = 300
    Height = 575
    Align = alClient
    Columns = <
      item
        Caption = 'Başlık'
        Width = 180
      end
      item
        Caption = 'Son Değiştirme'
        Width = 120
      end>
    RowSelect = True
    TabOrder = 1
    ViewStyle = vsReport
  end
end
