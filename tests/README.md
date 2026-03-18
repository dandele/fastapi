# BeeBus Invoice Extractors - Test Suite

Suite di test completa per verificare il funzionamento degli estrattori di fatture carburante.

## 📋 Struttura Test

### Test Unitari

- **`test_tamoil_extractor.py`** - Test per il nuovo TamoilExtractor
  - Verifica riconoscimento formato Tamoil
  - Test pattern regex per transazioni
  - Verifica estrazione targa con logica "transazioni in attesa"
  - Test gestione KM opzionale

- **`test_esso_extractor.py`** - Test per fix EssoExtractor
  - Verifica estrazione importo da "Totale incl. IVA EUR" (ultimo importo)
  - Test supporto campo KM opzionale
  - Verifica che tutte le transazioni abbiano importo > 0

- **`test_ip_extractor.py`** - Test per fix IPExtractor
  - Verifica supporto prodotti generici (GASOLIO, METANO, GPL, ecc.)
  - Test estrazione transazione METANO (prima non supportata)
  - Verifica pattern regex flessibile per prodotti

### Test di Integrazione

- **`test_integration.py`** - Test end-to-end completi
  - Test con PDF reali dalla cartella "Fatture nuove"
  - Verifica riconoscimento automatico fornitori (Factory)
  - Test critici per ogni fornitore
  - Verifica struttura CSV di output
  - Test gestione errori

## 🚀 Esecuzione Test

### Metodo 1: Script Runner (Consigliato)

```bash
python tests/run_tests.py
```

Lo script esegue tutti i test e genera un report dettagliato con:
- Riepilogo per categoria
- Verifiche critiche
- Percentuale di successo
- Dettagli test falliti

### Metodo 2: Pytest Diretto

Esegui tutti i test:
```bash
pytest
```

Esegui test specifici:
```bash
# Solo test Tamoil
pytest tests/test_tamoil_extractor.py

# Solo test ESSO
pytest tests/test_esso_extractor.py

# Solo test IP
pytest tests/test_ip_extractor.py

# Solo test integrazione
pytest tests/test_integration.py
```

Esegui test con dettagli verbose:
```bash
pytest -v
```

Esegui test specifici per classe:
```bash
pytest tests/test_tamoil_extractor.py::TestTamoilExtractor
pytest tests/test_tamoil_extractor.py::TestTamoilIntegration
```

### Metodo 3: Esegui Singolo Test

```bash
pytest tests/test_tamoil_extractor.py::TestTamoilExtractor::test_can_handle_tamoil_text -v
```

## ✅ Test Critici

Questi test **DEVONO** passare prima del merge:

### Tamoil
- ✓ Estrazione targa FK444ZJ da riga "Totale Carta"
- ✓ 2 transazioni estratte dal PDF reale
- ✓ Totale importo = 182.50 EUR (101.49 + 81.01)

### ESSO
- ✓ Transazione senza KM estratta (scontrino 006241)
- ✓ Importo estratto da "Totale incl. IVA EUR" (non da "Imp. Ticket")
- ✓ Tutti gli importi > 0

### IP
- ✓ Transazione METANO estratta (scontrino 00005546)
- ✓ Supporto prodotti generici (non solo GASOLIO/GASOLIO SELF)
- ✓ Pattern regex cattura qualsiasi prodotto maiuscolo

## 📊 Coverage

Per verificare la copertura del codice:

```bash
# Installa coverage
pip install pytest-cov

# Esegui test con coverage
pytest --cov=extractors --cov-report=html

# Apri report HTML
open htmlcov/index.html
```

## 🔍 Debug Test

Per debug dettagliato di un test:

```bash
# Con print e output completo
pytest tests/test_tamoil_extractor.py -v -s

# Con traceback completo
pytest tests/test_tamoil_extractor.py -v --tb=long

# Con pdb debugger
pytest tests/test_tamoil_extractor.py --pdb
```

## 📁 PDF di Test

I test di integrazione utilizzano PDF reali nella cartella:
```
/Users/mirkopapadopoli/Code/fastapi/Fatture nuove/
├── tamoil 1-10...pdf
├── esso del 1-10.pdf
├── ip del 1-10.pdf
└── q8 del 1-10.pdf
```

Se i PDF non sono presenti, i test di integrazione vengono saltati automaticamente.

## 🛠 Requisiti

```bash
pip install pytest pytest-cov
```

Opzionale (per report HTML):
```bash
pip install pytest-html
pytest --html=report.html
```

## 📝 Aggiungere Nuovi Test

1. Crea un file `test_*.py` nella directory `tests/`
2. Crea una classe `Test*` con i metodi `test_*`
3. Usa i fixture per setup/teardown
4. Aggiungi markers se necessario:
   ```python
   @pytest.mark.critical
   def test_importante(self):
       ...
   ```

## 🎯 Convenzioni

- Usa fixture per oggetti riutilizzabili
- Un test = una verifica specifica
- Nomi test descrittivi (cosa testa + cosa si aspetta)
- Usa `pytest.skip()` per test che dipendono da file esterni
- Usa `assert` con messaggi informativi
- Documenta test critici con docstring

## 📈 Risultati Attesi

Quando tutti i test passano, dovresti vedere:

```
✓ Test Unitari - TamoilExtractor: PASS
✓ Test Integrazione - Tamoil: PASS
✓ Test Unitari - EssoExtractor: PASS
✓ Test Integrazione - Esso: PASS
✓ Test Unitari - IPExtractor: PASS
✓ Test Integrazione - IP: PASS
✓ Test End-to-End Completi: PASS

Percentuale successo: 100.0%

✓ Il branch feature/tamoil-support-and-fixes è pronto per il merge
```
