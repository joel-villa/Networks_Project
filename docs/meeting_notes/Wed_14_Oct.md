# Wed 14 Oct

## Other NOtes

- Presentations on 1st week of December

## Weekly Progress

- Carly: 
  - Quinn's paper:
    - How many people could use this implementation?
- Joel: 
  - Latency working
- Natalie:
  - Implemented packet capturing
    - MQTT: make mesh nodes interact w/ devices (driver)
    - 'Able to see the raw'
  - Made a script for fingerprinting the current bot:
    - Packet is the same everytime => it's trivially easy to fingerprint
    - Added message padding to prevent this
  - Papers
    - Radio Security
    - Satelite Security + Testing
    - Law enforcement encrypts + unencrypts by using a key to determine what 
      channel you're going to use
      - Could just jam all frequencies to prevent this
- Quinn:
  - Wikipedia: HTML or Wikitext
  - Paper: village in Africa implemented 'VillageShare'
    - All info routed through a satelite
    - More packet loss at peak times (50%)
    - Would cache updates during off-peak times
    - Takeaway: how to deal with bursty traffic?

## Some Latency Results

- Why higher latency?
  - Forward error correction? Easier to correct larger packets
  - Could be a DDOS prevention?

## Internet Gateway Object Digaram

- Doesn't have computer:
  - Gets plain text
- Has a computer:
  - Using curl + raw

## Issue with Requested Nodes

The Heltec T114 w/o screens are not user friendly (need to be outside of case
to be plugged in), what to do?

- Joel will send email

## Action Items for Next Week

- Carly:
  - flash node
  - RDT 
- Joel:
  - Finish Frame loss  implementation
- Natalie:
  - Inspect previous meshcore vulnerabilities that have been 'patched'
  - Packet metadata capture
- Quinn:
  - RDT
