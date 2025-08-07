Option Explicit

Sub WorksheetToJson()
    Dim ws As Worksheet
    Dim templateJson As String
    Dim i As Long

    Set ws = ActiveSheet

    ' Build the header with id and description
    templateJson = "{""id"": """ & ws.Name & """," & vbCrLf & _
                   "  ""description"": """ & EscapeJson(ws.Range("A1").Value) & """," & vbCrLf & _
                   "  ""fields"": [" & vbCrLf

    i = 2
    Do While ws.Cells(i, 1).Value <> ""
        Dim labelText As String
        Dim typeText As String

        labelText = ws.Cells(i, 1).Value
        typeText  = LCase(Trim(ws.Cells(i, 2).Value))

        ' Start new field entry
        templateJson = templateJson & "    "

        If typeText = "info" Then
            ' Display‐only info block
            templateJson = templateJson & "{""type"": ""info"", ""text"": """ & EscapeJson(labelText) & """}"

        ElseIf InStr(ws.Cells(i, 2).Value, ";") > 0 Then
            ' Dropdown: semicolon-separated options in the Type cell
            Dim parts As Variant, j As Long
            parts = Split(ws.Cells(i, 2).Value, ";")
            templateJson = templateJson & "{""label"": """ & EscapeJson(labelText) & """, ""type"": ""dropdown"", ""options"": ["
            For j = LBound(parts) To UBound(parts)
                templateJson = templateJson & """" & EscapeJson(Trim(parts(j))) & """"
                If j < UBound(parts) Then templateJson = templateJson & ", "
            Next j
            templateJson = templateJson & "]}"

        Else
            ' Regular input types: text, number, textarea, etc.
            templateJson = templateJson & "{""label"": """ & EscapeJson(labelText) & """, ""type"": """ & typeText & """}"
        End If

        ' Add comma if more rows follow
        i = i + 1
        If ws.Cells(i, 1).Value <> "" Then
            templateJson = templateJson & "," & vbCrLf
        Else
            templateJson = templateJson & vbCrLf
        End If
    Loop

    ' Close JSON
    templateJson = templateJson & "  ]" & vbCrLf & "}"

    ' Write out to sheetname.json
    Dim fso As Object, fileOut As Object
    Set fso = CreateObject("Scripting.FileSystemObject")
    Set fileOut = fso.CreateTextFile(ws.Name & ".json", True)
    fileOut.Write templateJson
    fileOut.Close

    MsgBox "JSON template saved as " & ws.Name & ".json", vbInformation
End Sub

' Helper to escape backslashes and quotes in JSON strings
Private Function EscapeJson(txt As String) As String
    txt = Replace(txt, "\", "\\")
    txt = Replace(txt, """", "\""")
    EscapeJson = txt
End Function

