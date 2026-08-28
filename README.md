# Non-Internet Based Communication

## Project Goals (Work In Progress):

1. Compilation of literature on methods of communication in emergency contexts
  i.e. **NO** internet connection
2. Build the network (acquire hardware, setup, etc.)
3. Educate the class on how to use mesh with the goal of answering the
   following questions:
    1. What is mesh?
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

### Further Goals (Feel Free to Suggest/Add To This):

#### Network Benchmarking

Collect data about the chosen networking hardware. Some potential data ideas 
are as follows (input-pending):

1. Communication latency (how quick data travels from point a to point b)
2. Communication bandwidth (how much data can be sent)
3. Communication ordering (the order in which messages are sent and recieved)
4. Measure of how adding more devices (repeaters) affects latency + bandwidth
5. Distance, Line of Sight, and Elevation: how do they affect communication 
   speeds?
6. Distance with devices (repeaters) in between (this is a more measurable
   extension of idea (4.)

Could also look into efficacy of writing programs which could do these tests
(I'm thinking something akin to SpeedTest or TraceRoute--Mesh has Traceroute
though)

#### Security Testing/Bolstering

I doubt we'd be able to make any meaningful additions in terms of security, 
but it may be interesting to look into what penetration testing looks like 
in the context of a non-Internet-based network

#### Application Development

Take this idea with a grain of salt, I don't know how feasible it is, but we 
could look into the capacity of making Apps for Mesh to do cool things such as
but not limited to:

1. File Transfer
2. Mesh-Networked Gameplay (something simple like Pong, idk)

This also may be swaying too much from the prime goal which is reliable 
communication in times of crisis (people playing games over network would 
unneccessarily use up resources)

#### Your Idea Here

## Relevant work
 
### Natalie's

- M. Matracia, N. Saeed, M. A. Kishk and M. -S. Alouini, "Post-Disaster Communications: Enabling Technologies, Architectures, and Open Challenges," in IEEE Open Journal of the Communications Society, vol. 3, pp. 1177-1205, 2022, doi: 10.1109/OJCOMS.2022.3192040.
keywords: {Computer architecture;Wireless communication;Satellites;Ad hoc networks;Routing;Mesh networks;Coverage;stochastic geometry;non-terrestrial networks;resilience;backhaul;6G},
    - https://ieeexplore.ieee.org/abstract/document/9832657
- Sujoy Saha, Subrata Nandi, Partha Sarathi Paul, Vijay K. Shah, Akash Roy, Sajal K. Das, Designing delay constrained hybrid ad hoc network infrastructure for post-disaster communication, Ad Hoc Networks, Volume 25, Part B, 2015, Pages 406-429, ISSN 1570-8705, https://doi.org/10.1016/j.adhoc.2014.08.009.
    - https://www.sciencedirect.com/science/article/pii/S1570870514001802
- Erika Rosas, Felipe Garay, Nicolas Hidalgo, Context-aware self-adaptive routing for delay tolerant network in disaster scenarios, Ad Hoc Networks, Volume 102, 2020, 102095, ISSN 1570-8705, https://doi.org/10.1016/j.adhoc.2020.102095.
    - https://www.sciencedirect.com/science/article/abs/pii/S1570870519301507

- El Gemayel, C.; El Gemayel, J.; Constantin, J. HERMES: Metric-Driven Multi-Transport Routing for Civilian Messaging During Connectivity Disruption. Network 2026, 6, 64. https://doi.org/10.3390/network6030064
    - https://www.mdpi.com/2673-8732/6/3/64

### Joel's

- S. C. Ng, G. Mao and B. D. O. Anderson, "On the Properties of One-Dimensional Infrastructure-Based Wireless Multi-Hop Networks," in IEEE Transactions on Wireless Communications, vol. 11, no. 7, pp. 2606-2615, July 2012, doi: 10.1109/TWC.2012.052412.111561.
keywords: {Ad hoc networks;Base stations;Wireless communication;Spread spectrum communication;Wireless sensor networks;Australia;Approximation methods;Wireless networks;1-D networks;random geometric graph;connectivity;clusters},
    - https://ieeexplore.ieee.org/abstract/document/627224

- R. Bruno, M. Conti and E. Gregori, "Mesh networks: commodity multihop ad hoc networks," in IEEE Communications Magazine, vol. 43, no. 3, pp. 123-131, March 2005, doi: 10.1109/MCOM.2005.1404606.
keywords: {Mesh networks;Spread spectrum communication;Ad hoc networks;Wireless mesh networks;IP networks;Intelligent transportation systems;Mobile ad hoc networks;Wireless LAN;Buildings;Testing},
    - https://ieeexplore.ieee.org/abstract/document/1404606

