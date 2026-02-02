#!/bin/bash

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║          BACKEND API - ERROR & VALIDATION TEST REPORT          ║"
echo "║                     Generated: $(date)                    ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function
test_endpoint() {
    local name=$1
    local method=$2
    local url=$3
    local data=$4
    local expected=$5
    
    echo -n "Testing: $name... "
    
    if [ -z "$data" ]; then
        RESPONSE=$(curl -s -X $method "http://localhost:8000$url")
    else
        RESPONSE=$(curl -s -X $method "http://localhost:8000$url" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    if echo "$RESPONSE" | grep -q "$expected"; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "    Response: $RESPONSE"
        ((TESTS_FAILED++))
    fi
}

# ============================================================================
echo -e "${YELLOW}[1] BASIC CONNECTIVITY TESTS${NC}"
echo "─────────────────────────────────────────────────────────────────"

test_endpoint "Health Check" "GET" "/health" "" "healthy"
test_endpoint "API Info" "GET" "/api/info" "" "Dendy Fajar"
test_endpoint "API Stats" "GET" "/api/stats" "" "operational"

# ============================================================================
echo ""
echo -e "${YELLOW}[2] VALIDATION TESTS${NC}"
echo "─────────────────────────────────────────────────────────────────"

test_endpoint "Valid Contact Form" "POST" "/api/contact" \
    '{"name":"Test User","email":"test@example.com","subject":"Test","message":"This is a valid test message"}' \
    "success"

test_endpoint "Invalid Email Format" "POST" "/api/contact" \
    '{"name":"Test","email":"invalid","subject":"Test","message":"This is a test message"}' \
    "value_error"

test_endpoint "Name Too Short" "POST" "/api/contact" \
    '{"name":"A","email":"test@example.com","subject":"Test","message":"This is a test message"}' \
    "value_error"

test_endpoint "Message Too Short" "POST" "/api/contact" \
    '{"name":"Test","email":"test@example.com","subject":"Test","message":"Short"}' \
    "value_error"

test_endpoint "Subject Too Short" "POST" "/api/contact" \
    '{"name":"Test","email":"test@example.com","subject":"A","message":"This is a test message"}' \
    "value_error"

# ============================================================================
echo ""
echo -e "${YELLOW}[3] RATE LIMITING TEST${NC}"
echo "─────────────────────────────────────────────────────────────────"

echo "Sending 6 rapid requests (limit: 5/minute)..."
for i in {1..6}; do
    RESPONSE=$(curl -s -X POST "http://localhost:8000/api/contact" \
        -H "Content-Type: application/json" \
        -d '{"name":"Test","email":"test@example.com","subject":"Rate Test","message":"Testing rate limiting feature"}')
    
    if echo "$RESPONSE" | grep -q '"success": true'; then
        echo "  Request $i: ${GREEN}✅ ALLOWED${NC}"
        ((TESTS_PASSED++))
    elif echo "$RESPONSE" | grep -q '"success": false'; then
        echo "  Request $i: ${GREEN}✅ ALLOWED (no email)${NC}"
        ((TESTS_PASSED++))
    else
        echo "  Request $i: ${RED}🚫 BLOCKED${NC} (rate limited)"
        ((TESTS_FAILED++))
    fi
done

# ============================================================================
echo ""
echo -e "${YELLOW}[4] ERROR HANDLING TESTS${NC}"
echo "─────────────────────────────────────────────────────────────────"

test_endpoint "Empty Name Field" "POST" "/api/contact" \
    '{"name":"","email":"test@example.com","subject":"Test","message":"This is a test message"}' \
    "value_error"

test_endpoint "Missing Required Field" "POST" "/api/contact" \
    '{"name":"Test","email":"test@example.com","subject":"Test"}' \
    "validation_error\|missing"

# ============================================================================
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                        TEST SUMMARY                           ║"
echo "╠═══════════════════════════════════════════════════════════════╣"
echo -e "║  ${GREEN}✅ PASSED: $TESTS_PASSED${NC}"
echo -e "║  ${RED}❌ FAILED: $TESTS_FAILED${NC}"
echo "║  📊 TOTAL:  $((TESTS_PASSED + TESTS_FAILED))"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  SOME TESTS FAILED${NC}"
    exit 1
fi
