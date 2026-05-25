# Data Sources and Replacement Guide

The bundled CSV files are seed data for a working Streamlit prototype.

For a production version, replace these files with official public-data exports or API results:

- `data/rest_stops.csv`: rest stop name, direction, route, region, coordinates, traffic focus, hours.
- `data/menu_items.csv`: rest stop id, food area, menu item, category, price, availability, signature flag, rating, description.
- `data/stores.csv`: food area / store type, description, opening hours.

Phone numbers are intentionally removed from the dashboard because inaccurate contact data can reduce trust.
