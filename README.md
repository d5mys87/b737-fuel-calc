# B737 Fuel Calculator - User Guide

A web application for performing Fuel Quantity Indication Checks on Boeing 737 aircraft.

**Reference Documents:** FMSM 12-11-03 | AMM-28-41-00

---

## Quick Start

1. Open the app at: **https://d5mys87.github.io/b737-fuel-calc/**
2. Set **Pitch** and **Roll** in the Settings panel
3. For each tank (Left/Center/Right):
   - Uncheck "Mark EMPTY" if the tank has fuel
   - Enter your estimated fuel quantity
   - Select the appropriate stick and reading
4. View the total fuel on the cockpit display

---

## Installation (Optional)

This app can be installed on your device for quick access:

| Platform | How to Install |
|----------|----------------|
| **Android** | Tap "Install App" banner or Menu > "Add to Home Screen" |
| **iOS** | Tap Share > "Add to Home Screen" |
| **Desktop** | Click install icon in address bar |

Once installed, the app works offline.

---

## Using the App

### Step 1: Configure Settings

At the top of the app, set:

- **Pitch** - Select the aircraft pitch angle (default: Pitch K)
- **Roll** - Select the aircraft roll angle (default: 10.0)

### Step 2: Enter Fuel Data for Each Tank

The app has three tabs: **Left Wing**, **Center**, and **Right Wing**.

For each tank:

1. **Mark EMPTY checkbox**
   - Checked = Tank is empty (0 kg)
   - Unchecked = Tank has fuel, enter readings below

2. **Est. (Estimated Fuel)**
   - Enter your expected fuel quantity in kg
   - A stick recommendation will appear based on this value

3. **Stick Selection**
   - Left/Right Wing: Sticks 3-8 (default: Stick 8)
   - Center Tank: Sticks 1-2 (default: Stick 1)

4. **Reading**
   - Select the reading from your fuel stick measurement
   - Available readings are filtered based on your Pitch, Roll, and Stick selection

### Step 3: View Results

The **cockpit display** at the top shows:
- Individual tank quantities (TANK 1, CTR, TANK 2)
- Total fuel in kilograms

---

## Stick Recommendations

When you enter an estimated fuel quantity, the app suggests which stick to use:

### Wing Tanks (Left/Right)
| Fuel Range (kg) | Recommended Stick |
|-----------------|-------------------|
| 0 - 623 | Below Limit |
| 623 - 1,680 | Use Stick 3 |
| 1,680 - 2,673 | Use Stick 4 |
| 2,673 - 3,132 | Use Stick 5 |
| 3,132 - 3,491 | Use Stick 6 |
| 3,491 - 3,790 | Use Stick 7 |
| 3,790 - 7,974 | Use Stick 8 |
| 7,974 - 13,902 | Use Stick 8 (+1) |
| > 13,902 | Full / Over Limit |

### Center Tank
| Fuel Range (kg) | Recommended Stick |
|-----------------|-------------------|
| 0 - 500 | Below Limit |
| 500 - 2,500 | Use Stick 1 |
| > 2,500 | Use Stick 2 |

---

## Understanding the Display

### Cockpit Display Colors

| Color | Meaning |
|-------|---------|
| **Green total** | All readings verified within limits |
| **Red total (pulsing)** | One or more tanks have variance exceeding limits |
| **Gray total** | No fuel (all tanks empty) |
| **Red tank value** | That specific tank has a variance alert |
| **White tank value** | Tank reading is verified or empty |

### Display Border

| Border Color | Meaning |
|--------------|---------|
| Gray | Normal operation |
| Red with glow | Variance alert active |

---

## Messages and Alerts

### Success Messages

| Message | Meaning |
|---------|---------|
| **Verified: X kg** | The calculated fuel matches your estimate within acceptable limits |
| **[Tank] Tank = 0 Kgs** | Tank is marked as empty |

### Warning Messages

| Message | Meaning |
|---------|---------|
| **No data for Roll X** | No database entries exist for the selected roll angle with current settings. Try a different roll value. |
| **No match found** | The combination of stick, pitch, roll, and reading doesn't exist in the database. Verify your selections. |

### Error Messages

| Message | Meaning |
|---------|---------|
| **VARIANCE > 160 KGS** (Wing tanks) | The difference between your estimated fuel and the calculated fuel exceeds 160 kg. This may indicate a measurement error or fuel quantity discrepancy. |
| **VARIANCE > 520 KGS** (Center tank) | The difference between your estimated fuel and the calculated fuel exceeds 520 kg. This may indicate a measurement error or fuel quantity discrepancy. |

---

## Variance Limits

The app compares your estimated fuel quantity against the calculated value from the database:

| Tank Type | Maximum Allowed Variance |
|-----------|-------------------------|
| Wing Tanks (Left/Right) | 160 kg |
| Center Tank | 520 kg |

**When variance is exceeded:**
- The calculated value still appears in the totalizer (shown in red)
- The error message shows both calculated and estimated values
- Investigate the discrepancy before proceeding

**Possible causes of variance:**
- Incorrect stick reading
- Wrong pitch or roll setting
- Measurement error
- Actual fuel quantity discrepancy

---

## Troubleshooting

### "No data" shown for readings
- Check that Pitch and Roll settings are correct
- Some pitch/roll combinations may not have data for all sticks
- Try selecting a different roll value

### App not loading
- Check your internet connection (first load requires internet)
- Try refreshing the page
- Clear browser cache if issues persist

### Installed app showing old version
- Open browser DevTools (F12)
- Go to Application > Storage
- Click "Clear site data"
- Reload the app

---

## Data Sources

This application uses certified fuel quantity reference data:
- **App_Ready_Fuel_Database.csv** - ~65,000 lookup entries
- **Master_Stick_Recommendations.csv** - Stick selection guidelines

**Disclaimer:** This tool is for reference only. Always follow official aircraft documentation and procedures for fuel quantity verification.

---

## Support

For issues or feedback, visit: https://github.com/d5mys87/b737-fuel-calc/issues
