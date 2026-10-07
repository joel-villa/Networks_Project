# LoRaX: Repurposing LoRa as a Low Data Rate Messaging System to Extend Internet Boundaries

M. Vigil-Hayes, M. N. Hossain, A. K. Elliott, E. M. Belding, and E. Zegura, “LoRaX: Repurposing LoRa as a Low Data Rate Messaging System to Extend Internet Boundaries,” ACM SIGCAS/SIGCHI Conference on Computing and Sustainable Societies (COMPASS), pp. 195–213, June 2022, doi: 10.1145/3530190.3534807.

- Note that I am taking these notes with an emphasis on benchmarking

## TLDR

From a benchmarking perspective, this paper affirms that (for the most part) 
typical benchmarking techniques can be applied to LoRa, with that caveat being 
the uniqueness that comes with LoRa and the Chirp Spread Spectrum.

## Definitions

- Round Trip Time: "Round-trip time (RTT) in networking is the time it takes
  to get a response after you initiate a network request"
    - Source: https://aws.amazon.com/what-is/rtt-in-networking/
- End-to-end latency:  E2E latency refers to the total time taken for a data 
  event to be ingested, processed, and delivered to its final destination

## Quotes + Commentary

### 4 Evualtion

#### 4.1 Measurement Methodology

> "In particular,
we focus on the end-to-end latency that a user experiences when
initiating an Internet service action on an end device as well as
the round trip time to receive a confirmation"
- This is literally the easiest thing to benchmark glad its what they prescribe

> "Therefore we
also measure packet loss that would lead to either a failure report
to the user or retransmissions that increase effective latency"
- So you're telling me, that if we do those two things + affects of bursty 
  traffic (which I think we should), then we'd be doing more than a published 
  paper. Wicked!

> " In particular, as illustrated in Figure 6,
our measurement setup utilizes two compound repeaters (Figure 5)"
- Just me or are those compound repeaters fucking hot?

> "We restricted the payload sizes to be 13 bytes as this was
the minimum number of bytes required for encoding the necessary
data to make a successful Etsy API call"
- Again, I think this should make us consider using something like Etsy where 
  we can feasibly reduce information, we can't really do that with Wikipedia 
  pages, less we're willing to use a compression algorithm (zip). Also do we 
  know if we're guaranteed ordered delivery? Guess that's something to look 
  out for in benchmarking! :D
