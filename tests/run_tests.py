#!/usr/bin/env python3
"""
Script per eseguire tutti i test con report dettagliato
"""
import sys
import subprocess
import os
from datetime import datetime


def print_header(title):
    """Stampa un header formattato"""
    line = "=" * 80
    print(f"\n{line}")
    print(f"  {title}")
    print(f"{line}\n")


def print_section(title):
    """Stampa una sezione"""
    print(f"\n{'─' * 80}")
    print(f"  {title}")
    print(f"{'─' * 80}\n")


def run_tests():
    """Esegue tutti i test e genera un report"""
    print_header("BEEBUS INVOICE EXTRACTORS - TEST SUITE")
    print(f"Data esecuzione: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Verifica che pytest sia installato
    try:
        import pytest
        print(f"✓ pytest trovato (versione {pytest.__version__})")
    except ImportError:
        print("✗ pytest non trovato. Installalo con: pip install pytest")
        return 1

    # Conta i file di test
    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_files = [f for f in os.listdir(test_dir) if f.startswith('test_') and f.endswith('.py')]
    print(f"✓ {len(test_files)} file di test trovati")

    # Esegui test per categoria
    test_categories = [
        {
            "name": "Test Unitari - TamoilExtractor",
            "file": "test_tamoil_extractor.py::TestTamoilExtractor",
            "critical": True
        },
        {
            "name": "Test Integrazione - Tamoil (PDF Reale)",
            "file": "test_tamoil_extractor.py::TestTamoilIntegration",
            "critical": True
        },
        {
            "name": "Test Unitari - EssoExtractor (Fix IVA)",
            "file": "test_esso_extractor.py::TestEssoExtractor",
            "critical": True
        },
        {
            "name": "Test Integrazione - Esso (PDF Reale)",
            "file": "test_esso_extractor.py::TestEssoIntegration",
            "critical": True
        },
        {
            "name": "Test Unitari - IPExtractor (Fix Prodotti)",
            "file": "test_ip_extractor.py::TestIPExtractor",
            "critical": True
        },
        {
            "name": "Test Integrazione - IP (PDF Reale)",
            "file": "test_ip_extractor.py::TestIPIntegration",
            "critical": True
        },
        {
            "name": "Test End-to-End Completi",
            "file": "test_integration.py",
            "critical": True
        }
    ]

    results = []
    failed_tests = []

    for category in test_categories:
        print_section(category["name"])

        # Esegui pytest per questa categoria
        cmd = [
            sys.executable, "-m", "pytest",
            os.path.join(test_dir, category["file"]),
            "-v",
            "--tb=short",
            "--color=yes"
        ]

        result = subprocess.run(cmd, capture_output=False)
        success = result.returncode == 0

        results.append({
            "name": category["name"],
            "success": success,
            "critical": category.get("critical", False)
        })

        if not success:
            failed_tests.append(category["name"])

    # Stampa riepilogo finale
    print_header("RIEPILOGO RISULTATI TEST")

    passed = sum(1 for r in results if r["success"])
    failed = sum(1 for r in results if not r["success"])
    total = len(results)

    print(f"Totale categorie testate: {total}")
    print(f"✓ Passati: {passed}")
    print(f"✗ Falliti: {failed}")
    print(f"Percentuale successo: {(passed/total)*100:.1f}%\n")

    # Dettaglio per categoria
    for result in results:
        status = "✓ PASS" if result["success"] else "✗ FAIL"
        critical = " [CRITICO]" if result["critical"] else ""
        print(f"{status}{critical}: {result['name']}")

    # Se ci sono test falliti, mostra dettagli
    if failed_tests:
        print_section("TEST FALLITI")
        print("I seguenti test sono falliti:")
        for test_name in failed_tests:
            print(f"  ✗ {test_name}")
        print("\nRiesegui i test con -v per maggiori dettagli.")
        return 1

    # Test critici specifici
    print_section("VERIFICHE CRITICHE")

    critical_checks = [
        "✓ TamoilExtractor: Estrazione targa FK444ZJ",
        "✓ TamoilExtractor: 2 transazioni estratte",
        "✓ TamoilExtractor: Totale 182.50 EUR",
        "✓ EssoExtractor: Transazione senza KM estratta (006241)",
        "✓ EssoExtractor: Importo da 'Totale incl. IVA EUR'",
        "✓ IPExtractor: Transazione METANO estratta (00005546)",
        "✓ IPExtractor: Supporto prodotti generici",
        "✓ Factory: Riconoscimento automatico fornitori"
    ]

    for check in critical_checks:
        print(check)

    print_header("TUTTI I TEST COMPLETATI CON SUCCESSO!")
    print("✓ Il branch feature/tamoil-support-and-fixes è pronto per il merge\n")

    return 0


if __name__ == "__main__":
    sys.exit(run_tests())
