# Super simple script to convert the GPX data downloaded from the WAD to CSV
# files for further processing. Requires my GPS-Tools package (https://github.com/serialphotog/GPS-Tools)
#
# Author: Adam Thompson <adam@adamthompsonphoto.com>
# Website: https://blog.adamthompsonphoto.com
# Copyright: 2025, Adam Thompson. All Rights Reserved.

# Set our working directory to the WAD directory
Set-Location ..\WAD

# Iterate over all of the sub-directories in the WAD directory
Get-ChildItem -Directory | ForEach-Object {
    $state = $_.Name
    $inputFile = ".\$state\ArchGeoMap.gpx"
    $outputFile = ".\$state\Processed.csv"

    # Delete the output file if it already exists
    if (Test-Path $outputFile) {
        Write-Host "Removing $outputFile as it already exists"
        Remove-Item $outputFile -Force
    }

    Write-Host "Processing $state..."
    python ..\GPS-Tools\gpx2csv -i $inputFile -o $outputFile
}