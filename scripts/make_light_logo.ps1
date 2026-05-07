$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Drawing

$inPath = Join-Path $PSScriptRoot "..\\Guestbook.png"
$outPath = Join-Path $PSScriptRoot "..\\Guestbook-light.png"

$img = [System.Drawing.Image]::FromFile($inPath)
$bmp = New-Object System.Drawing.Bitmap($img.Width, $img.Height)
$g = [System.Drawing.Graphics]::FromImage($bmp)

$g.Clear([System.Drawing.Color]::White)
$g.DrawImage($img, 0, 0, $img.Width, $img.Height)

$g.Dispose()
$img.Dispose()

$bmp.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()

Write-Output "Wrote $outPath"

