# The "Sick" Servo Database

*From Micro Tensioners to Industrial Monsters*

This list is categorized by **Use Case**. Do not buy a Monster Servo to pull a tiny trigger, and do not buy a Micro Servo to lift a leg.

------

## Tier 1: The "Sasori" Tensioners (Clutch & Trigger)

**Best For:** Capstan Amplifier inputs, clutch engagement, finger tendons, or switching mechanisms. **Requirement:** High speed, metal gears (to handle shock), small footprint.

### 1. The Budget King: MG90S (Metal Gear)

The absolute standard for cheap, durable micro actuation. Do not buy the plastic "SG90"—they strip instantly. The "S" stands for Metal.

- **Torque:** ~2 kg-cm
- **Speed:** 0.10s / 60°
- **Price:** ~$4 each (usually sold in packs).
- **🛒 Link:** [Search Amazon: MG90S Metal Gear Servo](https://www.amazon.com/s?k=MG90S+Metal+Gear+Servo)

### 2. The High-End Pro: KST X08 V5

Used in competitive RC gliders. Machined aluminum casing, high voltage (HV) compatible, zero slop.

- **Torque:** ~2.8 kg-cm
- **Speed:** Blindingly fast.
- **Price:** ~$40 each.
- **🛒 Link:** [Search Amazon: KST X08 Servo](https://www.amazon.com/s?k=KST+X08+Servo)

------

## Tier 2: The Workhorses (Direct Drive)

**Best For:** Wrists, Heads, Necks, or Grippers. These are standard PWM servos (3 wires).

### 3. The Standard: DS3235 ("The Blue One")

If you see a DIY robot on YouTube, it probably uses this. It is waterproof, strong, and cheap.

- **Torque:** 35 kg-cm
- **Internal:** Stainless Steel Gears.
- **Price:** ~$25.
- **🛒 Link:** [Search Amazon: DS3235SG 35kg Servo](https://www.amazon.com/s?k=DS3235SG+35kg+Servo)

### 4. The Budget Alternative: ANNIMOS 25kg ("The Red One")

Slightly cheaper than the blue one. Good for non-critical joints like opening a lid or moving an ear.

- **Torque:** 25 kg-cm
- **Price:** ~$15.
- **🛒 Link:** [Search Amazon: Annimos 25kg Servo](https://www.amazon.com/s?k=Annimos+25kg+Digital+Servo)

------

## Tier 3: The Smart Servos (Serial Bus)

**Best For:** Clean wiring. You can daisy-chain these (plug one into the next) so you only run one cable for the whole arm. They also provide data back (Temperature, Position, Voltage).

### 5. LewanSoul / Hiwonder LX-16A

The entry-level smart servo.

- **Torque:** 17 kg-cm
- **Comms:** Serial Bus (Requires a small USB adapter board to talk to Arduino/PC).
- **Price:** ~$17.
- **🛒 Link:** [Search Amazon: LewanSoul LX-16A Bus Servo](https://www.amazon.com/s?k=LewanSoul+LX-16A+Bus+Servo)

### 6. Feetech SCS15

Higher build quality and better protocol documentation than LewanSoul. Used in low-cost research robots.

- **Torque:** 15 kg-cm
- **Price:** ~$25.
- **🛒 Link:** [Search Amazon: Feetech SCS15 Smart Servo](https://www.amazon.com/s?k=Feetech+SCS15+Smart+Servo)

------

## Tier 4: The Monsters (Industrial Power)

**Best For:** Main limb joints if you refuse to use Brushless motors. These can break fingers.

### 7. AGFRC A81BH (Brushless Servo)

This uses a tiny brushless motor *inside* the servo case. It is silent, efficient, and insanely precise.

- **Torque:** 40+ kg-cm
- **Speed:** 0.08s (Instant).
- **Price:** ~$90.
- **🛒 Link:** [Search Amazon: AGFRC Brushless Servo](https://www.amazon.com/s?k=AGFRC+Brushless+Servo)

### 8. Feetech SM85CL ("The Brick")

A literal block of aluminum. Designed for heavy robot arms.

- **Torque:** **80 kg-cm**
- **Price:** ~$60 - $80.
- **🛒 Link:** [Search Amazon: Feetech 80kg Robot Servo](https://www.amazon.com/s?k=Feetech+80kg+Robot+Servo)

------

## ⚡ Crucial Wiring Tips

1. **Do NOT power these from the Arduino 5V pin.**
   - Even the small MG90S draws too much current. You will brown-out your brain.
   - **Solution:** Use a **UBEC** (Universal Battery Eliminator Circuit) or a **Buck Converter** to drop your 20V drill battery down to 6V/7.4V for the servos.
   - **🛒 Link:** [Search Amazon: 5V 3A UBEC](https://www.amazon.com/s?k=5V+3A+UBEC)
2. **Voltage Matters**
   - Standard Servos = 6V.
   - "HV" (High Voltage) Servos = 7.4V or 8.4V.
   - *Warning:* If you put 8.4V into a 6V servo, it will smoke instantly.
3. **Smart Servo Controllers**
   - If you buy Tier 3 (Smart Servos), you **Must** buy the **"Debug Board"** (USB Linker) to verify them and set their IDs before installing.