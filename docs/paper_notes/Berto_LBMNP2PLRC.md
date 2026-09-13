# A LoRa-Based Mesh Network for Peer-to-Peer Long-Range Communication

R. Berto, P. Napoletano, and M. Savi, “A LoRa-Based Mesh Network for Peer-to-Peer Long-Range Communication,” Sensors, vol. 21, no. 13, p. 4314, Jan. 2021, doi: 10.3390/s21134314.

## TLDR

## Defintions

- Chirp Sum Spectrum (CSS): "Chirp spread spectrum is a technique known from the physical layer of LoRaWAN [8]. The standard uses chirp spread spectrum (CSS) as modulation to transmit over large distances in the 868MHz band"
    - https://doi.org/10.1109/SCVT.2016.7797659
- Forward Error Correction (FEC): "is a process of adding redundant bits to the data to be transmitted. During the transmission, data may get corrupted by interference (changes from 0 to 1 / 1 to 0). These error correction bits are used at the receivers for restoring corrupted bits."a
    - https://www.thethingsnetwork.org/docs/lorawan/fec-and-code-rate/
- "star-of-star" topology: "where end devices communicate with one or more gateways (using LoRa as the physical layer) and where each gateway dispatches LoRaWAN frames to the network server using a higher-throughput backhaul interface (e.g., WiFi or 5G)"
    - See article
- “star-of-meshes” topology: "gateways still play a central role as concentrators, and that data need to be finally conveyed through Internet/broadband access, to a remote location before being made accessible to applications."
    - See article

## Questions and Cmmentary

> "the gateway is a single point of failure whose malfunctioning would compromise the operation of the whole LPWAN network."
- Hence why we need to make a bot/app that anyone could easily deploy! I 
      am excited! How to make this bot as accessible as possible should be one 
      of our priorities. How to do that?
> "
