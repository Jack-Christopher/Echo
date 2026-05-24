' Hidden logon launcher for Task Scheduler (no visible console).
Option Explicit

Dim shell, fso, root, pythonw, logDir, logFile, cmd

Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(WScript.ScriptFullName)

WScript.Sleep 20000

logDir = shell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Echo\logs"
If Not fso.FolderExists(logDir) Then
    fso.CreateFolder logDir
End If
logFile = logDir & "\startup-last.log"

pythonw = root & "\.venv\Scripts\pythonw.exe"
If Not fso.FileExists(pythonw) Then
    pythonw = root & "\.venv\Scripts\python.exe"
    If Not fso.FileExists(pythonw) Then
        pythonw = "pythonw"
    End If
End If

cmd = "cmd /c set PYTHONIOENCODING=utf-8&& cd /d """ & root & """ && """ & pythonw & """ -m echo.main >> """ & logFile & """ 2>&1"
shell.Run cmd, 0, False
