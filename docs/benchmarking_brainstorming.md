# Benchmarking Notes

The goal of benchmarking within this project is to get a better idea of the 
hardware we are working with, i.e. its capabilities/constraints.

## Preliminary Questions

- If a ping-pong (i.e. there and back) message is not easily programmable, 
  than we're going to run into many issues benchmarking, this should be 
  found out soon!
- Meshcore = save shortest path found from flooding. Is that shortest path 
  the shortest in latency (time)?
- What is even measurable on meshcore? latency duh, bandwidth duh, but other 
  than that? Definitely those metrics mentioned in the FAQ!
- Does MeshCore have a network management protocol?
- What does Mesh claim is the maximum throughput of their devices? Transmission 
  delay?

## Benchmarking Questions 

- How does variable height impact packet latency/packet loss
- How does variable hops impact packet latency/packet loss
- How does variable distance impact latency/packet loss 
    - With and without intermediary repeaters
    - This will also helpt to discover more about how shortest path works 
      in real world
    - Goal: If I message a node in range, but there's intermediary nodes, 
      should I use them? Why/why not?
- How does variable traffic intensity impact packet latency/packet loss?
- Flooding vs. Saved path performacne?
    - This would help us answer: is meshcore even preferrable to meshtastic?
    - Presumably flooding will always be fastest, but the negative is network 
      congestion, so a test of 
