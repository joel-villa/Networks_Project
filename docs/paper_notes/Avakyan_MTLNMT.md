# Methodology for testing LPWAN networks with mesh topology

Y. Avakyan, E. Kuznetsova, and R. Kirichek, “Methodology for testing LPWAN networks with mesh topology,” The 4th International Conference on Future Networks and Distributed Systems (ICFNDS), pp. 1–6, Nov. 2020, doi: 10.1145/3440749.3442623

## TLDR

Not a great paper, found some potentially useful resources though:
1. IETF RFC 2544:
    - https://www.rfc-editor.org/info/rfc2544/
2. Mesh simulation w/ omnet++: 
    - https://www.rfc-editor.org/info/rfc2544/#appendix-A
    - https://omnetpp.org/download-items/FLoRA.html
    - https://omnetpp.org/download/


## Definitions

## Quotes + Commentary

> "The proposed methodology is based on the IETF RFC 2544 specification. Model-based testing allows automating the testing process. For this, a simulation model of an LPWAN network with mesh topology based on LoRaWAN was developed in the OMNeT++ simulation environment."
- Both seem like strong places to look:
    - https://www.rfc-editor.org/info/rfc2544/#appendix-A
    - https://omnetpp.org/download-items/FLoRA.html
    - https://omnetpp.org/download/
    - https://inet.omnetpp.org/Installation.html

> "Some articles include methodologies for testing LPWAN networks. In one of them, a methodology for testing various LPWAN technologies is proposed, designed to determine the most effective one when used in the same conditions [4].Another article contains a measurement methodology for experimentally evaluating timing performance of an entire real LoRaWAN infrastructure [5].It proposes to measure network latency using messages containing timestamps. The article [6] discusses an approach to studying the characteristics of a LoRaWAN network using test benches and conducting tests with different network parameters and conditions"
- These might some more good resources, there is a bit of weird grammar in this
  paragraph, hopefully that isn't too concerning, let me check the number of 
  papers that cite this one: 1, eeesh. I'm going to read it anyway with that in
  mind.

### Introduction

### Technology Overview

### Model Network

### Testing Methodology

- Quickly reading through this, I can tell this is not a useful source, sigh.
  I'll check on the ones it cited...

### Simulation Modeling

### Test Results

### Conclusion
