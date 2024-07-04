English version [here](README.md)

---

# Resilient Network Controller

> Il progetto Resilient Network Controller è progettato per garantire che le operazioni di rete rimangano fluide e ininterrotte, anche in caso di guasti agli switch. Riorganizzando dinamicamente la rete e fornendo monitoraggio in tempo reale e risposte automatizzate, questa soluzione migliora l'affidabilità e le prestazioni delle reti moderne, rendendole più resilienti ed efficienti.

## Contenuti
- [Caratteristiche Principali](#caratteristiche-principali)
- [Benefici](#benefici)
- [Casi d'Uso](#casi-duso)
- [Iniziare](#iniziare)
- [Rappresentazione Grafica](#rappresentazione-grafica)
- [Testing](#testing)

---

### Caratteristiche Principali

- **Riorganizzazione Dinamica della Rete**:
    - Il controller monitora continuamente lo stato di tutti gli switch all'interno della rete.
    - Al rilevamento di un guasto allo switch, il controller identifica immediatamente percorsi alternativi e riconfigura la rete per bypassare lo switch guasto.
    - Questa riorganizzazione riduce al minimo i tempi di inattività e garantisce che i servizi di rete rimangano ininterrotti.

- **Risposta Automatizzata**:
    - Implementa meccanismi di risposta automatizzati per gestire i guasti degli switch senza intervento manuale.
    - Garantisce un rapido recupero e riduce il rischio di interruzioni prolungate della rete.

### Benefici

- **Maggiore Uptime della Rete**: Riduce l'impatto dei guasti degli switch, garantendo che i servizi di rete rimangano disponibili.
- **Affidabilità Migliorata**: Migliora l'affidabilità complessiva della rete fornendo percorsi ridondanti e meccanismi di failover.
- **Conveniente**: Riduce la necessità di gestione e risoluzione dei problemi di rete manuale, abbassando i costi operativi.
- **Prestazioni Migliorate**: Mantiene prestazioni ottimali della rete adattandosi dinamicamente ai cambiamenti della topologia di rete.

### Casi d'Uso

- **Reti Aziendali**: Garantisce la continuità aziendale mantenendo i servizi di rete in ambienti aziendali.
- **Data Center**: Migliora l'affidabilità delle reti dei data center, prevenendo interruzioni nelle applicazioni e nei servizi critici.
- **Reti Universitarie**: Fornisce connettività robusta per le istituzioni educative, supportando l'accesso ininterrotto alle risorse e ai servizi online.


## Iniziare

Comandi di Inizializzazione
Per avviare la rete e il controller, basta eseguire lo script:

```bash
./run.sh
```
Questo script si occuperà di:
- Impostare i permessi necessari per i vari script
- Convertire i file .sh in formato Unix
- Avviare il controller in background
- Creare la rete

## Descrizione della Rete
Ci sono 4 host (h) accoppiati come segue:
- h1 con h2
- h3 con h4

Ci sono 7 switch (s) che creano 3 canali:
1. h1 e h2 hanno un canale dedicato per i messaggi UDP sulla porta 9999 (connessione s2 - s1 - s4)
2. h3 e h4 hanno un canale dedicato per i messaggi UDP sulla porta 9997 (connessione s5 - s6 - s7)
3. Canale doppio su s2 - s3 - s4 --> 5Mbps per canale. Tutti i messaggi TCP, ICMP e UDP con porte non specificate passano di qui.

## Rappresentazione Grafica
<p align="center">
  <img src="images/bash network.png" width="600">
</p>

## Testing

<details>
<summary>Comandi Mininet per Verificare il Corretto Funzionamento</summary>

---

Verifica connessioni
```bash
pingall
```

Verifica pacchetti ICMP
```bash
h* ping -c3 h*
```

Verifica pacchetti TCP
```bash
iperf h* h*
```

Verifica pacchetti UDP
- Imposta il ricevitore
```bash
h1 iperf -s -u -p 9999 -b 10M &
```
- Imposta il mittente
```bash
h2 iperf -c h1 -u -p 9999 -b 10M -t 10 -i 1
```

Cambia la porta per verificare che i pacchetti UDP con porte diverse da quella specificata finiscano nella coda da 5Mbps.
  
</details>

<details>
<summary>Script Bash per Verificare il Corretto Funzionamento</summary>

---

Per controllare le regole di tutte le tabelle degli switch
```bash
./show_tables.sh
```

Cambia Scenario
- Disconnetti switch:
```bash
sudo ovs-vsctl del-controller s6
```
- Riconnetti switch:
```bash
sudo ovs-vsctl set-controller s6 tcp:127.0.0.1:6633
```

</details>

---

```
                   |---10Mbps--- s1 ---10Mbps---|
                   |                            |
h0 ----10Mbps---- s2                            s4 ----10Mbps---- h1
                 |  |                          |  |
                 |  |---5Mbps--- s3 ---5Mbps---|  |
                 |                                |
                 |                                |
h2 ---10Mbps--- s5                                s7 ---10Mbps--- h3
                 |                                |
                 |----10Mbps---- s6 ----10Mbps----|
```
```
         ------ s0 ------ 
         |              | 
         |              | 
h0 ---- s1 ---- s2 ---- s3 ---- h1
         |              |
         |              |
h2 ---- s4 ---- s6 ---- s6 ---- h3
```
