# Setup Guide - OPC UA Browser/Exporter

Questa guida fornisce istruzioni dettagliate per configurare l'ambiente di sviluppo e installare tutte le dipendenze necessarie per il progetto OPC UA Browser/Exporter.

## Prerequisiti

- **Python 3.10 o superiore** installato sul sistema
- **pip** (package installer per Python)
- **git** (opzionale, per clonare il repository)

### Verifica della Versione Python

```bash
python --version
# oppure
python3 --version
```

Se la versione è inferiore a 3.10, aggiorna Python prima di procedere.

## Passo 1: Clonare o Scaricare il Progetto

### Opzione A: Clonare con Git

```bash
git clone <repository-url>
cd opc-ua-browser
```

### Opzione B: Scaricare e Estrarre

Scarica il progetto come archivio ZIP ed estrailo in una directory locale.

## Passo 2: Creare l'Ambiente Virtuale

La creazione di un ambiente virtuale isola le dipendenze del progetto dal sistema Python globale.

### Su Linux/macOS

```bash
python3 -m venv venv
```

### Su Windows

```cmd
python -m venv venv
```

## Passo 3: Attivare l'Ambiente Virtuale

### Su Linux/macOS

```bash
source venv/bin/activate
```

### Su Windows (Command Prompt)

```cmd
venv\Scripts\activate.bat
```

### Su Windows (PowerShell)

```powershell
venv\Scripts\Activate.ps1
```

**Nota:** Se ricevi un errore di policy su Windows PowerShell, esegui:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Una volta attivato, dovresti vedere `(venv)` all'inizio del prompt della tua shell.

## Passo 4: Aggiornare pip

```bash
pip install --upgrade pip
```

## Passo 5: Installare le Dipendenze

### Installazione Base

```bash
pip install -r requirements.txt
```

### Installazione in Modalità Sviluppo (con dipendenze opzionali)

```bash
pip install -e ".[dev]"
```

Questo comando installa il pacchetto in modalità "editable" permettendoti di modificare il codice senza dover reinstallare.

## Passo 6: Verificare l'Installazione

Controlla che tutte le dipendenze siano state installate correttamente:

```bash
pip list
```

Dovresti vedere elencate le seguenti librerie:
- `asyncua`
- `loguru`
- `tqdm`

## Passo 7: Testare l'Installazione

Verifica che la CLI sia accessibile:

```bash
python -m opc_browser.cli --help
```

oppure, se hai installato il progetto:

```bash
opc-browser --help
```

Dovresti vedere l'output dell'help con tutti i comandi e le opzioni disponibili.

## Troubleshooting

### Problema: "ModuleNotFoundError"

**Soluzione:** Assicurati che l'ambiente virtuale sia attivato e che tutte le dipendenze siano state installate correttamente.

### Problema: Errori di Permesso durante l'Installazione

**Soluzione su Linux/macOS:**
```bash
pip install --user -r requirements.txt
```

### Problema: Conflitti di Dipendenze

**Soluzione:** Ricrea l'ambiente virtuale da zero:

```bash
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate  # o activate.bat su Windows
pip install -r requirements.txt
```

## Disattivare l'Ambiente Virtuale

Quando hai finito di lavorare sul progetto:

```bash
deactivate
```

## Prossimi Passi

Consulta il file `README.md` per esempi di utilizzo e documentazione completa della CLI.

## Supporto

Per problemi o domande:
- Verifica la documentazione nel `README.md`
- Controlla i requisiti di sistema
- Consulta la documentazione ufficiale di [asyncua](https://github.com/FreeOpcUa/opcua-asyncio)