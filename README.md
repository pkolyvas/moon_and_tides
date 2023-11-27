# Moon and Tides 

A RPi Zero & 3D printed project. 

You'll find the code, 3D models, and instructions for building here. 


## Requirements



## Todo

- Function(s) to get and store the next high or low tide on boot. Tides are periodic (avg. 24h 50m 30s - (ref)[https://en.wikipedia.org/wiki/Tide_clock])
  - Or get tides via API with more data: https://api.marea.ooo/doc/v2#overview
- Function to get the current phase of the moon (develop in house or Moon API: https://moon-api.com)
- Design display screens for high and low tide
- Build a function to switch between moon and tide in the globe
- Build a function to rotate the occlusion half dome to the correct location based on the current moon phase
- Multiple network: https://raspberrypi.stackexchange.com/questions/11631/how-to-setup-multiple-wifi-networks



- Motor is 1.8 degrees per step. 
- 200 steps full circle.
- Full moon at 100 steps
- 100 steps = phase of 0.50
- I can get the accurate position (number of steps) by multiplying the steps by the phase. 
- When the motor moves I will need to save the current position and phase in case we need to pick up from a power outage
- Will also need the ability to recalibrate
- Will need to compare current phase to last phase and move to correct position. Optional boot-up check? Move to full moon, adjust full moon, confirm. 
