object MainForm: TMainForm
  Left = 0
  Top = 0
  Caption = 'Delphi Note App'
  ClientHeight = 600
  ClientWidth = 800
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -12
  Font.Name = 'Segoe UI'
  Font.Style = []
  Position = poScreenCenter
  OnCreate = FormCreate
  OnShow = FormShow
  TextHeight = 15
  object ToolBar: TToolBar
    Left = 0
    Top = 0
    Width = 800
    Height = 41
    AutoSize = True
    Caption = 'ToolBar'
    EdgeBorders = [ebBottom]
    Images = ImageList
    TabOrder = 0
    object btnNewCategory: TToolButton
      Left = 0
      Top = 2
      Action = actAddCategory
    end
    object btnNewNote: TToolButton
      Left = 23
      Top = 2
      Action = actAddNote
    end
    object btnDelete: TToolButton
      Left = 46
      Top = 2
      Action = actDelete
    end
    object ToolButton4: TToolButton
      Left = 69
      Top = 2
      Width = 8
      Caption = 'ToolButton4'
      ImageIndex = 3
      Style = tbsSeparator
    end
    object btnSave: TToolButton
      Left = 77
      Top = 2
      Action = actSaveNote
    end
  end
  object StatusBar: TStatusBar
    Left = 0
    Top = 581
    Width = 800
    Height = 19
    Panels = <>
  end
  object pnlLeft: TPanel
    Left = 0
    Top = 41
    Width = 200
    Height = 540
    Align = alLeft
    BevelOuter = bvNone
    Caption = 'pnlLeft'
    TabOrder = 2
    object tvCategories: TTreeView
      Left = 0
      Top = 0
      Width = 200
      Height = 540
      Align = alClient
      Indent = 19
      TabOrder = 0
      OnChange = tvCategoriesChange
    end
  end
  object Splitter1: TSplitter
    Left = 200
    Top = 41
    Width = 5
    Height = 540
    Align = alLeft
    ResizeStyle = rsLine
  end
  object pnlRight: TPanel
    Left = 205
    Top = 41
    Width = 595
    Height = 540
    Align = alClient
    BevelOuter = bvNone
    Caption = 'pnlRight'
    TabOrder = 4
    object pnlNoteListHeader: TPanel
      Left = 0
      Top = 0
      Width = 595
      Height = 41
      Align = alTop
      BevelOuter = bvNone
      Caption = 'pnlNoteListHeader'
      TabOrder = 0
      object SearchBox: TSearchBox
        Left = 8
        Top = 8
        Width = 579
        Height = 25
        TabOrder = 0
        OnInvokeSearch = SearchBoxInvokeSearch
      end
    end
    object lvNotes: TListView
      Left = 0
      Top = 41
      Width = 595
      Height = 150
      Align = alTop
      Columns = <
        item
          Caption = 'Title'
          Width = 300
        end
        item
          Caption = 'Last Modified'
          Width = 150
        end>
      GridLines = True
      RowSelect = True
      TabOrder = 1
      ViewStyle = vsReport
      OnItemClick = lvNotesItemClick
    end
    object Splitter2: TSplitter
      Left = 0
      Top = 191
      Width = 595
      Height = 5
      Cursor = crVSplit
      Align = alTop
      ResizeStyle = rsLine
    end
    object reNoteContent: TRichEdit
      Left = 0
      Top = 196
      Width = 595
      Height = 344
      Align = alClient
      Font.Charset = ANSI_CHARSET
      Font.Color = clWindowText
      Font.Height = -13
      Font.Name = 'Arial'
      Font.Style = []
      Lines.Strings = (
        'reNoteContent')
      ParentFont = False
      ScrollBars = ssVertical
      TabOrder = 3
    end
  end
  object ActionList: TActionList
    Images = ImageList
    Left = 280
    Top = 112
    object actAddCategory: TAction
      Caption = 'New Category'
      ImageIndex = 0
      OnExecute = actAddCategoryExecute
    end
    object actAddNote: TAction
      Caption = 'New Note'
      ImageIndex = 1
      OnExecute = actAddNoteExecute
    end
    object actDelete: TAction
      Caption = 'Delete'
      ImageIndex = 2
      OnExecute = actDeleteExecute
    end
    object actSaveNote: TAction
      Caption = 'Save'
      ImageIndex = 3
      OnExecute = actSaveNoteExecute
    end
  end
  object ImageList: TImageList
    Left = 368
    Top = 112
  end
end
