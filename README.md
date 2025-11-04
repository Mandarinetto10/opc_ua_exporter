# 🔌 OPC UA Browser/Exporter

Un tool CLI professionale e completo per navigare ed esportare l'Address Space di server OPC UA. Implementato seguendo i principi SOLID, SRP, DRY e OCP con supporto asincrono completo.

## ✨ Caratteristiche

- 🌐 **Client OPC UA Asincrono** basato su `asyncua`
- 🔍 **Browsing Ricorsivo** con controllo della profondità
- 📊 **Export Multi-Formato** (CSV, JSON, XML) tramite Strategy Pattern
- 🔐 **Autenticazione Completa** (username/password, security policies con certificati)
- 🛡️ **Security Policies** complete (Basic256Sha256, AES128/256, ecc.)
- 📝 **Logging Professionale** con `loguru` e messaggi di errore dettagliati
- ⚡ **Gestione Eccezioni Completa** con hint contestuali
- 🏗️ **Architettura Modulare** e testabile
- 🐍 **Type Hints** completi per Python 3.10+

## 📋 Requisiti

- Python 3.10 o superiore
- Accesso a un server OPC UA (locale o remoto)
- Certificati SSL (per connessioni sicure)

## 🚀 Installazione

Consulta il file [SETUP.md](SETUP.md) per istruzioni dettagliate passo-passo.

**Quick Start:**

```bash
# Crea ambiente virtuale
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Installa dipendenze
pip install -r requirements.txt

# Genera certificati (se necessario per security)
python -m opc_browser.cli generate-cert

# Verifica installazione
python -m opc_browser.cli --help
```

## 📖 Utilizzo

La CLI supporta tre sottocomandi principali:
- `browse` - Navigazione interattiva dell'address space
- `export` - Esportazione nodi su file (CSV/JSON/XML)
- `generate-cert` - Generazione certificati self-signed per connessioni sicure

### Sintassi Generale

```bash
python -m opc_browser.cli {browse|export|generate-cert} [OPZIONI]
```

**⚠️ Nota Importante**: 
- All'avvio di ogni comando, il tool mostra un riepilogo completo dei parametri utilizzati
- Se la connessione al server fallisce, il tree non viene stampato
- Gli errori sono loggati con hint contestuali per facilitare il troubleshooting

---

## 🔍 Comando: `browse`

Naviga l'Address Space del server e visualizza la struttura ad albero nella console.

### Comportamento Dettagliato

1. **Validazione Parametri**: Controlla formato Node ID e configurazione security
2. **Logging Parametri**: Mostra tutti i parametri di connessione (URL, hostname, porta, security, auth)
3. **Connessione Sicura**: Stabilisce connessione con security policy e certificati se configurati
4. **Browse Ricorsivo**: Naviga l'address space fino alla profondità configurata
5. **Visualizzazione Tree**: Mostra l'albero dei nodi con emoji, tipi e valori
6. **Statistiche Finali**: Mostra summary con totale nodi, profondità, namespaces

### Output Tipico

````text
# Esempio di output del comando browse

└── Objects
    ├── Server
    │   ├── ServerStatus
    │   ├── SecurityPolicy
    │   └── UserTokenPolicies
    ├── Objects
    │   ├── MyObject
    │   │   ├── Variable1
    │   │   └── Variable2
    │   └── AnotherObject
    │       └── VariableA
    └── Views
        └── MyView
            ├── Component1
            └── Component2
````

### Argomenti Comuni

| Argomento | Breve | Descrizione | Default |
|-----------|-------|-------------|---------|
| `--server-url` | `-s` | **[Obbligatorio]** Endpoint del server OPC UA | - |
| `--node-id` | `-n` | Node ID di partenza | `i=84` (RootFolder) |
| `--depth` | `-d` | Profondità massima di navigazione | `3` |
| `--security` | `-sec` | Security policy | `None` |
| `--mode` | `-m` | Security mode (richiesto se --security != None) | - |
| `--cert` | - | Path certificato client (richiesto per security) | - |
| `--key` | - | Path chiave privata client (richiesto per security) | - |
| `--user` | `-u` | Username per autenticazione | - |
| `--password` | `-p` | Password per autenticazione | - |

### Security Policies Supportate

- **None**: Nessuna sicurezza
- **Basic256**: Legacy (deprecato, ma supportato)
- **Basic128Rsa15**: Legacy (deprecato, ma supportato)
- **Basic256Sha256**: Sicurezza moderna standard
- **Aes128_Sha256_RsaOaep**: AES 128-bit
- **Aes256_Sha256_RsaPss**: AES 256-bit (massima sicurezza)

### Security Modes

- **Sign**: Solo firma digitale
- **SignAndEncrypt**: Firma e cifratura (raccomandato)

### Esempi di Browse

#### Esempio 1: Connessione Base (Nessuna Autenticazione)

```bash
python -m opc_browser.cli browse --server-url opc.tcp://localhost:4840
```

#### Esempio 2: Browse con Profondità Personalizzata

```bash
python -m opc_browser.cli browse -s opc.tcp://localhost:4840 -n "ns=2;i=1000" -d 5
```

#### Esempio 3: Browse con Autenticazione

```bash
python -m opc_browser.cli browse -s opc.tcp://192.168.1.100:4840 -u admin -p password123
```

#### Esempio 4: Browse con Security Policy e Certificati

```bash
python -m opc_browser.cli browse \
  -s opc.tcp://secure-server.com:4840 \
  --security Basic256Sha256 \
  --mode SignAndEncrypt \
  --cert certificates/client_cert.pem \
  --key certificates/client_key.pem \
  -u operator \
  -p secure_pass
```

#### Esempio 5: Browse con Massima Sicurezza (AES256)

```bash
python -m opc_browser.cli browse \
  -s opc.tcp://factory.com:4840 \
  --security Aes256_Sha256_RsaPss \
  --mode SignAndEncrypt \
  --cert certs/factory_client.pem \
  --key certs/factory_key.pem \
  -u admin \
  -p admin_pass \
  -d 5
```

---

## 💾 Comando: `export`

Esporta l'Address Space in formati strutturati (CSV, JSON, XML).

### Argomenti Aggiuntivi per Export

| Argomento | Breve | Descrizione | Default |
|-----------|-------|-------------|---------|
| `--format` | `-f` | Formato di export: `csv`, `json`, `xml` | `csv` |
| `--output` | `-o` | Percorso file di output | `export/opcua_export_<timestamp>.<format>` |
| `--namespaces-only` | - | Esporta solo informazioni sui Namespace | `False` |
| `--namespace-filter` | - | Esporta solo nodi da namespace specifico (indice numerico, es. `2`) | `None` |
| `--include-values` | - | Include i valori correnti delle variabili | `False` |

### 🎯 Filtrare per Namespace

Il filtro per namespace è essenziale quando vuoi esportare solo i nodi di un namespace applicativo specifico (es. `urn:Studio`).

**Come trovare l'indice del namespace:**
1. **Opzione 1 - Browse iniziale senza filtro:**
   ```bash
   python -m opc_browser.cli browse -s opc.tcp://localhost:48010 -u admin -p pass -d 1
   ```
   
   L'output mostrerà:
   ```
   🌐 NAMESPACES:
      [0] http://opcfoundation.org/UA/
      [1] urn:WSM-01153:Studio:OpcUaServer
      [2] urn:Studio
          └─ 70 nodes
   ```

2. **Opzione 2 - Export completo e analisi:**
   ```bash
   python -m opc_browser.cli export -s opc.tcp://localhost:48010 -f csv -o temp.csv
   ```
   
   Guarda la sezione `# Namespaces` in fondo al CSV.

**Una volta identificato l'indice (es. 2 per `urn:Studio`):**
```bash
# Esporta SOLO i nodi del namespace urn:Studio (index 2)
python -m opc_browser.cli export \
  -s opc.tcp://localhost:48010 \
  -u Admin -p 1 \
  --security Aes128_Sha256_RsaOaep \
  --mode Sign \
  --cert certificates/client_cert.pem \
  --key certificates/client_key.pem \
  --namespace-filter 2 \
  -d 10 \
  -f csv \
  -o studio_namespace.csv
```

**Cosa succede:**
- ✅ Il browser naviga tutto l'address space fino a depth 10
- ✅ Al termine del browse, filtra e mantiene SOLO i nodi con `namespace_index=2`
- ✅ L'export conterrà solo nodi di `urn:Studio`
- ✅ Il Summary mostrerà il numero effettivo di nodi filtrati

### Esempi di Export

#### Esempio 1: Export Base in CSV

```bash
python -m opc_browser.cli export -s opc.tcp://localhost:4840
```

Output: `export/opcua_export_20250104_143022.csv`

#### Esempio 2: Export in JSON con Nome File Personalizzato

```bash
python -m opc_browser.cli export -s opc.tcp://localhost:4840 -f json -o mio_server.json
```

**Struttura JSON generata:**
```json
{
  "metadata": {
    "total_nodes": 150,
    "max_depth_reached": 3,
    "success": true
  },
  "namespaces": [
    {"index": 0, "uri": "http://opcfoundation.org/UA/"},
    {"index": 1, "uri": "urn:MyCompany:MyServer"}
  ],
  "nodes": [
    {
      "node_id": "i=84",
      "browse_name": "Root",
      "display_name": "Root",
      "node_class": "Object"
    }
  ]
}
```

#### Esempio 3: Export in XML con Valori delle Variabili

```bash
python -m opc_browser.cli export -s opc.tcp://localhost:4840 -f xml -o dati_completi.xml --include-values
```

**Struttura XML generata:**
```xml
<?xml version='1.0' encoding='utf-8'?>
<OpcUaAddressSpace>
  <Metadata>
    <TotalNodes>150</TotalNodes>
    <MaxDepthReached>3</MaxDepthReached>
    <Success>True</Success>
  </Metadata>
  <Namespaces>
    <Namespace>
      <Index>0</Index>
      <URI>http://opcfoundation.org/UA/</URI>
    </Namespace>
  </Namespaces>
  <Nodes>
    <Node>
      <NodeId>i=84</NodeId>
      <BrowseName>Root</BrowseName>
      <DisplayName>Root</DisplayName>
      <NodeClass>Object</NodeClass>
      <Depth>0</Depth>
    </Node>
  </Nodes>
</OpcUaAddressSpace>
```

#### Esempio 4: Export Solo Namespace

```bash
python -m opc_browser.cli export -s opc.tcp://localhost:4840 -f json -o namespaces.json --namespaces-only
```

#### Esempio 5: Export Completo con Autenticazione e Profondità

```bash
python -m opc_browser.cli export -s opc.tcp://192.168.1.50:4840 \
  -u admin -p admin123 -n "ns=2;i=5000" -d 10 \
  -f csv -o export/produzione_completa.csv --include-values
```

#### Esempio 6: Export XML con Security

```bash
python -m opc_browser.cli export -s opc.tcp://secure.factory.com:4840 \
  --security Basic256Sha256 --mode SignAndEncrypt \
  --cert certificates/client_cert.pem --key certificates/client_key.pem \
  -u operator -p op_pass -f xml -o secure_export.xml -d 7
```

---

## 🔐 Comando: `generate-cert`

Genera un certificato client self-signed per l'autenticazione OPC UA.

### Sintassi

```bash
python -m opc_browser.cli generate-cert [OPZIONI]
```

### Argomenti

| Argomento         | Descrizione                                                                 | Default                                                   |
|-------------------|-----------------------------------------------------------------------------|-----------------------------------------------------------|
| `--dir`           | Directory dove salvare i certificati                                        | `certificates`                                            |
| `--cn`            | Common Name del certificato                                                 | `OPC UA Python Client`                                    |
| `--org`           | Organization Name                                                           | `My Organization`                                         |
| `--country`       | Country code (2 lettere)                                                    | `IT`                                                      |
| `--days`          | Validità del certificato in giorni                                          | `365`                                                     |
| `--uri`           | Application URI (deve corrispondere a quello richiesto dal server OPC UA)   | `urn:example.org:FreeOpcUa:opcua-asyncio`                |
| `--hostname`      | Hostname/DNS name da includere nel certificato (può essere ripetuto)        | `localhost` + hostname locale (auto-detected)             |

**Note Importanti:**  
- ✅ Tutti gli argomenti sono opzionali e hanno valori di default sensati
- 🔄 `--hostname` viene popolato automaticamente con `localhost` e il nome del computer locale
- 🔖 L'Application URI di default (`urn:example.org:FreeOpcUa:opcua-asyncio`) corrisponde a quello usato internamente da `asyncua`
- 📌 Se il server richiede un URI diverso, usa `--uri` per personalizzarlo
- 🏷️ Puoi specificare più volte `--hostname` per includere più DNS names/IP

### Esempi

```bash
# Genera certificato con impostazioni di default (raccomandato)
python -m opc_browser.cli generate-cert

# Genera certificato con Application URI personalizzato
python -m opc_browser.cli generate-cert --uri "urn:mycompany:opcua:client"

# Genera certificato con hostname aggiuntivi
python -m opc_browser.cli generate-cert \
  --hostname server.local \
  --hostname 192.168.1.100 \
  --org "My Company" \
  --days 730

# Genera certificato per un ambiente specifico
python -m opc_browser.cli generate-cert \
  --uri "urn:factory:scada:client" \
  --hostname production-server \
  --hostname backup-server \
  --cn "Factory SCADA Client" \
  --org "ACME Corporation"
```

### Output

- `client_cert.pem` - Certificato client
- `client_key.pem`  - Chiave privata
- `client_cert.der` - Certificato in formato DER (alcuni server lo richiedono)

I file saranno salvati nella directory specificata (`--dir`).

### Dove usare questi certificati?

Utilizza i file generati con i parametri `--cert` e `--key` nei comandi `browse` ed `export`:

```bash
python -m opc_browser.cli browse \
  --server-url opc.tcp://server:4840 \
  --security Basic256Sha256 \
  --mode SignAndEncrypt \
  --cert certificates/client_cert.pem \
  --key certificates/client_key.pem
```

## 📂 Struttura del Progetto

```
opc-ua-browser/
├── pyproject.toml          # Configurazione progetto
├── requirements.txt        # Dipendenze Python
├── SETUP.md               # Guida setup dettagliata
├── README.md              # Questo file
├── export/                # Directory export (auto-creata)
└── src/
    └── opc_browser/
        ├── __init__.py
        ├── cli.py         # Entry point CLI (argparse)
        ├── models.py      # Dataclasses per nodi OPC UA
        ├── client.py      # Client OPC UA (connessione/autenticazione)
        ├── browser.py     # Logica di browsing ricorsivo
        ├── exporter.py    # Context per Strategy Pattern
        ├── generate_cert.py  # Generazione certificati
        └── strategies/
            ├── __init__.py
            ├── base.py    # ABC per Strategy
            ├── csv_strategy.py
            ├── json_strategy.py
            └── xml_strategy.py
```

## 🔧 Configurazione del Logging

Il logging è gestito automaticamente da `loguru`. I log includono:

- ✅ Tentativi di connessione
- ✅ Successo/fallimento operazioni
- ✅ Inizio/fine browsing
- ✅ Inizio/fine export
- ⚠️ Warning e errori

Per aumentare il livello di verbosity, modifica `src/opc_browser/cli.py`.

## 🎯 Principi di Design

### SOLID
- **S**ingle Responsibility: ogni modulo ha una responsabilabilità chiara
- **O**pen/Closed: Strategy Pattern per estendere formati di export
- **L**iskov Substitution: le strategie sono intercambiabili
- **I**nterface Segregation: interfacce minimali e specifiche
- **D**ependency Inversion: dipendenze verso astrazioni

### Design Patterns Implementati
- **Strategy Pattern**: per export multi-formato (CSV/JSON/XML)
- **Dataclass Pattern**: per modellazione dati type-safe

## 🧪 Testing

```bash
# Installa dipendenze dev
pip install -e ".[dev]"

# Esegui test
pytest tests/

# Con coverage
pytest --cov=opc_browser tests/
```

## 🐛 Troubleshooting

### Errore: "Cannot connect to server"

- Verifica che il server OPC UA sia in esecuzione
- Controlla l'URL del server (formato: `opc.tcp://host:port`)
- Verifica firewall e porte

### Errore: "Authentication failed"

- Verifica username e password
- Controlla la security policy richiesta dal server
- Alcuni server richiedono certificati client

### Errore: "Bad_NodeIdUnknown"

- Il Node ID specificato non esiste
- Verifica la sintassi del Node ID: `ns=X;i=Y` o `ns=X;s=StringId`
- Usa `browse` per esplorare i nodi disponibili

### Errore: "Invalid Node ID format"

- **Formato corretto**: `i=123` (namespace 0), `ns=2;i=456` (con namespace), `ns=2;s=MyNode` (string ID)
- **Formato errato**: `ns=2` (manca identificatore), `2;i=456` (manca prefisso ns)
- Usa `browse` senza `-n` per esplorare l'albero e trovare ID validi

### Warning: "No nodes discovered"

- Il nodo specificato esiste ma non ha figli
- Potresti non avere permessi per accedere ai suoi child nodes
- Verifica con un livello di profondità maggiore (`-d 5` o più)
- Prova a partire da un nodo parent (es. `i=85` per Objects)

### Tree troppo grande da visualizzare

- La visualizzazione è limitata a 500 nodi per performance
- Usa il comando `export` per salvare l'intero albero su file
- Riduci la profondità con `-d 2` o `-d 1` per browse più focalizzati

### Errore: "Certificate and private key are required"

- Quando usi `--security` con valore diverso da `None`, devi fornire:
  - `--cert path/to/certificate.pem`
  - `--key path/to/private_key.pem`
  - `--mode Sign` o `--mode SignAndEncrypt`
- Genera i certificati come descritto nella sezione "Gestione Certificati"

### Errore: "Certificate file not found"

- Verifica che il path del certificato sia corretto
- Usa path assoluti o relativi dalla directory corrente
- Controlla i permessi di lettura del file

### Errore: "BadSecurityChecksFailed"

- Il server ha rifiutato il certificato client
- Verifica che il certificato sia trusted dal server
- Alcuni server richiedono che il certificato sia aggiunto alla loro trust list
- Controlla le politiche di sicurezza del server

### Errore: "Security mode is required"

- Quando usi `--security` (eccetto `None`), devi specificare `--mode`
- Esempio corretto: `--security Basic256Sha256 --mode SignAndEncrypt`

## 🔐 Gestione Certificati

Per utilizzare le security policies (eccetto `None`), è necessario generare certificati client.

### Generazione Certificati con Python (Raccomandato per Windows)

```bash
# Installa dipendenze (include cryptography)
pip install -r requirements.txt

# Genera certificati automaticamente
python generate_certificates.py

# I certificati saranno salvati in: certificates/client_cert.pem e certificates/client_key.pem
```

### Generazione Certificati con OpenSSL (Linux/macOS)

```bash
# Crea directory per i certificati
mkdir certificates
cd certificates

# Genera chiave privata
openssl genrsa -out client_key.pem 2048

# Genera certificato self-signed (valido 365 giorni)
openssl req -new -x509 -key client_key.pem -out client_cert.pem -days 365

# Informazioni da inserire (esempio):
# Country Name: IT
# State: Lazio
# Locality: Rome
# Organization Name: My Company
# Organizational Unit: Engineering
# Common Name: OPC UA Client
# Email Address: client@example.com
```

### Utilizzo Certificati

```bash
python -m opc_browser.cli browse \
  -s opc.tcp://server:4840 \
  --security Basic256Sha256 \
  --mode SignAndEncrypt \
  --cert certificates/client_cert.pem \
  --key certificates/client_key.pem
```

### Personalizzazione Certificati

Puoi modificare lo script `generate_certificates.py` per personalizzare:
- Organization Name
- Country Code
- Common Name
- Validity Period
- Subject Alternative Names (DNS, IP)

## 📚 Riferimenti

- [OPC UA Specification](https://opcfoundation.org/developer-tools/specifications-unified-architecture)
- [asyncua Documentation](https://github.com/FreeOpcUa/opcua-asyncio)
- [loguru Documentation](https://loguru.readthedocs.io/)
- [tqdm Documentation](https://tqdm.github.io/)

## 📄 Licenza

MIT License - Vedi file LICENSE per dettagli

## 🤝 Contributi

I contributi sono benvenuti! Per favore:
1. Forka il progetto
2. Crea un branch per la tua feature (`git checkout -b feature/AmazingFeature`)
3. Committa le modifiche (`git commit -m 'Add AmazingFeature'`)
4. Pusha il branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request