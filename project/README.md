


quello che prima era un semplice passaggio tra una porta e l'altra,
   ad esempio: s2 --> iperf h3 h4,
   ora devo settare il match per vedere che pacchetto è


sudo ovs-vsctl del-controller s3


sudo ovs-vsctl set-controller s3 tcp:127.0.0.1:6633


h0 ---10Mps---                              ---10Mps--- h1
             |                              |
             |                              |
             |  |---5Mps--- s0 ---5Mps---|  |
             |  |                        |  |
              s1                          s3
             |  |                        |  |
             |  |---5Mps--- s2 ---5Mps---|  |
             |                              |
             |                              |
h2 ---10Mps---                              ---10Mps--- h3
             |                              |
             |-----5Mps---- s4 ----5Mps-----|




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







