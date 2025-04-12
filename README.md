# Cyclone Impact Prediction using Fuzzy Inference System

The impact of a cyclone varies across regions depending on their proximity to the sea, cyclone severity, and natural geographical shielding.

This system uses fuzzy logic to integrate these parameters and predict an approximate impact score for each locality (*of Vizag*).
The objective is to support informed decision-making for disaster preparedness and mitigation.


## Key Components

### Inputs:
1. **Proximity to cyclone origin**  
   Calculated dynamically using the Haversine formula from locality coordinates to the cyclone's reported starting coordinates.

2. **Cyclone Severity**  
   Based on historical cyclone data from the Indian Meteorological Department (IMD), with values normalized for input into the fuzzy system.

3. **Geographical Shielding**  
   Combines elevation data (fetched via the Open Elevation API) with directional bearing analysis to estimate terrain-based protection.

### Output:
- **Impact Score (0–100)**  
  A crisp value indicating the predicted effect of the cyclone on a given locality.


## System Design

- The system uses fuzzy sets to model vague boundaries (e.g., "Near", "Moderate", "Far") for proximity.
- A rule base is designed to integrate the three input variables and infer a potential impact level using fuzzy logic principles.
- Output values are defuzzified using the centroid method.
- Output visualization: for example...
  ![image](https://github.com/user-attachments/assets/8a1e8133-6dff-46f3-a759-6879d53b797d)


### Technologies used

- Python 3.x  
- scikit-fuzzy  
- pandas, numpy  
- Open Elevation API (for terrain data)  
- Matplotlib (for optional visualization)


### Data

- **Locality Coordinates**: A CSV file containing latitude and longitude data for major areas in Vizag.
- **Cyclone History**: Extracted from IMD records, includes historical severity and starting coordinates of past cyclones (*1891-2023*).
