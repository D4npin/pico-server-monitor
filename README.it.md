🇮🇹 Italiano | [🇬🇧 English](README.md)

---

# Pico Server Monitor

Mostra lo stato di un server CasaOS su un display LCD 1602A, tramite un Raspberry Pi Pico W.

<p align="center">
  <img src="docs/circuit.jpg" width="600" alt="Montaggio completo: Pico W, display LCD 1602A, LED e pulsante">
</p>

## Funzionalità

- Utilizzo della CPU, temperatura, RAM libera e percentuale usata
- Spazio usato e libero su due dischi
- Uptime e load average
- Pulsante per cambiare schermata
- LED di avviso: acceso fisso sopra una prima soglia di temperatura, lampeggiante sopra una seconda soglia più alta

## Come funziona

Il server esegue [Glances](https://github.com/nicolargo/glances) in Docker, che espone un'API REST.
Il Pico W legge i dati via Wi-Fi con [MicroPython](https://micropython.org/download/RPI_PICO_W/) e li scrive sul display.

> [!NOTE]
> Il Pico W supporta solo reti Wi-Fi a 2.4 GHz.

---

## Componenti

- Raspberry Pi Pico W
- Display LCD 1602A (16 pin, 4 bit, 2 righe)
- Trimmer 10 kΩ
- LED rosso
- Resistenza 220 Ω (per la retroilluminazione) e resistenza 220 Ω (per il LED)
- Pulsante
- Breadboard e cavi

---

## Collegamenti

### Display LCD 1602A

| Pin LCD | Nome | Collegamento |
|---|---|---|
| 1 | VSS | GND |
| 2 | VDD | 5V (VBUS) |
| 3 | V0 | cursore del trimmer |
| 4 | RS | GP16 |
| 5 | RW | GND |
| 6 | E | GP17 |
| 11-14 | D4-D7 | GP18-GP21 |
| 15 | A | 5V tramite resistenza 220 Ω |
| 16 | K | GND |

I capi esterni del trimmer vanno a 5V e GND.

### LED di avviso

| Componente | Collegamento |
|---|---|
| Anodo (gamba lunga) | GP15 tramite resistenza 220 Ω |
| Catodo (gamba corta) | GND |

### Pulsante

| Componente | Collegamento |
|---|---|
| Contatto 1 | GP14 |
| Contatto 2 | GND |

Non serve una resistenza esterna: il codice usa il pull-up interno del Pico.

---

## Installazione

### 1. Server

1. Copia `server/docker-compose.yml` sul server (oppure importalo come app personalizzata su CasaOS).
2. Avvia Glances:
```bash
   docker compose up -d
```
3. Verifica che l'API risponda:
```bash
   curl http://IP_SERVER:61208/api/4/fs
```
   Annota i valori di `mnt_point` dei tuoi dischi: ti serviranno per la configurazione.

### 2. Pico W

1. Installa il firmware MicroPython per **Pico W** (tieni premuto BOOTSEL mentre colleghi l'USB e copia il file `.uf2`).
2. Con [Thonny](https://thonny.org) salva sul Pico i file `pico/lcd.py` e `pico/main.py`.
3. Copia `pico/config.example.py`, rinominalo `config.py` e compilalo (vedi sotto).
4. Salva `config.py` sul Pico e premi **F5** per provare.
5. Per l'uso normale, scollega il Pico dal PC e alimentalo con un caricatore USB: `main.py` parte da solo.


---

## Configurazione

Parti dalla [configurazione di esempio](pico/config.example.py) e modifica questi valori:

| Variabile | Significato |
|---|---|
| `SSID` | Nome della rete Wi-Fi |
| `PASSWORD` | Password del Wi-Fi |
| `GLANCES` | Indirizzo di Glances, ad esempio `http://192.168.1.50:61208` |
| `TEMP_ON` | Temperatura (°C) da cui il LED resta acceso fisso |
| `TEMP_BLINK` | Temperatura (°C) da cui il LED lampeggia |
| `DISKS` | Elenco dei dischi da mostrare: etichetta di 3 lettere e `mnt_point` come appare in `/api/4/fs` |

---

## Schermate

Il pulsante passa da una schermata alla successiva.

1. **Sistema:** CPU %, temperatura, RAM libera e % usata
2. **Dischi:** percentuale usata e spazio libero dei due dischi
3. **Uptime:** tempo di attività e load average (1, 5 e 15 minuti)

---

## Problemi comuni

- **Display illuminato ma vuoto:** regola il trimmer del contrasto.
- **`ImportError: no module named 'lcd'`:** `lcd.py` non è stato salvato sul Pico (non sul computer), oppure ha un nome diverso.
- **`Permission denied: '/dev/ttyACM0'` (Linux):** aggiungi il tuo utente al gruppo che possiede la porta (`uucp` su Arch, `dialout` su Debian/Ubuntu), poi esci e rientra dalla sessione.
- **"Glances offline" sul display:** controlla l'IP in `config.py` e che il container sia attivo.
- **Il Wi-Fi non si connette:** verifica che la rete sia a 2.4 GHz e che SSID e password siano corretti.

---

## Link utili

- [Glances](https://github.com/nicolargo/glances)
- [MicroPython per Pico W](https://micropython.org/download/RPI_PICO_W/)
- [Documentazione MicroPython](https://docs.micropython.org)



