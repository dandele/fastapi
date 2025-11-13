#!/usr/bin/env python3
"""
Script di test per BeeBus Fatture Extractor
Testa l'estrazione da tutte le tipologie di fatture
"""
import requests
import json
from pathlib import Path

# Configurazione
BASE_URL = "http://localhost:8000"
FATTURE_DIR = Path("Fatture")

def print_section(title):
    """Stampa una sezione formattata"""
    print("\n" + "="*60)
    print(f"🔍 {title}")
    print("="*60)

def test_health():
    """Test health check"""
    print_section("Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

def test_supported_providers():
    """Test lista fornitori supportati"""
    print_section("Fornitori Supportati")
    response = requests.get(f"{BASE_URL}/supported-providers")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

def test_single_extraction(file_path):
    """Test estrazione singola fattura"""
    print_section(f"Estrazione: {file_path.name}")

    if not file_path.exists():
        print(f"❌ File non trovato: {file_path}")
        return None

    with open(file_path, 'rb') as f:
        files = {'file': (file_path.name, f, 'application/pdf')}
        response = requests.post(f"{BASE_URL}/extract", files=files)

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Fornitore identificato: {data.get('fornitore', 'N/A')}")
        print(f"✅ Record estratti: {data.get('records_count', 0)}")
        print(f"✅ Totale importo: €{data.get('total_amount', 0):.2f}")

        # Mostra prime 3 transazioni
        if data.get('data'):
            print("\n📋 Prime 3 transazioni:")
            for i, record in enumerate(data['data'][:3], 1):
                print(f"  {i}. {record.get('Data_Rifornimento')} - "
                      f"Targa: {record.get('Targa')} - "
                      f"€{record.get('Importo_Totale', 0):.2f}")
        return data
    else:
        print(f"❌ Errore: {response.text}")
        return None

def test_batch_extraction():
    """Test estrazione batch di tutte le fatture"""
    print_section("Estrazione Batch (tutte le fatture)")

    fatture = [
        FATTURE_DIR / "Fattura IP.pdf",
        FATTURE_DIR / "fattura esso.pdf",
        FATTURE_DIR / "fattura q8.pdf"
    ]

    # Filtra solo i file esistenti
    existing_files = [f for f in fatture if f.exists()]

    if not existing_files:
        print("❌ Nessuna fattura trovata")
        return

    files = [
        ('files', (f.name, open(f, 'rb'), 'application/pdf'))
        for f in existing_files
    ]

    response = requests.post(f"{BASE_URL}/extract-batch", files=files)

    # Chiudi i file
    for _, (_, file_obj, _) in files:
        file_obj.close()

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ File processati: {data.get('processed_files', 0)}")
        print(f"✅ Totale record: {data.get('total_records', 0)}")

        if data.get('results'):
            print("\n📊 Riepilogo per file:")
            for result in data['results']:
                print(f"  • {result['filename']}: "
                      f"{result['records_count']} record, "
                      f"€{result['total_amount']:.2f}, "
                      f"Fornitore: {result.get('fornitore', 'N/A')}")
    else:
        print(f"❌ Errore: {response.text}")

def test_csv_export():
    """Test esportazione CSV"""
    print_section("Esportazione CSV")

    fatture = [
        FATTURE_DIR / "Fattura IP.pdf",
        FATTURE_DIR / "fattura esso.pdf",
        FATTURE_DIR / "fattura q8.pdf"
    ]

    existing_files = [f for f in fatture if f.exists()]

    if not existing_files:
        print("❌ Nessuna fattura trovata")
        return

    files = [
        ('files', (f.name, open(f, 'rb'), 'application/pdf'))
        for f in existing_files
    ]

    response = requests.post(f"{BASE_URL}/extract-csv", files=files)

    for _, (_, file_obj, _) in files:
        file_obj.close()

    if response.status_code == 200:
        data = response.json()
        csv_content = data.get('csv_data', '')
        filename = data.get('filename', 'output.csv')

        # Salva il CSV
        output_path = Path(filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)

        print(f"✅ CSV salvato: {output_path}")
        print(f"✅ Totale record: {data.get('total_records', 0)}")
        print(f"✅ File processati: {data.get('processed_files', 0)}")

        # Mostra prime righe
        lines = csv_content.split('\n')[:5]
        print("\n📄 Prime righe del CSV:")
        for line in lines:
            print(f"  {line}")
    else:
        print(f"❌ Errore: {response.text}")

def main():
    """Esegue tutti i test"""
    print("\n" + "🚀 BeeBus Fatture Extractor - Test Suite".center(60, "="))

    try:
        # Test 1: Health check
        test_health()

        # Test 2: Fornitori supportati
        test_supported_providers()

        # Test 3: Estrazione singole fatture
        test_single_extraction(FATTURE_DIR / "Fattura IP.pdf")
        test_single_extraction(FATTURE_DIR / "fattura esso.pdf")
        test_single_extraction(FATTURE_DIR / "fattura q8.pdf")

        # Test 4: Batch
        test_batch_extraction()

        # Test 5: CSV export
        test_csv_export()

        print("\n" + "="*60)
        print("✅ Tutti i test completati!")
        print("="*60 + "\n")

    except requests.exceptions.ConnectionError:
        print("\n❌ ERRORE: Impossibile connettersi al server!")
        print("Assicurati che il server sia avviato con: python main.py")
        print("="*60 + "\n")
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        print("="*60 + "\n")

if __name__ == "__main__":
    main()
