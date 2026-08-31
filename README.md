# 🌡️ Heat Impact db42ee0d47fbcb0eef94e58037fb5da0
## Quantifying the Relationship Between Urban Temperature, Community Vulnerability, and Retail Activity Across U.S. Cities

> **Data Analysis & Correlation Track**

Heat Impact is a data analytics project that investigates how urban temperature relates to **people, communities, and business activity** across U.S. cities.

The project uses **FortyGuard's temperature and heatmap intelligence as the core data source**, combining it with socioeconomic, demographic, and retail/business datasets to identify measurable relationships between heat exposure and real-world outcomes.

Rather than simply asking **"Where is it hot?"**, Heat Impact asks:

> **"Who is exposed to higher temperatures, and how does urban heat relate to economic activity?"**

---

# 🎯 Problem Statement

Extreme urban temperatures can affect more than the physical environment.

Heat can influence:

- Community vulnerability
- Energy demand
- Human activity
- Retail activity
- Business operations
- Infrastructure
- Urban planning

However, temperature alone does not explain the complete impact.

Heat Impact combines temperature observations with external datasets to investigate whether measurable relationships exist between **urban heat, socioeconomic conditions, and retail activity**.

---

# 🔎 Core Research Questions

The project focuses on three main questions.

### 1. Where is urban heat concentrated?

Using FortyGuard's spatial temperature data:

- Which cities experience higher temperatures?
- How much does temperature vary within a city?
- Which areas have the highest and lowest temperatures?
- How does temperature change across different dates?

### 2. Who is exposed?

We investigate relationships between temperature and socioeconomic characteristics such as:

- Population
- Population density
- Income
- Poverty
- Housing characteristics
- Other available vulnerability indicators

### 3. How does heat relate to business activity?

We investigate whether temperature is associated with changes in:

- Retail activity
- Sales
- Foot traffic
- Other available business indicators

The goal is not to claim causation, but to identify statistically meaningful **associations and patterns**.

---

### Heat Intelligence API

Completed Heat Intelligence activities provide endpoint-specific intelligence reports through a temporary PDF download link.

The project retrieves the report, extracts relevant analytical information, and incorporates it into the broader analytics workflow where applicable.


# 📈 Analytical Methodology

## 1. Exploratory Data Analysis

The first stage examines:

* Temperature distributions
* Geographic patterns
* Outliers
* Missing values
* Temporal variation
* City-level differences

---
# 📊 Dashboard

The final analytical results will be presented through an interactive dashboard designed to answer two key questions:

1. **Where is heat risk highest across the U.S.?**
2. **Why is a particular city experiencing higher heat risk?**

---

## Dashboard Page 1 — 🇺🇸 U.S. Heat Risk Overview

### Purpose

Provide an immediate overview of **heat risk across U.S. cities** and identify locations with the highest exposure.

### 🎯 Key Performance Indicators

| KPI                         | Variable / Calculation                   |
| --------------------------- | ---------------------------------------- |
| 🏙️ Cities Analyzed         | `COUNT(city)`                            |
| 🌡️ Average Temperature     | `AVG(temperature_celsius)`               |
| 🔥 Hottest City             | `MAX(temperature_celsius)`               |
| ⚠️ Highest Heat Index       | `MAX(heat_index)`                        |
| 🏙️ Highest UHI             | `MAX(uhi_intensity)`                     |
| 📈 Avg. Temperature Anomaly | `AVG(temperature_deviation_from_normal)` |

> **Design principle:** Avoid overcrowding the dashboard with KPIs. These six provide a concise summary of the overall heat-risk situation.

### 🗺️ Main Visual — U.S. Heat Risk Map

An interactive U.S. map showing heat risk by city.

**Mapping:**

* **Location:** `city`
* **Latitude:** `latitude`
* **Longitude:** `longitude`
* **Size:** `population`
* **Color:** `heat_risk_score`

This allows users to quickly understand:

> **Where is the heat, and how many people are potentially exposed?**

### 🏆 City Heat-Risk Ranking

| Rank | City      | Temp | Heat Index |   UHI | Anomaly | 2050 Warming |
| ---: | --------- | ---: | ---------: | ----: | ------: | -----------: |
|    1 | Phoenix   | 44°C |       47°C | 5.8°C |  +5.2°C |       +3.1°C |
|    2 | Las Vegas |  ... |        ... |   ... |     ... |          ... |
|    3 | ...       |  ... |        ... |   ... |     ... |          ... |

This provides an immediately understandable comparison of high-risk cities.

### 📊 Visual 2 — Top 10 Hottest Cities

A horizontal bar chart ranking the hottest cities.

**Measure:**

```text
temperature_celsius
```

**Sort:** Descending

Example:

```text
Phoenix       ████████████████████ 44°C
Las Vegas     ██████████████████   42°C
...
```

### 🔥 Visual 3 — Heat Stress Ranking

Top 10 cities ranked by:

```text
heat_index
```

This helps distinguish:

> **Temperature ≠ Human Heat Stress**

A city with a slightly lower temperature can still have greater human heat stress because of humidity and other environmental conditions.

### 📈 Visual 4 — Temperature Anomaly

Rank cities by:

```text
temperature_deviation_from_normal
```

Focus on cities with the **largest positive deviations** from their historical normal.

This is analytically stronger than ranking cities only by absolute temperature because it identifies locations experiencing unusually high temperatures.

### 📊 Visual 5 — Temperature Distribution

Histogram showing the distribution of city temperatures.

```text
Number of Cities
      │
      │        ███
      │      ███████
      │    ███████████
      │  ███████████████
      └────────────────────
               °C
```

**Question answered:**

> Is extreme heat concentrated in a few cities, or is it widespread?

### 🔎 Dashboard Filters

Place the primary filters at the top of the dashboard:

* `State`
* `City`
* `Date`
* `Climate Type`
* `Heat Stress Level`

---

# Dashboard Page 2 — 🏙️ City Heat Intelligence

### Purpose

Provide an interactive **city-level drill-down** for detailed heat analysis.

This page is not another U.S. overview. Instead, it allows users to investigate **why a specific city is experiencing higher heat risk**.

### 🔎 User Selection

Users can filter by:

* `City`
* `State`
* `Date`

For example:

```text
City  → Phoenix
State → Arizona
Date  → 2024-08-15
```

Once selected, the entire dashboard updates for that city and date.

---

## 🌡️ Section 1 — Temperature

### KPI Cards

| KPI                     | Variable                            |
| ----------------------- | ----------------------------------- |
| 🌡️ Average Temperature | `average_temperature`               |
| 🔻 Minimum Temperature  | `min_temperature`                   |
| 🔥 Maximum Temperature  | `max_temperature`                   |
| 📈 Temperature Anomaly  | `temperature_deviation_from_normal` |

### Temperature Comparison

Show the relationship between:

* Current / Average Temperature
* Historical Typical Temperature
* Temperature Anomaly
* Minimum Temperature
* Maximum Temperature
* Record Temperature

---

## 🧍 Section 2 — Human Heat Stress

Human heat stress should be one of the **most visually prominent sections** of the dashboard.

### KPI Cards

| KPI                  | Variable            |
| -------------------- | ------------------- |
| 🔥 Heat Index        | `heat_index`        |
| 🌡️ WBGT             | `wbgt`              |
| 🌡️ UTCI             | `utci`              |
| ⚠️ Heat Stress Level | `heat_stress_level` |

These indicators provide different perspectives on how environmental conditions translate into **human thermal stress**.

### 🌡️ Heat Stress Gauge

Display the current heat-stress category using a gauge:

```text
Low ───── Moderate ───── High ───── Extreme
                         ▲
                    Phoenix
```

The gauge should dynamically update based on the selected city and date.

---

## 🏙️ Section 3 — Urban Heat Island

Analyze how urbanization contributes to elevated temperatures.

Key indicators:

* `uhi_intensity`
* `daytime_uhi`
* `nighttime_uhi`
* `urban_rural_difference`

This section helps answer:

> **How much additional heat is associated with the urban environment?**

---

## 📈 Section 4 — Temperature Time Series

Display temperature changes over time.

```text
Temperature
     │
     │       ╭──╮
     │   ╭───╯  ╰──
     │───╯
     └────────────────
             Date
```

Recommended measures:

* Average Temperature
* Maximum Temperature
* Heat Index
* Temperature Anomaly

This allows users to identify:

* Heat waves
* Sudden temperature increases
* Persistent warming
* Unusual temperature periods

---

## 🔮 Section 5 — Future Heat Risk

Where available, include projected warming indicators such as:

* `projected_2050_temperature`
* `projected_2050_warming`
* Future temperature anomaly

This connects **current heat exposure** with potential **future climate risk**.

---

## 🎯 Dashboard Story

The two-page dashboard follows a simple analytical flow:

```text
U.S. Overview
      ↓
Identify High-Risk Cities
      ↓
Select City
      ↓
Analyze Temperature
      ↓
Measure Human Heat Stress
      ↓
Analyze Urban Heat Island
      ↓
Explore Historical Trends
      ↓
Understand Future Risk
```

This structure allows the dashboard to move from:

> **"Where is the heat risk?"**

to:

> **"Why is this city at higher risk, and how could the risk evolve?"**

---

# 🧰 Technologies

### Data Collection

* Python
* REST APIs
* FortyGuard API
* Geocoding API

### Data Processing

* Python
* Pandas
* NumPy
* GeoJSON
* PDF extraction

### Statistical Analysis

* SciPy
* Statistical correlation
* Regression analysis

### Visualization

* Power BI
* Matplotlib
* Seaborn

### Development

* Git
* GitHub
* `.env` environment configuration

---

# 💡 Expected Insights

The project aims to answer questions such as:

### Urban Heat

> Which U.S. cities and areas experience the highest temperatures?

### Heat Equity

> Are hotter areas associated with greater socioeconomic vulnerability?

### Business Impact

> Is temperature associated with changes in retail activity?

### Spatial Variation

> How much can temperature vary within the same city?

### Cross-City Comparison

> Which characteristics are most strongly associated with urban temperature?

---

# 🌎 Potential Impact

The findings could support:

### Urban Planning

Identify areas that may require additional heat mitigation strategies.

### Public Policy

Understand whether vulnerable communities are disproportionately exposed to heat.

### Retail & Business Planning

Identify potential relationships between extreme temperatures and business activity.

### Climate Resilience

Provide data-driven evidence for prioritizing urban heat interventions.


[Dashboard Screenshot]
