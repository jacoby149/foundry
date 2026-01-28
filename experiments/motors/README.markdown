# Detailed Motor Sourcing Guide

## Tier A: The "Scrapyard" Option (Hoverboard Hubs)

**Best for:** Maximum torque per dollar. Indestructible. Heavy. **The Strategy:** You are buying replacement wheels for "Self Balancing Scooters."

- **eBay (The Gold Mine):**
  - **Search Terms:** "Hoverboard Motor Replacement", "6.5 inch hub motor", "Self balancing scooter wheel".
  - **Link:** [eBay Search: Hoverboard Motors](https://www.ebay.com/sch/i.html?_nkw=hoverboard+motor+replacement)
  - *Note:* Look for "3 wire" (Phase) + "5 wire" (Sensor) bundles.
- **Amazon (New/Prime):**
  - If you don't want to wait for eBay shipping.
  - **Link:** [Replacement Hoverboard Motors on Amazon](https://www.amazon.com/s?k=hoverboard+replacement+motor)
- **The "How-To" Hack (CRITICAL):**
  - You cannot just bolt a pipe to the rubber tire. You need to remove the tire and drill the metal.
  - **Video Guide:** [How to turn a Hoverboard Motor into a Robot Actuator (YouTube)](https://www.youtube.com/results?search_query=hoverboard+motor+robot+actuator)
  - **ODrive Guide:** [Hoverboard Motor Configuration Guide](https://docs.odriverobotics.com/v/latest/guides/hoverboard.html)

------

## Tier B: The "Maker" Option (E-Skate Outrunners)

**Best for:** Lighter weight, standard mounting holes. Requires a timing belt (6:1) to work well. **Target Spec:** Size 6374 or 6384, KV < 190.

- **Flipsky (The Go-To Budget Brand):**
  - They supply the DIY E-Skate community. Reliable enough for robots.
  - **Product:** 6374 Battle Hardened Motor (190KV or 140KV).
  - **Link:** [Flipsky 6374 Motors](https://flipsky.net/collections/e-skateboard-motors/products/flipsky-electric-skateboard-motor-6374-190kv-3250w)
- **HobbyKing (Turnigy SK8):**
  - The classic RC supplier.
  - **Product:** Turnigy SK8 6374-149KV.
  - **Link:** [HobbyKing SK8 Motors](https://hobbyking.com/en_us/turnigy-sk8-6374-149kv-sensored-brushless-motor-14p.html)
- **Alien Power Systems (High End DIY):**
  - Based in UK. They sell low KV motors specifically for this stuff.
  - **Link:** [Alien Power 63mm Motors](https://alienpowersystem.com/shop/brushless-motors/63mm/)

------

## Tier C: The "Pro" Option (Integrated Actuators)

**Best for:** If you have a research grant. These are what the MIT Mini Cheetah actually uses. They have the gearbox built inside.

- CubeMars (T-Motor Industrial):
  - The **AK Series** is the industry standard for legged robots.
  - **Product:** AK60-6 (Small), AK80-9 (Medium).
  - **Link:** [CubeMars AK Series Actuators](https://store.cubemars.com/category.php?id=58)

------

## Crucial Accessories (The Transmission)

If you use **Tier B (E-Skate Motors)**, you cannot connect the motor directly to the leg (it spins too fast). You need a **Reduction**.

### 1. Timing Belts & Pulleys

- **Standard:** **HTD 5M** (High Torque Drive, 5mm pitch). This is stronger than 3D printer belts (GT2).
- The Setup:
  - **Motor Pulley:** 12 Tooth or 15 Tooth (Steel).
  - **Leg Pulley:** 72 Tooth or 90 Tooth (3D Printed or Aluminum).
  - **Belt:** HTD 5M Loop (calculate length based on distance).
- Where to buy:
  - **McMaster-Carr:** [Timing Belts & Pulleys](https://www.mcmaster.com/timing-belts/)
  - **Amazon:** Search "HTD 5M Pulley 15T".

### 2. Encoders (If Motor doesn't have them)

- **Hoverboard Motors:** Have Hall Sensors built-in (Good enough).

- **E-Skate Motors:** Usually have Hall Sensors.

- If you need high precision:

   

  Use an External Encoder.

  - **AS5047P:** The ODrive favorite. Magnetic absolute encoder.
  - **Link:** [DigiKey - AS5047P](https://www.digikey.com/en/products/detail/ams/AS5047P-TS_EK_AB/5452344)

------

## Summary Recommendation for your Build

**Start with Tier A (Hoverboard Motors).**

1. Go to eBay.
2. Buy 2 used motors (~$40 total).
3. Buy an ODrive S1 or a cheap VESC.
4. Try to control the motor with your laptop.
5. Once you feel that massive torque, build the pipe skeleton around it.