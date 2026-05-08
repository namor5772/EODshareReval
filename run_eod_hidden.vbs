' run_eod_hidden.vbs
' ----------------------------------------------------------------------------
' Silent launcher for the Desktop shortcut.
'
' Spawns run_eod_downloader_and_report.bat with NO visible console window,
' returns immediately, and lets the batch run hidden until it shells out to
' Notepad++ (which is a separate GUI process and therefore appears normally).
'
' WshShell.Run(command, intWindowStyle, bWaitOnReturn)
'   intWindowStyle = 0  -> hidden
'   bWaitOnReturn  = False -> fire-and-forget; this script exits at once
'
' Caveat: if the batch ever hits its `pause` lines on error, the hidden
' cmd.exe will sit invisibly until killed via Task Manager. Run the .bat
' directly to debug failures.
' ----------------------------------------------------------------------------

Option Explicit

Dim fso, sh, scriptDir, batPath
Set fso = CreateObject("Scripting.FileSystemObject")
Set sh  = CreateObject("WScript.Shell")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
batPath   = scriptDir & "\run_eod_downloader_and_report.bat"

sh.CurrentDirectory = scriptDir
sh.Run """" & batPath & """", 0, False
