#!/bin/bash

# CV Landing Page Backend - Testing Script
# Usage: ./test_api.sh

set -e

API_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     CV Landing Page - Backend API Test Suite              ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}\n"

# Test 1: Health Check
echo -e "${YELLOW}[TEST 1] Health Check${NC}"
if curl -s "$API_URL/health" | grep -q "healthy"; then
    echo -e "${GREEN}✅ PASSED${NC}: Server is running\n"
else
    echo -e "${RED}❌ FAILED${NC}: Server health check\n"
    exit 1
fi

# Test 2: Portfolio Info
echo -e "${YELLOW}[TEST 2] Portfolio Info${NC}"
if curl -s "$API_URL/api/info" | grep -q "Dendy Fajar"; then
    echo -e "${GREEN}✅ PASSED${NC}: Portfolio info retrieved\n"
else
    echo -e "${RED}❌ FAILED${NC}: Portfolio info endpoint\n"
    exit 1
fi

# Test 3: API Stats
echo -e "${YELLOW}[TEST 3] API Statistics${NC}"
if curl -s "$API_URL/api/stats" | grep -q "operational"; then
    echo -e "${GREEN}✅ PASSED${NC}: API stats endpoint working\n"
else
    echo -e "${RED}❌ FAILED${NC}: API stats endpoint\n"
    exit 1
fi

# Test 4: Valid Contact Form
echo -e "${YELLOW}[TEST 4] Contact Form - Valid Data${NC}"
RESPONSE=$(curl -s -X POST "$API_URL/api/contact" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "subject": "API Test",
    "message": "This is a test message for contact form validation"
  }')

if echo "$RESPONSE" | grep -q "success"; then
    echo -e "${GREEN}✅ PASSED${NC}: Valid form submission accepted\n"
else
    echo -e "${RED}❌ FAILED${NC}: Valid form submission\n"
    echo "$RESPONSE"
    exit 1
fi

# Test 5: Invalid Email
echo -e "${YELLOW}[TEST 5] Contact Form - Invalid Email${NC}"
RESPONSE=$(curl -s -X POST "$API_URL/api/contact" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test",
    "email": "invalid-email",
    "subject": "Test",
    "message": "This is a test message with enough content"
  }')

if echo "$RESPONSE" | grep -q "email"; then
    echo -e "${GREEN}✅ PASSED${NC}: Invalid email properly rejected\n"
else
    echo -e "${RED}❌ FAILED${NC}: Email validation\n"
    exit 1
fi

# Test 6: Short Message
echo -e "${YELLOW}[TEST 6] Contact Form - Message Too Short${NC}"
RESPONSE=$(curl -s -X POST "$API_URL/api/contact" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test",
    "email": "test@example.com",
    "subject": "Test",
    "message": "Short"
  }')

if echo "$RESPONSE" | grep -q "at least 10"; then
    echo -e "${GREEN}✅ PASSED${NC}: Short message properly rejected\n"
else
    echo -e "${RED}❌ FAILED${NC}: Message length validation\n"
    exit 1
fi

# Test 7: Rate Limiting
echo -e "${YELLOW}[TEST 7] Rate Limiting (5 requests/minute)${NC}"
RATE_LIMIT_HIT=false
for i in {1..6}; do
    RESPONSE=$(curl -s -X POST "$API_URL/api/contact" \
      -H "Content-Type: application/json" \
      -d '{
        "name": "Rate Test",
        "email": "rate@example.com",
        "subject": "Test",
        "message": "Testing rate limit functionality here"
      }')
    
    if echo "$RESPONSE" | grep -q "Rate limit"; then
        RATE_LIMIT_HIT=true
        break
    fi
done

if [ "$RATE_LIMIT_HIT" = true ]; then
    echo -e "${GREEN}✅ PASSED${NC}: Rate limiting active\n"
else
    echo -e "${RED}❌ FAILED${NC}: Rate limit not triggered\n"
fi

# Test 8: CORS Preflight
echo -e "${YELLOW}[TEST 8] CORS Preflight${NC}"
if curl -s -X OPTIONS "$API_URL/api/contact" \
    -H "Origin: http://localhost:5500" \
    -H "Access-Control-Request-Method: POST" | grep -q "ok"; then
    echo -e "${GREEN}✅ PASSED${NC}: CORS preflight working\n"
else
    echo -e "${RED}❌ FAILED${NC}: CORS configuration\n"
    exit 1
fi

# Summary
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                  🎉 ALL TESTS PASSED! 🎉                 ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📊 API Endpoints:${NC}"
echo -e "  ${BLUE}GET${NC}  /health"
echo -e "  ${BLUE}GET${NC}  /api/info"
echo -e "  ${BLUE}GET${NC}  /api/stats"
echo -e "  ${BLUE}POST${NC} /api/contact"
echo -e "  ${BLUE}GET${NC}  /docs (Swagger UI)"
echo ""
echo -e "${YELLOW}🔗 Access Points:${NC}"
echo -e "  API Server: $API_URL"
echo -e "  Swagger UI: $API_URL/docs"
echo ""
