# This script uses `csvDuplicateFinder.py` to locate likely duplicate arches
# in the processed NABS data by looking for arches that have identical latitude
# and longitude values.
#
# Author: Adam Thompson <adam@adamthompsonphoto.com>
# Website: https://blog.adamthompsonphoto.com
# Copyright: 2025, Adam Thompson. All Rights Reserved.

# Set our working directory to the NABS directory
Set-Location ..\NABS

# Iterate over all of the sub-directories in the NABS directory
Get-ChildItem -Directory | ForEach-Object {
    $state = $_.Name
    $inputFile = ".\$state\converted.csv"
    $outputFile = ".\$state\duplicates.csv"

    # Delete the output file if it already exists
    if (Test-Path $outputFile) {
        Write-Host "Removing $outputFile as it already exists"
        Remove-Item $outputFile -Force
    }

    Write-Host "Looking for duplicates in $state..."
    python ..\Arch-Tools\csvDuplicateFinder.py -i $inputFile -o $outputFile --latitude Latitude --longitude Longitude
}