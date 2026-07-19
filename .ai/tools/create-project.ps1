[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$TargetDirectory,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    throw "Python 3 is required to resolve source and target paths safely."
}
$SourceDirectory = (& $python.Source -c "import pathlib, sys; print(pathlib.Path(sys.argv[1]).resolve())" (Join-Path $PSScriptRoot "../..")).Trim()
$TargetDirectory = (& $python.Source -c "import pathlib, sys; print(pathlib.Path(sys.argv[1]).resolve())" $TargetDirectory).Trim()
if ($LASTEXITCODE -ne 0 -or -not $SourceDirectory -or -not $TargetDirectory) {
    throw "Could not resolve source and target paths safely."
}
$PathComparison = if ($IsWindows) { [System.StringComparison]::OrdinalIgnoreCase } else { [System.StringComparison]::Ordinal }

if ($SourceDirectory -eq $TargetDirectory -or $TargetDirectory.StartsWith($SourceDirectory + [System.IO.Path]::DirectorySeparatorChar, $PathComparison)) {
    throw "Target must be different from and outside the template source directory."
}
$existing = if (Test-Path -LiteralPath $TargetDirectory) {
    Get-ChildItem -LiteralPath $TargetDirectory -Force | Select-Object -First 1
} else {
    $null
}
if ($existing -and -not $Force) {
    throw "Target directory is not empty: $TargetDirectory. Use -Force only for an intentional merge."
}

$excludedTopLevel = @(
    ".git", ".idea", "README.md", "CHANGELOG.md", "CONTRIBUTING.md", "tests"
)
$excludedRelativePaths = @(
    ".ai/work",
    ".ai/CURRENT_PLAN.md",
    "docs/architecture/decisions/ADR-0001-ai-control-plane.md",
    "docs/specifications/REQ-ai-control-plane-layout.md",
    "docs/requirements/REQ-template-hardening.md",
    "docs/specifications/REQ-template-hardening.md",
    ".github/workflows/template-copy.yml",
    ".ai/DECISIONS.md",
    ".ai/tools/create-project.sh",
    ".ai/tools/create-project.ps1",
    ".ai/tools/verify-template.sh",
    ".ai/config/project.env"
)
$excludedNames = @(
    ".git", ".idea", ".vscode", ".cursor", ".claude", ".codex",
    ".venv", "venv", "node_modules", "__pycache__",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", "coverage",
    "build", "dist", "target"
)
$CommandContext = $PSCmdlet

function Copy-TemplateItem {
    param(
        [Parameter(Mandatory = $true)] [System.IO.FileSystemInfo]$Item,
        [Parameter(Mandatory = $true)] [string]$Destination
    )
    $relativePath = [System.IO.Path]::GetRelativePath($SourceDirectory, $Item.FullName).Replace('\', '/')
    if (
        $relativePath -in $excludedRelativePaths -or
        $Item.Name -in $excludedNames -or
        $Item.Extension -in @(".pyc", ".pyo", ".zip")
    ) {
        return
    }
    if ($Item.PSIsContainer) {
        if ($CommandContext.ShouldProcess($Destination, "Create template directory")) {
            New-Item -ItemType Directory -Force -Path $Destination | Out-Null
        }
        Get-ChildItem -LiteralPath $Item.FullName -Force | ForEach-Object {
            Copy-TemplateItem -Item $_ -Destination (Join-Path $Destination $_.Name)
        }
    } elseif ($CommandContext.ShouldProcess($Destination, "Copy template file")) {
        Copy-Item -LiteralPath $Item.FullName -Destination $Destination -Force
    }
}

Write-Host "[create-project] Source: $SourceDirectory"
Write-Host "[create-project] Target: $TargetDirectory"
if ($CommandContext.ShouldProcess($TargetDirectory, "Create target directory")) {
    New-Item -ItemType Directory -Force -Path $TargetDirectory | Out-Null
}
Get-ChildItem -LiteralPath $SourceDirectory -Force | Where-Object {
    $_.Name -notin $excludedTopLevel
} | ForEach-Object {
    Copy-TemplateItem -Item $_ -Destination (Join-Path $TargetDirectory $_.Name)
}

$CurrentPlan = Join-Path $TargetDirectory ".ai/CURRENT_PLAN.md"
if ($CommandContext.ShouldProcess($CurrentPlan, "Create idle current-work pointer")) {
    # Write bytes explicitly so the pointer is identical to the shell script's
    # output (LF newlines, no BOM) on every PowerShell edition and platform.
    [System.IO.File]::WriteAllText(
        $CurrentPlan, "# Current work`n`nNo active requirement.`n"
    )
}

if ($WhatIfPreference) {
    Write-Host "[create-project] WhatIf preview complete; the target was not changed."
} else {
    Write-Host "[create-project] Template copied successfully."
    Write-Host "[create-project] Next: edit .ai/project.yaml and run python .\.ai\tools\bootstrap.py"
}
