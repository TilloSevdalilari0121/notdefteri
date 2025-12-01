object CerceveDuzenleyici: TCerceveDuzenleyici
  Width = 700
  Height = 600
  TabOrder = 0
  object SekmeKontrolu: TPageControl
    Left = 0
    Top = 0
    Width = 700
    Height = 600
    ActivePage = tsKarsilama
    Align = alClient
    TabOrder = 0
    object tsKarsilama: TTabSheet
      Caption = 'Hoş Geldiniz'
      object Label1: TLabel
        Left = 32
        Top = 24
        Width = 478
        Height = 33
        Caption = 'Profesyonel Not Defterine Hoş Geldiniz!'
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clWindowText
        Font.Height = -29
        Font.Name = 'Segoe UI'
        Font.Style = [fsBold]
        ParentFont = False
      end
      object Label2: TLabel
        Left = 32
        Top = 72
        Width = 469
        Height = 15
        Caption = 'Düzenlemeye başlamak için listeden bir not seçin veya yeni bir not oluşturun.'
      end
    end
  end
end
