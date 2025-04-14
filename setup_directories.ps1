# PowerShell Script to set up required directories for Online Exam Proctor System

Write-Host "Setting up required directories for Online Exam Proctor System..." -ForegroundColor Green

# Create utils directory if it doesn't exist
if (-not (Test-Path "utils")) {
    Write-Host "Creating utils directory..." -ForegroundColor Cyan
    New-Item -Path "utils" -ItemType Directory | Out-Null
    
    # Create coco.txt with required classes
    Write-Host "Creating coco.txt file with required classes..." -ForegroundColor Cyan
    @"
person
laptop
cell phone
remote
keyboard
mouse
book
"@ | Out-File -FilePath "utils\coco.txt" -Encoding utf8
}

# Create output directories in static folder
if (-not (Test-Path "static")) {
    Write-Host "Creating static directory..." -ForegroundColor Cyan
    New-Item -Path "static" -ItemType Directory | Out-Null
}

# Create output folders
$outputFolders = @("OutputVideos", "OuputAudios", "Profiles")
foreach ($folder in $outputFolders) {
    $path = "static\$folder"
    if (-not (Test-Path $path)) {
        Write-Host "Creating $path directory..." -ForegroundColor Cyan
        New-Item -Path $path -ItemType Directory | Out-Null
    }
}

# Initialize violation.json if it doesn't exist
if (-not (Test-Path "violation.json")) {
    Write-Host "Creating violation.json file..." -ForegroundColor Cyan
    @"
[]
"@ | Out-File -FilePath "violation.json" -Encoding utf8
}

# Initialize result.json if it doesn't exist
if (-not (Test-Path "result.json")) {
    Write-Host "Creating result.json file..." -ForegroundColor Cyan
    @"
[]
"@ | Out-File -FilePath "result.json" -Encoding utf8
}

Write-Host "Setup completed successfully!" -ForegroundColor Green 