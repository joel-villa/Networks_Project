# A LoRa-Based Mesh Network for Peer-to-Peer Long-Range Communication

R. Berto, P. Napoletano, and M. Savi, “A LoRa-Based Mesh Network for Peer-to-Peer Long-Range Communication,” Sensors, vol. 21, no. 13, p. 4314, Jan. 2021, doi: 10.3390/s21134314.

## TLDR

This article seems to be a foundational piece, in what is the modern advances 
in LoRa based Mesh networks. It gives some foundational knowledge on how the 
hardware works, which seems to be largely applicable to MeshCore directly, in 
their testing, they use the V2 of a device that we currently own the V3 version
of.

## Defintions

- Chirp Sum Spectrum (CSS): "Chirp spread spectrum is a technique known from the physical layer of LoRaWAN [8]. The standard uses chirp spread spectrum (CSS) as modulation to transmit over large distances in the 868MHz band"
    - https://doi.org/10.1109/SCVT.2016.7797659
    - Basedo on Q 5.1, I am convinced that Meshcore uses CSS: https://docs.meshcore.io/faq/
        - NOTE: SF is specifically for Chirp Sum Spectrum
- Forward Error Correction (FEC): "is a process of adding redundant bits to the data to be transmitted. During the transmission, data may get corrupted by interference (changes from 0 to 1 / 1 to 0). These error correction bits are used at the receivers for restoring corrupted bits."a
    - https://www.thethingsnetwork.org/docs/lorawan/fec-and-code-rate/
- Code Rate: "Code Rate of a forward error correction expresses the proportion of bits in a data stream that actually carry useful information."
    - https://www.thethingsnetwork.org/docs/lorawan/fec-and-code-rate/
    - NOTE: MeshCore uses a Code Rate of 4/5, see: https://docs.meshcore.io/faq/
- Spreading Factor: "The spreading factor controls the chirp rate, and thus controls the speed of data transmission. Lower spreading factors mean faster chirps and therefore a higher data transmission rate. For every increase in spreading factor, the chirp sweep rate is halved, and so the data transmission rate is halved."
    - https://www.thethingsnetwork.org/docs/lorawan/spreading-factors/
- "star-of-star" topology: "where end devices communicate with one or more gateways (using LoRa as the physical layer) and where each gateway dispatches LoRaWAN frames to the network server using a higher-throughput backhaul interface (e.g., WiFi or 5G)"
    - See article
- “star-of-meshes” topology: "gateways still play a central role as concentrators, and that data need to be finally conveyed through Internet/broadband access, to a remote location before being made accessible to applications."
    - See article
- Simplex, Half-Duplex, Duplex:
    - Simplex: one device can receive, one device can transmit
    - Half-Duplex: Both devices can recieve and transmit, just not at the same 
      time
    - Full-Duplex: Both devices can recieve adn transmit at the same time
    - https://www.geeksforgeeks.org/computer-networks/difference-between-simplex-half-duplex-and-full-duplex-transmission-modes/

## Questions and Cmmentary

### 1. Introduction and Background

> "the gateway is a single point of failure whose malfunctioning would compromise the operation of the whole LPWAN network."

- Hence why we need to make a bot/app that anyone could easily deploy! I 
  am excited! How to make this bot as accessible as possible should be one 
  of our priorities. How to do that?

### 2. Related Work

> "avoids the presence of a single point of failure, being thus more flexible"

- We need to make it so that any device can become a 'gateway node'. Would 
  this necessitate us knowing various hardware? Or is it as simple as reading 
  the output from a Google Query? Another question: do we even want to use 
  Google? Some other options: Qwant, Ecosia, DuckDuckGo.

##  3. System Architecture

> "The network stack proposed here considers three layers (see Figure 1): (i) a physical layer based on the standard LoRa communication protocol; (ii) a link, network and transport layer for addressing, routing and meshing; (iii) an application layer as interface with real applications (possibly accessible by external networks), including a middleware that enqueues and assigns priorities to the messages that need to be aired. The first two layers are based on a public library designed for embedded microprocessors, named RadioHead"
- I attempted to find if Meshcore used this same library, or if there was 
  any info on a link layer, was not successful. Begs the question: what is the 
  setup for Meshcore's link-layer?

> "For our implementation we use the ESP32 Heltec WiFi LoRa V2 board (https://heltec.org/project/wifi-lora-32/ (accessed on 22 June 2021)), which comes with the Semtech SX1276 LoRa transceiver (https://www.semtech.com/products/wireless-rf/lora-transceivers/sx1276 (accessed on 22 June 2021)) and costs around USD 20"
- Wicked! Natalie got the V3 board! I still wonder if benchmarking would 
  require at least 9 nodes? Should I ask Dr. Bienz? I have yet to find any 
  strong resources on this
- Meshcore minimizes 'flood' messaging by store paths to nodes, but I couldn't 
  find if there is a limit on the number of addresses, presumably it is 
  dependent on your hardware?

## 4. Experimental Evalution

> "Since the employed controller only permits half-duplex communication, the overall transceiver system should be designed to spend as much time as possible in an active listen state so that expensive retransmissions, due to missing payloads or acknowledgments (ACKs), are avoided"

- I can't find if Meshcore is half-duplex or full-duplex. That would be good 
  to know presumably

> "For each transmission setup, we evaluated the delivery time when a 240-bytes payload message is sent. The maximum payload that can be sent by the SX1276 transceiver is 255 bytes,"

- Looking at the Meshcore packet format documentation, they are using a total 
  of at most 253 bytes, makes sense why message limit is 150 bytes now.

> "It is clear that SF plays a key role: the higher the SF is, the higher the delivery time."

- Meschore's SF by default is 7
    - https://docs.meshcore.io/faq/

> ""
