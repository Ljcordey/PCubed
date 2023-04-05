$folderPath = Split-Path $MyInvocation.MyCommand.Path
$filter = "*.pdf"

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $folderPath
$watcher.Filter = $filter
$watcher.IncludeSubdirectories = $false
$watcher.EnableRaisingEvents = $true

$action = {
    Write-Host "Hello, world!"
}

$onCreated = Register-ObjectEvent $watcher "Created" -Action $action

# Uncomment the next line to stop the watcher
#$watcher.Dispose()