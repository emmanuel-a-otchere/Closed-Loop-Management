Closed Loop Management
===

## This is information engineering to support the management information systems for closed loops.** 

In the chart below, we describe mainly what some of the associated relationships mean to the model. 
All relatioships have not been infered in order not to clutter the simplicity implied in this diagram. Example, a POLICY can be linked also to a CLOSEDLOOP or WORKFLOW, but for purposes of decluttering, and by showing the a CLOSED LOOP (also ClosedLoop) is made of WORKFLOW, and a WORKFLOW made of ACTIVITIES. 
I expect the reader or user is able to infer that POLICY can also have a relationship with a CLOSED LOOP. 

In a similar context, a GOAL and METRIC can be linked to any of the entities in the model, but to simplify the view, an exempler articulation of the relationship has been provided to enable "infer the possibilities".  

## Key Concepts
* Goal \
Represents the target or outcome to be realized from performing something.

* Activity \
A unit of work that is done, or to is performed.

* Workflow \
A set of activities that, altogether, realize an objective.

* Objective \
An objective is short-term goal.

* Closed Loop \
ClosedLoop is a set of workflows with a control flow or control point and feedback that realizes a determined goal.

* Closed Loop Design \
The translation of requirements for a closed loop, into a specification that defines and plans a closed loop for use.

* Closed Loop Control \
The management of defined closed loops

* Closed Loop Automation \
Closed loops that have minimum or no human input.

* AI Closed Loop Automation \
Machine driven intelligence used to remove human involvement in automated Closed loops. 

* Closed Loop Validation \
The activities that test and prove that a closed loop specification meets the goals supporting its requirement.

* Closed Loop Publishing \
The activities that deploy and announce the presence of a closed loop.

* Closed Loop Administration \
The activities that oversee the successful running of a closed loop.

* Closed Loop Reporting \
The visibility and observability delivered or extracted from a closed loop.

* Closed Loop Automation Management Platform\
A set of closedloop management capabilities to support all the lifecycle operations of a closedloops.

* Closed Loop Component \
Represents a management function or component (e.g. ODA Component) that is utilized by the closed loop to realize its operational goals. 

* Closed Loop Activity \ 
A Closed Loop Activity is a formalized unit of task among many others in a closed loop. A closed loop activity embodies a set of internal actions that are not exposed to the rest of the closed loop operations. In essence it a blackbox that provides a specific objective whose internals to arriving at any outcome is not transparent to be influenced. 

* Closed Loop Workflow \
A Closed Loop Workflow is a formalize set of activities that altogether represent an identified flow within the closed loop operations. A closed loop workflow may represent concepts like "happy path", "sad path" or "negative feedback" or "positive feedback" paths etc. The closed loop workflow is identified with a specific closed loop. A closed loop workflow has an objective that can be set and managed based on a workflow manager. 

* Closed Loop Workflow Management \
Closed Loop Workflow Management is a capability to plan, execute, check and apply closed loop workflows based on te closed loop management dictates. It has a control over the closed loop workflow but subject to the goals of closed loop management. 

* Closed loop Management \ 
Closed Loop Management is a capability to plan, execute, check and apply closed loops based on closed loop goals. It has control over the closed loop and underlying capabilities. 

* Closed Loop Goal Management \
Closed Loop Goal Management is a capability to plan, execute, check and apply closed loop goals based on closed loop defined expectations. It enables managing the goals of a closed loop along with making changes to goals or managing goal conflict. 


**Closed Loop, and the family of concerns that affect Managing Closed Loops** 

<p align="center">
  <img width="800" height="auto" src="https://user-images.githubusercontent.com/111851430/186325543-bc3d4a5b-d316-4763-89e1-74e16efe8960.png" style="border-radius:50%" >
</p>

*Figure 1 Simplified cross-sectional model for automating closedloops*


## Entity Relationship Diagram
In this detailed entity relationship diagram (ERD), albeit also stripped down view, i'm diagraming the details of the classes and base attributes that will be supporting the physical data model. 

In the context of business process modeling, Action and Activity can be used to refer to similar concepts. Both Action and Activity can be thought of as representing a task or unit of work that needs to be performed as part of a larger process. However, for purposes of this modeling, we are applying some distinguishing differences between Action and Activity that are worth noting:

   * Scope: Action typically refers to a small, atomic task that is performed as part of a larger process. In contrast, Activity typically refers to a larger, more complex task that may involve multiple steps and may involve other actions or activities as part of its execution.
   * Level of abstraction: Action is usually a more specific, concrete concept than Activity, which tends to be more abstract. For example, "sending an email" might be considered an action, while "performing customer outreach" might be considered an activity.
   * Relationship to business process: Action is typically seen as a lower-level building block that is used to construct more complex processes. Activity, on the other hand, is usually seen as a higher-level concept that represents a more significant piece of work within a business process. 

A HL representative model is below.

![image](https://user-images.githubusercontent.com/30234220/210195303-dce97a55-e340-4896-a971-46d3f6edc1f5.png)
*Figure 1-1 An abstract model linking the core concepts.*

The assumption used in defining this mode are that there is existence, and management, somewhere the less detailed aspects of this model. This includesion information about partyRoles in say a Directory System (e.g. Active Directory etc.), existing of a Policy Management Server etc.

Given the above assumption, managing goals, ownership, attributed tactical strategies (activities or workflows) to support realizing the closedloops goal are out of scope - for now. Importance has been placed on identifying the sequence and indeed the various workflows - feedforward (control path) and feedback workflows - that enable realize the goals attributed to a closed loop. 


<p align="center">
  <img width="800" height="auto" src="https://user-images.githubusercontent.com/111851430/205546702-3d963692-8f61-47b5-a357-a6bae1dfdea4.png" style="border-radius:50%" >
</p>

*Figure 2 A stripped out ERD focused around the core concepts to manage closed loops*


>Note. This stripped down version is meant to enable capture the bearest minimums to create a functioning information network. Some extra rich details on the clases have been left out to enable implementation flavors to occur. There are added capabilities to enable manage entities like goals, measures, activities, actors/roles, workflows etc.  

## State Model
The state model is helpful to understand the lifecycle from strategy, capability development, business value definition and operatoins (fulfillment, assurance and reporting) of the closedloop. 

The model presented here is based on OODA-model which provide a rich and diverse view of the possible interactions towards full autonomy. The choice of OODA model is because of richness of interactions that are possible, and the implied intent of enabling as much consequential autonomy. 

<p align="center">
  <img width="800" height="auto" src="https://user-images.githubusercontent.com/111851430/205808347-77fa4988-1b48-4706-9811-e77c3ba090f4.png" style="border-radius:50%" >
  
*Figure 3 Lifecycle stagest to manage different models of closed loops*

## Software and Integration Design
The following provide requirement for design of software and relevant integration needs. Details of functions are provided below. 

### Software and Integation requirements
The softare and integration requirement cover:

#### Strategy to Capability readiness of closed loop management. 
In this scope we will cover the definition and design of the closed loop along with detailed specifications that model the capabilities in order to achieve readiness for verification, validation and onboarding into an environment for operations.  

The strategy to capability readiness requirement ensures that the closed loop can be defined based on an owners expected goals, associated policies and key requirements. This stage also help to set roles and parties that provide inputs to set the closed loop strategy and tactics, while identifying related capabilities to realize such tactics. 

Define and design functions will provide all the functional capablities needed by the closedloop strategy owner to manage the goal of the closedloop. This includes full closedloop goal management objects and associated objects like policies, business rules and measures. This addresses. 

#### Lifecycle Management
This is the where a the capability of the closed loop is attributed to actual resources, such as resources needed to operationalize and support the closed loop towards achieving its goal. It also implies ensuring there are functions to enable mantain the integrity of the envrionment(s) the closed loop must operate in. 
This includes the physical/virtual resource requirement management downstream by way of the components that support the activities and workflow execution, and their selection, validation and verification testing of the underlying activities and workflow/activity for the objectives they support to realizing the overarching goal of the closedloop for the environment targeted. The key areas inolved are:

In this stage, there is the management of the Validation and verification of closedloop and underlying or supporting "resources", management of the publication of the closedloop to a deployment environment; as well as the management of the specification lifecycle and relationships. 

#### Operatons Management
This is the stage where the closed loop is already active or available to be operated. This is the stage a controller can control the closedloop functionally, including activities needed by a closed loop operator to handle day-to-day running of the closedloop, such as: 
   * Administrtion of closedloop, such as starting and stopping it. 
   * Control of closedloop capabiities and underlying resources.
   * Monitoring  closedloop.
   * Reporting closedloop.
   * Governing closedloops - Where governing closed loop functionally includes activities to manage the operations of the closedloop in tandem with other closedllops with integrity, and addressing conflict in underlying resources allocation that can/may impeade achievement of closedloop goals under specific risk conditions. These include:
      * Managing goal conflicts
      * Managing closedloop performance
      * Auditing closedloops
      * Change control of closedloop
      * Risk Management of closedloop


## Relevent Functions and sub-functions
In defining the management requirement for closed loop, refer to the lifecycle, figure 3, to conceive the organization of the different states as outcome of the management functions. In loose terms, these functions are considered components, or realized as functions in other components as per the dictates of the an environment design or architecture. 
A component here is described as a unit of "Software Specification boarded on providing a set of functions closely related to a unique role" that unit of software performs in an a defined environment.
ClosedLoop Management components are hereby clustered into 3 capabilities - the Design studio, Manager and Controller. 

<p align="center">
  <img width="800" height="auto" src="https://user-images.githubusercontent.com/111851430/207787691-4342621e-dad6-4af5-bece-3131ad510707.png" style="border-radius:50%" >

*Figure 4 Closed Loop Management function and sub-functions*

#### 1. Closed Loop Design Studio 
The ClosedLoop Design Studio provides the functions to engage a designer with the requisite approvals, manage ontology related to closedloops, and to enable model closedloops with all the supporting functions needed to specify the closedloop. 

  + 1.1. Closed Loop Design user interface \
  Closed Loop Design user interface is a sub-function of the Closed Loop Deisgn Studio. It provides an integrated design environment to enable a Closed Loop designer to build and configure Closed loops. The interface serves as a gateway to enable the right personas with the right capabilities to define and closed loop goals and related policies, build closedloop models, closed loop workflows, set goals/objectives and to manage closedloop ontologies.

  + 1.2. Closed Loop Model Builder \
  Closed Loop Model Builder is a sub-function of Closed Loop Design Studio. It provides the functions for a closed loop owner or closed loop designer to build the closed loop objects, and use them to build underlying workflows. The Model builder provides the functions to fully realize and verify the closedloop workflows and goals, as well as simulate, as well as document the closedloop design.
 
  + 1.3. Closed Loop Ontology Manager \
  Closed Looop Ontology Manager is a sub-function of Closed Loop Deisgn Studio. It provides the functions to manage closed loop ontologies. Closed Loop ontologies are considered a key technology enabling semantic interoperability and integration of data and processes. The Ontology manager provides functions to define the taxonomy for closed loops based on a specific domain(s) or field of applicability of closed loops. It enables a rich data understanding of the domain or field in relation to activities, workflows and existing closed loops. 

#### 2. Closed Loop Manager 
Closed Loop Manager provides the function to handle the post specification of a closedloop. It manages the need to validate, verify, expose or publish and catalog closed loops.

  + 2.1. Closed Loop Validator \
  Closed Loop Validator is sub-function of the Closed Loop Manager and is meant to support workflow managers, system/closed loop/ goal integrators and environment administrators (systems admins, network admins, goal admins) to take a modeled closedloop in for: dynamic testing (unit testing of workflows, integration testing of the closedloop architecture, system testing of the closedloop design specification and acceptance testing against the original requirement description); check validity against the needs of the owner; and testing integrity with respective to environment (single or multi-environment in the case of closed loops that traverse multiple environment. 

  + 2.2. Closed Loop Publisher \
  Closed Loop Publisher is a sub-function of the Closed Loop Manager and is meant to provide the enablers to publish a closed loop that has been verified, validated and certified ready for operation into an environment's catalog.

  + 2.3. Closed Loop Catalog Manager \
  Closed Loop Catalog Manager is a sub-function of the Closed Loop Manager which serves as the closed loop catalog. This function will manage availability and exposure, as well as manage changes to closed loops in their environments. Closed loop catalog management can include maintaining descriptions, settings changes to goals and objectives of closed loops and their exposed workflows, and managing inventorying of closedloops resources (workflows, activities and underlying physical/virtual resources).

#### 3. Closed Loop Controller 
Closed Loop Controller is function to enable monitor, orchestrate, administer and choreograph closed loops. It available for closed loop operators to enable monitor, orchestrate closedloops (based on closedloop mechanisms models), administer closedloop in operations and manage closedloop interacting and integrating in or across environments (choreograph).  

  + 3.1. Closed Loop Monitor \
  Closed Loop Monitor is a sub-function of the Closed Loop Controller. This sub-function is responsible for monitoring closed loops against defined goals/objectives, and the environments they operate in by providing information (including reports, performance data and stats) about closedloop operations, and enabling capture events needed to support both the closed loop operations, closed loop management goals and closed loop state changes.

  + 3.2. Closed Loop Orchestrator \
  Closed Loop Orchestrator is a sub-function of the Closed Loop Controller. The sub-function provides control of interactions and integrations of closedloop mechanisms with the underlying or supporting resources/systems/components/entities. 

  + 3.3. Closed Loop Administrator \
  Closed Loop Administrator is a sub-function of the Closed Loop Controller which provides the capability to administer (systems, network, security etc.) the START, END, RESTART, RELOAD, ENABLE, DISABLING active or running closed loops. It also provides capabilities to test or check the health of closed loops towards meeting the management needs or the goals linked to design of the closed loop.

  + 3.4. Closed Loop Choreographer \
  Closed Loop Choreographer is a sub-function of Closed Loop Controller. This sub-functions includes capabilities to provide an environment or multi-environment governance that means cordinating the managing the interactions between different closed loops based on shared resources or shared environments, as well as oversight on the performance of closed loops in relation to their operating environment. This sub-function provides conflict resolution, resource allocation and availability according to set environment management goals. 



















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
