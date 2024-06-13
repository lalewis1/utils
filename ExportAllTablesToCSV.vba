Public Sub ExportAllTablesToCSV()

    Dim i As Integer
    Dim name As String
    
    For i = 0 To CurrentDb.TableDefs.Count
        name = CurrentDb.TableDefs(i).name
        
        If Not Left(name, 4) = "msys" And Not Left(name, 1) = "~" Then
            DoCmd.TransferText acExportDelim, , name, _
                "c:\myexportdir\" & name & ".csv", _
                True
        End If
    
    Next i

End Sub

