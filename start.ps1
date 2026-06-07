Param(
    [switch]$Headless,
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$NoBrowser
)
$ErrorActionPreference = "Stop"
$WebappStart = Join-Path $PSScriptRoot "webapp\start.ps1"
if ($FrontendOnly) {
    Set-Location (Join-Path $PSScriptRoot "webapp")
    npm run dev
    exit
}
& $WebappStart `
    -Headless:$Headless `
    -BackendOnly:$BackendOnly `
    -FrontendOnly:$FrontendOnly `
    -NoBrowser:$NoBrowser
