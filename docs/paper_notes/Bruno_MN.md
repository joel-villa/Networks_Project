# Mesh Networks: Commodity Multihop Ad Hoc Networks

R. Bruno, M. Conti and E. Gregori, "Mesh networks: commodity multihop ad hoc networks," in IEEE Communications Magazine, vol. 43, no. 3, pp. 123-131, March 2005, doi: 10.1109/MCOM.2005.1404606. keywords: {Mesh networks;Spread spectrum communication;Ad hoc networks;Wireless mesh networks;IP networks;Intelligent transportation systems;Mobile ad hoc networks;Wireless LAN;Buildings;Testing},

Text: https://ieeexplore.ieee.org/abstract/document/1404606

## TLDR

An article from 2005, that has an in-depth overview of the
mesh-network landscape of the time. Some key takeaways that directly
relate to our project are as follows: using mesh as an accessible means
to extend internet access is not unprecedented; ad-hoc networks have a
network-diameter bottleneck; all layers of an ad-hoc network must be self-
manageable, self-configurable, and self-healing; fairness in ad-hoc networks
is complex.

## Definitions

1. Ad Hoc Network: "A wireless network that allows easy connection 
   establishment between wireless client devices in the same physical area 
   without the use of an infrastructure device, such as an access point or a 
   base station." https://csrc.nist.gov/glossary/term/ad_hoc_network
2. Network Diameter: "is the longest shortest path between any two nodes in a 
   graph. In plain terms, it tells you the worst-case communication distance 
   inside a network, whether that network is a LAN, a WAN, a social graph, or 
   a biological system. If you need a fast way to judge how “wide” a network 
   really is, this is the metric to start with." 
   https://www.ituonline.com/tech-definitions/what-is-network-diameter/
3. Beamforming: "beamforming creates an effective antenna pattern at the 
   receiver with high gain in the direction of the desired signal and low gain 
   in all other directions." from this paper
## Quotes and Comments

> "An example of the first class are so-called community networks built (mainly) on 802.11 technology and aimed at providing Internet access to a community of users that can share the same Internet access link [3]. Some examples of this are Seattle Wireless, Champaign-Urbana Community Wireless Network (CUWiN), San Francisco BAWUG, and the Roofnet system at MIT (MIT Roofnet)"

Let's go we're not the first to do this! I wonder if these systems are still 
up and running? Seems like No

> "Portsmouth Real-Time Travel Information System (PORTAL), a system that, as part of a citywide public transportation communications network, aims at providing real-time travel information to passengers.3 This system is realized by equipping more than 300 buses with mesh technology provided by MeshNetworks Inc"

Very cool, doesn't seem like they are currently still using Mesh, that's okay, 
proof of concept!

> "Reliability. The wireless backbone provides redundant paths between each pair of endpoints, significantly increasing communications reliability, eliminating single points of failure and potential bottleneck links within the mesh. Network resilience and robustness against potential problems (e.g., node failures, and path failures due totemporary obstacles or external radio interference) is also ensured by the existence of multiple possible destinations (i.e., any of the egress points toward the wired Internet) and alternative routes to these destinations."

Answers the question: "why are more repeaters always a good thing?" I wonder 
why meshtastic was made to have a limited number of hops? What is the benefit? 
It feels like it's taking away one of the main strenghts of an ad-hoc network.

> "Self-management. The adoption of peer-topeer networking to build a wireless distribution system provides all the advantages of ad hoc networking, such as self-configuration and self-healingness. Consequently, network setup is automatic and transparent to users. For instance, when adding additional nodes in the mesh, these nodes use their meshing functionalities to automatically discover all possible wireless routers and determine the optimal paths to the wired network. In addition, the existing wireless routers reorganize, taking into account the new available routes. Thus, the network can easily be expanded, because the network self-reconfigures to assimilate the new elements."

Now we're talking. This makes too much sense. I guess this argues another 
issue: What to do when not enough mesh resources in your area? Hmmm. Hard to 
say, but I guess you can't really get the benefits of an ad-hoc network without 
the cons... This is potentially one benefit of hot-spots over mesh, where 
the infrastructure is there already? At least in the context of 'extending the 
internet'.

> "community networks could be used to provide shared cost-effective broadband Internet access to a neighborhood, to implement neighborhood surveillance and emergency response systems, and to distribute content useful to the neighborhood (e.g., a neighborhood portal providing a community with an online bulletin board that allows neighbors to post items for sale or trade gossip)."

Bars! I wonder if this paper touches on how such a network could be undermined?

> "Consequently, IEEE 802.11 is the radio technology used in the Roofnet community, because cheap network cards operating in unlicensed bands are available."

I wonder if MeshCore uses an IEEE standard? Gemini says no

> "Only the gateways (i.e., the nodes bridging the mesh network with the wired Internet backbone) are equipped with directional antennas to provide extended coverage."

So we aren't the first to do this for real, fire! This made me think of some 
questions about benchmarking our internet access bot, how can we ensure that 
we are not doing a DDOS attack on the mesh-network? Is there a way to make it 
so that we know any messages are only going through our specific repeaters (I
think so)? Oooh, idea! We do the mountain benchmarking test if possible, and 
get the best repeater setup found. and use that exact same setup, have all 
mesh nodes set to make the same query at the same time from the network (idk 
if this is possible) and see how slow things go...

> "The company has developed its own wireless routing protocol, called Predictive Wireless Routing Protocol (PWRP), that does not rely only on hop count to detect transmission paths, but compares packet error rates and other network conditions to determine the best path at a given moment"

I wonder what MeshCore's path finding algorithm is? Couldn't find anything on 
this in https://docs.meshcore.io/faq/

> "In practice, this simplification will undoubtedly lead to the well-known scalability limits of ad hoc networks due to the dramatic degradation of throughput and delay performance as the network diameter increases [5]"

What is network diameter? What causes these limitations? A: longest, shortest 
path

> "Diversity provides the receiver with several (ideally independent) replicas of the transmitted signal and is therefore a powerful technique to combat fading and interference. On the other side, spatial multiplexing divides the channel into multiple “spatial channels” through which independent data streams or signals can be coded and transmitted simultaneously"

Gosh I wish this paper wasn't so old, but this is good note as to why multiple 
repeaters may be a good thing. I don't think Meshcore allows for multiple 
repeaters to broadcast the same message. Am I wrong? It seems like there are 
obvious advantages and disadvantages to that. 

> "it is worth pointing out that mesh networking, as a special case of ad hoc networking, should fully implement self-management, self-configuration, and self-healing features in all layers of the network architecture"

This feels like a strong warning for our bot implementation. 
Self-configuration can be achieced through open-source code. Self-healing: how
to prevent the source node from being overloaded? What does it mean to self 
heal in this context? Self-management: isn't this just inherint with Mesh? ie 
you get to choose whether or not to use the bot, which bot to use, whether you 
want to setup a bot of your own, etc?

> "In [10] a novel fairness model has been proposed that addresses the requirements of multihop aggregated flows, aimed at eliminating the spatial bias by ensuring that each user receives the same fair share of resources independent of how far it is from the Internet entry point (i.e., independent of its spatial location)."

Now this is just cool. I wonder if there is any recent research on fairness 
in multihop networking that we could look at?
