' =====================================================
' 合并脚本：Config.vbs + License.vbs
' 功能：
'   1. 显示授权信息（5秒自动关闭）
'   2. 创建符号链接 %USERPROFILE%\AppData\Local\Fork\gitInstance
'      指向当前目录下的 gitInstance 文件夹
'   3. 拷贝当前目录下的 settings.json 到 %USERPROFILE%\AppData\Local\Fork\
'   4. 拷贝当前目录下 LicenseData 文件夹中的所有文件到 %ProgramData%\Fork\
' 输出：控制台（使用 cscript 运行）
' 注意：创建符号链接需要管理员权限
' =====================================================

Option Explicit

' 如果未使用 cscript 运行，则自动以 cscript 重新启动
If InStr(1, WScript.FullName, "cscript.exe", vbTextCompare) = 0 Then
    Dim shellRestart
    Set shellRestart = CreateObject("WScript.Shell")
    shellRestart.Run "cscript.exe //nologo """ & WScript.ScriptFullName & """", 1, False
    Set shellRestart = Nothing
    WScript.Quit 0
End If

' 显示授权信息（5秒后自动关闭）
Dim popupShell
Set popupShell = CreateObject("WScript.Shell")
popupShell.Popup "Licensed to Lu Hao, 2026", 5, "Licensing Information", 64
Set popupShell = Nothing

' 创建全局对象
Dim fso, wshShell
Set fso = CreateObject("Scripting.FileSystemObject")
Set wshShell = CreateObject("WScript.Shell")

' 获取当前脚本所在目录
Dim scriptDir
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)


' ========== 第一部分：创建符号链接 & 拷贝 settings.json ==========
WScript.Echo "----------------------------------------------------------"
WScript.Echo "  Creating symbol link and copying settings.json ..."
WScript.Echo "----------------------------------------------------------"

Dim userProfile, targetLink, gitInstancePath, forkDir
Dim linkCreated, settingsFile, targetSettingsPath, copySettingsSuccess

gitInstancePath = fso.BuildPath(scriptDir, "gitInstance")
If Not fso.FolderExists(gitInstancePath) Then
    WScript.Echo "  Error: Source directory does not exist - " & gitInstancePath
    linkCreated = False
Else
    userProfile = wshShell.ExpandEnvironmentStrings("%USERPROFILE%")
    targetLink = fso.BuildPath(userProfile, "AppData\Local\Fork\gitInstance")
    forkDir = fso.GetParentFolderName(targetLink)
    
    If fso.FileExists(targetLink) Or fso.FolderExists(targetLink) Then
        WScript.Echo "  The symbol link exist, deleting..."
        On Error Resume Next
        wshShell.Run "cmd /c rmdir """ & targetLink & """", 0, True
        If fso.FileExists(targetLink) Then
            wshShell.Run "cmd /c del /f /q """ & targetLink & """", 0, True
        End If
        On Error Goto 0
    End If
    
    If Not fso.FolderExists(forkDir) Then
        fso.CreateFolder forkDir
        WScript.Echo " Creating directory: " & forkDir
    End If
    
    Dim cmd
    cmd = "cmd /c mklink /D """ & targetLink & """ """ & gitInstancePath & """"
    WScript.Echo "  " & cmd
    wshShell.Run cmd, 0, True
    
    linkCreated = fso.FolderExists(targetLink)
    If linkCreated Then
        WScript.Echo "  Symbol link created successfully: " & vbCrLf & "    " & targetLink & " -> " & gitInstancePath
    Else
        WScript.Echo "  Symbol link creating failed, maybe administrators privilege needed."
    End If
End If

settingsFile = fso.BuildPath(scriptDir, "settings.json")
targetSettingsPath = fso.BuildPath(forkDir, "settings.json")
copySettingsSuccess = False

If fso.FileExists(settingsFile) Then
    On Error Resume Next
    fso.CopyFile settingsFile, targetSettingsPath, True
    If Err.Number = 0 Then
        copySettingsSuccess = True
        WScript.Echo "  settings.json copied successfully: " & vbCrLf & "    " & targetSettingsPath
    Else
        WScript.Echo "  settings.json copying failed: " & Err.Description
    End If
    On Error Goto 0
Else
    WScript.Echo "  settings.json not found, skipping copying. It should be at：" & settingsFile
End If

' ========== 第二部分：拷贝 LicenseData 文件夹内容 ==========
WScript.Echo vbCrLf & "----------------------------------------------------------"
WScript.Echo "  Copying LicenseData files..."
WScript.Echo "----------------------------------------------------------"

Dim sourceFolder, programData, targetPath, fileCollection, file
Dim successCount, failCount

sourceFolder = fso.BuildPath(scriptDir, "LicenseData")
If Not fso.FolderExists(sourceFolder) Then
    WScript.Echo "  Error: source directory not found - " & sourceFolder
    successCount = 0
    failCount = 0
Else
    programData = wshShell.ExpandEnvironmentStrings("%ProgramData%")
    targetPath = fso.BuildPath(programData, "Fork")
    
    If Not fso.FolderExists(targetPath) Then
        On Error Resume Next
        fso.CreateFolder targetPath
        If Err.Number <> 0 Then
            WScript.Echo "  The directory can't be created：" & targetPath & ", run it with Administrators user."
            WScript.Quit 2
        End If
        On Error Goto 0
        WScript.Echo "  Creating directory: " & targetPath
    End If
    
    successCount = 0
    failCount = 0
    Set fileCollection = fso.GetFolder(sourceFolder).Files
    For Each file In fileCollection
        On Error Resume Next
        fso.CopyFile file.Path, targetPath & "\", True
        If Err.Number = 0 Then
            successCount = successCount + 1
            WScript.Echo "    Copyied: " & file.Name
        Else
            failCount = failCount + 1
            WScript.Echo "    Copying failed: " & file.Name & " - " & Err.Description
        End If
        On Error Goto 0
    Next
    Set fileCollection = Nothing
End If

' ========== 输出最终汇总 ==========
WScript.Echo vbCrLf & "------------------------ Summary -------------------------"
WScript.Echo "  Creating Symbol link: " & IIf(linkCreated, "Successful", "Failed")
WScript.Echo "  Copying settings.json: " & IIf(copySettingsSuccess, "Successful", "Failed or skipped")
WScript.Echo "  Copying LicenseData: " & successCount & " files Successful, " & failCount & " files failed"
WScript.Echo "----------------------------------------------------------"
WScript.Echo vbCrLf

' 倒计时提醒 10 秒（同一行刷新）
Dim i
For i = 30 To 1 Step -1
    WScript.StdOut.Write Chr(13) & "The window will be closed after " & i & " seconds..."
    WScript.Sleep 1000
Next
WScript.StdOut.WriteLine ""  ' 换行，避免最后一行覆盖提示

Set fso = Nothing
Set wshShell = Nothing

If linkCreated And copySettingsSuccess And failCount = 0 Then
    WScript.Quit 0
Else
    WScript.Quit 1
End If

Function IIf(condition, truePart, falsePart)
    If condition Then IIf = truePart Else IIf = falsePart
End Function
