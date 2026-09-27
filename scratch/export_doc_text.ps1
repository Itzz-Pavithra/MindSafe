$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $docPath = "C:\Users\pavit\OneDrive\Desktop\Research paper.docx"
    # Open ReadOnly = $true
    $doc = $word.Documents.Open($docPath, $false, $true)
    $text = $doc.Content.Text
    [System.IO.File]::WriteAllText("c:\Users\pavit\OneDrive\Desktop\MindSafe\scratch\paper_full_text.txt", $text, [System.Text.Encoding]::UTF8)
    Write-Output "EXTRACTED_SUCCESS: $($text.Length) characters"
    $doc.Close([ref]$false)
} catch {
    Write-Error "ERROR: $_"
} finally {
    $word.Quit([ref]$false)
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}
