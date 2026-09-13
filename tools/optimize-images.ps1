# ------------------------------------------------------------------
# Santhi Yoga India — web image optimiser (Windows PowerShell, no installs)
#
# Creates compressed JPG copies in assets/img at two widths (720 + 1280)
# for responsive srcset. Originals are never modified.
#   • applies the phone's EXIF rotation
#   • strips all metadata (including GPS location) by re-drawing the pixels
#   • optional horizontal flip (for mirrored selfie-camera shots)
#
# Usage:  powershell -ExecutionPolicy Bypass -File tools\optimize-images.ps1 [-Only <output-name>]
# To add photos later, add a line to $map below and run it again
# (use -Only with the new output name to process just that photo).
# HEIC is not supported by Windows without the HEVC codec — export as JPG first.
# ------------------------------------------------------------------
param([string]$Only)
Add-Type -AssemblyName System.Drawing

$root = Split-Path -Parent $PSScriptRoot
$out  = Join-Path $root 'assets\img'
New-Item -ItemType Directory -Force $out | Out-Null

$dl = "$env:USERPROFILE\Downloads"
# source file                                   => output base name (SEO-friendly)          flip
$map = @(
  @("$dl\IMG_5730.jpeg",                          'santhi-yoga-pavilion-class-fort-kochi',      $false),
  @("$dl\IMG_5159.jpeg",                          'savasana-rest-yoga-pavilion',                 $false),
  @("$dl\IMG_6035.JPG",                           'headstand-guidance-yoga-class-kerala',        $false),
  @("$root\WhatsApp Image 2026-04-22 at 3.26.37 PM.jpeg", 'master-aksharanand-a-s',              $false),
  @("$root\IMG_7499.jpg.PNG",                     'hands-on-yoga-adjustment-fort-kochi',         $true),
  @("$root\IMG_0900.PNG",                         'shared-vegetarian-meal-yoga-students',        $false),
  @("$root\IMG_0901.PNG",                         'yoga-student-mealtime-kerala',                $false),
  @("$root\IMG_8088.JPG.jpeg",                    'handstand-practice-yoga-retreat',             $false),
  @("$root\IMG_8521.JPG.jpeg",                    'traditional-ceremony-yoga-teacher-training',  $false),
  @("$root\IMG_863.jpg.jpeg",                     'yoga-retreat-group-kerala-hills',             $false),
  @("$root\IMG_8631.JPG.jpeg",                    'yoga-retreat-hilltop-group',                  $false),
  @("$root\IMG_7993.JPG.jpeg",                    'retreat-hike-hilltop-view',                   $false),
  @("$root\IMG_7902.JPG.jpeg",                    'cultural-excursion-yoga-students-kerala',     $false),
  @("$root\IMG_8415.jpg.jpeg",                    'yoga-pavilion-garden-fort-kochi',             $false),
  @("$root\IMG_7843.PNG",                         'waterfall-retreat-excursion-kerala',          $false),
  # Free Pexels photo by Mohammed Nasim (Pexels licence: free use, no attribution required)
  @("$root\photos\pexels-nasimgs-12593493.jpg",   'chinese-fishing-nets-fort-kochi',             $false)
)
if ($Only) { $map = @($map | Where-Object { $_[1] -eq $Only }) }
$widths = @(720, 1280)

$jpeg = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' }
$params = New-Object System.Drawing.Imaging.EncoderParameters 1
$params.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter ([System.Drawing.Imaging.Encoder]::Quality), 78L

foreach ($m in $map) {
  $src = $m[0]; $name = $m[1]; $flip = $m[2]
  if (-not (Test-Path -LiteralPath $src)) { Write-Output "MISSING: $src"; continue }
  $img = [System.Drawing.Image]::FromFile($src)
  if ($img.PropertyIdList -contains 274) {
    switch ($img.GetPropertyItem(274).Value[0]) {
      3 { $img.RotateFlip('Rotate180FlipNone') }
      6 { $img.RotateFlip('Rotate90FlipNone') }
      8 { $img.RotateFlip('Rotate270FlipNone') }
    }
  }
  if ($flip) { $img.RotateFlip('RotateNoneFlipX') }
  foreach ($w in $widths) {
    $tw = [math]::Min($w, $img.Width)
    $th = [int][math]::Round($img.Height * $tw / $img.Width)
    $bmp = New-Object System.Drawing.Bitmap $tw, $th
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.InterpolationMode = 'HighQualityBicubic'; $g.SmoothingMode = 'HighQuality'; $g.PixelOffsetMode = 'HighQuality'
    $g.DrawImage($img, 0, 0, $tw, $th)
    $file = Join-Path $out ("{0}-{1}.jpg" -f $name, $w)
    $bmp.Save($file, $jpeg, $params)
    $g.Dispose(); $bmp.Dispose()
    Write-Output ("{0}  {1}x{2}  {3:N0} KB" -f (Split-Path $file -Leaf), $tw, $th, ((Get-Item $file).Length / 1KB))
  }
  $img.Dispose()
}
