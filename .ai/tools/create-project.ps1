[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$TargetDirectory,
    [switch]$Force,
    [switch]$Update,
    [switch]$Apply,
    [string]$PatchFile = "template-update.patch"
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
if ($Apply -and -not $Update) {
    throw "-Apply is only valid together with -Update."
}

$ExcludeManifest = Join-Path $SourceDirectory ".ai/config/copy-exclude.txt"
if (-not (Test-Path -LiteralPath $ExcludeManifest)) {
    throw "Copy exclude manifest is missing: $ExcludeManifest"
}

function Read-ManifestSection {
    param(
        [Parameter(Mandatory = $true)] [string]$Section
    )
    $active = $false
    $values = New-Object System.Collections.Generic.List[string]
    foreach ($line in [System.IO.File]::ReadLines($ExcludeManifest)) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#")) {
            continue
        }
        if ($trimmed.StartsWith("[") -and $trimmed.EndsWith("]")) {
            $active = ($trimmed -eq "[$Section]")
            continue
        }
        if ($active) {
            $values.Add($trimmed)
        }
    }
    return $values.ToArray()
}

$excludedRelativePaths = Read-ManifestSection "relative_paths"
$excludedRootDirectories = Read-ManifestSection "root_directories"
$excludedNames = Read-ManifestSection "state_names"
$excludedExtensions = Read-ManifestSection "state_file_extensions"
$updateProtected = Read-ManifestSection "update_protected"
$CommandContext = $PSCmdlet

function Get-RelativeTemplatePath {
    param([Parameter(Mandatory = $true)] [System.IO.FileSystemInfo]$Item)
    return [System.IO.Path]::GetRelativePath($SourceDirectory, $Item.FullName).Replace('\', '/')
}

function Test-TemplateExcluded {
    param([Parameter(Mandatory = $true)] [string]$RelativePath)
    foreach ($segment in $RelativePath.Split('/')) {
        if ($excludedNames -contains $segment) {
            return $true
        }
    }
    foreach ($directory in $excludedRootDirectories) {
        if ($RelativePath -eq $directory -or $RelativePath.StartsWith($directory + "/", [System.StringComparison]::Ordinal)) {
            return $true
        }
    }
    if ($excludedRelativePaths -contains $RelativePath) {
        return $true
    }
    foreach ($extension in $excludedExtensions) {
        if ($RelativePath.EndsWith($extension, [System.StringComparison]::Ordinal)) {
            return $true
        }
    }
    return $false
}

function Copy-TemplateItem {
    param(
        [Parameter(Mandatory = $true)] [System.IO.FileSystemInfo]$Item,
        [Parameter(Mandatory = $true)] [string]$Destination
    )
    $relativePath = Get-RelativeTemplatePath -Item $Item
    if (
        $relativePath -in $excludedRelativePaths -or
        ($Item.PSIsContainer -and $relativePath -in $excludedRootDirectories) -or
        $Item.Name -in $excludedNames -or
        $Item.Extension -in $excludedExtensions
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

function Invoke-CreateMode {
    $existing = if (Test-Path -LiteralPath $TargetDirectory) {
        Get-ChildItem -LiteralPath $TargetDirectory -Force | Select-Object -First 1
    } else {
        $null
    }
    if ($existing -and -not $Force) {
        throw "Target directory is not empty: $TargetDirectory. Use -Force only for an intentional merge."
    }

    Write-Host "[create-project] Source: $SourceDirectory"
    Write-Host "[create-project] Target: $TargetDirectory"
    if ($CommandContext.ShouldProcess($TargetDirectory, "Create target directory")) {
        New-Item -ItemType Directory -Force -Path $TargetDirectory | Out-Null
    }
    Get-ChildItem -LiteralPath $SourceDirectory -Force | Where-Object {
        $_.Name -notin $excludedNames -and
        $_.Name -notin $excludedRootDirectories -and
        $_.Name -notin $excludedRelativePaths
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
}

function Test-FilesEqual {
    param([string]$First, [string]$Second)
    $firstBytes = [System.IO.File]::ReadAllBytes($First)
    $secondBytes = [System.IO.File]::ReadAllBytes($Second)
    if ($firstBytes.Length -ne $secondBytes.Length) {
        return $false
    }
    for ($i = 0; $i -lt $firstBytes.Length; $i++) {
        if ($firstBytes[$i] -ne $secondBytes[$i]) {
            return $false
        }
    }
    return $true
}

function Get-UnifiedDiff {
    param([string]$RelativePath, [string]$DiffTool)
    $src = Join-Path $SourceDirectory $RelativePath
    $dst = Join-Path $TargetDirectory $RelativePath
    if (Test-Path -LiteralPath $dst) {
        $out = & $DiffTool -u -L "a/$RelativePath" -L "b/$RelativePath" -- $dst $src 2>$null
    } else {
        $empty = New-TemporaryFile
        try {
            $out = & $DiffTool -u -L "/dev/null" -L "b/$RelativePath" -- $empty.FullName $src 2>$null
        } finally {
            Remove-Item -LiteralPath $empty.FullName -Force -ErrorAction SilentlyContinue
        }
    }
    $global:LASTEXITCODE = 0
    return ($out -join "`n")
}

function Invoke-UpdateMode {
    if (-not (Test-Path -LiteralPath $TargetDirectory -PathType Container)) {
        throw "Update target does not exist: $TargetDirectory"
    }
    if (-not (Test-Path -LiteralPath (Join-Path $TargetDirectory "AGENTS.md")) -or
        -not (Test-Path -LiteralPath (Join-Path $TargetDirectory ".ai") -PathType Container)) {
        throw "Target does not look like a template-based project (missing AGENTS.md or .ai/): $TargetDirectory. Use create mode for a brand-new project."
    }

    $added = New-Object System.Collections.Generic.List[string]
    $updated = New-Object System.Collections.Generic.List[string]
    $protectedDiff = New-Object System.Collections.Generic.List[string]
    $unchanged = 0
    Get-ChildItem -LiteralPath $SourceDirectory -Recurse -File -Force | ForEach-Object {
        $rel = Get-RelativeTemplatePath -Item $_
        if (Test-TemplateExcluded -RelativePath $rel) {
            return
        }
        $dst = Join-Path $TargetDirectory $rel
        if (-not (Test-Path -LiteralPath $dst)) {
            $added.Add($rel)
        } elseif (Test-FilesEqual -First $_.FullName -Second $dst) {
            $script:unchanged++
        } elseif ($updateProtected -contains $rel) {
            $protectedDiff.Add($rel)
        } else {
            $updated.Add($rel)
        }
    }

    Write-Host "[update] Source: $SourceDirectory"
    Write-Host "[update] Target: $TargetDirectory"
    Write-Host ("[update] new: {0}, changed: {1}, protected conflicts: {2}, unchanged: {3}" -f `
            $added.Count, $updated.Count, $protectedDiff.Count, $unchanged)
    if ($added.Count) { Write-Host "  New template files (added):"; $added | ForEach-Object { Write-Host "    - $_" } }
    if ($updated.Count) { Write-Host "  Changed template files (reusable, safe to update):"; $updated | ForEach-Object { Write-Host "    - $_" } }
    if ($protectedDiff.Count) { Write-Host "  Protected project files (differ; manual merge):"; $protectedDiff | ForEach-Object { Write-Host "    - $_" } }

    if ($WhatIfPreference) {
        Write-Host "[update] WhatIf preview complete; the target was not changed."
        return
    }
    if (($added.Count + $updated.Count + $protectedDiff.Count) -eq 0) {
        Write-Host "[update] Project already matches the template. Nothing to do."
        return
    }

    $diffTool = (Get-Command diff -ErrorAction SilentlyContinue)
    $manualPatch = if ($PatchFile.EndsWith(".patch")) {
        $PatchFile.Substring(0, $PatchFile.Length - ".patch".Length) + ".manual.patch"
    } else {
        $PatchFile + ".manual"
    }

    if ($Apply) {
        foreach ($rel in ($added + $updated)) {
            $dst = Join-Path $TargetDirectory $rel
            New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dst) | Out-Null
            Copy-Item -LiteralPath (Join-Path $SourceDirectory $rel) -Destination $dst -Force
        }
        Write-Host ("[update] Applied {0} new and {1} changed template files." -f $added.Count, $updated.Count)
    } elseif ($diffTool) {
        $lines = foreach ($rel in ($added + $updated)) { Get-UnifiedDiff -RelativePath $rel -DiffTool $diffTool.Source }
        [System.IO.File]::WriteAllText($PatchFile, (($lines -join "`n") + "`n"))
        Write-Host "[update] Wrote template patch: $PatchFile"
        Write-Host "[update] Review it, then apply with: git -C `"$TargetDirectory`" apply `"$PatchFile`""
        Write-Host "[update] Or re-run with -Apply to integrate the safe changes directly."
    } else {
        throw "diff was not found. Install diffutils/Git, or re-run with -Apply to integrate changes directly."
    }

    if ($protectedDiff.Count) {
        if ($diffTool) {
            $lines = foreach ($rel in $protectedDiff) { Get-UnifiedDiff -RelativePath $rel -DiffTool $diffTool.Source }
            [System.IO.File]::WriteAllText($manualPatch, (($lines -join "`n") + "`n"))
            Write-Host "[update] Protected files changed in the template. Merge these by hand: $manualPatch"
        } else {
            foreach ($rel in $protectedDiff) {
                Copy-Item -LiteralPath (Join-Path $SourceDirectory $rel) -Destination ((Join-Path $TargetDirectory $rel) + ".template-new") -Force
            }
            Write-Host "[update] Protected files changed; template versions saved next to them as *.template-new for manual merge."
        }
        Write-Host "[update] These project-owned files were NOT modified."
    }
}

if ($Update) {
    Invoke-UpdateMode
} else {
    Invoke-CreateMode
}
