<#
.SYNOPSIS
    Generates a custom 256x256 .ico file for the Desktop shortcut.

.DESCRIPTION
    Draws a stock-chart-themed icon (dark teal rounded square with white
    bar chart and a green upward trend arrow) and writes it as a PNG-embedded
    ICO file ("eod_icon.ico" in the repo root). Re-run any time to regenerate.
#>

Add-Type -AssemblyName System.Drawing

$repoDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$icoPath = Join-Path $repoDir 'eod_icon.ico'
$size = 256

$bmp = New-Object System.Drawing.Bitmap $size, $size
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g.Clear([System.Drawing.Color]::Transparent)

# --- Rounded background (dark teal gradient) ---
$bgRect = New-Object System.Drawing.Rectangle 8, 8, ($size - 16), ($size - 16)
$radius = 40
$path = New-Object System.Drawing.Drawing2D.GraphicsPath
$path.AddArc($bgRect.X, $bgRect.Y, $radius, $radius, 180, 90)
$path.AddArc($bgRect.Right - $radius, $bgRect.Y, $radius, $radius, 270, 90)
$path.AddArc($bgRect.Right - $radius, $bgRect.Bottom - $radius, $radius, $radius, 0, 90)
$path.AddArc($bgRect.X, $bgRect.Bottom - $radius, $radius, $radius, 90, 90)
$path.CloseFigure()

$bgBrush = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
    $bgRect,
    [System.Drawing.Color]::FromArgb(255, 18, 60, 50),
    [System.Drawing.Color]::FromArgb(255, 6, 30, 25),
    [System.Drawing.Drawing2D.LinearGradientMode]::ForwardDiagonal)
$g.FillPath($bgBrush, $path)

# Subtle inner border
$borderPen = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(60, 255, 255, 255)), 2
$g.DrawPath($borderPen, $path)

# --- Bar chart (ascending bars, white with green tops) ---
$baseY = 200
$barColors = @(
    [System.Drawing.Color]::FromArgb(255, 200, 230, 210),
    [System.Drawing.Color]::FromArgb(255, 150, 220, 170),
    [System.Drawing.Color]::FromArgb(255, 100, 210, 130),
    [System.Drawing.Color]::FromArgb(255, 60, 200, 90)
)
$barXs     = @(50, 95, 140, 185)
$barHeights = @(40, 65, 95, 130)
for ($i = 0; $i -lt 4; $i++) {
    $brush = New-Object System.Drawing.SolidBrush $barColors[$i]
    $h = $barHeights[$i]
    $rect = New-Object System.Drawing.Rectangle $barXs[$i], ($baseY - $h), 30, $h
    $g.FillRectangle($brush, $rect)
    $brush.Dispose()
}

# --- Trend arrow (bright green, going up-right across the top of bars) ---
$arrowPen = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(255, 120, 255, 140)), 10
$arrowPen.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
$arrowPen.EndCap   = [System.Drawing.Drawing2D.LineCap]::Round
$arrowPen.LineJoin = [System.Drawing.Drawing2D.LineJoin]::Round

$pts = @(
    (New-Object System.Drawing.Point 65,  170),
    (New-Object System.Drawing.Point 110, 145),
    (New-Object System.Drawing.Point 155, 115),
    (New-Object System.Drawing.Point 200, 75)
)
$g.DrawLines($arrowPen, $pts)

# Arrowhead
$arrowFill = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 120, 255, 140))
$head = @(
    (New-Object System.Drawing.Point 200, 60),
    (New-Object System.Drawing.Point 220, 95),
    (New-Object System.Drawing.Point 180, 95)
)
$g.FillPolygon($arrowFill, $head)

# --- "$" badge top-left ---
$dollarFont  = New-Object System.Drawing.Font 'Segoe UI', 60, ([System.Drawing.FontStyle]::Bold)
$dollarBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 255, 255, 255))
$g.DrawString('$', $dollarFont, $dollarBrush, 30, 28)

$g.Dispose()

# --- Encode as PNG-embedded ICO ---
$ms = New-Object System.IO.MemoryStream
$bmp.Save($ms, [System.Drawing.Imaging.ImageFormat]::Png)
$pngBytes = $ms.ToArray()
$ms.Dispose()
$bmp.Dispose()

$fs = [System.IO.File]::Create($icoPath)
$bw = New-Object System.IO.BinaryWriter $fs

# ICONDIR (6 bytes)
$bw.Write([uint16]0)        # Reserved, must be 0
$bw.Write([uint16]1)        # Type: 1 = icon
$bw.Write([uint16]1)        # Image count

# ICONDIRENTRY (16 bytes)
$bw.Write([byte]0)          # Width (0 = 256)
$bw.Write([byte]0)          # Height (0 = 256)
$bw.Write([byte]0)          # Color palette count (0 for >=8bpp)
$bw.Write([byte]0)          # Reserved
$bw.Write([uint16]1)        # Color planes
$bw.Write([uint16]32)       # Bits per pixel
$bw.Write([uint32]$pngBytes.Length)   # PNG size
$bw.Write([uint32]22)       # Offset to PNG data (6 + 16)

# PNG payload
$bw.Write($pngBytes)
$bw.Close()
$fs.Close()

Write-Host "Custom icon written to: $icoPath" -ForegroundColor Green
