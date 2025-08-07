Option Explicit

Sub WorksheetToJsonInferred()
    Dim ws As Worksheet
    Dim templateJson As String
    Dim lastCol As Long, lastRow As Long
    Dim col As Long, row As Long
    Dim header As String, cellValue As String
    Dim dict As Object
    Dim key As Variant
    Dim distinctCount As Long
    Dim isNumericCol As Boolean
    Dim totalLen As Long, avgLen As Double
    Const thresholdDistinct As Long = 10
    Const thresholdTextLength As Long = 50

    Set ws = ActiveSheet
    lastRow = ws.UsedRange.Rows(ws.UsedRange.Rows.Count).Row
    lastCol = ws.UsedRange.Columns(ws.UsedRange.Columns.Count).Column

    ' Start JSON
    templateJson = "{""id"": """ & EscapeJson(ws.Name) & """," & vbCrLf & _
                   "  ""fields"": [" & vbCrLf

    Set dict = CreateObject("Scripting.Dictionary")

    For col = 1 To lastCol
        header = Trim(CStr(ws.Cells(1, col).Value))
        If Len(header) = 0 Then GoTo SkipCol

        ' Collect distinct values and compute stats
        dict.RemoveAll
        totalLen = 0
        isNumericCol = True

        For row = 2 To lastRow
            cellValue = Trim(CStr(ws.Cells(row, col).Value))
            If Len(cellValue) > 0 Then
                If Not dict.Exists(cellValue) Then
                    dict.Add cellValue, 1
                    totalLen = totalLen + Len(cellValue)
                    If Not IsNumeric(cellValue) Then isNumericCol = False
                End If
            End If
        Next row

        distinctCount = dict.Count
        If distinctCount > 0 Then
            avgLen = totalLen / distinctCount
        Else
            avgLen = 0
        End If

        ' Build field entry
        templateJson = templateJson & "    {"

        If distinctCount > 1 And distinctCount <= thresholdDistinct Then
            ' Dropdown
            templateJson = templateJson & _
                """label"": """ & EscapeJson(header) & """, " & _
                """type"": ""dropdown"", ""options"": ["
            Dim idx As Long: idx = 0
            For Each key In dict.Keys
                templateJson = templateJson & """" & EscapeJson(key) & """"
                idx = idx + 1
                If idx < dict.Count Then templateJson = templateJson & ", "
            Next key
            templateJson = templateJson & "]}"

        ElseIf isNumericCol And distinctCount > 0 Then
            ' Number
            templateJson = templateJson & _
                """label"": """ & EscapeJson(header) & """, " & _
                """type"": ""number""}"

        ElseIf avgLen > thresholdTextLength Then
            ' Textarea
            templateJson = templateJson & _
                """label"": """ & EscapeJson(header) & """, " & _
                """type"": ""textarea""}"

        Else
            ' Default to text
            templateJson = templateJson & _
                """label"": """ & EscapeJson(header) & """, " & _
                """type"": ""text""}"
        End If

        ' Add comma or newline
        If col < lastCol Then
            templateJson = templateJson & "," & vbCrLf
        Else
            templateJson = templateJson & vbCrLf
        End If

SkipCol:
    Next col

    ' Close JSON
    templateJson = templateJson & "  ]" & vbCrLf & "}"

    ' Write to file named after the sheet
    Dim fso As Object, fileOut As Object
    Set fso = CreateObject("Scripting.FileSystemObject")
    Set fileOut = fso.CreateTextFile(ws.Name & ".json", True)
    fileOut.Write templateJson
    fileOut.Close

    MsgBox "Generated JSON template: " & ws.Name & ".json", vbInformation
End Sub

' Escape backslashes and quotes for JSON safety
Private Function EscapeJson(txt As String) As String
    txt = Replace(txt, "\", "\\")
    txt = Replace(txt, """", "\""")
    EscapeJson = txt
End Function

