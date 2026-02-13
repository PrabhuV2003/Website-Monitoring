# Quick Email Setup Script for WordPress Monitor
# This script helps you configure SMTP credentials for automated email delivery

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  WordPress Monitor - Email Configuration Setup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check current configuration
Write-Host "Checking current email configuration..." -ForegroundColor Yellow
Write-Host ""

$currentUsername = $env:SMTP_USERNAME
$currentPassword = $env:SMTP_PASSWORD

if ($currentUsername) {
    Write-Host "  SMTP_USERNAME: " -NoNewline
    Write-Host "SET ($currentUsername)" -ForegroundColor Green
} else {
    Write-Host "  SMTP_USERNAME: " -NoNewline
    Write-Host "NOT SET" -ForegroundColor Red
}

if ($currentPassword) {
    Write-Host "  SMTP_PASSWORD: " -NoNewline
    Write-Host "SET (hidden)" -ForegroundColor Green
} else {
    Write-Host "  SMTP_PASSWORD: " -NoNewline
    Write-Host "NOT SET" -ForegroundColor Red
}

Write-Host ""
Write-Host "------------------------------------------------------------" -ForegroundColor Cyan

# Ask if user wants to configure
Write-Host ""
$configure = Read-Host "Do you want to configure SMTP credentials? (yes/no)"

if ($configure -notmatch '^y(es)?$') {
    Write-Host ""
    Write-Host "Setup cancelled." -ForegroundColor Yellow
    Write-Host ""
    exit
}

# Get SMTP username (email)
Write-Host ""
Write-Host "------------------------------------------------------------" -ForegroundColor Cyan
Write-Host "STEP 1: SMTP Username (Your Email Address)" -ForegroundColor Green
Write-Host "------------------------------------------------------------" -ForegroundColor Cyan
Write-Host ""
Write-Host "Enter your email address (e.g., monitor@gmail.com):"
if ($currentUsername) {
    Write-Host "Current: $currentUsername" -ForegroundColor DarkGray
    Write-Host "Press Enter to keep current value, or type new value:"
}

$username = Read-Host "Email"

if ([string]::IsNullOrWhiteSpace($username)) {
    if ($currentUsername) {
        $username = $currentUsername
        Write-Host "Keeping current value: $username" -ForegroundColor Yellow
    } else {
        Write-Host "Error: Email address is required!" -ForegroundColor Red
        exit 1
    }
}

# Get SMTP password
Write-Host ""
Write-Host "------------------------------------------------------------" -ForegroundColor Cyan
Write-Host "STEP 2: SMTP Password" -ForegroundColor Green
Write-Host "------------------------------------------------------------" -ForegroundColor Cyan
Write-Host ""
Write-Host "For Gmail users: Use an App Password, NOT your regular password!" -ForegroundColor Yellow
Write-Host ""
Write-Host "How to get Gmail App Password:" -ForegroundColor Cyan
Write-Host "  1. Go to: https://myaccount.google.com/security" -ForegroundColor Gray
Write-Host "  2. Enable 2-Step Verification" -ForegroundColor Gray
Write-Host "  3. Go to: App passwords" -ForegroundColor Gray
Write-Host "  4. Select 'Mail' and generate password" -ForegroundColor Gray
Write-Host "  5. Copy the 16-character password" -ForegroundColor Gray
Write-Host ""
Write-Host "Enter your SMTP password (or App Password for Gmail):"

$password = Read-Host "Password" -AsSecureString
$passwordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($password)
)

if ([string]::IsNullOrWhiteSpace($passwordPlain)) {
    Write-Host "Error: Password is required!" -ForegroundColor Red
    exit 1
}

# Ask about permanence
Write-Host ""
Write-Host "------------------------------------------------------------" -ForegroundColor Cyan
Write-Host "STEP 3: Save Configuration" -ForegroundColor Green
Write-Host "------------------------------------------------------------" -ForegroundColor Cyan
Write-Host ""
Write-Host "How do you want to save these credentials?"
Write-Host ""
Write-Host "  1. Current session only (temporary)" -ForegroundColor Yellow
Write-Host "     - Available only while this PowerShell window is open"
Write-Host "     - Lost when you close PowerShell"
Write-Host ""
Write-Host "  2. Permanent for current user (recommended)" -ForegroundColor Green
Write-Host "     - Available to all PowerShell sessions"
Write-Host "     - Persists across restarts"
Write-Host "     - Stored in Windows user environment variables"
Write-Host ""

$choice = Read-Host "Enter choice (1 or 2)"

# Set environment variables based on choice
Write-Host ""
Write-Host "Setting environment variables..." -ForegroundColor Yellow

if ($choice -eq "2") {
    # Set permanently for user
    [System.Environment]::SetEnvironmentVariable('SMTP_USERNAME', $username, 'User')
    [System.Environment]::SetEnvironmentVariable('SMTP_PASSWORD', $passwordPlain, 'User')
    
    # Also set for current session
    $env:SMTP_USERNAME = $username
    $env:SMTP_PASSWORD = $passwordPlain
    
    Write-Host ""
    Write-Host "SUCCESS! Credentials saved permanently." -ForegroundColor Green
    Write-Host ""
    Write-Host "Environment variables set:" -ForegroundColor Cyan
    Write-Host "  SMTP_USERNAME = $username" -ForegroundColor Gray
    Write-Host "  SMTP_PASSWORD = ********" -ForegroundColor Gray
    Write-Host ""
    Write-Host "These will be available in all future PowerShell sessions." -ForegroundColor Yellow
} else {
    # Set only for current session
    $env:SMTP_USERNAME = $username
    $env:SMTP_PASSWORD = $passwordPlain
    
    Write-Host ""
    Write-Host "SUCCESS! Credentials set for current session." -ForegroundColor Green
    Write-Host ""
    Write-Host "Environment variables set:" -ForegroundColor Cyan
    Write-Host "  SMTP_USERNAME = $username" -ForegroundColor Gray
    Write-Host "  SMTP_PASSWORD = ********" -ForegroundColor Gray
    Write-Host ""
    Write-Host "WARNING: These will be lost when you close PowerShell!" -ForegroundColor Yellow
    Write-Host "Run this script again with option 2 to make them permanent." -ForegroundColor Yellow
}

# Verify
Write-Host ""
Write-Host "------------------------------------------------------------" -ForegroundColor Cyan
Write-Host "Verification" -ForegroundColor Green
Write-Host "------------------------------------------------------------" -ForegroundColor Cyan
Write-Host ""
Write-Host "Current environment variables:" -ForegroundColor Cyan
Write-Host "  SMTP_USERNAME = $env:SMTP_USERNAME" -ForegroundColor Gray
Write-Host "  SMTP_PASSWORD = " -NoNewline -ForegroundColor Gray
Write-Host "SET (hidden for security)" -ForegroundColor Green

# Next steps
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Update recipients in config.yaml:" -ForegroundColor Cyan
Write-Host "   alerts:" -ForegroundColor Gray
Write-Host "     email:" -ForegroundColor Gray
Write-Host "       recipients:" -ForegroundColor Gray
Write-Host "         - 'client@example.com'" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Test email delivery:" -ForegroundColor Cyan
Write-Host "   python test_email.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Start automated monitoring:" -ForegroundColor Cyan
Write-Host "   python scheduler.py" -ForegroundColor Gray
Write-Host ""
Write-Host "For detailed instructions, see: AUTOMATED_EMAIL_SETUP.md" -ForegroundColor Yellow
Write-Host ""
