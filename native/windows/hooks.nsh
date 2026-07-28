!macro KillFleetProcesses
  DetailPrint "Stopping lewm MCP processes..."
  ExecWait 'taskkill /F /IM lewm-mcp-backend.exe /T' $0
  ExecWait 'taskkill /F /IM lewm-mcp-native.exe /T' $0
  !if "${INSTALLMODE}" == "currentUser"
    nsis_tauri_utils::KillProcessCurrentUser "lewm-mcp-backend.exe"
    Pop $0
    nsis_tauri_utils::KillProcessCurrentUser "lewm-mcp-native.exe"
    Pop $0
  !else
    nsis_tauri_utils::KillProcess "lewm-mcp-backend.exe"
    Pop $0
    nsis_tauri_utils::KillProcess "lewm-mcp-native.exe"
    Pop $0
  !endif
  Sleep 3000
!macroend

!macro NSIS_HOOK_PREINSTALL
  !insertmacro KillFleetProcesses
!macroend

!macro NSIS_HOOK_PREUNINSTALL
  !insertmacro KillFleetProcesses
!macroend
