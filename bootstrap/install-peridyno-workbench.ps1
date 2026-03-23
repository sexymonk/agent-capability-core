[CmdletBinding()]
param(
    [string]$WorkspaceBase = "",
    [string]$AuxRoot = "",
    [string]$WorkbenchRepoUrl = "https://github.com/sexymonk/peridyno-agent-workbench.git",
    [ValidateSet('auto', 'strict', 'non_intrusive', 'repair')]
    [string]$RestoreMode = 'auto',
    [string]$AIProvider = 'auto',
    [ValidateSet('auto', 'direct', 'proxy', 'mirror')]
    [string]$NetworkProfile = 'auto',
    [switch]$AllowCompatibleToolchains,
    [switch]$PullDependencies,
    [switch]$CheckCudaDocs,
    [switch]$NoInstallToolchains,
    [switch]$NoAdmin,
    [string]$OfflineCacheRoot = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$coreRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
. (Join-Path $coreRoot 'scripts\lib\workspace-bootstrap.ps1')

$workspaceBaseResolved = Get-DefaultWorkspaceBase -RequestedPath $WorkspaceBase
$auxBaseResolved = Get-DefaultAuxBase -RequestedPath $AuxRoot
$allowInstall = -not $NoInstallToolchains
$networkConfig = Resolve-NetworkConfig -RequestedProfile $NetworkProfile -ManifestNetworkProfiles (Get-WorkspaceManifestData -WorkspaceRoot $coreRoot).network_profiles
Ensure-BasicBootstrapTools -AllowInstall:$allowInstall -NetworkConfig $networkConfig -NoAdmin:$NoAdmin

$workbenchRepoSpec = [pscustomobject]@{
    repo_id = 'peridyno-agent-workbench'
    clone_url = $WorkbenchRepoUrl
    visibility = 'private'
    auth_mode = 'gh-cli-https'
}
$workbenchRoot = Join-Path $workspaceBaseResolved 'peridyno-agent-workbench'
Ensure-RepositoryCheckout -RepoSpec $workbenchRepoSpec -DestinationPath $workbenchRoot -PullLatest:$PullDependencies -SkipCheckout:($RestoreMode -eq 'repair')

$bootstrapScript = Join-Path $workbenchRoot 'bootstrap-workbench.ps1'
if (-not (Test-Path $bootstrapScript)) { throw "Workbench bootstrap script not found: $bootstrapScript" }

& $bootstrapScript `
    -WorkspaceRoot $workbenchRoot `
    -WorkspaceBase $workspaceBaseResolved `
    -AuxRoot $auxBaseResolved `
    -RestoreMode $RestoreMode `
    -AIProvider $AIProvider `
    -NetworkProfile $NetworkProfile `
    -AllowCompatibleToolchains:$AllowCompatibleToolchains `
    -PullDependencies:$PullDependencies `
    -CheckCudaDocs:$CheckCudaDocs `
    -NoInstallToolchains:$NoInstallToolchains `
    -NoAdmin:$NoAdmin `
    -OfflineCacheRoot $OfflineCacheRoot | Out-Host
if ($LASTEXITCODE -ne 0) { throw "Workbench bootstrap failed with exit code $LASTEXITCODE" }
