# Meeting Minutes Wed 23 Sep

## Catchup

- Joel:
    - Read an RFC
    - Simulation is possible, but maybe 
    - Goals:
        - Start basic benchmarking
        - Hopefully find a paper on benchmarking LoRa
- Quinn:
    - Papers:
        - Speeds are in kB/min
        - Border paper
            - Decentralized LoRaWAN: 5 base stations
            - Centralized 
    - Demo:
        - Server node can do LLM
        - 150 chars is restrictive
- Carly:
    - Papers:
        - Take environment into account 
        - Rayleigh Fading:
            - Statistical model for how radio waves propogate
            - Probability of reaching certain distances
        - Multi-path Effects: 
            - Multiple antenas in an area, interferance with attenas
            - Q: How is interference prevented
        - Preventing packet clash/dropout:
            - Spread, frequency
    - Goals:
- Natalie:
    - Github:
        - Open Security Issues:
            - Old concerning
            - Encryption without padding
        - Had a buffer overflow attack?
            - Send an oversized packet -> can overwrite the public key of the 
              sender, allowing for impersonation
        - CVE: security flaw identifier
            - Of those seen, none seem applicable to us
    - Tore:
        - Anyone can be stood up as a server
        - Elegant way to deal with data?
    - Drivers for the Heltec devices:
        - MacOS: 1
        - Linux & Windows

## The Meat Meeting

- Natalie and Quinn objects to the name

### The Why

- MeshCore = more private
- MeshCore = more access
- Both or one specifically?
- Access is main concern:
    - Privacy is a secondary concern, that we should not loose track of
- There are reasons why you don't trust your idea, reasons why you may wnt a 
  buffer

### Reasearch Questions

- What does it mean to share internet over a Mesh Network
- What does it mean to test the performance of an internet connection over 
  MeshCore
- How quickly can you send how much data?
- Is it possible to a replace an Internet connection without access to an ISP
- If it is possible can it be done in a secure way?
- How can you ensure with keeping the philosophy of anyone can be a server 
  while also allowing user privacy
- How can we make it so not all the trust is on a single node?
- Are there ways of fingerprinting public key?
- Pros and Cons of Mesh Network?
    - Jamming = useless
    - What other disadvantages?
- Is path saving fingerprintable?
- How easy is it to triangulate where a person is?
- Bunch of benchmarking questions

### The What

- Should we change scope to not all of Internet, but only specific ones?
- High level outline?
- The role of code? 
    - According to Dr. Palacios: could be an appendix in the paper -> link to 
      github + demo in presentation
      
## Stop! Demo Time

- It would be easy to implement history
- NSFW filtering, character limit, chunking, etc

## Goals For Next 

- Joel
    - Ping pong test + LoRaWAN Benchmarking test
- Quinn
    - Paper on actual implementations of the network
- Carly
    - Hardware related privacy papers
- Natalie 
    - Find security vulnerabilities on GitHub, plus implementation of 
      the 
    - Fuzzing bug test (bug in Meshcore)
