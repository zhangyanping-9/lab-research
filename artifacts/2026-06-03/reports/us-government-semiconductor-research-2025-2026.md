# US Government / Defense Semiconductor Research Directions (2025-2026)

> Comprehensive research on programs, funding, focus areas, milestones, and key institutions across 20+ US government semiconductor R&D organizations.
> Compiled: 2026-06-03

---

## Table of Contents

1. [DARPA ERI 2.0 — NGMM, JUMP 2.0, Minitherms3D](#1-darpa-eri-20)
2. [Natcast / NSTC — CHIPS Act EUV Accelerator](#2-natcast--nstc)
3. [SRC JUMP 2.0 — 7 Research Centers](#3-src-jump-20)
4. [DoD Microelectronics Commons — 8 Hubs](#4-dod-microelectronics-commons)
5. [NY CREATES / Albany NanoTech — High NA EUV](#5-ny-creates--albany-nanotech)
6. [NIST Semiconductor Program — Metrology & Standards](#6-nist-semiconductor-program)
7. [Lawrence Livermore National Laboratory](#7-lawrence-livermore-national-laboratory)
8. [Sandia National Laboratories](#8-sandia-national-laboratories)
9. [Oak Ridge National Laboratory](#9-oak-ridge-national-laboratory)
10. [Argonne National Laboratory / Q-NEXT](#10-argonne-national-laboratory--q-next)
11. [Berkeley Lab Molecular Foundry](#11-berkeley-lab-molecular-foundry)
12. [Los Alamos National Laboratory](#12-los-alamos-national-laboratory)
13. [Brookhaven National Laboratory / CFN](#13-brookhaven-national-laboratory--cfn)
14. [NREL Wide Bandgap Semiconductors](#14-nrel-wide-bandgap-semiconductors)
15. [Fermilab SQMS](#15-fermilab-sqms)
16. [AFRL — Air Force Research Laboratory](#16-afrl)
17. [NRL — Naval Research Laboratory](#17-nrl)
18. [ARL — Army Research Laboratory](#18-arl)
19. [MIT Lincoln Laboratory](#19-mit-lincoln-laboratory)

---

## 1. DARPA ERI 2.0

### Overview
DARPA's **Electronics Resurgence Initiative (ERI)** launched in 2017 as a $2B+ program. **ERI 2.0** launched October 2025, focusing on 3D heterogeneous integration and beyond-Moore technologies.

### ERI 2.0 — Key Technical Focus
- **3D SoC**: Targeting 90nm mature process nodes to achieve 50x better performance-per-watt than 7nm
- **Carbon Nanotube FETs (CNFETs)**: MIT/Max Shulaker group pioneered vertical stacking of CNFET logic + RRAM memory
- **Monolithic 3D Integration**: Dec 2025 -- Stanford, CMU, SkyWater fabricated first commercial monolithic 3D chip (Si CMOS logic + RRAM + CNFET layers at ~415C thermal budget), achieving 4x performance of 2D chips
- **SkyWater Technology** partnering to commercialize 3D CNT technology

---

### NGMM — Next-Generation Microelectronics Manufacturing ($840M)

| Parameter | Detail |
|-----------|--------|
| **Total Investment** | $1.4B ($840M DARPA + $552M Texas) |
| **Lead Institution** | Texas Institute for Electronics (TIE) @ UT Austin |
| **Goal** | First US national center for 3D heterogeneous integration (3DHI) |
| **Model** | "High-mix, low-volume" foundry bridging lab-to-fab gap |

**Timeline**:
- Phase 1 awarded Jul 2024 (2.5 yrs, infrastructure + basic capabilities)
- Q1 2026: All fab tools in place at Austin facility
- Phase 2: 2.5 yrs building 3DHI prototypes + automation

**Participants**: 32 defense/commercial companies + 18 universities including:
- **Penn State** ($7.5M) -- glass packaging for 3DHI
- **Georgia Tech** -- 3DHI design, fabrication, assembly, characterization

**Three Exemplar Projects**: Phased-array radar, IR focal plane array imager, compact power converter

---

### Minitherms3D

| Parameter | Detail |
|-----------|--------|
| **Agency** | DARPA Microsystems Technology Office |
| **Duration** | 4 years, 3 phases (began early 2023) |
| **Objective** | Scalable thermal mgmt for 3DHI chip stacks |

**Phase 2 Awards (2025)**:
- **Teledyne Scientific & Imaging**: $9.8M (through Jan 2028)
- **HRL Laboratories**: $7.8M option exercised Aug 2025 (total ~$15.2M)

**Technical Targets**:
- Phase 1: 3-tier stack, 4 kW dissipation
- Phase 2: 5-tier stack, 6.8 kW dissipation
- Hotspots >1 kW/cm^2, avg heat flux >150 W/cm^2
- Heat rejection system target: <0.006 m^3

---

### JUMP 2.0
*(Covered in detail under SRC section -- co-sponsored with DARPA)*

---

## 2. Natcast / NSTC

### Overview
The **National Semiconductor Technology Center (NSTC)**, operated by **Natcast** (non-profit designated by DOC), is the flagship R&D entity under the CHIPS and Science Act.

### NSTC EUV Accelerator -- Albany, NY

| Event | Date |
|-------|------|
| CHIPS funding awarded | Oct 31, 2024 |
| Operations begin | Jul 1, 2025 |
| Grand opening / ribbon-cutting | Jul 14, 2025 |
| Standard NA EUV (0.33 NA) | Available Jul 2025 |
| High NA EUV access | Expected end of 2026 |
| NanoFab Reflection completion | End of 2026 |
| High NA EUV equipment arrival | Mid-2026 |

**Funding**:
- $825M federal CHIPS Act funding to NY CREATES
- NanoFab Reflection building: $410M
- Broader ecosystem: ~$100B in NY semiconductor investments

**Facility Capabilities**:
- Cutting-edge EUV lithography tools (0.33 NA + High NA)
- 310,000 sq ft NanoFab Reflection building (50,000 sq ft cleanroom)
- Collaboration space for industry/academia/gov partners
- Workforce development programs

**Industry Partners**: IBM, Micron, Applied Materials, Tokyo Electron, SCREEN ($75M/10yr R&D), Edwards Vacuum, Menlo Micro, TTM Technologies

### Three NSTC Flagship R&D Facilities

| Facility | Location | Status |
|----------|----------|--------|
| **EUV Accelerator** | Albany, NY | Opened Jul 2025 |
| **Design & Collaboration Facility (DCF)** | Sunnyvale, CA | Expected operational 2025 |
| **Prototyping & NAPMP Advanced Packaging Facility** | TBD | Expected ~2028 |

**Recent RFIs (Jul 2025)**:
1. Interconnect Materials and Processes for Computing Applications
2. Co-Packaged Optical Engine Development for AI Infrastructure

**NSTC Leadership**: Deirdre Hanford (Natcast CEO)

---

## 3. SRC JUMP 2.0

### Overview
**Joint University Microelectronics Program 2.0** -- SRC-led public-private partnership with **DARPA**, co-sponsored by SRC, DARPA, commercial semiconductor industry, and defense industrial base.

**Total Investment**: $331M

### The 7 Research Centers

| Theme | Center Name | Lead University |
|-------|-------------|----------------|
| Cognition | Center for Co-Design of Cognitive Systems | Georgia Tech |
| Communications/Connectivity | Center for Ubiquitous Connectivity (CUbiC) | Columbia University |
| Intelligent Sensing to Action | Center on Cognitive Multispectral Sensors | Georgia Tech |
| Distributed Compute Systems | Evolvable Comp. for Next-Gen Distributed Compute | UIUC |
| Intelligent Memory/Storage | Processing with Intelligent Storage & Memory (PRISM) | UC San Diego |
| Advanced Monolithic/Heterogeneous Integration | Heterogeneous Integration of Micro Electronic Systems (CHIMES) | Penn State |
| High-Performance Energy-Efficient Devices | Superior Energy-efficient Materials and Devices (SUPREME) | Cornell |

**Industry Participants**: Intel, Samsung, GlobalFoundries, Micron, IBM, TSMC, Boeing, ARM, Analog Devices, Qorvo, SK Hynix, MediaTek, Raytheon

**Timeline**: Active through 2025-2026 (SRC site updated May 2026)

---

## 4. DoD Microelectronics Commons

### Overview
National network of **8 regional innovation hubs** funded through CHIPS and Science Act. Total: **$2B (FY23-FY27)**.

### The 8 Hubs

| Hub | Lead | Location | FY23 Award | Members |
|-----|------|----------|-----------|---------|
| **NORDTECH** | Research Foundation for SUNY | Albany, NY | $40.0M | 51 |
| **CA DREAMS** | USC Information Sciences Institute | Southern CA | $26.9M | 16 |
| **SWAP** | Arizona State University | Tempe/Phoenix, AZ | $39.8M | 27 |
| **MMEC** | Midwest Microelectronics Consortium | OH | $24.3M | 65 |
| **NEMC** | MassTech Collaborative | MA | $19.7M | 90 |
| **SCMC** | Applied Research Institute | IN | $32.9M | 130 |
| **CLAWS** | NC State University | NC | $39.4M | 7 |
| **NW-AI Hub** | Stanford University | Northern CA | $15.3M | 44 |

### Budget Breakdown (FY23-27)

- FY26 allocation: ~$320M to hubs, ~$41M Tri-Service Labs, ~$39M admin
- Six technical areas each receiving ~$53.3M in FY26:
  1. Secure Edge / IoT Computing
  2. 5G/6G Technology
  3. AI Hardware
  4. Quantum Technology
  5. Electromagnetic Warfare
  6. Commercial Leap Ahead Technologies

### 2025-2026 Activity

- **FY26 Call for Projects**: Released Nov 21, 2025; white papers due Jan 12, 2026
- **2026 Annual Meeting**: Feb 18-20, 2026, Washington DC
- **Year 2 awards**: Apr-May 2026 (e.g., NORDTECH ~$25M in 2nd-year awards)
- **$160M additional investments** (Nov 2024): $148M to hubs for infrastructure/workforce
- **33 project awards** totaling ~$269M across 6 technical areas

**Notable Outcomes**:
- CA DREAMS cut RF chip dev time in half for 5G/6G/EW
- AmmP3 ($28.3M) and GaNAmp ($33.7M) -- lab-to-fab transitions with Northrop Grumman

---

## 5. NY CREATES / Albany NanoTech

### Overview
NY CREATES owns and operates the **Albany NanoTech Complex**, home to the **NSTC EUV Accelerator**.

**Total Ecosystem Investment**: $25B+ public-private (includes $1B NY State + $9B industry leveraged)

### Key Milestones

| Event | Date |
|-------|------|
| NSTC EUV Accelerator Grand Opening | Jul 14, 2025 |
| Standard NA EUV available | Mid-2025 |
| NanoFab Reflection topping-out | Dec 8, 2025 |
| High NA EUV equipment arrival | Mid-2026 |
| NanoFab Reflection completion | End 2026 |

### Facilities
- **NanoFab Reflection**: 310,000 sq ft with 50,000 sq ft cleanroom
- Houses ASML High NA EUV -- world's most advanced tool for sub-2nm features
- IBM demonstrated sub-2nm capability at this complex in 2021

**Economic Impact**: $124B in planned semiconductor capital investments across NY.

---

## 6. NIST Semiconductor Program

### Overview
CHIPS Act allocated **$11B for semiconductor R&D**; NIST leads CHIPS for America Programs.

### CHIPS Metrology Program -- Seven Grand Challenges

| Grand Challenge | Focus Area |
|----------------|------------|
| GC1 | Materials Purity, Properties, and Provenance |
| GC2 | Advanced Metrology for Future Manufacturing |
| GC3 | Metrology for Advanced Packaging |
| GC4 | Modeling & Simulating Semiconductor Materials/Devices/Components |
| GC5 | Modeling & Simulating Semiconductor Manufacturing Processes |
| GC6 | Standardizing New Materials, Processes, and Equipment |
| GC7 | Security and Provenance of Microelectronic Components/Products |

**64 funded research projects** across all grand challenges.

### Key 2025-2026 Activities

- **CSF 2.0 for Semiconductor Manufacturing**: Draft published Feb 2025
- **Trust & Provenance Workshop**: Apr 15, 2025; follow-up Oct 21, 2025
- **Metrology R&D Workshop**: Apr 20-21, 2025 (AMD, Plexus, TTM, Amkor, IBM)
- **SMART USA Institute**: Digital twins for semiconductor manufacturing
- **Procurement actions**: AFM for SEM (2D materials), Mid-IR Optical Frequency Combs, Mid-IR Femtosecond Laser Source for plasma etching metrology

**NVLAP Expansion**: New microelectronics-specific accreditation parameters + new SRMs and SRIs.

---

## 7. Lawrence Livermore National Laboratory

### Key Research Areas

#### Massively Parallel Two-Photon Lithography (TPL)
- Published in *Nature* 648, 591-599 (2025)
- Collaboration with Stanford: metalens arrays splitting laser into 120,000+ focal spots
- **1000x higher throughput** than commercial systems, sub-113nm features
- **2025 R&D 100 Award** winner
- Webinar: Feb 24, 2026 (licensing/co-development)

#### Diamond Optically Gated JFET
- High-power diamond semiconductor transistor for grid control
- 3 devices in series: >6 kV (double existing WBG commercial options)
- DOE self-funded, ~$3M

#### Other Research
- **Semiconductor Opening Switch (SOS)** diodes for pulsed power
- **Superconducting quantum circuits** (neon-ice-modulated, published PR Applied Feb 2026)
- **3D nuclear battery** (radiovoltaic) for space/biomedical
- AI for science (Claude deployed to ~10,000 scientists, Jul 2025)

---

## 8. Sandia National Laboratories

### MESA Facility & Fabrication

- **MESA Silicon Microfabrication**: 186 consecutive lots on/ahead of schedule; production cycles cut in half for CMOS7, CMOS8, Si Photonics, Quantum Ion Trap
- **CMOS8**: Achieved level-5 technology readiness + level-4 manufacturing readiness
- **$30M budget request** for photolithography capability + microelectronics components modernization (critical decision zero in FY2026)

### Advanced Research

- **Heterogeneously Integrated Photonics Platform** (UV to SWIR) -- Apr 2026 webinar with CA DREAMS
- **LDRD Campaigns** (FY2026, $45M each over 7 years):
  1. Radiation Assured Design and Testing for Electronics
  2. Digitally Realized/Enabled Agile Advanced Manufacturing

### Quantum & Materials

- Ge quantum well mobility enhancement (tin + silicon doping)
- Cryogenic phononic four-wave mixing in AlScN/SiC (APL, Jun 2026)
- III-V semiconductor radiation damage models (OSTI 2025)

### Workforce
- Partnership with Central New Mexico CC for quantum technician training (Jun 2025)
- Co-founded new microelectronics research center (Jan 2025)
- **IEEE Fellows 2026**: Edward Cole, Charles Hanley

---

## 9. Oak Ridge National Laboratory

### Key Research (2025-2026)

#### Ferroelectric Aluminum Nitride (May 2026)
- Writing ferroelectric regions in AlN using He ion beam
- Reduced switching voltage ~40%, boosted electromechanical response
- Lower-energy non-volatile memory compatible with existing CMOS

#### GaN Power Converters (May 2026)
- High-efficiency GaN converters: 10-20x faster switching than Si
- Designed for AI data center applications
- Validated at GRID-C

#### AI-Driven Autonomous Discovery (CNMS)
- Adaptive synthesis for oxide membranes
- Multimodal fusion for ferroelectric memory degradation
- Part of DOE "Alphafold for Microelectronics" initiative

#### Quantum-Relevant Magnetism (Mar 2026)
- Ta-W-Se crystal with unexpected atomic self-organization
- Triangular 10-atom clusters triggering magnetic transitions below 50K
- Potential for spintronics

#### AXESS Project (Fermilab-led multi-lab)
- AI-accelerated chip design (months to weeks)
- 500x speedup for qubit readout design
- Targets quantum computing, fusion energy, particle physics

#### Infrastructure
- **Lux supercomputer** (2026): $1B partnership with AMD + HPE
- Complements Frontier (exascale) + Discovery (2028)

---

## 10. Argonne National Laboratory / Q-NEXT

### 12-Qubit Silicon Quantum Dot Processor (2025-2026)
- Argonne + Intel: "Tunnel Falls" processor
- Fabricated on Intel 300mm wafers with EUV lithography
- >95% yield across tens of thousands of quantum dot devices per wafer
- Published in *Nature Communications*

### Q-NEXT Renewal (Nov 2025)
- DOE renewed for **5 years at $125M** ($25M FY2026)
- New Director: **Martin Holt** (Argonne)
- Three science goals:
  1. Quantum communication networks (metro-scale)
  2. Quantum sensing (medical imaging, navigation, physics)
  3. Quantum materials integration

### SLAC & Stanford Collaboration
- First high-bandwidth multi-qubit-type quantum network
- SLAC superconducting quantum foundry (co-located with LCLS/SSRL)

### Open Quantum Initiative
- 27 undergraduate fellows (Summer 2025)
- New awards: Prof. Michael Flatte (U Iowa) -- $482K (Apr 2026)

---

## 11. Berkeley Lab Molecular Foundry

### Photon-Avalanching Nanoparticles (Feb 2025)
- First intrinsic optical bistability at nanoscale (30nm K-Pb-halide nanoparticles)
- Record-high nonlinearity, 3x greater than previous materials
- Published in *Nature Photonics*
- Potential for optical transistors and memory

### Short-Range Ordering in Semiconductors (Sep 2025)
- Ge(Sn,Si) short-range order motifs confirmed experimentally
- Published in *Science*
- 4D-STEM + ML identified 6 recurring atomic motifs
- Andrew Minor (NCEM director) co-led

### AI-Driven Thin Film Deposition (2026)
- AI-assisted PVD for quantum transducers
- Integrating lithium niobate with superconductors

### Other Research
- **Polymer PIC platform** (NASA STTR Phase I, $148,646, Sep 2025-Oct 2026)
- **WANDA & HERMAN robots**: automated nanoparticle synthesis + AI
- **mu-Atoms EFRC**: DOE center for atomic ordering in semiconductors

---

## 12. Los Alamos National Laboratory

### CHIME Microelectronics Science Research Center
- Multi-institution project: Co-design and Heterogeneous Integration in Microelectronics for Extreme Environments
- **NSOC** (Nano Solutions On-Chip) led by Jennifer Hollingsworth @ CINT
- Quantum dots using photons + electrons as info carriers
- 3D stacking of electronic + photonic components
- Partners: UPenn, Columbia, UW-Madison, Duke, Sandia

### GaN-on-SiC High-Power RF Amplifiers
- Replacing klystrons with solid-state GaN-on-SiC HEMTs at 805 MHz
- Targeting 1.25 MW output with modular 5 kW GaN pallets
- For LANSCE CCL operations beyond 2050

### Novel Computing Paradigms (Jul 2026 Workshop)
- Neuromorphic and near-memory computing
- Memristive/ferroelectric devices, magnetic/photonic platforms
- Co-hosted with Prof. Judith Driscoll (Cambridge)

### Other Research
- **HPC Storage Acceleration**: MaxLinear Panther SoC -- 39x write speedup, 57 GB/s read (Jun 2026)
- **Space-based AlN growth** (NASA SBIR with Nitride Global/Axiom Space, Feb 2026)
- **D-Wave quantum computer** as physics simulation platform

---

## 13. Brookhaven National Laboratory / CFN

### CFN Research Focus (2025-2026)

#### EUV Interference Lithography
- Postdoctoral position (Feb 2026): advancing EUV interference lithography
- Sub-15nm patterning for "Angstrom era" chip manufacturing
- Sub-30nm mask development

#### 2D Materials for Steep-Slope Transistors
- TMDC heterostructures for energy-efficient microelectronics
- Part of DOE MSRC project

#### Superconducting Qubits
- Preetha Sarkar won Research SLAM (Dec 2025) for higher-temperature qubits
- Compatible with existing Si manufacturing techniques
- Transition metal silicide devices at 300mm wafer scale (NY CREATES)

### Facility
- 5,000 sq ft class 100/1000 cleanroom
- 2026 NSLS-II + CFN Users' Meeting (Apr 21 - May 6, 2026): AI showcase, operando science, nanotomography, quantum materials
- Director: Kevin Yager (Interim CFN Director)

---

## 14. NREL Wide Bandgap Semiconductors

### Core Research Areas
- UWBG (Eg > 3.4 eV) and WBG (Eg > 2.7 eV) semiconductors
- Materials: GaN, AlGaN, AlN, Ga2O3, ternary oxides/nitrides, Zintl-phase quantum dots

### Computational Screening (Aug 2025)
- High-throughput screening of 1,300+ compounds for GaN alternatives
- >250 candidates surpass GaN in Johnson/Baliga high-frequency FOMs
- **InBO3** (bandgap 4.9-5.2 eV): predicted n-type Baliga FOM ~6,000x Si
- Top thermal conductors: Si3N4, MgSiN2, ZnSiN2, ZnGeN2, BeS

### Substrate Engineering for AlGaN (Mar 2025)
- Tantalum carbide (TaC) as lattice-matched virtual substrate for vertical AlGaN
- TaC: matched thermal expansion, high conductivity, reduced dislocations
- First-principles models for rocksalt-wurtzite interfaces

### Earth-Abundant Quantum Dots (Sep 2025)
- BaCd2P2 Zintl-phase semiconductor quantum dots
- Defect-tolerant, tunable photoluminescence
- Zn substitution to reduce Cd content

### Hiring (2026)
- Postdoctoral researcher for Ga2O3 and AlGaN power diodes/transistors
- TCAD device design, cleanroom processing, dielectric passivation

**Key Researchers**: Andriy Zakutayev, Stephan Lany, Dennice Roberts, Sage Bauers, Nancy Haegel

---

## 15. Fermilab SQMS

### SQMS 2.0 Renewal (Late 2025)
- DOE renewed SQMS for 5 years at **$125M**
- 40+ partner institutions, 300+ scientists/engineers

### Three Major Goals
1. Chip-based materials/device breakthroughs
2. 100+ qudit SRF quantum processor at Fermilab
3. First scalable quantum data-center unit

### Technical Milestones
- Transmon coherence >1 ms
- Two-cell cavity-qudit systems >20 ms coherence
- Fock states up to N=20 with >95% fidelity, two-mode entanglement 99.9% fidelity
- Identified oxygen vacancies in Nb2O5 as primary TLS loss source
- Surface encapsulation (Nb capped with Ta) for loss mitigation
- Sapphire substrate loss: tan delta ~4e-8 after annealing

### New Partnerships
- **Northern Illinois University** (Dec 2025)
- **Bluefors**: Cryogenic cooling for scalable quantum architectures
- **USRA**: NASA Quantum AI Lab support

### Quantum Sensing
- Dark matter searches using ultra-coherent SRF cavities
- Gravitational wave detection

---

## 16. AFRL

### Key Programs & Funding

#### UAlbany Grant (Aug 2025)
- $1.65M, 3-year grant for nanoscale device fabrication
- Neuromorphic chip technology (memristors) for low-power defense AI
- Work at NY CREATES Albany NanoTech + NORDTECH hub

#### MINSAV (Ongoing through Oct 2029)
- Microelectronics Innovation for Next-generation System Advancement and Validation
- Design/fab of microelectronics for autonomous systems, AI, PNT, EW, strategic applications
- Updated May 30, 2025

#### SRC $24M AF Contract (Jan 2026)
- Next-gen embedded AI/ML for ground, air, space domains
- Ultra-low SWaP hardware for contested environments, edge processing

#### Raytheon/AFRL TFLN Wafer Production (Feb 2026)
- Domestic thin-film lithium niobate wafer production
- >100 GHz modulators, quantum computing, advanced sensing
- Tech transfer to G&H; low-rate initial production early 2026

#### AFRL Patent Holiday (Jan 2026)
- Free 2-year licenses for 25+ patents including:
  - Secure logic devices with hardware Trojan protection
  - Advanced materials, rare-earth-free magnets

#### AMAC IDIQ (2026)
- Major new contract vehicle: AI, quantum, microelectronics, hypersonics, space
- 5-year + 3 optional years

---

## 17. NRL

### Key Research Areas

#### NRL4 ASIC Development
- 32-channel front-end ASIC for gamma-ray astrophysics (COSI NASA mission, launch 2027)
- 6.8 mW/channel, 3 keV FWHM resolution, 14.5 ns timing

#### Wide-Bandgap Semiconductors
- John Lyons elected 2025 APS Fellow for Ga2O3 and GaN work
- GaN multi-channel power switches with ion-implanted ohmic contacts (2025)
- Innovation Day (May 2025): GaN RF transistors, SiC/GaN power electronics, MWIR detectors

#### Radiation Hardness
- Adrian Ildefonso received Alan Berman Award for laser-based SEE testing (replacing accelerator testing)

#### FY26 Budget: "Electric Materials" Initiative ($114.7M)
- Semiconductor growth: MBE, MOCVD, ALD, e-beam deposition
- Atomically thin monolayer films
- Nanometer-scale fabrication (e-beam, FIB, AFM)

#### 2026 Sources Sought (Est. $2-10M)
- Electronic Sciences & Technology Division support
- Modeling, simulation, fabrication, testing (Mar 2026)

---

## 18. ARL

### Key Research Areas

#### SEMI FlexTech RFP (2026, funded by ARL)
- Awards: $250K-$500K per project
- Flexible hybrid electronics, 2D materials, advanced bonding, flexible energy storage
- Proposals due Jul 6, 2026

#### Ferroelectric & MEMS Research (Summer 2025)
- Microsystems, ferroelectrics, 2.5D integration, MEMS
- Circuit design, chip-to-chip bonding, EM spectrum sensing

#### Predictive Modeling for RF Electronics (2024-2025)
- Dr. Mahesh Neupane: DEVCOM Modeling & Simulation Award
- Quantum mechanics-based multiscale modeling of multiphase polar heterostructures
- Transistors for extreme environments targeting 2045+ technologies

#### ARL BAAs
- Ultra-low-power microelectronics, reliability, SWaP-C optimization
- Neuromorphic computing, ruggedized computing, quantum detection

#### ARL-USMA Collaboration (May 2026)
- 20+ projects: advanced photonics, quantum sensing, additive manufacturing, AI

#### Awards
- **2025 S&T Reinvention Laboratory of the Year** (announced Mar 2026)
- Thorium-229 nuclear clock (with UCLA/UC Boulder)
- Catalyst Pathfinder Program: 40+ prototypes, 10 fielded

---

## 19. MIT Lincoln Laboratory

### Microelectronics Laboratory (MEL)
- US Government's most capable **200mm wafer fabrication prototyping facility**
- Lithography: 193nm, 248nm, 365nm + maskless laser/e-beam
- End-to-end: superconducting electronics, quantum circuits, rad-hard devices, imagers, PICs, MEMS

### Key Research Breakthroughs

#### Chip-Based Trapped-Ion Cooling (Feb 2026)
- Photonic chip with nanoscale antennas for polarization-gradient cooling
- 10x below Doppler limit, ~100 microseconds (several times faster)
- Published in *Light: Science & Applications* and *PRL*

#### Visible Red Lasers in SiN Chips (Oct 2025)
- First visible red lasers grown directly in silicon nitride photonic chips
- III-V + Si photonics bridge for quantum computing, biosensing, AR
- Supported by **DARPA LUMOS**

#### GaN CMOS p-FET Development
- Improving contact resistance for fully integrated GaN CMOS platforms
- Higher breakdown voltage, switching frequency, operating temp than Si

#### Sliding Ferroelectric Memory (2D Materials)
- Rhombohedral-stacked bilayer MoS2 for non-volatile memory
- Ultra-thin, stable polarization at atomic level

#### Ultra-Wide Bandgap Research (Hiring Apr 2026)
- SiC, GaN, Diamond for RF/power electronics/extreme environments
- MOSFETs, IGBTs, BJTs, HEMTs: design, epitaxy, fab, packaging

### Workforce
- **Summer Research Program 2026**: Advanced Imager Technology + Microfabrication
- Pay: $24.50-$43.00/hr (US citizenship + clearance required)

### Events
- **Feb 12, 2026**: PIC fabrication presentation (Dan Pulver, Dr. Dave Kharas)
- **May 29, 2026**: "Advanced Technology at MIT LL" (Paul Juodawlkis, IEEE/Optica Fellow)
- **Jun 2025**: Hosted 2025 EUVL and Source Workshop (High NA, hyper-NA, 2-7nm wavelength)

---

## Cross-Cutting Themes

1. **3D Heterogeneous Integration**: Central to DARPA NGMM, Minitherms3D, LANL CHIME, LLNL TPL
2. **Wide/Ultra-Wide Bandgap Semiconductors**: NREL, NRL, ARL, MIT LL, LLNL, LANL all active in GaN, SiC, Ga2O3, Diamond, AlN
3. **Quantum Technologies**: Q-NEXT (Argonne), SQMS (Fermilab), CFN (BNL), LANL quantum computing, MIT LL trapped-ion
4. **AI/ML for Semiconductor Design**: AXESS (Fermilab/ORNL), Molecular Foundry AI-PVD, CFN AI-enabled science, AFRL neuromorphic
5. **EUV Lithography**: NSTC EUV Accelerator, CFN EUV interference lithography, MIT LL EUVL workshop
6. **Advanced Packaging**: NGMM ($1.4B), NIST GC3, Microelectronics Commons, NY CREATES
7. **Radiation Hardening**: Sandia LDRD, NRL SEE testing, LANL extreme environments, ARL ruggedized computing
8. **Domestic Supply Chain**: CHIPS Act ecosystem, SkyWater commercialization, TFLN wafer onshoring (AFRL/Raytheon)

---

*Research compiled from public sources -- DARPA, DoD, DOE, DOC, NIST, NASA, and lab press releases and publications.*
