# Closed-Loop-Management

## This is information engineering to support the management information systems for closed loops.** 

In the chart below, we describe mainly what some of the associated relationships mean to the model. All relatioships have not been infered in order not to clutter the simplicity implied in this diagram. Example, a POLICY can be linked also to a CLOSEDLOOP or WORKFLOW, but for purposes of decluttering, and by showing the a CLOSEDLOOP is made of WORKFLOW and a WORKFLOW made of ACTIVITY, the reader is able to infer that POLICY can also have a relationship with a CLOSEDLOOP. 

In a similar context, a GOAL and METRIC can be linked to any of the entities in the model, but to simplify the view, an exempler articulation of the relationship has been provided to enable "infer the possibilities".  

**Closed Loop, and the family of concerns that affect Managing Closed Loops** 
![image](https://user-images.githubusercontent.com/111851430/186325543-bc3d4a5b-d316-4763-89e1-74e16efe8960.png)
*Figure 1. Simplified cross-sectional model for automating closedloops*


## Entity Relationship Diagram
In this detailed entity relationship diagram (ERD), albeit also stripped down view, i'm diagraming the details of the classes and base attributes that will be supporting the physical data model. 

The assumption used in defining this mode are that there is existence, and management, somewhere the less detailed aspects of this model. This includesion information about partyRoles in say a Directory System (e.g. Active Directory etc.), existing of a Policy Management Server etc.

Given the above assumption, managing goals, ownership, attributed tactical strategies (activities or workflows) to support realizing the closedloops goal are out of scope - for now. Importance has been placed on identifying the sequence and indeed the various workflows - feedforward (control path) and feedback workflows - that enable realize the goals attributed to a closed loop. 


![clam-diagram0](https://user-images.githubusercontent.com/111851430/205546702-3d963692-8f61-47b5-a357-a6bae1dfdea4.png)
*Figure 2. A stripped out ERD focused around the core concepts to manage closedloops*

I'll share more about the data dictionery, along with modular set of data models on an ongoing basis.

>Note. This stripped down version is meant to enable capture the bearest minimums to create a functioning information network. Some extra rich details on the clases have been left out to enable implementation flavors to occur. There are added capabilities to enable manage entities like goals, measures, activities, actors/roles, workflows etc.  

## State Model
The state model is helpful to understand the lifecycle from strategy, capability development, business value definition and operatoins (fulfillment, assurance and reporting) of the closedloop. 

The model presented here is based on OODA-model which provide a rich and diverse view of the possible interactions towards full autonomy. The choice of OODA model is because of richness of interactions that are possible, and the implied intent of enabling as much consequential autonomy. 

*Figure 3. Lifecycle stagest to manage different models of closed loops
![image](https://user-images.githubusercontent.com/111851430/205808347-77fa4988-1b48-4706-9811-e77c3ba090f4.png)





**This is Work In Progress.**
Copyright 2022-2023 Emmanuel A. Otchere https://www.linkedin.com/in/eaojnr/

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
