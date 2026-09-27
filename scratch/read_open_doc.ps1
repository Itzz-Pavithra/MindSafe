$word = [System.Runtime.InteropServices.Marshal]::GetActiveObject("Word.Application")
foreach ($doc in $word.Documents) {
    Write-Output "DOCUMENT: $($doc.FullName)"
    $text = $doc.Content.Text
    Write-Output "LENGTH: $($text.Length)"
    [System.IO.File]::WriteAllText("c:\Users\pavit\OneDrive\Desktop\MindSafe\scratch\paper_text.txt", $text, [System.Text.Encoding]::UTF8)
    Write-Output "Saved text to scratch/paper_text.txt"
}
