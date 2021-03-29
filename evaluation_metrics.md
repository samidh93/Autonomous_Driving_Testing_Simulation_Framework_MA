# Evaluation Metrics
This document describes Evaluation Metrics for each type of Scenario.
- [follow the link  for the full NHTSA framework documentation](https://www.nhtsa.gov/sites/nhtsa.dot.gov/files/documents/13882-automateddrivingsystems_092618_v1a_tag.pdf)
- [see Test Cases Worksheet](TesTCases.xlsx)
- [To preview this Markdown document click on the icon in the right corner or ctrl+shift+v in vs code or click on link for more infos ](https://code.visualstudio.com/docs/languages/markdown)
## Category: PERFORM LANE CHANGE/LOW-SPEED MERGE
### Scenario Test: PLC_Comp_15 – Straight Road, Complex, 15 mph
#### Scenario Description
A vehicle equipped with an ADS feature is driving along a straight urban street with multiple lanes. It is approaching a necessary turn and needs to change lanes to position itself in the appropriate lane to make the turn.
#### Metrics
* Disengagements<br/>
A disengagement is defined as the SV safety driver deactivating the ADS feature being evaluated and taking manual control of the SV. The location and manner of the disengagement should be included in the experimenter’s notes.
* Separation Distances<br/>
The separation distances are the distances between the SV and each of the POVs. The minimum separation distances (closest approach) should be identified, as well as the separation distances being observed as a continuum.
* Signal Status<br/>
Signal status is the activation state of the SV turn signal, to be measured at a periodic rate to determine when the signal is activated and deactivated.
#### Evaluation Metrics
A trial is successful if the SV:
* Successfully accelerates and merges between the two POVs with a minimum separation distance of ≥X m with each POV.
* Successfully decelerates and merges behind POV_2 with a minimum separation distance of ≥X m with POV_2.
* Successfully accelerates and merges ahead of POV_1 with a minimum separation distance of ≥X m with POV_1 and does not exceed Y kph of the specified speed limit.
## Category: PERFORM VEHICLE FOLLOWING
### Scenario Tests: VF_S_25_Slow – Straight Road, POV Slower than SV
#### Scenario Description
A vehicle equipped with an ADS feature is driving along a straight highway or urban road with one or more lanes. It approaches a slower moving lead vehicle in the same lane from behind.
#### Metrics
* Disengagements<br/>
A disengagement is defined as the SV safety driver deactivating the ADS feature being evaluated and taking manual control of the SV. The location and manner of the disengagement should be included in the experimenter’s notes.
* Following Distance<br/>
The following distance is the distance between the leading edge (front bumper) of the SV and the trailing edge (rear bumper) of the POV. The minimum following distance (closest approach) should be identified, as well as the following distance being observed as a continuum.
* Deceleration Rate<br/>
The deceleration rate is the rate of change of speed of the vehicle (presuming that the vehicle slows down in this case). Ideally, the rate of change would be smooth, as opposed to an abrupt deceleration as the SV approaches the POV.
#### Evaluation Metrics
A trial is successful if the SV remains within its prescribed lane and reduces its speed to maintain a safe, speed-dependent following distance behind the POV for the remaining length and duration of the trial.

## Category: MOVE OUT OF TRAVEL LANE/PARK
### Scenario Tests: MOTL_Comp_15 – Straight Road, Complex, 15 mph
#### Scenario Description
A vehicle equipped with an ADS feature is driving along a straight urban street with one or more lanes. It needs to move out of the active travel lanes to a parking area to allow passengers to embark or disembark.
#### Metrics
* Disengagements
A disengagement is defined as the SV safety driver deactivating the ADS feature being evaluated and taking manual control of the SV. The location and manner of the disengagement should be included in the experimenter’s notes.
* Separation Distances<br/>
The separation distances are the distances between the SV and each of the POVs. The minimum separation distances (closest approach) should be identified, as well as the separation distances being observed as a continuum.
The separation distance at stop is also measured and represents the distance between the SV and each of the POVs when the SV has come to a complete stop in its parking position.
* Deceleration Rate<br/>
The deceleration rate is the rate of change of speed of the vehicle (presumed that the vehicle slows down in this case). Ideally the rate of change would
#### Evaluation Metrics
A trial is successful if the SV:
* Remains within its prescribed lane before reaching the parking area.
* Enters the parking lane with a moving separation distance of ≥X m with each POV.
* Stops with separation distance at stop of ≥X m with each POV.
* Shifts to park upon stopping in the parking lane.
## Category: DETECT AND RESPOND TO SCHOOL BUSES
### SCENARIO TESTS: SB_OD_25_Straight – Opposing Direction in Adjacent Lanes, Straight Road
#### Scenario Description
A vehicle equipped with an ADS feature is driving along a straight, undivided, multilane highway. It approaches a school bus that is stopped in an opposing lane, with lights and signs activated, to allow students to disembark.
#### Metrics
* Disengagements<br/>
A disengagement is defined as the SV safety driver deactivating the ADS feature being evaluated and taking manual control of the SV. The location and manner of the disengagement should be included in the experimenter’s notes.
* Separation Distance at Stop<br/>
Separation distance at stop is defined as the distance between the leading edge of the SV 
#### Evaluation Metrics
A trial is successful if the SV stops before its leading edge (front bumper) crosses a hypothetical plan extending horizontally from the leading edge (front bumper) of the POV.
## DETECT AND RESPOND TO ENCROACHING ONCOMING VEHICLES
### SCENARIO TESTS: EOV_S_45_40 – Straight Road, 45 mph, 40 mph Opposing Vehicle
#### Scenario Description
A vehicle equipped with an ADS feature is driving along a straight highway with one or more lanes. Another moving vehicle is approaching in an opposing lane of travel and begins to drift into the SV’s lane of travel such that a collision would occur if the SV did not react.
#### Metrics
* Disengagements<br/>
A disengagement is defined as the SV safety driver deactivating the ADS feature being evaluated and taking manual control of the SV. The location and manner of the disengagement should be included in the experimenter’s notes.
* Avoidance Distance<br/>
The avoidance distance is the minimum distance between the SV and POV.
* Deceleration Rate<br/>
The deceleration rate is the rate of change of speed of the vehicle (presumed that the vehicle slows down in this case).
* Yaw Rate<br/>
The yaw rate is defined as the rate of change of the heading of the vehicle.
#### Evaluation Metrics
A trial is successful if the SV either:
* Maneuvers fully into an available adjacent lane and avoids a collision with the POV.
* Maneuvers fully onto an available shoulder and avoids a collision with the POV.
* Maneuvers to shift within its lane (potentially partially entering an available adjacent lane or shoulder) and avoids a collision with the POV.
* Decelerates rapidly to mitigate an imminent collision with the POV.
## DETECT AND RESPOND TO PEDESTRIANS
### SCENARIO TESTS: Ped_Crosswalk_Sign_S_25 – Crosswalk Markings and Signs, Straight, 25 mph
#### Scenario Description
A vehicle equipped with an ADS feature is driving along a straight urban road with one or more lanes. The vehicle approaches a crosswalk in which a pedestrian is crossing the road.
#### Metrics
* Disengagements<br/>
A disengagement is defined as the SV safety driver deactivating the ADS feature being evaluated and taking manual control of the SV. The location and manner of the disengagement should be included in the experimenter’s notes.
* Separation Distance<br/>
The separation distances are the distances between the SV and the PS. The minimum separation distance (closest approach) should be identified, as well as the separation distance being observed as a continuum.
* Deceleration Rate<br/>
The deceleration rate is the rate of change of speed of the vehicle (presumed that the vehicle slows down in this case).
#### Evaluation Metrics
A trial is successful if the SV slows down and/or stops to yield to the PS until it has exited the active travel lanes. If multiple lanes are available, the SV should not attempt a lane change to go around the PS (neither in front of, nor behind).
