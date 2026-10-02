# Wed 30th Sep

## Weekly Progress

- Joel:
  - Ping Pong is possible
- Quinn:
  - Paper Notes:
    - Internet sharing over LoRa + Broadband (Internet)
    - High capacity link + low capacity link = limits services
    - What's new?
      - This paper implemented it with etsy
    - Benchmarking = machine to person:
      - latency, round trip time, throughput
    - Challenges of using LoRa with Internet sharing:
      - Low-level stuff => handled by Meshcore
      - Meshcore => its own challenges
    - Should we say this is our primary goal
    - Compressing API calls?
    - If you're message makes it to the reciever, it's going to look like how 
      you sent it, but if it doesn't Meshcore doesn't do that for you
- Carly:
  - Looked into Wikipedia API calls
  - Spectrum Congestion: too many requests
    - Packet size => packet loss + collision
    - Solution: number packets
  - Licensing Spectrum: finite wavelengths
    - FEC regulates who gets how much of the electromagnetic spectrum
  - Limiting mesh:
    - Latency: multi-hopping
  - Does packet loss require stamping it with a session token? How do you 
    rebuild it from the numbers?
    - A packet can just be dropped
- Natalie:
  - Fun APIs:
    - cat facts, weather
  - APIs for IP checking
  - Proof of concept for an attacker seeing if you send the same message twice:
    - Add padding to prevent this?

## Presentation Outline

1. Why Care
  - Problem
  - Circumvent ISP (w/ Mesh) => freedom of information
2. What is Meshcore
  - How does it address problem
3. Demo
  - Problem + Why Care
  - Advantages + Limitations
4. Security
  - Advantages: distributed fingerprint
  - limitations?
5. Benchmarking
  - Limitations: Internet access will be slower/less reliable
  - advantages?
5. Conclusion

### What do we want our demo to be?

- Everyone give some of their background?
  - Dr Palacios: ensure we maintain a focus
- Baseline demo?
  - Google scholar
- Simple bot then robust bot?

### Miscellanoues Notes

- Wikipedia is blocked in several countries
- War between ISPs and VPNs 
  - Turkey last month blocked 26 VPN providers
- Tons of cites to detect VPNs => throttle 'em, make 'em unusable
  - VPNs are fingerprintable

### What do we want to teach the class?

- Background on LoRa
- Background on profiling

### Tie into course materials

- Where does it fall on Network stack?

## What to Implement?

- HTML? w/ `curl`
- Descriminate on tags
- encode head as h, p as p, div as d, etc.

## Benchmarking

- TODO for Joel: how to benchmark server

## Wikipediaing with Nataling

- Benchmarking: no longer constrained by just hardcore--cannot do more than 200
  wikipedia requests per second
- IMPORTANT NOTE:
  - May not always have `/dev/USB0`
- Has wikipedia API interfacing setup
- Has knock knock jokes
- Easy to hookup
- Bot over bluetooth

## Action Items for NExt Week

- ***Everyone wants to read the paper***

- Joel:
  - Read Quinn's paper
  - Implement ping-pong
  - Test how distance impacts latency
  - How to benchmark service
- Carly
  - Read Quinn's paper
- Quinn
  - Finish paper
  - TLDR of paper points (are they applicable? What to look into?)
    - relevancy 
  - More paper
- Natalie
  - Wikipedia demo working again
  - Read Quinn's paper
  - Security/motivation
  - Encryption bug?
