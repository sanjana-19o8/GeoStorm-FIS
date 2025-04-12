# Cyclone Impact Estimation using Fuzzy Logic

## Objective
This project presents a fuzzy inference system (FIS) designed to estimate the potential impact of cyclones on different localities in Visakhapatnam (Vizag), India. The model is built to support disaster preparedness by predicting cyclone effects using fuzzy logic principles based on real meteorological and geographical data.

## System Overview
Cyclone impact in Vizag varies across its localities due to factors like distance from the cyclone's origin, the severity of the storm, and geographical protection. This fuzzy system incorporates these parameters to infer a continuous-valued impact score.

### Inputs and Fuzzy Sets:
1. **Proximity to Cyclone Origin**
   - Computed using Haversine distance between cyclone origin (lat, lon) and each locality
   - Fuzzy sets: `Near`, `Medium`, `Far`

2. **Cyclone Severity**
   - Based on normalized wind speed or storm category from IMD historical cyclone records
   - Fuzzy sets: `Low`, `Moderate`, `High`

3. **Geographical Shielding**
   - Based on elevation data (Open Elevation API) and bearing/direction analysis
   - Fuzzy sets: `Poor`, `Moderate`, `Good`

### Output:
- **Impact Score (0-100)**
   - Fuzzy sets: `Low`, `Medium`, `High`
   - Defuzzified using centroid method

## Fuzzy Rules
The system is governed by a rule base derived from domain intuition and tuned with IMD cyclone data.

1. If `Proximity` is *Near* AND `Severity` is *High* AND `Shielding` is *Poor` => `Impact` is *High*
2. If `Proximity` is *Far* OR `Shielding` is *Good` => `Impact` is *Low*
3. If `Proximity` is *Medium* AND `Severity` is *Moderate* AND `Shielding` is *Moderate` => `Impact` is *Medium*
4. If `Proximity` is *Near* AND `Shielding` is *Good` AND `Severity` is *Low` => `Impact` is *Medium*

Additional nuanced rules are included based on direction of wind path, terrain complexity, and proximity thresholds calculated from Vizag’s cyclone history.

## Inference Flow
1. Input: Cyclone origin coordinates (lat, lon), severity value
2. Compute proximity for each locality
3. Fetch elevation and compute shielding factor per locality
4. Fuzzify all inputs
5. Apply fuzzy rules and infer impact level
6. Defuzzify impact to yield final score per locality

## Historical Cyclone Data (IMD)
- **Dataset**: 1100 cyclone entries from Indian Meteorological Department (IMD)
- Used to:
   - Define realistic proximity ranges
   - Normalize severity values
   - Test prediction consistency for past cyclones (e.g., Hudhud 2014, Titli 2018)

## Sample Output (Hudhud 2014)
| Locality         | Proximity (km) | Severity | Shielding | Predicted Impact |
|------------------|----------------|----------|-----------|------------------|
| Bheemunipatnam   | 15.4           | High     | Poor      | High (82.6)      |
| Madhurawada      | 21.8           | High     | Good      | Medium (62.3)    |
| Pendurthi        | 33.7           | Moderate | Moderate  | Medium (47.1)    |
| Gajuwaka         | 41.5           | Low      | Good      | Low (24.8)       |

## Conclusion
This fuzzy logic-based system provides a robust, interpretable, and extensible framework to model cyclone impact using real geographical and meteorological data. It can be deployed for regional disaster prediction and expanded with live data integration (e.g., NOAA or IMD APIs).

## Future Work
- Real-time cyclone tracking and prediction
- Integration with GIS dashboards
- Machine learning-assisted rule tuning

