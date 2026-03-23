[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string[]]$WorkspaceRoot,
    [string]$RuntimeHome = "",
    [Alias('CodexHome')]
    [string]$LegacyCodexHome = "",
    [string]$BackupRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Read-JsonYaml {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path $Path)) { throw "JSON-compatible YAML file not found: $Path" }
    return Get-Content -Raw $Path | ConvertFrom-Json
}

function Ensure-Dir {
    param([Parameter(Mandatory = $true)][string]$Path)
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
    return (Resolve-Path $Path).Path
}

function Backup-And-Remove {
    param(
        [Parameter(Mandatory = $true)][string]$ExistingPath,
        [Parameter(Mandatory = $true)][string]$ResolvedBackupRoot
    )
    if (-not (Test-Path $ExistingPath)) { return }
    $name = Split-Path $ExistingPath -Leaf
    $timestamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
    $destination = Join-Path $ResolvedBackupRoot "${name}_$timestamp"
    Move-Item -Path $ExistingPath -Destination $destination
}

function Ensure-Junction {
    param(
        [Parameter(Mandatory = $true)][string]$LinkPath,
        [Parameter(Mandatory = $true)][string]$TargetPath,
        [Parameter(Mandatory = $true)][string]$ResolvedBackupRoot
    )
    if (Test-Path $LinkPath) {
        $item = Get-Item -LiteralPath $LinkPath -Force
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            $resolved = (Resolve-Path $LinkPath).Path
            if ($resolved -eq (Resolve-Path $TargetPath).Path) { return }
        }
        Backup-And-Remove -ExistingPath $LinkPath -ResolvedBackupRoot $ResolvedBackupRoot
    }
    $parent = Split-Path $LinkPath -Parent
    if ($parent) { Ensure-Dir -Path $parent | Out-Null }
    New-Item -ItemType Junction -Path $LinkPath -Target $TargetPath | Out-Null
}

$resolvedRuntimeHome = if ($RuntimeHome) { Ensure-Dir -Path $RuntimeHome } elseif ($LegacyCodexHome) { Ensure-Dir -Path $LegacyCodexHome } else { Ensure-Dir -Path (Join-Path $HOME '.codex') }
$resolvedBackupRoot = if ($BackupRoot) { Ensure-Dir -Path $BackupRoot } else { Ensure-Dir -Path (Join-Path (Join-Path $resolvedRuntimeHome '.runtime-link-backups') (Get-Date -Format 'yyyyMMdd_HHmmss')) }
$skillsRoot = Ensure-Dir -Path (Join-Path $resolvedRuntimeHome 'skills')
$results = @()

foreach ($workspace in $WorkspaceRoot) {
    $resolvedWorkspace = (Resolve-Path $workspace).Path
    $manifest = Read-JsonYaml -Path (Join-Path $resolvedWorkspace 'workspace.manifest.yaml')
    foreach ($skill in @($manifest.runtime_mounts.skills)) {
        $name = [string]$skill.name
        $source = Join-Path $resolvedWorkspace ([string]$skill.source)
        if (-not (Test-Path $source)) { throw "Skill source missing: $source" }
        $link = Join-Path $skillsRoot $name
        Ensure-Junction -LinkPath $link -TargetPath $source -ResolvedBackupRoot $resolvedBackupRoot
        $results += [pscustomobject]@{ workspace = $resolvedWorkspace; kind = 'skill'; name = $name; link = $link; target = $source }
    }
}

$results | ConvertTo-Json -Depth 5
