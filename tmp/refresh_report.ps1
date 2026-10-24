$ErrorActionPreference = 'Stop'
$word = $null
$document = $null
$docxPath = [System.IO.Path]::GetFullPath('deliverables\Bao_Cao_Thuc_Tap_Tot_Nghiep_FPT_YOLO.docx')
$pdfPath = [System.IO.Path]::GetFullPath('tmp\Bao_Cao_Thuc_Tap_Tot_Nghiep_FPT_YOLO.pdf')

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.ScreenUpdating = $false
    $document = $word.Documents.Open($docxPath, $false, $false)
    $document.Fields.Update() | Out-Null
    foreach ($toc in $document.TablesOfContents) { $toc.Update() }
    foreach ($figureList in $document.TablesOfFigures) { $figureList.Update() }
    $document.Fields.Update() | Out-Null
    $document.Save()
    $pageCount = $document.ComputeStatistics(2)
    $document.ExportAsFixedFormat($pdfPath, 17)
    Write-Output "Updated fields; pages=$pageCount; pdf=$pdfPath"
}
finally {
    if ($document -ne $null) { $document.Close($false) | Out-Null }
    if ($word -ne $null) { $word.Quit() | Out-Null }
    if ($document -ne $null) { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($document) }
    if ($word -ne $null) { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
