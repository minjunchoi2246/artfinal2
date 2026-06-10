# Korean Highway Rest Stop Food Dashboard

## Overview

The **Korean Highway Rest Stop Food Dashboard** is an interactive Streamlit-based web dashboard that visualizes food information from highway rest stops across Korea.

The project was designed to help users quickly explore:

* Rest stop food areas
* Menu items
* Prices
* Operating hours
* Signature foods
* User ratings

The dashboard combines map interaction, menu databases, and visual analytics into a navigation-style experience for long-distance drivers and travelers.

---

# Project Motivation

During long-distance travel, drivers often need to make quick decisions about:

* Where to stop
* What food is available
* Which rest stop has better food options
* Whether food areas are still operating

However, this information is usually fragmented across:

* Public databases
* Map applications
* Blogs
* Individual websites

This project reorganizes that information into a single interactive dashboard.

The main goal is not only to show restaurant data, but to support real-time travel decision-making.

---

# Main Features

## 1. Interactive National Rest Stop Map

* Nationwide rest stop visualization
* Marker-based interaction
* Navigation-style dashboard experience
* Two dashboard view modes:

  * High-Traffic Rest Stops
  * View All Rest Stops

Users can click rest stop markers to explore detailed information.

---

## 2. Rest Stop Detail Dashboard

Each selected rest stop includes:

* Highway route
* Direction
* Operating hours
* Food areas and store types
* Menu previews
* Price information
* Signature menu highlights

The layout is designed to resemble a travel-oriented information panel.

---

## 3. Food Menu Database

The dashboard contains:

* Korean menu names
* Food categories
* Menu descriptions
* Prices
* Signature food labels
* Recommended menu tags

Each rest stop currently contains:

* 12 menu items minimum
* Multiple food area categories

---

## 4. Rating System

Users can:

* Leave star ratings
* Write short comments
* Compare overall menu impressions

Ratings are stored in:

```text
data/ratings.csv
```

---

## 5. Dashboard Analytics

The project includes:

* Menu price comparison charts
* Food category distributions
* Rest stop summary tables
* Interactive filtering

Charts are generated dynamically using Plotly.

---

# Current Dataset 규모

## Rest Stops

* 64 nationwide rest stops

## Menu Items

* 768 menu items

## Food Areas / Stores

* 320 food area records

## Focus Enhancement Area

Additional data density was added to:

* Seoul–Chungcheong–Jeolla highway corridors

while still maintaining a nationwide dashboard structure.

---

# Technology Stack

| Category        | Technology                         |
| --------------- | ---------------------------------- |
| Frontend        | Streamlit                          |
| Data Processing | Pandas                             |
| Visualization   | Plotly                             |
| Map System      | Folium                             |
| Map Integration | streamlit-folium                   |
| Language        | Python                             |
| Deployment      | GitHub + Streamlit Community Cloud |

---

# Project Structure

```text
rest_stop_dashboard/
│
├── app.py
├── requirements.txt
├── README.md
├── DATA_SOURCES.md
│
├── data/
│   ├── rest_stops.csv
│   ├── menu_items.csv
│   ├── stores.csv
│   └── ratings.csv
│
└── .streamlit/
    └── config.toml
```

---

# Data Structure

## 1. rest_stops.csv

Contains:

* Rest stop names
* Highway routes
* Geographic coordinates
* Direction information
* Traffic priority classification

---

## 2. menu_items.csv

Contains:

* Menu names
* Categories
* Descriptions
* Prices
* Signature menu status
* Recommendation flags

---

## 3. stores.csv

Contains:

* Food area names
* Store types
* Operating hours
* Rest stop mapping

---

## 4. ratings.csv

Stores:

* User ratings
* Comments
* Rest stop review logs

---

# Installation

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

---

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 3. Run the Dashboard

```bash
streamlit run app.py
```

---

# Deployment

This project is designed for:

* GitHub
* Streamlit Community Cloud

To deploy:

1. Upload the repository to GitHub
2. Connect the repository to Streamlit Cloud
3. Set `app.py` as the main file
4. Deploy

---

# Dashboard View Modes

## High-Traffic Rest Stops

Displays major high-traffic highway rest stops.

Useful for:

* Long-distance travelers
* Freight drivers
* Main highway routes

---

## View All Rest Stops

Displays the full nationwide dataset.

Useful for:

* Exploration
* Regional comparison
* Broader travel planning

---

# Future Expansion Ideas

Possible future improvements include:

* Official Korea Expressway Corporation API integration
* Real-time operating hour updates
* GPS-based nearby rest stop recommendations
* Real-time traffic analysis
* AI food recommendation systems
* User authentication
* Database migration from CSV to cloud database
* Mobile optimization improvements

---

# Public Data / API Considerations

This project currently uses structured sample/demo datasets for presentation and dashboard prototyping purposes.

Future versions may integrate:

* Korea Expressway Corporation public APIs
* Public Data Portal datasets
* Real-time menu databases

However, there are several limitations:

* API request limits
* Authentication key requirements
* Frequent menu and price updates
* Incomplete coverage for private expressways

Because of these limitations, the current project uses manually structured datasets for stability and presentation quality.

---

# Key Design Philosophy

This project is not simply a restaurant listing application.

The dashboard was designed around one core idea:

> Highway rest stop food information is a travel decision-support system.

Drivers make fast decisions while moving.
Therefore, the interface focuses on:

* visual clarity
* quick comparison
* intuitive navigation
* minimal interaction steps

---

# Author

Choi Min Joon
Film & Media / Dashboard Project

---

# License

This project is intended for educational and portfolio purposes.
