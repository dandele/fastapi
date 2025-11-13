#!/bin/bash

# Script per testare il sistema in locale

echo "🚀 BeeBus Fatture Extractor - Test Locale"
echo "========================================="
echo ""

# Colori per output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:8000"

# 1. Test Health Check
echo -e "${YELLOW}1️⃣  Testing Health Check...${NC}"
curl -s "$BASE_URL/health" | python -m json.tool
echo ""

# 2. Test Fornitori Supportati
echo -e "${YELLOW}2️⃣  Testing Supported Providers...${NC}"
curl -s "$BASE_URL/supported-providers" | python -m json.tool
echo ""

# 3. Test Estrazione Fattura IP
echo -e "${YELLOW}3️⃣  Testing IP Invoice Extraction...${NC}"
if [ -f "Fatture/Fattura IP.pdf" ]; then
    curl -X POST "$BASE_URL/extract" \
      -F "file=@Fatture/Fattura IP.pdf" \
      -H "accept: application/json" | python -m json.tool
    echo ""
else
    echo -e "${RED}File 'Fatture/Fattura IP.pdf' non trovato${NC}"
fi

# 4. Test Estrazione Fattura Esso
echo -e "${YELLOW}4️⃣  Testing Esso Invoice Extraction...${NC}"
if [ -f "Fatture/fattura esso.pdf" ]; then
    curl -X POST "$BASE_URL/extract" \
      -F "file=@Fatture/fattura esso.pdf" \
      -H "accept: application/json" | python -m json.tool
    echo ""
else
    echo -e "${RED}File 'Fatture/fattura esso.pdf' non trovato${NC}"
fi

# 5. Test Estrazione Fattura Q8
echo -e "${YELLOW}5️⃣  Testing Q8 Invoice Extraction...${NC}"
if [ -f "Fatture/fattura q8.pdf" ]; then
    curl -X POST "$BASE_URL/extract" \
      -F "file=@Fatture/fattura q8.pdf" \
      -H "accept: application/json" | python -m json.tool
    echo ""
else
    echo -e "${RED}File 'Fatture/fattura q8.pdf' non trovato${NC}"
fi

# 6. Test Batch (tutte le fatture)
echo -e "${YELLOW}6️⃣  Testing Batch Extraction (all invoices)...${NC}"
curl -X POST "$BASE_URL/extract-batch" \
  -F "files=@Fatture/Fattura IP.pdf" \
  -F "files=@Fatture/fattura esso.pdf" \
  -F "files=@Fatture/fattura q8.pdf" \
  -H "accept: application/json" | python -m json.tool
echo ""

echo -e "${GREEN}✅ Test completati!${NC}"
