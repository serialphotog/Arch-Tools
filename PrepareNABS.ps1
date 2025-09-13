# Simple script to prepare my downloads of raw NABS arch data for further 
# processing.
#
# Author: Adam Thompson <adam@adamthompsonphoto.com>
# Website: https://blog.adamthompsonphoto.com
# Copyright: 2025, Adam Thompson. All Rights Reserved.

# Set our working directory to the NABS directory
Set-Location ..\NABS

# Process each CSV file in the folder
Get-ChildItem -Filter "*.csv" | ForEach-Object {
    # Get the state code (The CSV filename minus the extension)
    $state = $_.BaseName

    # Build the target directory name (just the state code)
    $targetDir = Join-Path $PWD $state

    # Create the state directory if it doesn't exist
    if (-not (Test-Path $targetDir)) {
        New-Item -ItemType Directory -Path $targetDir | Out-Null
    }

    # Build the target path with the new filename ("raw.csv")
    $targetFile = Join-Path $targetDir "raw.csv"

    # Move and rename the file
    Move-Item -Path $_.FullName -Destination $targetFile -Force

    Write-Host "Moved $($_.Name) to $targetFile"
}