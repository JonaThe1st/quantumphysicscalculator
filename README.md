# Quantum Physics Calculator (Flask)

A modular Flask web application for simple quantum-physics-related conversions.

## Features

- Application factory pattern for scalable app initialization
- Blueprint-based routing
- Dedicated service layer for business logic
- Validation utilities for request payload handling
- Minimal homepage using Flask templates and static CSS
- Clean server-rendered GUI form for interactive conversions
- API endpoint for unit conversions
- Supports scientific notation such as 1e-3 and 2*10^5
- Uses scipy.constants for physical constants
- Supports SI-style prefixes: k, M, G, T, m, mu (and u)
- Includes a swap button in the GUI to flip source and target units

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── api.py
│   │   └── pages.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── conversion_service.py
│   ├── static/
│   │   └── css/
│   │       └── styles.css
│   ├── templates/
│   │   ├── base.html
│   │   └── index.html
│   └── utils/
│       ├── __init__.py
│       └── validators.py
├── tests/
│   ├── __init__.py
│   └── test_app.py
├── requirements.txt
├── run.py
└── README.md
```

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
python run.py
```

The homepage will be available at:

`http://127.0.0.1:5000/`

## API

### Health Check

- Method: `GET`
- URL: `/api/v1/health`

### Convert

- Method: `POST`
- URL: `/api/v1/convert`
- JSON body:

```json
{
  "value": 532,
  "source_unit": "nm",
  "target_unit": "eV"
}
```

- Supported units:
  - `eV`
  - `J`
  - `nm`
  - `T` (via Bohr magneton)
  - `K` (via Boltzmann constant)
  - `Hz` (frequency via Planck constant h)
  - `rad_s` (angular frequency via reduced Planck constant ħ)

- Prefix examples:
  - `keV`, `MeV`, `mJ`, `uJ`, `GHz`, `mK`

## Notes on Maintainability

- Route files only orchestrate request/response behavior.
- Conversion logic is isolated in `app/services/conversion_service.py`.
- Input validation is isolated in `app/utils/validators.py`.
- New conversion rules can be added to the conversion map in one place.
