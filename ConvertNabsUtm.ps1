# Simple script to convert all of the present UTM coordinates in the NABS data
# to decimal degrees.
#
# Author: Adam Thompson <adam@adamthompsonphoto.com>
# Website: https://blog.adamthompsonphoto.com
# Copyright: 2025, Adam Thompson. All Rights Reserved.

# Set our working directory to the NABS directory
Set-Location ..\NABS

# Iterate over all of the sub-directories in the NABS directory
Get-ChildItem -Directory | ForEach-Object {
    $state = $_.Name
    $inputFile = ".\$state\raw.csv"
    $outputFile = ".\$state\converted.csv"

    Write-Host "Processing $state..."
    python ..\Arch-Tools\ProcessNabsUtm.py --input $inputFile --output $outputFile
}