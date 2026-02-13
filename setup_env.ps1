# WordPress Monitor - Environment Setup Script (PowerShell)
# This script helps you configure environment variables for the scheduler

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "WordPress Monitor - SMTP Setup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (Test-Path ".env") {
    Write-Host "Found existing .env file" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to update it? (y/n)"
    if ($overwrite -ne "y") {
        Write-Host "Setup cancelled" -ForegroundColor Red
        exit
    }
}

# Gmail App Password instructions
Write-Host ""
Write-Host "GMAIL APP PASSWORD SETUP:" -ForegroundColor Green
Write-Host "1. Go to: https://myaccount.google.com/apppasswords" -ForegroundColor White
Write-Host "2. Sign in to your Google account" -ForegroundColor White
Write-Host "3. Select 'Mail' and your device" -ForegroundColor White
Write-Host "4. Click 'Generate'" -ForegroundColor White
Write-Host "5. Copy the 16-character password (no spaces)" -ForegroundColor White
Write-Host ""

# Get SMTP credentials
$smtpUsername = Read-Host "Enter your Gmail address (e.g., yourname@gmail.com)"
$smtpPassword = Read-Host "Enter your Gmail App Password (16 characters, no spaces)" -AsSecureString
$smtpPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($smtpPassword)
)

# Create .env file
$envContent = @"
# WordPress Monitor Environment Variables
# Generated on $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

# SMTP Email Configuration
SMTP_USERNAME=$smtpUsername
SMTP_PASSWORD=$smtpPasswordPlain

# Dashboard secret key (auto-generated)
DASHBOARD_SECRET_KEY=$(([char[]]([char]'a'..[char]'z') + ([char[]]([char]'A'..[char]'Z')) + 0..9 | Get-Random -Count 32) -join '')

# Optional configurations (uncomment and fill if needed)
# PAGESPEED_API_KEY=
# SLACK_WEBHOOK_URL=
# DISCORD_WEBHOOK_URL=
# WP_MONITOR_PASSWORD=
# DB_USERNAME=
# DB_PASSWORD=
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8

Write-Host ""
Write-Host "✓ .env file created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Update config/config.yaml with recipient email addresses" -ForegroundColor White
Write-Host "2. Run the test script: python test_email.py" -ForegroundColor White
Write-Host "3. Start the scheduler: python scheduler.py" -ForegroundColor White
Write-Host ""
Write-Host "IMPORTANT: Never commit the .env file to version control!" -ForegroundColor Red
Write-Host ""
