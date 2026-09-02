#!/bin/bash

echo "========================================"
echo " ENHANCED SCRAPER LAUNCHER - LINUX/MAC"
echo "========================================"
echo
echo "This will launch 6 individual scrapers + 1 monitor"
echo "Each scraper runs in its own terminal tab/window"
echo
echo "Scrapers will run until ALL products are collected"
echo "Target: 100,000+ products across all platforms"
echo
echo "Press Enter to continue or Ctrl+C to cancel..."
read -r

echo
echo "🚀 Starting all enhanced scrapers..."
echo

# Function to launch in new terminal based on system
launch_scraper() {
    local name="$1"
    local script="$2"
    local title="$3"
    
    echo "⚡ Launching $name scraper..."
    
    # Try different terminal emulators
    if command -v gnome-terminal >/dev/null 2>&1; then
        gnome-terminal --tab --title="$title" -- bash -c "python3 $script; echo 'Scraper finished. Press Enter to close...'; read"
    elif command -v xterm >/dev/null 2>&1; then
        xterm -T "$title" -e "python3 $script; echo 'Scraper finished. Press Enter to close...'; read" &
    elif command -v konsole >/dev/null 2>&1; then
        konsole --new-tab -p tabtitle="$title" -e bash -c "python3 $script; echo 'Scraper finished. Press Enter to close...'; read" &
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        osascript -e "tell application \"Terminal\" to do script \"cd $(pwd) && python3 $script\""
    else
        # Fallback: run in background with nohup
        echo "   Running $name in background (no GUI terminal found)..."
        nohup python3 "$script" > "${name}_scraper.log" 2>&1 &
    fi
    
    sleep 2
}

# Launch each scraper
launch_scraper "Jeevee" "enhanced_jeevee_scraper.py" "JEEVEE SCRAPER"
launch_scraper "CGDigital" "enhanced_cgdigital_scraper.py" "CGDIGITAL SCRAPER"
launch_scraper "Hukut" "enhanced_hukut_scraper.py" "HUKUT SCRAPER"
launch_scraper "Oliz" "enhanced_oliz_scraper.py" "OLIZ SCRAPER"
launch_scraper "Better" "enhanced_better_scraper.py" "BETTER SCRAPER"
launch_scraper "HardwarePasal" "enhanced_hardwarepasal_scraper.py" "HARDWAREPASAL SCRAPER"

echo "⚡ Launching Progress Monitor..."
if command -v gnome-terminal >/dev/null 2>&1; then
    gnome-terminal --tab --title="SCRAPER MONITOR" -- bash -c "python3 scraper_monitor.py; echo 'Monitor finished. Press Enter to close...'; read"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    osascript -e "tell application \"Terminal\" to do script \"cd $(pwd) && python3 scraper_monitor.py\""
else
    echo "   Monitor running in background..."
    nohup python3 scraper_monitor.py > monitor.log 2>&1 &
fi

echo
echo "✅ All scrapers launched successfully!"
echo
echo "📊 Monitor: Real-time progress tracking"
echo "🔄 Scrapers: Individual platform scrapers"
echo
echo "💡 INSTRUCTIONS:"
echo "  • Each scraper runs independently until completion"
echo "  • Monitor shows live progress every 30 seconds"
echo "  • Close individual terminals to stop scrapers"
echo "  • Run enhanced_master_consolidator.py to merge databases"
echo
echo "⚠️  IMPORTANT:"
echo "  • Scrapers handle rate limiting automatically"
echo "  • Expected runtime: 2-8 hours depending on network"
echo "  • Check individual logs if running in background"
echo
echo "Press Enter to exit launcher (scrapers will continue)..."
read -r

echo "👋 Launcher finished. Scrapers are running independently."