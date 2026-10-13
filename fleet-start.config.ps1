# Per-repo fleet start config for lewm-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'lewm-mcp'
    BackendPort  = 10927
    FrontendPort = 10928
    HealthPath   = '/api/health'
    WebRoot      = 'webapp'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'lewm_mcp.server:app'
        SyncExtras    = @('dev')
        SyncOnStart  = $true
        Env           = @{ WEB_PORT = '10927' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
