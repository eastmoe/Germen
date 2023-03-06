Attribute VB_Name = "NewMacros"
Sub ∂Œ¬‰”Îªª––«–ªª()
Attribute ∂Œ¬‰”Îªª––«–ªª.VB_ProcData.VB_Invoke_Func = "Normal.NewMacros.∂Œ¬‰”Îªª––«–ªª"
'
' ∂Œ¬‰”Îªª––«–ªª ∫Í
'
'
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "^p"
        .Replacement.Text = ""
        .Forward = True
        .Wrap = wdFindAsk
        .Format = False
        .MatchCase = False
        .MatchWholeWord = False
        .MatchByte = True
        .MatchWildcards = False
        .MatchSoundsLike = False
        .MatchAllWordForms = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    With Selection.Find
        .Text = "  "
        .Replacement.Text = "^p  "
        .Forward = True
        .Wrap = wdFindAsk
        .Format = False
        .MatchCase = False
        .MatchWholeWord = False
        .MatchByte = True
        .MatchWildcards = False
        .MatchSoundsLike = False
        .MatchAllWordForms = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
End Sub
