# Non-Internet Based Communication

## Current Hardware Ideas

- Mesh
- Bluetooth
- Ultrasonic (Wavest): https://github.com/bennjordan/Wavest


## Project Goals (Work In Progress):

1. Compilation of literature on methods of communication in emergency contexts
  i.e. **NO** internet connection
2. Inhouse testing of things (acquire hardware, setup, etc.)
3. Educate the class on how to use mesh or some other form of
  communication. With the goal of answering the following questions:
    1. What is mesh (or other method)? Non internet based method of local 
    communication 
    2. How expensive is the hardware? 
    3. Where to buy?
    4. How to setup?
    5. **How to ensure privacy/security?**
        1. Is it encrypted?
        2. How to know when data is recieved? Do you care?
        3. Handshake?
    10. What is the range? 
    11. What kind of information/files can be sent?
    12. Why would this stay up in a scenario when the internet goes down?
    13. How are messages prioratized? In what order are messages recieved?
4. Collect data about the chosen networking hardware. Some potential data 
ideas are as follows (input-pending):
    1. Communication latency (how quick data travels from point a to point b)
    2. Communication bandwidth (how much data can be sent)
    3. Communication ordering (the order in which messages are sent and recieved)
    4. Measure of how adding more devices (repeaters) affects latency + bandwidth
       (this could help argue for a larger scale project, if measurable
       improvements are seen)
    6. Some ideas with privacy concerns:
        1. Distance: how does it affect latency and bandwidth? (requires location
          tracking)
        2. Distance with devices(repeaters) in between (this is a more measurable
           extension of idea (iv.)
5. Publish open-source code for these data tests/see if any already exist
    1. Something akin to Speedtest and Traceroute, but for Mesh?
### Relevant work
- [Post-Disaster Communications: Enabling Technologies, Architectures, and Open Challenges]([url](https://ieeexplore.ieee.org/abstract/document/9832657))
- [Designing delay constrained hybrid ad hoc network infrastructure for post-disaster communication]([url](https://www.sciencedirect.com/science/article/abs/pii/S1570870514001802))
- [Context-Aware Self-Adaptive Routing for Delay Tolerant Network in Disaster Scenarios]([url](https://www.sciencedirect.com/science/article/abs/pii/S1570870519301507))
- [HERMES: Metric-Driven Multi-Transport Routing for Civilian Messaging During Connectivity Disruption]([url](https://www.mdpi.com/2673-8732/6/3/64?))

