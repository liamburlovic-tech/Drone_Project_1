# Custom-Frame ISR Quadcopter

An **unarmed ISR (intelligence, surveillance, reconnaissance) demonstrator**: a quadcopter with a 3D-printed airframe I designed in CAD and carbon-fiber arms, flying PX4 on a Pixhawk 6C. In Phase 2, an onboard NVIDIA Jetson detects a target and follows it on its own.

| Phase | Goal | Status |
|---|---|---|
| **Phase 1 — Flight platform** | Custom CAD frame flying reliably on PX4, through an autonomous waypoint mission | 🟡 In progress |
| **Phase 2 — Onboard tracking** | Jetson + YOLO detects a designated target and commands the drone to follow it | ⚪ Not started |
| Phase 3 — GPS-denied navigation | Deferred | ⚪ |

## Milestones (verification gates)
| Gate | Milestone |
|---|---|
| G1 | CAD complete; FEA on arms and hub; mass budget |
| G2 | Bench build: PX4 configured, failsafes and kill switch checked (props off) |
| G3 | First hover; vibration and PID check |
| G4 | Position hold, endurance and failsafe flight tests |
| G5 | Autonomous waypoint mission → **Phase 1 complete** |
| G6–G8 | Phase 2: Jetson bench test → ground tracking test → in-flight tracking demo |

Progress is tracked in [Issues](../../issues) and [Milestones](../../milestones). Each issue references requirement IDs (e.g., `AF-5`) from the [requirements spec](docs/requirements-spec.md).

## Key specs (targets)
- 450–500 mm diagonal, 10" props, 2216 920KV motors, 4S 5,000 mAh LiPo
- All-up weight ≤ 2.0 kg; thrust-to-weight ≥ 2:1; hover ≥ 10 min with the Jetson running
- PETG printed hub and mounts, 16 mm carbon-fiber tube arms, TPU landing feet

## Repo layout
```
cad/              Onshape exports (STEP, STL), drawings, FEA results
docs/             Requirements spec, BOM, test reports
firmware/params/  PX4 parameter files (.params) per build revision
software/         Phase 2 tracking code (Python, MAVSDK, YOLO)
test/             Test procedures, checklists, flight-log summaries
```

## Toolchain
Onshape · SimScale/FEA · OrcaSlicer · PX4 · QGroundControl · PX4 Flight Review · MAVSDK-Python · Ultralytics YOLO + TensorRT · JetPack 6

## Safety and compliance
FAA-registered, Remote ID broadcast module, flown within visual line of sight under FAA rules. Failsafes (RC loss, low battery, geofence) and a transmitter kill switch are verified on the bench before every new configuration flies. No payloads, weapons or effectors of any kind.
