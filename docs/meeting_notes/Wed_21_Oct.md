# Wed 21 Oct

## Progress Update

- Carly didnt find much on reliable transfer
- Joel
  - Currently implementing loss tests (close to finished)
- Natalie 
- Quinn didnt find much on reliable transfer

## Mentioned in the meeting

* We would like to produce skeleton code to be spinning up threads for clients at the gateway
* Acks, 
	Retries 5 times displayed when trying to message someone offline
	Just rely on the reliability already offered by the service
	Don't spam messages, build in a sleep
* Using the service
	between phone and desktop clients, difference only on the client side
* Modular service user can choose among
* Interact with the desktop app
	Python gui
	CLI input (minimal implementation)
	HTML input for requesting a pages, looks like the wikipedia front page	
* Natalie wants to emphasize the ability to build on it in the future (more apps -> more APIs)
* Carly thinks a 'startup page' allowing the selection of which API you want to use is helpful
* Writing some skeleton code
	Begin with hardcoded contacts for messaging, consider adding complexity later for discovering services by a # channel or other
	Per-user state in wikipedia application
		initial query, possible options based on initial query
		make meshcore instance a field of the user instance
* Clicking on links? 

## Important Stuff

## Goals for Next Week

- Carly: receiving input in HTML and passing it off to our python program
- Joel
  - Finish loss test implementation
  - Start implementing the gateway app 
  - Look into programatically preventing/setting hopping
  - Configure and run latency + loss tests s.t. they can finish in a reasonable
    time (1-2hrs) when testing multiple devices over variable distance, hopping,
    altitude, etc.
- Natlaie: create user interaction loop with new client
- Quinn: wikitext to html parser, adjacent issues. Report on receiving input from HTML
