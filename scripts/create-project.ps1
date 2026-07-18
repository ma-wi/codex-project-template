[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$TargetDirectory,

    [switch]$Force
)

$ErrorActionPreference = "Stop"
$SourceDirectory = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$TargetDirectory = [System.IO.Path]::GetFullPath($TargetDirectory)

if ($SourceDirectory -eq $TargetDirectory) {
    throw "Source and target must be different directories."
}

New-Item -ItemType Directory -Force -Path $TargetDirectory | Out-Null
$existing = Get-ChildItem -LiteralPath $TargetDirectory -Force -ErrorAction Stop | Select-Object -First 1
if ($existing -and -not $Force) {
    throw "Target directory is not empty: $TargetDirectory. Use -Force only when merging is intentional."
}

$excludedTopLevel = @(".git", ".idea")
$excludedNames = @(
    "project.env", ".venv", "venv", "node_modules", "__pycache__",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", "coverage",
    "build", "dist", "target"
)

Write-Host "[create-project] Source: $SourceDirectory"
Write-Host "[create-project] Target: $TargetDirectory"

Get-ChildItem -LiteralPath $SourceDirectory -Force | Where-Object {
    $_.Name -notin $excludedTopLevel
} | ForEach-Object {
    $destination = Join-Path $TargetDirectory $_.Name
    if ($PSCmdlet.ShouldProcess($destination, "Copy template item")) {
        Copy-Item -LiteralPath $_.FullName -Destination $destination -Recurse -Force
    }
}

foreach ($name in $excludedNames) {
    Get-ChildItem -LiteralPath $TargetDirectory -Force -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -eq $name } |
        Sort-Object FullName -Descending |
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
}

Get-ChildItem -LiteralPath $TargetDirectory -Force -Recurse -Include *.pyc,*.pyo,*.zip -ErrorAction SilentlyContinue |
    Remove-Item -Force -ErrorAction SilentlyContinue

Write-Host "[create-project] Template copied successfully."
Write-Host "[create-project] Next: edit config/ai-project.yaml and run ./scripts/bootstrap.sh"
