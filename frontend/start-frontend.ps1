# PowerShell script to start React frontend
Set-Location "C:\Users\ASUS\captry\attandance\automated-attendance-system\frontend"
Write-Host "Current directory: $(Get-Location)"
Write-Host "Package.json exists: $(Test-Path 'package.json')"
Write-Host "Starting React development server..."
npm start