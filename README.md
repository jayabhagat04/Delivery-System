# Delivery System

## Project Purpose
This project is a simple logistics simulation built in Python.  
It reads warehouse, agent, and package data from JSON input, assigns each package to the nearest delivery agent, calculates the travel distance for each delivery, and generates a final report showing delivery performance.
The main goal of the project is to simulate one day of delivery operations in a clean and understandable way.

## How It Works
The program performs the following steps:
1. Reads the input JSON file.
2. Extracts warehouse, agent, and package information.
3. Assigns each package to the nearest agent based on the distance between the agent and the warehouse.
4. Calculates total travel distance:
   - Agent to warehouse
   - Warehouse to package destination
5. Generates a report containing:
   - Packages delivered by each agent
   - Total distance traveled by each agent
   - Efficiency of each agent
   - Best performing agent

## Files in This Project
- `delivery_system.py` : Main Python solution file
- `base_case.json` : Sample input file
- `report.json` : Output generated from sample input
- `Python Assignment(Delivery System Test Cases)/` : Contains test case input files
- `reports/` : Contains output reports for all test cases

## How to Run
To run the program with the default sample input:
- python delivery_system.py

To run with a specific test case:
 - python delivery_system.py "Python Assignment(Delivery System Test Cases)\test_case_1.json" report1.json
