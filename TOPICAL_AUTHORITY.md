# Kolam.co.id topical-authority map

Last reviewed: 2026-07-23 (Asia/Jakarta)

## Purpose and boundary

Kolam.co.id should become an Indonesian knowledge hub for swimming pools and closely related recreational-water systems: planning, architecture, engineering, construction, equipment, water quality, safety, operation, maintenance, troubleshooting, renovation, and commercial ownership.

Primary audiences:

- Homeowners considering, building, operating, or repairing a pool.
- Architects, interior/landscape designers, engineers, and contractors.
- Hotel, villa, apartment, school, sports, fitness, and waterpark operators.
- Pool technicians, maintenance teams, and procurement staff.
- Buyers who need to understand specifications before contacting a contractor or supplier.

Primary conversion:

- A qualified request for design, construction, renovation, maintenance, equipment, or expert assessment.

Explicit boundaries:

- Koi ponds, aquaculture, reservoirs, wastewater treatment, and general plumbing belong elsewhere unless the comparison directly helps a swimming-pool decision.
- Medical and health claims require qualified sources/review.
- Structural, electrical, chemical, diving, public-health, and code-compliance instructions require expert review and current Indonesian/local primary sources.
- City pages are not created merely by swapping place names. A local page needs distinct service coverage, projects, climate/water constraints, logistics, staff/partner details, pricing factors, and evidence.
- Kolam.co.id is the broad learning hub. `kontraktorkolam.co.id` should own contractor-selection and design-build transaction detail. The role of `kolam.id` must be differentiated before parallel article production.

## Existing-site evidence

Repository sitemap snapshot:

| Evidence | Count | Interpretation |
|---|---:|---|
| URLs in `sitemap-complete.xml` | 730 | Historical static export, not a clean canonical inventory |
| `/artikel/` URLs | 37 | Small educational layer |
| City/service-pattern URLs | about 420 | High doorway/duplication risk; audit before retaining |
| Category/archive pagination URLs | about 86 | Should normally be excluded from the canonical content map |
| Blog pagination URLs | about 84 | Navigation/archive pages, not authority topics |

Known overlap families requiring consolidation before new publication:

- clean/clear/healthy pool water;
- general water maintenance;
- generic pool problems and quick fixes;
- DIY pool construction/installation;
- benefits of owning/installing a pool;
- filter importance, cleaning, and troubleshooting;
- leak/patch/repair pages.

## Topic architecture

Every broad topic below expands into multiple distinct article intents in `ARTICLE_CATALOG.md`.

| ID | Broad topic | Subtopics to cover completely | Required formats/evidence | Boundary against other topics |
|---|---|---|---|---|
| K00 | Foundations and vocabulary | pool anatomy, system diagram, circulation path, glossary, units, indoor/outdoor, in-ground/above-ground, skimmer/overflow, freshwater/saltwater | labeled diagrams, glossary, system map | Defines terms only; detailed design lives in specialist clusters |
| K01 | History, culture, and trends | ancient baths, competitive-pool evolution, hotel/resort trends, wellness pools, Indonesian pool culture, city/climate demand, future technology | timelines, sourced trend data, interviews | No unsupported “city loves pools” claims |
| K02 | Pool purposes and typologies | residential, lap, plunge, therapy, children, hotel, apartment, school, sports, competition, diving, waterpark, rooftop, infinity, natural, portable | use-case decision matrix, real examples | One page per materially different user/outcome |
| K03 | Dimensions, geometry, and standards | Olympic dimensions, lane widths, depths, slopes, transitions, freeboard, steps, ladders, benches, ledges, gutters, beach entry, turning walls, diving zones | dimension drawings, standard citations, calculators | Do not split synonyms that need the same drawing/answer |
| K04 | Site planning and architecture | orientation, sun/wind, privacy, views, house relationship, circulation, deck, plant room, service access, noise, drainage, indoor humidity, rooftop constraints | plans, shadow/wind studies, project photos | Structural calculations remain K05; landscape planting K22 |
| K05 | Structure, soil, and loads | soil investigation, groundwater, excavation, reinforced concrete shell, shotcrete/gunite, block systems, fiberglass, settlement, hydrostatic uplift, joints, crack control, rooftop loads | engineer-reviewed diagrams, field photos, failure cases | No DIY structural instructions without review |
| K06 | Waterproofing, joints, and finishes | positive/negative waterproofing, crystalline/cementitious/membrane systems, waterstops, movement joints, plaster, tile, mosaic, pebble, paint, grout, coping, slip resistance, finish discoloration | mock-ups, product data, failure photos | Chemistry stains diagnosed with K12/K18 |
| K07 | Hydraulics and circulation | turnover, flow rate, velocity, head loss, pipe sizing, suction/return balance, inlet placement, dead zones, skimmer, overflow gutter, balance tank, main drains, vacuum lines, air locks, water hammer | hydraulic diagrams, calculators, commissioning measurements | Pump hardware detail K09; filter media K08 |
| K08 | Filtration | filtration purpose, sand, cartridge, DE, glass media, regenerative, filter sizing, micron rating, pressure, backwash, rinse, channeling, media replacement, multiport valve | cutaway diagrams, pressure logs, comparison tests | Sanitizing pathogens belongs K11 |
| K09 | Pumps and plant-room equipment | pump types, curves, duty point, variable speed, priming, cavitation, seals, bearings, noise, vibration, efficiency, redundancy, placement, ventilation, flooded suction | pump-curve examples, energy calculator, sound measurements | Hydraulic demand K07; electrical protection K16 |
| K10 | Water balance and chemistry | pH, alkalinity, calcium hardness, TDS, saturation indices, source water, testing methods, dosing math, chemical interactions, dilution, scaling, corrosion | test-method comparison, dosing calculator, dated standards | Disinfection residual/pathogen control K11 |
| K11 | Sanitization and microbiology | chlorine forms, free/combined chlorine, chloramines, breakpoint, salt chlorination, bromine, UV, ozone, AOP, bacteria, viruses, protozoa, swimmer hygiene, public-pool response | public-health sources, expert review, incident protocols | Algae-specific ecology/treatment K12 |
| K12 | Algae, biofilm, clarity, and staining | green/mustard/black algae, biofilm, cloudy water, metals, organic staining, scale, pollen/dust, phosphates, prevention, brushing, circulation diagnosis | microscopy/photos where possible, decision trees | Avoid one generic “make water clear” page |
| K13 | Pool components and fittings | skimmers, drains, inlets, gutters, surge tanks, level controllers, valves, unions, gauges, strainers, vac ports, autofill, covers, reels, ladders, handrails | exploded diagrams, selection tables | Equipment families receive dedicated decision pages |
| K14 | Cleaning and routine maintenance | daily/weekly/monthly routines, brushing, skimming, vacuuming, robotic cleaners, manual vacuums, filter care, plant-room logs, seasonal closures, opening after vacancy | checklists, maintenance log templates, videos | Fault diagnosis belongs K18 |
| K15 | Safety, accessibility, and supervision | barriers, covers, alarms, anti-entrapment, depth markers, slip resistance, lighting, rescue equipment, child safety, accessibility, staff supervision, weather/lightning | code citations, audit checklist, expert review | Medical emergency treatment is outside scope |
| K16 | Electrical, controls, and automation | bonding/earthing, RCD/GFCI, IP ratings, cable routes, underwater lights, panels, timers, sensors, dosing controllers, remote monitoring, interlocks, fail-safe design | licensed-electrician review, schematics, commissioning checklist | Lighting experience/design separated from electrical safety |
| K17 | Heating, cooling, covers, and energy | heat pumps, solar thermal, boilers, chillers, evaporation, wind, insulation, covers, heat-loss calculation, pump energy, lighting energy, operating schedules | energy calculators, measured case studies | No savings claim without climate/tariff assumptions |
| K18 | Troubleshooting and failure diagnosis | low flow, air bubbles, lost prime, pressure high/low, leaks, cracks, settlement, tile failure, noisy pumps, cloudy/green water, recurring chlorine demand, overflow loss, equipment trips | symptom-to-cause trees, test sequence, stop-and-call criteria | Separate symptom intents; do not publish generic “all problems” pages |
| K19 | Renovation and retrofit | condition survey, leak localization, resurfacing, tile replacement, coping/deck changes, plumbing retrofit, equipment upgrade, overflow conversion, accessibility, energy retrofit, project sequencing | before/after cases, scope matrix, budget assumptions | Transaction/service detail links to contractor hub |
| K20 | Construction process and quality control | brief, survey, concept, design, permits, excavation, structure, MEP rough-in, waterproof test, finishing, equipment, filling, commissioning, handover, warranty, documentation | stage gates, inspection forms, real project photos | Cost/procurement K21; detailed engineering in specialist clusters |
| K21 | Cost, quotation, procurement, and ownership | CAPEX components, OPEX, size/finish effects, equipment choices, bid comparison, BOQ, exclusions, contingencies, lifecycle cost, warranty, spare parts, contractor selection | dated cost models, editable BOQ/checklist | Never publish timeless exact prices |
| K22 | Deck, landscape, and outdoor integration | deck materials, drainage, shade, planting, root risk, leaf load, privacy, furniture, outdoor shower, pool house, lighting atmosphere, mosquitoes, pets | landscape plans, material samples, maintenance effects | General gardening belongs `taman.co.id` |
| K23 | Commercial and institutional operations | hotel, villa, apartment, school, gym, club, therapy, competition, waterpark, occupancy/bather load, staffing, logs, downtime, guest complaints, revenue, insurance | operator interviews, SOPs, log templates | One operational model per distinct facility |
| K24 | Swimming, sport, and user experience | lap design, starting blocks, lane ropes, timing, training temperature, teaching zones, diving basics, acoustics, glare, spectator experience | federation/coach sources, user studies | Technique coaching only where qualified |
| K25 | Environmental performance | water conservation, backwash recovery, rainwater, evaporation, efficient pumps, solar, low-chemical claims, discharge, drought, embodied materials, climate resilience | water/energy baselines, regulatory sources | Avoid unverified “eco” claims |
| K26 | Natural pools and water features | regeneration zones, biological filtration, planted systems, swimming ponds, fountains, reflecting pools, spas, hot tubs, cold plunge, hybrid systems | diagrams, water-quality limitations, comparisons | Aquaculture and ornamental fish remain outside core |
| K27 | Pool business and workforce | service business models, technician skills, maintenance contracts, inventory, route planning, QA, customer education, complaints, commercial KPIs | anonymized operational data, templates | Duit.co.id may own broader business-finance treatment |
| K28 | Original tools and evidence assets | volume, surface area, turnover, pump duty, filter size, balance tank, chemical dose, heat loss, evaporation, lifecycle cost, maintenance log, commissioning sheet | tested calculators, methodology, version/date | Tools support articles; they are not thin keyword pages |
| K29 | Local climate and service reality | rainfall, heat, dust, salinity, source-water quality, flooding, earthquake/soil, logistics, local codes, actual coverage | local primary data, local projects, named operations | No city-name substitution or unsupported service claims |

## Coverage dimensions

A broad topic is not complete until its article cluster addresses the applicable dimensions:

| Dimension | Question |
|---|---|
| Definition | What is it and what terms are commonly confused? |
| Mechanism | Why does it work or fail? |
| Types | What materially different variants exist? |
| Selection | Which variant fits which user/site? |
| Design | How is it sized, located, or integrated? |
| Installation | What sequence and quality gates matter? |
| Operation | How is it used and monitored? |
| Maintenance | What recurring care preserves performance? |
| Troubleshooting | Which symptom points to which cause/test? |
| Safety | What can injure people or damage property? |
| Standards | Which current authority governs the decision? |
| Cost | Which variables drive initial and lifetime cost? |
| Environment | What water, energy, waste, or climate impact matters? |
| Evidence | What original photo, measurement, calculation, or case can Kolam.co.id contribute? |
| Conversion | What is the reader's honest next action? |

## Internal-link architecture

| Page type | Links to | Purpose |
|---|---|---|
| `/panduan/kolam-renang/` hub | K00–K29 category hubs | Show the complete learning landscape |
| Foundation article | specialist article and relevant calculator | Move from concept to decision |
| Specialist article | prerequisite, comparison, troubleshooting, commercial page | Complete the user's next step |
| Troubleshooting article | mechanism, safe test, maintenance, repair assessment | Avoid blind product recommendations |
| Commercial page | specification, case study, process, cost boundary | Resolve trust and scope questions |
| Case study | exact design/technical pages and relevant service | Turn proof into reusable learning |
| Calculator/tool | methodology and decision articles | Explain inputs, limits, and actions |

Avoid automatic reciprocal links among Syamsul's pool domains. Link across domains only when their roles are distinct and the destination materially helps the reader.

## Publication gates

- Each proposed article owns one primary intent and has an explicit exclusion.
- Existing articles are audited for keep/rewrite/merge/redirect before assigning a new slug.
- New factual claims use current primary sources and dated evidence.
- Technical/safety articles identify the required expert reviewer.
- No new location page without distinct local evidence and a functioning service path.
- Every new article has at least one planned inbound and outbound contextual link.
- Production proceeds in bounded clusters, not by publishing this entire map automatically.

