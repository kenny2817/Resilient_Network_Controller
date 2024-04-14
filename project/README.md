## Comandi di inizzializzazione
Prima attivare il controller. 
ATTENZIONE: dopo l'avvio del comando si hanno 10 secondi per creare la network
```bash
ryu-manager ryu_controller.py &
```

Creare la network:
```bash
sudo python3 network.py
```

## Descrizione network
Gli host sono collegati a coppie:
h1 con h2 
e
h3 con h4

h1 e h2 hanno canale specifico per UDP messages su porta 9999 (collegamento s2 - s1 - s4)
h3 e h4 hanno canale specifico per UDP messages su porta 9997 (collegamento s5 - s6 - s7)

canale doppio su s2 - s3 - s4 --> 5Mbps per canale, qui passano tutti i messaggi tcp, icmp e udp con porta non specificata

## Comandi mininet per verificare corretto funzionamento
Controllo collegamenti:
```bash
pingall
```

Controllo pacchetti icmp:
```bash
h* ping -c3 h*
```

Controllo pacchetti tcp:
```bash
iperf h* h*
```

Controllo pacchetti udp:
Settare il receiver:
```bash
h1 iperf -s -u -p 9999 -b 10M &
```
Settare il sender:
```bash
h2 iperf -c h1 -u -p 9999 -b 10M -t 10 -i 1
```

Bisogna cambiare porta per verificare che i pacchetti udp di porte diverse da quella specifica finiscano sulla coda da 5Mbps.

## Comandi bash per verificare corretto funzionamento
Volendo si possono controllare le regole di tutte le switch tables con lo script bash:
```bash
./show_tables.sh
```

## Comandi bash per cambiare scenario

Per ora gli scenari funzionanti correttamente sono:
 - tutto funzionante
 - rotto s6

# disconnettere switch
```bash
sudo ovs-vsctl del-controller s6
```
# riconnettere switch
```bash
sudo ovs-vsctl set-controller s6 tcp:127.0.0.1:6633
```


## rappresentazione network

<p align="center">
  <img src="images/bash network.png" width="400">
</p>

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




h0            s0           h1
   \        /   \        /
    \      /     \      /
     \    /       \    /
      \  /         \  /
       s1           s3
      /  \         /  \
     /    \       /    \
    /      \     /      \
   /        \   /        \
h2           s2            h3
   \                     /
    \                   /
     \                 /
      \----- s4 ------/



h0                              h1
   \                          /
    \                        /
     \   ------ s0 ------   /
      \  |              |  /
       \ |              | /
        s1              s3
       / |              | \
      /  |              |  \
     /   ------ s2 ------   \
    /                        \
   /                          \
h2 ------------ s4 ------------ h3




         ------ s0 ------ 
         |              | 
         |              | 
h0 ---- s1              s3 ---- h1
       / |              | \
      /  |              |  \
     /   ------ s2 ------   \
    /                        \
   /                          \
h2 ------------ s4 ------------ h3


         ------ s0 ------ 
         |              | 
         |              | 
h0 ---- s1 ---- s2 ---- s3 ---- h1
         |              |
         |              |
h2 ---- s4 ---- s6 ---- s6 ---- h3



h0                        h1
   \                    /
    \                  /
     \       s0       /
      \    /    \    /
       \  /      \  /
        s1        s3
       /  \      /  \
      /    \    /    \
     /       s2       \
    /                  \
   /                    \
h2 --------- s4 -------- h3







