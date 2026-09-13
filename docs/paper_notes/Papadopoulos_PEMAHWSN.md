# Performance evaluation methods in ad hoc and wireless sensor networks: a literature study

G. Z. Papadopoulos, K. Kritsis, A. Gallais, P. Chatzimisios and T. Noel, "Performance evaluation methods in ad hoc and wireless sensor networks: a literature study," in IEEE Communications Magazine, vol. 54, no. 1, pp. 122-128, January 2016, doi: 10.1109/MCOM.2016.7378437. keywords: {Wireless sensor networks;Ad hoc networks;Analytical models;Performance evaluation},

https://ieeexplore.ieee.org/abstract/document/7378437

## TLDR

This papers is an analysis of the methodologies of over 1,000 ad-hoc network 
related papers, the author's emphasize reproducability, though they do not 
provide strong suggestions as to how to achieve this outside of a simulation 
setting. The paper gives a high-level suggestion in-terms of how to do 
performance evaluation in an ad-hoc context: initial real-world testing 
(to get a feeling for 'noise' in the network), followed by simulations, 
followed by a final stage of real-world testing--with an emphasis on 
reproducability throughout.

## Definitions

## Quotes and Comments

> "Simulators indeed fail to reproduce actual environmental conditions of deployed systems."

- This is unsurprising, I was thinking it would be extremely hard for us to 
  setup an accurate simulation with Radio, specifically utilizing Albuquerque's
  terrain. I wonder how many nodes/repeaters would be sufficient for real world
  tests?

> "More specifically, simulators allow users to implement some basic assumptions (e.g., link quality, radio propagation, medium interferences, topologies) [3]. Although the majority of the simulation models cannot capture real world complexity [4, 5], they are often utilized as a first step"

- This is convincing me that making a simulator may be a good/cool thing to do.
  I am worried that it would be too much of a time sink though. I feel like it 
  would be hard to do both simulation and real testing given our time/resource 
  constraints. I think real-world is the better option due to it being more 
  immeditately implementable. How to set this up in the most reproducable 
  manner? 

> "Hence, it would be ideal if the authors fi rst verify their model by employing experimental tests in order to reflect the reality that their proposals would face during real deployment."

- With the goal of reproducability the suggested methodology is small 
  real-world tests to get a sense of environment, followed by simulation, 
  followed by more real world tests to validate. This raises the question: how 
  small are these initial tests? How robust are the final ones?

> "To proceed, we looked for some critical information (e.g., simulation setup, simulator indication, simulator details such as version or library, number of nodes) that should be provided by the studied articles"

- Just in case we do simulation, this is important to note, though I don't 
  expect we will, as our project already has a pretty wide scope. 

> "Emulators such as TOSSIM2 and COOJA3 were developed to bridge the gap between simulation and experimentation, by being very close to real embedded systems in terms of architecture compilation targets"

- Now you're not wasting my time. I wonder if these are still arround today? 
  Is there one for Meshcore? Seems like a no: found two options that seem 
  AI generated: https://github.com/matthewdgreen/meshcore_sim, 
  https://www.reddit.com/r/meshcore/comments/1qgmask/meshcoresimcom/
- Making an emulator/simulator may be cool, but not for this class project 
