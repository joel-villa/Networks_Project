# Wed 7 Oct

## Quinn's Notes considering applying lessons from the paper,
* Extend the results of the paper, but considering only a single network regime (MeshCore in LoRa) to service limited requests to internet services
### Design
* Limit services offered to those MeshCore is capable of supporting required throughput, latency.
* Storing user data: some application (Wikipedia service) may not require storing any user data at the proxy. Others (Etsy) would require extensive user data storage
* Extending the internet: using MeshCore as the low-bandwidth regime introduces overhead associated with the service
* The proxy would need to translate (potentially) basic requests into fully qualified API calls
* Consider a user front-end for generating calls on behalf of the user. A TUI or CLI could solicit information from the user and translate into intermediary requests to the proxy
* Front end would differ per application (different services available require different forms of interaction with the user)
* Wikipedia: could the server offer additional useful optional services to the user (Ex: favoriting pages to avoid complicated interactions surfing the web, direct URL lookups)
* Extending reach: Paper mentions addtl. work in developing hardware to use a mesh network over off-the-shelf components, theoretically done for us by MeshCore
### Measurement evaluation
* Paper mentions explicit focus on user-perceived metrics: RTT, packet loss, latency perceived by user
* Service must offer reliable transmission or notify the user of its failure
* Paper explicitly disregards internet service component in measurements (since performance is dominated by LoRa communication)
* Timings conducted by sync'd clocks across gateways (hosts) and repeaters, get current time at packet arrival
### Consider for presentation
* Mention system cost for n users, m gateways. Demonstrate example configurations costs
* The paper mentions low data rate networks can add value where high rate networks not available, functionally they are not available if the services they host are blocked

## Joel

### Progress Update

- Finished reading RFC
- Skimmed the paper Quinn found, fully read the section on benchmarking
    - Takeaway: their benchmarking was very minimal. I think it would be easy (hopefully) to implement more than they did, considering we have Meshcore already defining our API calls!
- Implemented a ping-pong, it was super simple
    - Takeaway: MeshCore does ACKs, I will give more updates as the benchmarking becomes more intensive

### Goals for Next Week

- Finish coding the four applicable benchmarking tasks outlined by the RFC (testing along the way with two-three nodes). Those tests include:
    1. throughput (how much)
    2. latency (how fast)
    3. frame loss (how reliable)
    4. back-to-back traffic (how does it handle bursts of traffic). 
