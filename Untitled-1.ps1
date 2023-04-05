$folderPath = "C:\Users\loco2\OneDrive - EY\Documents\python projects\testfolder"
$pythonScriptPath = "C:\Users\loco2\OneDrive - EY\Documents\python projects\testfolder\test2.py"

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $folderPath
$watcher.IncludeSubdirectories = $false
$watcher.EnableRaisingEvents = $true

$onCreated = Register-ObjectEvent $watcher "Created" -Action {
    $pdfFilePath = $Event.SourceEventArgs.FullPath
    $extension = [System.IO.Path]::GetExtension($pdfFilePath)
    
    if ($extension -eq ".pdf") {
        & python $pythonScriptPath $pdfFilePath
    }
}

#Uncomment the next line to stop the watcher
#$watcher.Dispose()
