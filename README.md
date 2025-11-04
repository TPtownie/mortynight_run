

Wubba Lubba Dub Dub! Alright, Morty. Listen up. Your grandpa, Rick, did a thing. A real Rick thing. He found a planet. A whole planet populated by a million Jessica's - emotionally stable, well-adjusted Jessica's! Planet Jessica. It's great. It's really great.

Morty Express Challenge Diagram
But guess what? The Council of Ricks found out. Those bureaucratic blowhards in the Citadel decided that Morties having access to a source of genuine happiness would make them "less pliable." So, their grand plan is to hook every Morty up to a "Memory-B-Gone 5000" and wipe Planet Jessica from our collective, anxious consciousness.

Aw, geez, I know.

But you, you magnificent little Morty, overheard everything. You've barricaded yourself in an underground Citadel sub-level with 999 other Morties. You've got portal guns, but those are cheap knock-offs your Rick built in a drunken stupor. It can't make the jump directly to Planet Jessica - it's too far. So you have to travel through one of three highly questionable planets.

Your Objective
Write a script that interacts with an API to send 1000 Morties, in groups of up to 3, from the Citadel to Planet Jessica. You must travel through one of three intermediate planets. Your goal is to maximize the number of Morties who arrive safely.

The Paths (Choose Wisely, or Don't, Whatever)
You have three choices for your intermediate stop:

Planet A, index=0: "On a Cob" Planet
Planet B, index=1: Cronenberg World
Planet C, index=2: The Purge Planet
Risk Profile: The risk for each planet changes dynamically over time based on the number of trips taken.

How to Win
The challenge ends when morties_in_citadel is 0. Your final score is the value of morties_on_planet_jessica. Develop an algorithm that probes the different routes, analyzes the results, and adapts its strategy to the changing odds to save as many Morties as possible.

API Specification
You'll be interacting with a simple REST API.

Base URL: https://challenge.sphinxhq.com

1. Request API Token
Get an API token to authenticate your requests.

Endpoint: POST /api/auth/request-token/
Request Body:
{
  "name": "Your Name",
  "email": "your.email@example.com"
}
Response (200 OK): Token will be sent to your email
2. Start a New Episode
This endpoint initializes your escape attempt.

Endpoint: POST /api/mortys/start/
Headers: Authorization: Bearer YOUR_TOKEN
Request Body: None
Response (200 OK):
{
  "morties_in_citadel": 1000,
  "morties_on_planet_jessica": 0,
  "morties_lost": 0,
  "steps_taken": 0,
  "status_message": "Keep going! Or don't. I'm not your dad."
}
3. Send Morties Through a Portal
This is your main action. Send a group of Morties on their perilous journey.

Endpoint: POST /api/mortys/portal/
Headers: Authorization: Bearer YOUR_TOKEN
Request Body:
{
  "planet": 0 | 1 | 2,
  "morty_count": 1 | 2 | 3
}
Planet indices: 0 = "On a Cob" Planet, 1 = Cronenberg World, 2 = The Purge Planet

Response (200 OK):
{
  "morties_sent": 3,
  "survived": true,
  "morties_in_citadel": 747,
  "morties_on_planet_jessica": 203,
  "morties_lost": 50,
  "steps_taken": 84
}
4. Get Episode Status
Check your current progress.

Endpoint: GET /api/mortys/status/
Headers: Authorization: Bearer YOUR_TOKEN
Response (200 OK):
{
  "morties_in_citadel": 750,
  "morties_on_planet_jessica": 150,
  "morties_lost": 100,
  "steps_taken": 83,
  "status_message": "Keep going! Or don't. I'm not your dad."
}
💰 The Loot
Now Morty, you do this right, and there's actual real-world money in it for you. I know, I know, capitalism is a construct, the value of currency is arbitrary, blah blah blah. But you can't buy portal fluid with good intentions.

The Prizes:
🥇 First Place: $10,000 + Flight to San Francisco
That's right, Morty. Ten thousand Earth dollars. And get this - you'll fly out to SF to interview with the Sphinx team. Real tech company, Morty. Not like those fake ones that turned out to be fronts for interdimensional weapons dealers.
🥈 Second Place: $4,000 + Remote Interview
Four thousand dollars, Morty! Plus you get a remote interview with Sphinx. That's like... *burp*... I don't know, a lot of Szechuan sauce and a chance at a real job.
🥉 Third Place: $2,000 + Remote Interview
Price of a entry-level portal gun battery. Or therapy. You're gonna need one of those after this, Morty. Plus, hey, you get to interview remotely with Sphinx too.
💡 Hint from Rick
*burp* Alright, listen up Morty. Here's a tip from your genius grandpa: although the average survival rate is the same, the probabilities of the 3 planets are changing with time. Time being the number of trips. Some change faster than others. First, try to just observe each planet's frequency. Send all your Mortys to one planet and see what happens. Data is your friend. Gotta visualize it, Morty.

Good luck, Morty. Don't... y'know... don't screw this up. For Jessica.
