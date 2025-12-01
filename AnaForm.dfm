object FrmAna: TFrmAna
  Left = 0
  Top = 0
  Caption = 'Profesyonel Not Defteri'
  ClientHeight = 768
  ClientWidth = 1280
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -12
  Font.Name = 'Segoe UI'
  Font.Style = []
  Position = poScreenCenter
  OnCreate = FormCreate
  TextHeight = 15
  object Splitter1: TSplitter
    Left = 250
    Top = 25
    Width = 8
    Height = 743
    Align = alLeft
  end
  object Splitter2: TSplitter
    Left = 558
    Top = 25
    Width = 8
    Height = 743
    Align = alLeft
  end
  object AnaMenu: TMainMenu
    Left = 40
    Top = 88
    object Dosya1: TMenuItem
      Caption = '&Dosya'
      object YeniNot1: TMenuItem
        Action = EylemYeniNot
      end
      object N1: TMenuItem
        Caption = '-'
      end
      object Cikis1: TMenuItem
        Caption = '&Çıkış'
        OnClick = Cikis1Click
      end
    end
    object Gorunum1: TMenuItem
      Caption = '&Görünüm'
      object Temalar1: TMenuItem
        Caption = 'Temalar'
        object AcikTema1: TMenuItem
          Caption = 'Açık'
          GroupIndex = 1
          RadioItem = True
          OnClick = TemaMenuItemClick
        end
        object KoyuTema1: TMenuItem
          Caption = 'Koyu'
          GroupIndex = 1
          RadioItem = True
          OnClick = TemaMenuItemClick
        end
      end
    end
  end
  object EylemListesi: TActionList
    Images = ResimListesi
    Left = 112
    Top = 88
    object EylemYeniNot: TAction
      Caption = 'Yeni Not'
      ImageIndex = 1
      OnExecute = EylemYeniNotExecute
    end
    object EylemNotuKaydet: TAction
      Caption = 'Kaydet'
      ImageIndex = 3
      Enabled = False
      OnExecute = EylemNotuKaydetExecute
    end
    object EylemNotuSil: TAction
      Caption = 'Sil'
      ImageIndex = 2
      Enabled = False
      OnExecute = EylemNotuSilExecute
    end
  end
  object ResimListesi: TImageList
    Left = 184
    Top = 88
  end
  object StilYoneticisi: TStyleManager
    Left = 256
    Top = 88
  end
  object CerceveGezgin1: TCerceveGezgin
    Left = 0
    Top = 25
    Width = 250
    Height = 743
    Align = alLeft
    TabOrder = 0
  end
  object CerceveNotListesi1: TCerceveNotListesi
    Left = 258
    Top = 25
    Width = 300
    Height = 743
    Align = alLeft
    TabOrder = 1
  end
  object CerceveDuzenleyici1: TCerceveDuzenleyici
    Left = 566
    Top = 25
    Width = 714
    Height = 743
    Align = alClient
    TabOrder = 2
  end
  object AracCubugu: TToolBar
    Left = 0
    Top = 0
    Width = 1280
    Height = 25
    Caption = 'AracCubugu'
    Images = ResimListesi
    TabOrder = 3
    object btnYeniNot: TToolButton
      Left = 0
      Top = 0
      Action = EylemYeniNot
    end
    object btnNotuKaydet: TToolButton
      Left = 23
      Top = 0
      Action = EylemNotuKaydet
    end
    object btnNotuSil: TToolButton
      Left = 46
      Top = 0
      Action = EylemNotuSil
    end
  end
end
