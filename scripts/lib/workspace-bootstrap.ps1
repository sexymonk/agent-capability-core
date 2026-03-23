Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Read-JsonYaml {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { throw "JSON-compatible YAML file not found: $Path" }
    return Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
}

function Write-JsonYaml {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)]$Payload
    )
    $parent = Split-Path $Path -Parent
    if ($parent) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
    ($Payload | ConvertTo-Json -Depth 30) + "`n" | Set-Content -LiteralPath $Path -Encoding UTF8
}

function Ensure-Dir {
    param([Parameter(Mandatory = $true)][string]$Path)
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
    return (Resolve-Path -LiteralPath $Path).Path
}

function Get-WorkspaceManifestData {
    param([Parameter(Mandatory = $true)][string]$WorkspaceRoot)
    return Read-JsonYaml -Path (Join-Path $WorkspaceRoot 'workspace.manifest.yaml')
}

function Get-WorkspaceLockData {
    param([Parameter(Mandatory = $true)][string]$WorkspaceRoot)
    $lockPath = Join-Path $WorkspaceRoot 'workspace.lock.yaml'
    if (-not (Test-Path -LiteralPath $lockPath)) { return [pscustomobject]@{} }
    return Read-JsonYaml -Path $lockPath
}

function Get-WorkspaceId {
    param([Parameter(Mandatory = $true)][string]$WorkspaceRoot)
    $manifest = Get-WorkspaceManifestData -WorkspaceRoot $WorkspaceRoot
    $workspaceId = [string]$manifest.workspace_id
    if (-not $workspaceId) { $workspaceId = Split-Path $WorkspaceRoot -Leaf }
    return $workspaceId
}

function Get-WorkspaceApiVersion {
    param([Parameter(Mandatory = $true)][string]$WorkspaceRoot)
    $manifest = Get-WorkspaceManifestData -WorkspaceRoot $WorkspaceRoot
    $raw = if ($null -ne $manifest.workspace_api_version) { $manifest.workspace_api_version } else { $manifest.schema_version }
    return [int]$raw
}

function Get-WorkspaceRepoSpec {
    param(
        [Parameter(Mandatory = $true)][string]$WorkspaceRoot,
        [Parameter(Mandatory = $true)][string]$RepoId
    )
    $manifest = Get-WorkspaceManifestData -WorkspaceRoot $WorkspaceRoot
    foreach ($repo in @($manifest.repositories)) {
        $candidate = [string]$(if ($repo.repo_id) { $repo.repo_id } else { $repo.id })
        if ($candidate -eq $RepoId) { return $repo }
    }
    return $null
}

function Get-WorkspaceLockedRepo {
    param(
        [Parameter(Mandatory = $true)][string]$WorkspaceRoot,
        [Parameter(Mandatory = $true)][string]$RepoId
    )
    $lock = Get-WorkspaceLockData -WorkspaceRoot $WorkspaceRoot
    if (-not $lock.repositories) { return $null }
    return $lock.repositories.$RepoId
}

function Get-DefaultWorkspaceBase {
    param([string]$RequestedPath = '')
    if ($RequestedPath) { return Ensure-Dir -Path $RequestedPath }
    if (Test-Path 'D:\') { return Ensure-Dir -Path 'D:\Codex' }
    return Ensure-Dir -Path (Join-Path $HOME 'Codex')
}

function Get-DefaultAuxBase {
    param([string]$RequestedPath = '')
    if ($RequestedPath) { return Ensure-Dir -Path $RequestedPath }
    if (Test-Path 'D:\') { return Ensure-Dir -Path 'D:\codex_aux' }
    return Ensure-Dir -Path (Join-Path $HOME 'codex_aux')
}

function Test-IsAdministrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-CommandAvailable {
    param([Parameter(Mandatory = $true)][string]$CommandName)
    return $null -ne (Get-Command $CommandName -ErrorAction SilentlyContinue)
}

function Get-CommandPathOrEmpty {
    param([Parameter(Mandatory = $true)][string]$CommandName)
    $command = Get-Command $CommandName -ErrorAction SilentlyContinue
    if (-not $command) { return '' }
    return [string]$command.Source
}

function Resolve-NetworkConfig {
    param(
        [string]$RequestedProfile = 'auto',
        $MachineNetwork = $null,
        $ManifestNetworkProfiles = $null
    )
    $profiles = @{
        auto = @{ allow_proxy_env = $true; allow_mirrors = $true }
        direct = @{ allow_proxy_env = $false; allow_mirrors = $false }
        proxy = @{ allow_proxy_env = $true; allow_mirrors = $false }
        mirror = @{ allow_proxy_env = $true; allow_mirrors = $true }
    }
    if ($ManifestNetworkProfiles) {
        foreach ($item in $ManifestNetworkProfiles.PSObject.Properties) {
            $merged = @{}
            if ($profiles.ContainsKey($item.Name)) { $profiles[$item.Name].GetEnumerator() | ForEach-Object { $merged[$_.Key] = $_.Value } }
            foreach ($prop in $item.Value.PSObject.Properties) { $merged[$prop.Name] = $prop.Value }
            $profiles[$item.Name] = $merged
        }
    }
    $network = @{}
    if ($MachineNetwork) {
        foreach ($prop in $MachineNetwork.PSObject.Properties) { $network[$prop.Name] = $prop.Value }
    }
    $requested = if ($RequestedProfile) { $RequestedProfile } elseif ($network.ContainsKey('profile')) { [string]$network['profile'] } else { 'auto' }
    $proxyMap = @{}
    $mirrorMap = @{}
    if ($network.ContainsKey('proxy') -and $network['proxy']) {
        foreach ($prop in $network['proxy'].PSObject.Properties) { $proxyMap[$prop.Name] = [string]$prop.Value }
    }
    if ($network.ContainsKey('mirrors') -and $network['mirrors']) {
        foreach ($prop in $network['mirrors'].PSObject.Properties) { $mirrorMap[$prop.Name] = [string]$prop.Value }
    }
    $resolved = $requested
    if ($resolved -eq 'auto') {
        if ($proxyMap['http'] -or $proxyMap['https'] -or $proxyMap['no_proxy'] -or $env:HTTP_PROXY -or $env:HTTPS_PROXY -or $env:NO_PROXY) {
            $resolved = 'proxy'
        }
        elseif ($mirrorMap['pip_index_url'] -or $mirrorMap['qt_base_url'] -or $mirrorMap['cuda_docs_url']) {
            $resolved = 'mirror'
        }
        else {
            $resolved = 'direct'
        }
    }
    $profile = if ($profiles.ContainsKey($resolved)) { $profiles[$resolved] } else { $profiles['direct'] }
    return [pscustomobject]@{
        requested_profile = $requested
        selected_profile = $resolved
        proxy = [pscustomobject]@{
            http = if ($proxyMap['http']) { $proxyMap['http'] } elseif ($profile.allow_proxy_env) { [string]$env:HTTP_PROXY } else { '' }
            https = if ($proxyMap['https']) { $proxyMap['https'] } elseif ($profile.allow_proxy_env) { [string]$env:HTTPS_PROXY } else { '' }
            no_proxy = if ($proxyMap['no_proxy']) { $proxyMap['no_proxy'] } elseif ($profile.allow_proxy_env) { [string]$env:NO_PROXY } else { '' }
        }
        mirrors = [pscustomobject]@{
            pip_index_url = [string]$mirrorMap['pip_index_url']
            qt_base_url = [string]$mirrorMap['qt_base_url']
            cuda_docs_url = [string]$mirrorMap['cuda_docs_url']
        }
        offline_cache_root = [string]$network['offline_cache_root']
    }
}

function Apply-NetworkConfig {
    param([Parameter(Mandatory = $true)]$NetworkConfig)
    if ($NetworkConfig.proxy.http) { $env:HTTP_PROXY = [string]$NetworkConfig.proxy.http }
    if ($NetworkConfig.proxy.https) { $env:HTTPS_PROXY = [string]$NetworkConfig.proxy.https }
    if ($NetworkConfig.proxy.no_proxy) { $env:NO_PROXY = [string]$NetworkConfig.proxy.no_proxy }
    if ($NetworkConfig.mirrors.pip_index_url) { $env:PIP_INDEX_URL = [string]$NetworkConfig.mirrors.pip_index_url }
    if ($NetworkConfig.mirrors.qt_base_url) { $env:AQT_BASEURL = [string]$NetworkConfig.mirrors.qt_base_url }
    if ($NetworkConfig.mirrors.cuda_docs_url) { $env:CUDA_DOCS_URL = [string]$NetworkConfig.mirrors.cuda_docs_url }
}

function Assert-WingetAvailable {
    if (-not (Test-CommandAvailable -CommandName 'winget')) {
        throw 'winget is required for automatic bootstrap installs but was not found on this machine.'
    }
}

function Invoke-WingetInstall {
    param(
        [Parameter(Mandatory = $true)][string]$PackageId,
        [string]$Version = '',
        [string]$Override = '',
        [string]$Scope = 'machine',
        [string]$Source = '',
        [switch]$Interactive,
        [switch]$AllowWithoutAdmin
    )
    Assert-WingetAvailable
    if ($Scope -eq 'machine' -and -not (Test-IsAdministrator) -and -not $AllowWithoutAdmin) {
        throw "Administrator rights are required to install machine-scoped package $PackageId"
    }
    $args = @('install', '--id', $PackageId, '--exact', '--accept-package-agreements', '--accept-source-agreements', '--disable-interactivity')
    if ($Version) { $args += @('--version', $Version) }
    if ($Scope) { $args += @('--scope', $Scope) }
    if ($Override) { $args += @('--override', $Override) }
    if ($Source) { $args += @('--source', $Source) }
    if ($Interactive) { $args = $args | Where-Object { $_ -ne '--disable-interactivity' } }
    & winget @args | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "winget install failed for package $PackageId" }
}

function Ensure-BasicBootstrapTools {
    param(
        [switch]$AllowInstall,
        $NetworkConfig = $null,
        [switch]$NoAdmin
    )
    if ($NetworkConfig) { Apply-NetworkConfig -NetworkConfig $NetworkConfig }
    $toolCatalog = @(
        @{ command = 'git'; package = 'Git.Git'; version = ''; scope = 'machine'; override = '' },
        @{ command = 'gh'; package = 'GitHub.cli'; version = ''; scope = 'machine'; override = '' },
        @{ command = 'python'; package = 'Python.Python.3.12'; version = ''; scope = 'user'; override = '' },
        @{ command = 'cmake'; package = 'Kitware.CMake'; version = ''; scope = 'machine'; override = '' }
    )
    foreach ($tool in $toolCatalog) {
        if (Test-CommandAvailable -CommandName $tool.command) { continue }
        if (-not $AllowInstall) { throw "Missing required bootstrap tool: $($tool.command)" }
        Invoke-WingetInstall -PackageId $tool.package -Version $tool.version -Scope $tool.scope -Override $tool.override -AllowWithoutAdmin:($NoAdmin -or $tool.scope -ne 'machine')
    }
}

function Ensure-GitHubAuth {
    if (-not (Test-CommandAvailable -CommandName 'gh')) {
        throw 'GitHub CLI is required for private repository authentication.'
    }
    & gh auth status | Out-Null
    if ($LASTEXITCODE -eq 0) {
        & gh auth setup-git | Out-Null
        return
    }
    & gh auth login --web --git-protocol https | Out-Host
    if ($LASTEXITCODE -ne 0) { throw 'GitHub CLI login failed.' }
    & gh auth setup-git | Out-Host
    if ($LASTEXITCODE -ne 0) { throw 'gh auth setup-git failed.' }
}

function Ensure-RepositoryCheckout {
    param(
        [Parameter(Mandatory = $true)]$RepoSpec,
        [Parameter(Mandatory = $true)][string]$DestinationPath,
        [string]$LockedRef = '',
        [string]$Branch = '',
        [switch]$PullLatest,
        [switch]$SkipCheckout
    )
    $cloneUrl = [string]$RepoSpec.clone_url
    if (-not $cloneUrl) { throw "Repository spec is missing clone_url: $($RepoSpec | ConvertTo-Json -Compress)" }
    $authMode = [string]$RepoSpec.auth_mode
    if ($authMode -eq 'gh-cli-https') { Ensure-GitHubAuth }
    $parent = Split-Path $DestinationPath -Parent
    if ($parent) { Ensure-Dir -Path $parent | Out-Null }
    if (-not (Test-Path $DestinationPath)) {
        git clone $cloneUrl $DestinationPath | Out-Host
        if ($LASTEXITCODE -ne 0) { throw "git clone failed for $cloneUrl -> $DestinationPath" }
    }
    if (-not (Test-Path (Join-Path $DestinationPath '.git'))) { throw "Expected a git repository at $DestinationPath" }
    $dirty = git -C $DestinationPath status --porcelain 2>$null
    if ($dirty) { throw "Repository has local changes and cannot be auto-managed safely: $DestinationPath" }
    if ($SkipCheckout) { return }
    git -C $DestinationPath fetch --all --tags --prune | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "git fetch failed in $DestinationPath" }
    if ($LockedRef) {
        git -C $DestinationPath checkout $LockedRef | Out-Host
        if ($LASTEXITCODE -ne 0) { throw "git checkout failed for ref $LockedRef in $DestinationPath" }
        return
    }
    if ($PullLatest) {
        if ($Branch) {
            git -C $DestinationPath checkout $Branch | Out-Host
            if ($LASTEXITCODE -ne 0) { throw "git checkout failed for branch $Branch in $DestinationPath" }
        }
        git -C $DestinationPath pull --ff-only | Out-Host
        if ($LASTEXITCODE -ne 0) { throw "git pull --ff-only failed in $DestinationPath" }
    }
}

function Get-InstallStatePath {
    param(
        [Parameter(Mandatory = $true)][string]$WorkspaceId,
        [string]$RuntimeLocalHome = ''
    )
    $base = if ($RuntimeLocalHome) { $RuntimeLocalHome } else { Join-Path $HOME '.codex-local' }
    return Join-Path (Join-Path $base $WorkspaceId) 'install-state.json'
}

function Load-InstallState {
    param(
        [Parameter(Mandatory = $true)][string]$WorkspaceId,
        [string]$RuntimeLocalHome = ''
    )
    $path = Get-InstallStatePath -WorkspaceId $WorkspaceId -RuntimeLocalHome $RuntimeLocalHome
    if (-not (Test-Path -LiteralPath $path)) {
        return [ordered]@{ schema_version = 2; workspace_id = $WorkspaceId; updated_at = (Get-Date).ToString('o'); phases = [ordered]@{} }
    }
    return Read-JsonYaml -Path $path
}

function Save-InstallState {
    param(
        [Parameter(Mandatory = $true)][string]$WorkspaceId,
        [Parameter(Mandatory = $true)]$State,
        [string]$RuntimeLocalHome = ''
    )
    $path = Get-InstallStatePath -WorkspaceId $WorkspaceId -RuntimeLocalHome $RuntimeLocalHome
    $State.updated_at = (Get-Date).ToString('o')
    Write-JsonYaml -Path $path -Payload $State
    return $path
}

function Set-InstallStatePhase {
    param(
        [Parameter(Mandatory = $true)][string]$WorkspaceId,
        [Parameter(Mandatory = $true)][string]$Phase,
        [Parameter(Mandatory = $true)][string]$Status,
        [string]$RuntimeLocalHome = '',
        [string]$Message = '',
        [hashtable]$Details = @{}
    )
    $state = Load-InstallState -WorkspaceId $WorkspaceId -RuntimeLocalHome $RuntimeLocalHome
    if (-not $state.phases) { $state | Add-Member -NotePropertyName phases -NotePropertyValue ([ordered]@{}) -Force }
    $state.phases.$Phase = [ordered]@{ status = $Status; message = $Message; details = $Details; updated_at = (Get-Date).ToString('o') }
    Save-InstallState -WorkspaceId $WorkspaceId -State $state -RuntimeLocalHome $RuntimeLocalHome | Out-Null
}
