# Drone Requirements Specification — Phase 1 & 2
**Project:** Custom-Frame ISR Quadcopter
**Owner:** Liam | **Rev:** A | **Date:** 2026-11-17
**Status:** Draft for review

---

## 1. Purpose and scope

Build an **unarmed ISR (intelligence, surveillance, reconnaissance) demonstrator**: a quadcopter whose airframe is designed in CAD and 3D-printed. It carries an NVIDIA Jetson that detects a target and follows it on its own.

| Phase | Goal | Done when |
|---|---|---|
| **Phase 1 — Flight platform** | Custom CAD frame flying reliably on PX4 | Passes all Phase 1 requirements, including an autonomous waypoint mission and failsafe tests |
| **Phase 2 — Onboard tracking** | Jetson detects a designated target and commands the drone to follow it | Holds a moving target in frame for ≥ 60 s with no pilot stick input |

**Out of scope:** GPS-denied navigation (that's Phase 3, deferred), beyond-visual-line-of-sight flight, and any payload release, weapon or effector of any kind.

## 2. Constraints

| ID | Constraint |
|---|---|
| C-1 | Total budget target: $500–1,000 (see the BOM for the real total and ways to cut it) |
| C-2 | Companion computer: NVIDIA Jetson Orin Nano Super Developer Kit |
| C-3 | Flight stack: PX4 Autopilot on a Pixhawk-standard flight controller |
| C-4 | Printed parts must fit the Ender 3 V3 SE build volume (220 × 220 × 250 mm) and print in PLA or PETG (nozzle max 260 °C) |
| C-5 | Use existing open-source stacks (PX4, MAVSDK/ROS 2, Ultralytics YOLO) and keep custom code small |
| C-6 | All flights follow FAA rules (Section 4.8) |

## 3. Verification methods
**T** = Test, **D** = Demonstration, **A** = Analysis (hand calc, FEA, spreadsheet), **I** = Inspection

---

## 4. Requirements

### 4.1 Airframe (AF) — Phase 1
| ID | Requirement | Rationale | Verify |
|---|---|---|---|
| AF-1 | Motor-to-motor diagonal of 450–500 mm, sized for 10-inch props | A proven size class for a 1.5–2 kg quad carrying a Jetson | I |
| AF-2 | Frame = printed center hub and mounts + carbon-fiber tube arms (16 mm OD) | Arms are cheap to replace after crashes; printed hub shows design work | I |
| AF-3 | Every printed part fits within 220 × 220 × 250 mm | Printer limit (C-4) | I |
| AF-4 | All-up weight (AUW) ≤ 2.0 kg with battery and Jetson | Keeps thrust-to-weight and flight time in spec | T (scale) |
| AF-5 | Arm-tip deflection ≤ 2 mm at max motor thrust | Stiff arms give clean control and IMU data | A (FEA) |
| AF-6 | First arm bending natural frequency ≥ 20% away from the hover rotor frequency (~130–150 Hz, to be confirmed) | Avoids resonance that corrupts the IMU | A (FEA modal) + T (flight log FFT) |
| AF-7 | Flight controller sits on vibration-damped mounts at the center of mass | PX4 needs low vibration for a good state estimate | I + T |
| AF-8 | Hub survives a 1 m drop onto grass at AUW without structural cracking (arms may break) | Crash tolerance during learning | T |
| AF-9 | Battery mounts on a strap rail that lets its position move ±30 mm to trim the CG | Jetson mass shifts the CG | I |
| AF-10 | Phase 2 payload bay holds the Jetson and a forward/down-tilted camera on a printed mount with a fixed tilt of 0–45° | Tracking needs a view of the ground ahead | I |
| AF-11 | Landing gear clearance ≥ 60 mm under the lowest component | Protects the camera and Jetson | I |

### 4.2 Propulsion and power (PP) — Phase 1
| ID | Requirement | Rationale | Verify |
|---|---|---|---|
| PP-1 | Static thrust-to-weight ≥ 2.0 : 1 at AUW | Control margin for wind and maneuvers | T (thrust stand or manufacturer data) + A |
| PP-2 | Hover time ≥ 10 min with the Jetson running, landing at ≥ 20% battery | Enough time for a full tracking test | T |
| PP-3 | Hover throttle 35–55% | Too low hurts control resolution; too high leaves no margin | T (log) |
| PP-4 | 4S LiPo, XT60 connector, 4,000–5,500 mAh | Matches the motors and the Jetson buck converter | I |
| PP-5 | The Jetson is powered from its own 12 V buck converter (≥ 4.5 A), separate from the flight controller power module | NVIDIA asks for a stable 5–20 V input; a brownout on the Jetson must not affect flight | I + T |
| PP-6 | Battery voltage and current go to PX4 through a power module | Needed for the low-battery failsafes | T |
| PP-7 | Motor temperature ≤ 70 °C after a 10-min hover | Motor health | T (IR thermometer) |

### 4.3 Flight control (FC) — Phase 1
| ID | Requirement | Rationale | Verify |
|---|---|---|---|
| FC-1 | Runs PX4 on a Pixhawk 6C-class controller with GPS + compass | Industry-standard stack used across defense UAS | I |
| FC-2 | Supports Stabilized, Altitude, Position, Mission, Return and Offboard modes | Offboard is what Phase 2 uses | D |
| FC-3 | Position hold within ±1.5 m horizontal and ±0.5 m vertical in winds ≤ 10 mph | Steady platform for tracking | T (log) |
| FC-4 | Flies an autonomous waypoint mission of ≥ 4 waypoints and returns home | Phase 1 gate | D |
| FC-5 | IMU vibration levels fall in PX4 Flight Review's acceptable range | Validates AF-6/AF-7 | T |
| FC-6 | PID tuning documented with before/after step responses | Evidence of controls work | A + T |

### 4.4 Safety and failsafes (SF) — Phases 1 & 2
| ID | Requirement | Rationale | Verify |
|---|---|---|---|
| SF-1 | RC link loss > 1.5 s → Return to Launch | Standard failsafe | T (turn off transmitter in flight) |
| SF-2 | Battery ≤ 30% → Return; ≤ 20% → Land | Prevents dead-battery crashes | T |
| SF-3 | Geofence: 100 m radius, 50 m altitude; breach → Return | Keeps the drone in the test area | T |
| SF-4 | An emergency motor kill switch on the transmitter works in every mode | Last-resort safety | T (on the bench, props off) |
| SF-5 | The pilot can take control back from Offboard with one switch, at any time | The human always has authority | T |
| SF-6 | The Jetson can't arm, disarm or change the geofence; only the pilot can | Limits what software bugs can do | I (configuration) + T |
| SF-7 | Bench tests with props off; first power-up through a current-limited "smoke stopper" | Protects parts and people | I |
| SF-8 | A written pre-flight checklist is used before every flight | Operational discipline | I |

### 4.5 Communications (CM)
| ID | Requirement | Phase | Verify |
|---|---|---|---|
| CM-1 | RC link (2.4 GHz ExpressLRS) with ≥ 500 m line-of-sight range | 1 | T (range check) |
| CM-2 | Ground station (QGroundControl) shows live telemetry: position, battery, mode | 1 | D |
| CM-3 | Jetson ↔ flight controller over serial (TELEM2) via MAVLink or uXRCE-DDS at ≥ 10 Hz | 2 | T |
| CM-4 | The ground station can view a low-rate (≥ 5 FPS) annotated video stream from the Jetson over Wi-Fi within 100 m | 2 | D |

### 4.6 Compute and vision (CV) — Phase 2
| ID | Requirement | Rationale | Verify |
|---|---|---|---|
| CV-1 | Detects the target class (person or vehicle) at ≥ 15 FPS at 640 px input, using a TensorRT-optimized YOLO model | Fast enough for smooth tracking | T (bench) |
| CV-2 | Detection precision ≥ 0.8 for the target class at 8–15 m range in daylight | Avoids chasing false targets | T (labeled test set from own footage) |
| CV-3 | Camera-to-command latency ≤ 150 ms | Tracking loop stability | T (timestamp log) |
| CV-4 | The operator picks one target to follow (click in the ground-station video or nearest-to-center at engage) | Follows one designated target, not anything detected | D |
| CV-5 | Jetson draws < 15 W during flight (15 W power mode) | Power budget | T |
| CV-6 | Jetson runs headless and auto-starts the tracking software at boot | Nothing to plug in at the field | D |

### 4.7 Tracking behavior (TR) — Phase 2
| ID | Requirement | Rationale | Verify |
|---|---|---|---|
| TR-1 | Keeps the target's center within ±15% of the frame center for ≥ 60 s while it moves at ≤ 3 m/s (walking or jogging) | Main Phase 2 success metric | T (video and log) |
| TR-2 | Stand-off distance 8–15 m, altitude 5–15 m above ground | Safe separation; good image scale | T |
| TR-3 | Offboard velocity commands capped at 3 m/s horizontal and 1 m/s vertical | Bounds the software's authority | I + T |
| TR-4 | Target lost > 2 s → hold position; lost > 10 s → exit Offboard to Position mode and alert the ground station | Predictable lost-target behavior | T |
| TR-5 | Every tracking flight logs the annotated video, detections and PX4 log (ULog) | Evidence and debugging | I |
| TR-6 | Tracking tests use only consenting participants or the owner's own vehicle | Privacy and ethics | I (test log) |

### 4.8 Regulatory (RG)
| ID | Requirement | Verify |
|---|---|---|
| RG-1 | Drone registered with the FAA (it's well over 250 g) and marked with the registration number | I |
| RG-2 | Remote ID met with an FAA-compliant **broadcast module**, flown within visual line of sight | I |
| RG-3 | Pilot holds the right credential: TRUST certificate if flying recreationally, or a Part 107 certificate if any flight furthers a business or job purpose | I |
| RG-4 | Airspace checked before every flight (B4UFLY/LAANC); check authorization near Don Scott Airport (KOSU) and follow university drone policy | I |
| RG-5 | Max altitude 400 ft AGL; no flights over people or moving vehicles that aren't part of the test | I |

---

## 5. Mass budget (estimate — update with measured weights)
| Item | Est. mass (g) |
|---|---|
| Printed hub, mounts, landing gear + CF arms | 350 |
| Motors (4 × ~63 g) | 252 |
| ESCs (4) + wiring | 150 |
| Props (4) | 52 |
| Flight controller + GPS + power module | 90 |
| RC receiver + Remote ID | 35 |
| **Phase 1 subtotal (no battery)** | **~930** |
| Battery, 4S 5,000 mAh | ~520 |
| Jetson Orin Nano dev kit + buck converter + camera | ~230 |
| **AUW (Phase 2)** | **~1,680 (limit 2,000)** |

## 6. Power and flight-time estimate
- Hover power at ~1.7 kg with 10-inch props: roughly 200–230 W, plus ~15 W for the Jetson.
- Usable energy: 5,000 mAh × 14.8 V × 80% ≈ 59 Wh.
- Estimated hover time ≈ 59 Wh ÷ 240 W × 60 ≈ **~14 min**, which meets PP-2 (≥ 10 min) with margin. Verify in flight test.

## 7. Milestones and verification gates
| Gate | Milestone | Key requirements |
|---|---|---|
| G1 | CAD complete; FEA on arms and hub; mass budget | AF-1 to AF-6, AF-9 to AF-11 |
| G2 | Bench build: props off, PX4 configured, failsafes and kill switch checked | PP-5, PP-6, SF-4, SF-6, SF-7 |
| G3 | First hover (tethered or low), vibration and PID check | FC-5, FC-6, PP-3 |
| G4 | Position hold, endurance, failsafe flight tests | FC-3, PP-2, PP-7, SF-1 to SF-3, SF-5 |
| G5 | Autonomous waypoint mission → **Phase 1 complete** | FC-4, CM-1, CM-2 |
| G6 | Jetson on the bench: detection FPS, latency, MAVLink link | CV-1 to CV-3, CV-5, CV-6, CM-3 |
| G7 | Ground test: Jetson + camera tracking a walking person (props off) | CV-4, TR-4 |
| G8 | In-flight tracking demo → **Phase 2 complete** | TR-1 to TR-6, CM-4 |

## 8. Top risks
| Risk | Mitigation |
|---|---|
| Printed hub cracks or flexes | FEA first, PETG with high infill, CF tubes take the bending load |
| Arm resonance makes PX4 unstable | Modal FEA (AF-6), damped FC mount, PX4 notch filter |
| Jetson brownout or reboot mid-flight | Separate buck converter (PP-5); PX4 falls back to hold on Offboard loss (TR-4) |
| Software is too hard to write | Use MAVSDK-Python + Ultralytics examples; test in PX4 SITL simulation before flying |
| Over budget | See the BOM's cost-cut options |
| Crashes eat spare parts | Budget for spare props and arms; fly over grass |
