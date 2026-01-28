# Home Depot Robot Materials Database

This dataset covers standard construction materials available at retail hardware stores (Home Depot/Lowe's). Note that "Trade Size" does not equal physical dimensions for plumbing/electrical parts.

## 1. PVC Pipe (Plastic)

- **Standard:** ASTM D1785 (Schedule 40)
- **Use Case:** Light frames, prototyping.
- **Engineering Toolbox Source:** [PVC Pipe Dimensions](https://www.engineeringtoolbox.com/pvc-cpvc-pipes-dimensions-d_795.html)

**Simulation Properties:**

```
json
Copy code
{
  "material": "PVC (Polyvinyl Chloride)",
  "youngs_modulus_psi": 400000,
  "yield_strength_psi": 7000,
  "density_lbs_in3": 0.049
}
```

**Common Dimensions (Schedule 40):**

| Trade Size | Outside Diameter (OD) | Inside Diameter (ID) | Wall Thickness |
| :--------- | :-------------------- | :------------------- | :------------- |
| **1/2"**   | 0.840"                | 0.622"               | 0.109"         |
| **3/4"**   | 1.050"                | 0.824"               | 0.113"         |
| **1"**     | 1.315"                | 1.049"               | 0.133"         |
| **1-1/4"** | 1.660"                | 1.380"               | 0.140"         |

------

## 2. Galvanized / Black Iron Pipe (Steel)

- **Standard:** ASTM A53 / ANSI Schedule 40
- **Use Case:** Heavy bases, high-load static legs.
- **Engineering Toolbox Source:** [ANSI Schedule 40 Steel Pipe](https://www.engineeringtoolbox.com/ansi-steel-pipes-d_305.html)

**Simulation Properties:**

```
json
Copy code
{
  "material": "Carbon Steel",
  "youngs_modulus_psi": 29000000,
  "yield_strength_psi": 35000,
  "density_lbs_in3": 0.284
}
```

**Common Dimensions (Schedule 40):**

| Trade Size | Outside Diameter (OD) | Inside Diameter (ID) | Wall Thickness |
| :--------- | :-------------------- | :------------------- | :------------- |
| **1/2"**   | 0.840"                | 0.622"               | 0.109"         |
| **3/4"**   | 1.050"                | 0.824"               | 0.113"         |
| **1"**     | 1.315"                | 1.049"               | 0.133"         |

------

## 3. EMT Conduit (Electrical Tubing)

- **Standard:** ANSI C80.3
- **Use Case:** Lightweight steel frames (The "Budget" Robot Frame).
- **Engineering Toolbox Source:** [Electrical Conduit Sizes](https://www.engineeringtoolbox.com/conduit-size-d_1738.html)

**Simulation Properties:**

```
json
Copy code
{
  "material": "Low Carbon Steel (Galvanized)",
  "youngs_modulus_psi": 29000000,
  "yield_strength_psi": 30000,
  "density_lbs_in3": 0.284
}
```

**Common Dimensions (Thinwall):**

| Trade Size | Outside Diameter (OD) | Inside Diameter (ID) | Wall Thickness |
| :--------- | :-------------------- | :------------------- | :------------- |
| **1/2"**   | 0.706"                | 0.622"               | 0.042"         |
| **3/4"**   | 0.922"                | 0.824"               | 0.049"         |
| **1"**     | 1.163"                | 1.049"               | 0.057"         |

------

## 4. Copper Pipe (Plumbing)

- **Standard:** ASTM B88 (Type M is standard retail).
- **Use Case:** Aesthetics, soldered joints.
- **Engineering Toolbox Source:** [Copper Tube Dimensions](https://www.engineeringtoolbox.com/copper-tubes-dimensions-pressure-d_84.html)

**Simulation Properties:**

```
json
Copy code
{
  "material": "Copper",
  "youngs_modulus_psi": 17000000,
  "yield_strength_psi": 30000,
  "density_lbs_in3": 0.323
}
```

**Common Dimensions (Type M - Thin Wall):**

| Trade Size | Outside Diameter (OD) | Inside Diameter (ID) | Wall Thickness |
| :--------- | :-------------------- | :------------------- | :------------- |
| **1/2"**   | 0.625"                | 0.569"               | 0.028"         |
| **3/4"**   | 0.875"                | 0.811"               | 0.032"         |
| **1"**     | 1.125"                | 1.055"               | 0.035"         |

------

## 5. Structural Tubing (Hardware Aisle)

Unlike "Pipe," these items are measured by exact outside diameter. They are found in the metal rack, not the plumbing aisle.

### Aluminum Tube (Round)

- **Source:** [Aluminum Tube Properties](https://www.engineeringtoolbox.com/aluminum-tubes-dimensions-d_1636.html)
- **Properties:** E = 10,000,000 PSI | Yield = 35,000 PSI (for 6061-T6)

### Steel Tube (Round & Square)

- **Source:** [Steel Tube Properties](https://www.engineeringtoolbox.com/steel-tubes-dimensions-d_54.html)
- **Properties:** E = 29,000,000 PSI | Yield = 40,000+ PSI

------

## 6. Master Simulation Table (Young's Modulus)

Use this lookup table for your physics engine to calculate deflection/bending.

| Material Key      | Young's Modulus (PSI) | Stiffness Rating |
| :---------------- | :-------------------- | :--------------- |
| `pvc_plastic`     | 400,000               | Low (Floppy)     |
| `wood_pine`       | 1,500,000             | Low-Mid (Varies) |
| `aluminum_6061`   | 10,000,000            | Medium           |
| `copper_drawn`    | 17,000,000            | High             |
| `steel_structure` | 29,000,000            | Very High        |