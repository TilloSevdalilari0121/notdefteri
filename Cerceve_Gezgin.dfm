object CerceveGezgin: TCerceveGezgin
  Width = 250
  Height = 600
  TabOrder = 0
  object grpKategoriler: TGroupBox
    Left = 0
    Top = 0
    Width = 250
    Height = 300
    Align = alTop
    Caption = 'Kategoriler'
    TabOrder = 0
    object tvKategoriler: TTreeView
      Left = 2
      Top = 18
      Width = 246
      Height = 280
      Align = alClient
      Indent = 19
      TabOrder = 0
    end
  end
  object Splitter: TSplitter
    Left = 0
    Top = 300
    Width = 250
    Height = 5
    Cursor = crVSplit
    Align = alTop
    ResizeStyle = rsLine
  end
  object grpEtiketler: TGroupBox
    Left = 0
    Top = 305
    Width = 250
    Height = 295
    Align = alClient
    Caption = 'Etiketler'
    TabOrder = 1
    object clbEtiketler: TCheckListBox
      Left = 2
      Top = 18
      Width = 246
      Height = 275
      Align = alClient
      ItemHeight = 15
      TabOrder = 0
    end
  end
end
