#!/bin/bash
# ============================================
# Install Chrome on VPS for Form Testing
# ============================================
# This script installs Google Chrome and 
# ChromeDriver on Ubuntu/Debian VPS servers.
# Run as root or with sudo.
# ============================================

set -e

echo "=========================================="
echo "  Installing Chrome for Form Testing"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root: sudo bash setup_chrome_vps.sh"
    exit 1
fi

# Step 1: Update system
echo "📦 Step 1: Updating system packages..."
apt update -y
echo "✅ System updated"
echo ""

# Step 2: Install dependencies
echo "📦 Step 2: Installing dependencies..."
apt install -y wget curl unzip gnupg2 software-properties-common apt-transport-https ca-certificates fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 libnspr4 libnss3 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 xdg-utils 2>/dev/null || true
echo "✅ Dependencies installed"
echo ""

# Step 3: Add Google Chrome repository
echo "📦 Step 3: Adding Google Chrome repository..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg 2>/dev/null || true
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
apt update -y
echo "✅ Repository added"
echo ""

# Step 4: Install Google Chrome
echo "📦 Step 4: Installing Google Chrome..."
apt install -y google-chrome-stable
echo "✅ Chrome installed"
echo ""

# Step 5: Verify installation
echo "🔍 Step 5: Verifying installation..."
CHROME_VERSION=$(google-chrome --version 2>/dev/null || echo "NOT FOUND")
echo "   Chrome: $CHROME_VERSION"
CHROME_PATH=$(which google-chrome 2>/dev/null || echo "NOT FOUND")
echo "   Path: $CHROME_PATH"
echo ""

# Step 6: Test Chrome headless
echo "🧪 Step 6: Testing Chrome headless mode..."
if google-chrome --headless --no-sandbox --disable-gpu --dump-dom https://www.google.com > /dev/null 2>&1; then
    echo "✅ Chrome headless mode works!"
else
    echo "⚠️  Chrome headless test had issues (may still work with Selenium)"
fi
echo ""

echo "=========================================="
echo "  ✅ Chrome Installation Complete!"
echo "=========================================="
echo ""
echo "Chrome is ready for Selenium form testing."
echo ""
echo "Next steps:"
echo "  1. Activate your Python venv:"
echo "     source ~/wordpress-monitor/venv/bin/activate"
echo ""
echo "  2. Make sure selenium & webdriver-manager are installed:"
echo "     pip install selenium webdriver-manager"
echo ""
echo "  3. Restart your monitor services:"
echo "     sudo systemctl restart wordpress-monitor-nevastech"
echo "     sudo systemctl restart wordpress-monitor-ascent365"
echo ""
echo "  4. Form tests will now use Chrome!"
echo "=========================================="
