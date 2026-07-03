# Agentic Workflow Automation: Autonomous Travel Planner

An intelligent, multi-agent AI framework designed to automate the complex, multi-step process of travel research, budget analysis, and itinerary generation. 

This project demonstrates the application of **Agentic AI** and **Large Language Models (LLMs)** to transition highly manual, research-intensive workflows into streamlined, automated Business As Usual (BAU) processes.


## 📉 Business Case & Problem Statement
Planning a comprehensive travel itinerary requires aggregating unstructured data from multiple siloed sources (weather forecasts, flight schedules, hotel pricing, local attractions). 

**The 'As-Is' State:**
*   Highly manual data collection methodology.
*   Time-intensive cross-referencing of logistics, budgets, and schedules.
*   High probability of human error or overlooked constraints.

## 📈 Proposed Solution
**The 'To-Be' State:**
This project deploys an autonomous AI agent network that sequentially handles requirements elicitation (user preferences), qualitative/quantitative research, and solution delivery (the final itinerary). It utilizes LLMs equipped with external tool-calling capabilities to gather real-time data, process constraints, and generate an optimized schedule without human intervention.

---

## 🤖 System Architecture & Agent Roles

The framework utilizes a collaborative agent architecture where specific roles are assigned to distinct AI personas, mirroring a cross-functional business team.

1.  **The Requirements Analyst (Research Agent):**
    *   **Function:** Elicits and processes the primary user constraints (destination, dates, budget, interests).
    *   **Action:** Scours the web/APIs for real-time data regarding weather, current events, and local logistics.
2.  **The Process Optimizer (Logistics & Budget Agent):**
    *   **Function:** Validates the gathered data against the user's defined budget and time constraints.
    *   **Action:** Filters out sub-optimal options and identifies process gaps in the travel timeline (e.g., accounting for travel time between destinations).
3.  **The Solution Delivery Manager (Itinerary Coordinator):**
    *   **Function:** Synthesizes the validated data into a coherent, customer-facing final product.
    *   **Action:** Generates a highly detailed, day-by-day markdown itinerary complete with cost estimates and logistical dependencies.


## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/rahulsharma6969/Agentic-Travel-Planner.git](https://github.com/rahulsharma6969/Agentic-Travel-Planner.git)
   cd Agentic-Travel-Planner
