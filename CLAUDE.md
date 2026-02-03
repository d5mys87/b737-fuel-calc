# CLAUDE.md - AI Assistant Guide for B737 Fuel Calculator

## Project Overview

This is a **B737 Fuel Quantity Indication Check** web application built with Streamlit. It helps aircraft operators and pilots verify fuel quantity measurements on Boeing 737 aircraft by cross-referencing fuel stick readings against a comprehensive database.

### Key Purpose
- Input fuel tank readings from measurement sticks (Sticks 1-8)
- Cross-reference readings against the fuel database with pitch/roll parameters
- Receive stick recommendations based on estimated fuel quantities
- Verify calculations with variance warnings (160kg for wing tanks, 520kg for center tank)
- Display cockpit-style dashboard with total fuel across three tanks

### Compliance References
- **FMSM 12-11-03** - Fuel Measurement and Sequence Module
- **AMM-28-41-00** - Aircraft Maintenance Manual section 28-41-00

---

## Codebase Structure

```
b737-fuel-calc/
├── fuel_app.py                     # Main Streamlit application (single-file architecture)
├── App_Ready_Fuel_Database.csv     # Fuel lookup database (~65K rows)
├── Master_Stick_Recommendations.csv # Stick recommendations by fuel range (12 rows)
├── logo.png                        # Application branding logo
├── requirements.txt                # Python dependencies
├── CLAUDE.md                       # This file
└── .devcontainer/
    └── devcontainer.json           # GitHub Codespaces/VS Code dev container config
```

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Framework | Streamlit |
| Language | Python 3.11 |
| Data Processing | Pandas, NumPy |
| Deployment | GitHub Codespaces, Docker |
| Styling | Custom CSS via Streamlit markdown |

---

## Development Setup

### Local Development
```bash
pip install -r requirements.txt
streamlit run fuel_app.py
```

### GitHub Codespaces
The devcontainer automatically:
1. Uses Python 3.11 (Bookworm) image
2. Installs dependencies from `requirements.txt`
3. Launches Streamlit on port 8501
4. Opens the application preview

### Manual Streamlit Command
```bash
streamlit run fuel_app.py --server.enableCORS false --server.enableXsrfProtection false
```

---

## Key Files and Responsibilities

### `fuel_app.py` (332 lines)
Single-file monolithic application with logical sections:

| Lines | Section | Purpose |
|-------|---------|---------|
| 1-44 | Branding Block | Page config, CSS injection, mobile icons |
| 46-88 | Header | Fixed header with compliance badges |
| 89-92 | Title | Main page headline |
| 94-120 | Data Loading | Cached CSV loading with type coercion |
| 122-127 | Session State | Fuel quantity tracking across tabs |
| 129-145 | Core Logic | `get_fuel_qty()` function with fuzzy matching |
| 147-175 | Sidebar | Pitch and roll selection controls |
| 177-268 | Main UI Tabs | Three-tab interface for Left/Center/Right tanks |
| 270-332 | Scoreboard | Cockpit-style fuel gauge display |

### Data Files

**App_Ready_Fuel_Database.csv** - Main lookup database
```
Columns: Reading, Col_Index, Fuel_Qty, Roll_Input, Wing_Side, Stick, Pitch
- Reading: Fuel indicator reading value (numeric)
- Fuel_Qty: Calculated fuel quantity in kilograms
- Roll_Input: Aircraft roll angle in degrees
- Wing_Side: "Left" or "Right"
- Stick: "Stick 1" through "Stick 8"
- Pitch: Labeled values like "K (0.00)", "E (-3.00)"
```

**Master_Stick_Recommendations.csv** - Recommendation lookup
```
Columns: Tank_Scope, Min_Kg, Max_Kg, Recommended_Stick, Stick_ID
- Tank_Scope: "Main Wing Tank" or "Center Tank"
- Min_Kg/Max_Kg: Fuel quantity thresholds
- Recommended_Stick: Human-readable recommendation text
```

---

## Code Patterns and Conventions

### Caching Strategy
```python
@st.cache_data
def load_data():
    # Expensive CSV operations are cached
```

### Fuzzy Matching
Uses `np.isclose()` with tolerance for real-world measurement variations:
```python
subset = subset[np.isclose(subset['Roll_Input'], roll, atol=0.01)]
exact = subset[np.isclose(subset['Reading'], reading, atol=0.01)]
```

### Session State Management
Fuel quantities persist across tabs using Streamlit session state:
```python
for k in ['left_qty', 'center_qty', 'right_qty']:
    if k not in st.session_state: st.session_state[k] = 0
```

### UI Pattern
Each tank tab uses the reusable `render_tab()` function with parameters:
- `label`: Display name ("Left", "Center", "Right")
- `key`: Session state prefix
- `scope`: Tank scope for recommendations lookup
- `default_side`: Wing side for database filtering

### Branding Configuration
Hardcoded at top of file - update these for rebranding:
```python
GITHUB_USER = "d5mys87"
REPO_NAME = "b737-fuel-calc"
BRANCH = "main"
LOGO_URL = "https://raw.githubusercontent.com/d5mys87/b737-fuel-calc/main/logo.png"
```

---

## Variance Thresholds

| Tank Type | Variance Limit |
|-----------|----------------|
| Wing Tanks (Left/Right) | 160 kg |
| Center Tank | 520 kg |

If the difference between estimated and calculated fuel exceeds these limits, the application displays a warning and zeros the calculated quantity.

---

## Stick Assignments

| Stick | Tank |
|-------|------|
| Stick 1, Stick 2 | Center Tank |
| Stick 3-8 | Wing Tanks (Left/Right) |

Defaults:
- Wing tanks default to **Stick 8**
- Center tank defaults to **Stick 1**
- Pitch defaults to **Pitch K**
- Roll defaults to **10.0 degrees**

---

## Common Development Tasks

### Adding New Pitch/Roll Values
Update `App_Ready_Fuel_Database.csv` with new rows. The UI dynamically reads available values from the database.

### Modifying Variance Thresholds
Edit `fuel_app.py` line 249:
```python
limit_kg = 520 if label == "Center" else 160
```

### Updating Stick Recommendations
Modify `Master_Stick_Recommendations.csv` with new Min_Kg/Max_Kg ranges.

### Changing Default Values
- Pitch default: Lines 160-164 (searches for "K" in pitch label)
- Roll default: Lines 171-173 (looks for 10.0)
- Stick defaults: Lines 212-220

### Styling Changes
CSS is embedded in `fuel_app.py`:
- Header styles: Lines 49-76
- Scoreboard styles: Lines 279-307

---

## Testing Considerations

**Note: No automated tests exist in this repository.**

Manual testing checklist:
1. Verify data loads without errors
2. Test each tank tab (Left/Center/Right)
3. Verify stick recommendations appear for estimated values
4. Test variance warnings trigger correctly
5. Confirm scoreboard totals update properly
6. Test "Mark EMPTY" checkbox functionality
7. Verify mobile responsiveness

---

## AI Assistant Guidelines

### When Modifying This Codebase

1. **Single-file architecture**: All application code is in `fuel_app.py`. Avoid splitting into multiple files unless explicitly requested.

2. **Data integrity**: Never modify the CSV files without explicit instruction. These contain aviation-critical reference data.

3. **Streamlit patterns**:
   - `st.set_page_config()` must be the first Streamlit command
   - Use `@st.cache_data` for expensive operations
   - Use session state for cross-component data sharing

4. **Aviation context**: This is aviation safety-related software. Changes should be conservative and well-tested.

5. **Branding block**: Lines 6-44 are marked with clear comments. Keep branding configuration together.

6. **No build step**: This is a pure Python Streamlit app. Run directly with `streamlit run fuel_app.py`.

### Common Issues

- **CSV delimiter mismatch**: The loader tries comma first, then semicolon
- **Type coercion**: Numeric columns are explicitly converted with `pd.to_numeric()`
- **String normalization**: String columns are stripped with `.str.strip()`

### Git Workflow

- Main branch: `main`
- No CI/CD pipeline configured
- No pre-commit hooks

---

## Quick Reference

```bash
# Run the application
streamlit run fuel_app.py

# Run with specific Streamlit options
streamlit run fuel_app.py --server.enableCORS false --server.enableXsrfProtection false

# Install dependencies
pip install -r requirements.txt
```

**Application URL**: http://localhost:8501 (default Streamlit port)
