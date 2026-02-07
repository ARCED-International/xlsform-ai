# Common XLSForm Use Cases

This guide provides reusable XLSForm patterns for common survey modules.

## Crop Production Module

Survey structure:
```xlsx
type                name                label
begin_group         crop_production     Crop production
begin_repeat        crop                Crop
text                crop_name           Crop name
decimal             crop_area_ha        Area planted (hectares)
decimal             crop_yield_kg       Yield (kg)
select_one yes_no   crop_sold           Was any crop sold?
decimal             crop_sales_value    Sales value (local currency)
relevant            ${crop_sold} = '1'
end_repeat          crop
end_group           crop_production
```

Best practices:
- Use a repeat for multiple crops.
- Use relevance for sales value.
- Store numeric values as decimal.

## Household Consumption Module

Survey structure:
```xlsx
type                name                label
begin_group         consumption         Household consumption
select_one freq     meals_per_day       Meals per day
select_one yes_no   food_shortage       Food shortage in last 7 days?
text                shortage_reason     Main reason for shortage
relevant            ${food_shortage} = '1'
end_group           consumption
```

Choices:
```xlsx
list_name   name   label
freq        1      1
freq        2      2
freq        3      3
```

Best practices:
- Use numeric codes for frequency.
- Add relevance for follow-up questions.

## Household Roster (Basic)

Survey structure:
```xlsx
type                name                label
begin_repeat        person              Household member
text                person_name         Person name
integer             person_age          Age (years)
select_one gender   person_gender       Gender
end_repeat          person
```

Best practices:
- Make `person_name` required if you will reference it later.
- Use a named repeat for better navigation.

## Livestock Module

Survey structure:
```xlsx
type                name                label
begin_repeat        livestock           Livestock type
select_one animal   animal_type         Animal type
integer             animal_count        Count owned
end_repeat          livestock
```

Best practices:
- Use a repeat to allow multiple livestock types.
- Use integer for counts.

## WASH (Water, Sanitation, Hygiene)

Survey structure:
```xlsx
type                name                label
begin_group         wash                WASH
select_one water    water_source        Main water source
select_one yes_no   improved_source     Improved source?
select_one toilet   toilet_type         Toilet type
select_one yes_no   handwash            Handwashing station present?
end_group           wash
```

Best practices:
- Use standard categories for water/toilet types.
- Add relevance if improved_source depends on water_source list.

## Education

Survey structure:
```xlsx
type                name                label
begin_repeat        student             Student
text                student_name        Student name
select_one level    school_level        Current level
select_one yes_no   attends_school      Currently attending?
end_repeat          student
```

Best practices:
- Use a repeat for multiple students.
- Use `level` choices with numeric codes.

## Health (Basic)

Survey structure:
```xlsx
type                name                label
begin_group         health              Health
select_one yes_no   recent_illness      Illness in last 2 weeks?
text                illness_symptoms    Symptoms
relevant            ${recent_illness} = '1'
select_one yes_no   sought_care         Sought care?
relevant            ${recent_illness} = '1'
end_group           health
```

Best practices:
- Use relevance for follow-up questions.
- Consider skip logic for sensitive questions.

## Income and Employment

Survey structure:
```xlsx
type                name                label
begin_group         income              Income and Employment
select_one yes_no   employed            Currently employed?
select_one job      job_type            Job type
relevant            ${employed} = '1'
decimal             monthly_income      Monthly income (local currency)
relevant            ${employed} = '1'
end_group           income
```

Best practices:
- Use relevance for income fields.
- Allow "Don't know" in job_type if needed.

## Food Security (HFIAS-style short)

Survey structure:
```xlsx
type                name                label
begin_group         food_security       Food security
select_one freq     worry_food          Worried about food?
select_one freq     limited_variety     Limited variety of foods?
select_one freq     skipped_meals       Skipped meals?
end_group           food_security
```

Best practices:
- Use frequency choices (0-3 or 1-4) consistently.
- Keep recall period in labels (e.g., "last 4 weeks").

## Nutrition (Dietary Diversity)

Survey structure:
```xlsx
type                    name            label
begin_group             diet            Diet (last 24 hours)
select_multiple foods   food_groups     Foods consumed
end_group               diet
```

Best practices:
- Use standard food group lists.
- Add "None" only if explicitly needed.

## Assets and Wealth

Survey structure:
```xlsx
type                    name            label
begin_group             assets          Household assets
select_multiple assets  asset_list      Assets owned
end_group               assets
```

Best practices:
- Use a reusable asset list across surveys.
- Avoid long labels; use hints if needed.

## Expenditure (Simple)

Survey structure:
```xlsx
type                name                label
begin_group         expenditure         Expenditure
decimal             food_spend_week     Food spend last 7 days
decimal             transport_week      Transport spend last 7 days
decimal             health_month        Health spend last 30 days
end_group           expenditure
```

Best practices:
- Match recall periods to labels.
- Use currency name in labels if needed.

## Shocks and Coping

Survey structure:
```xlsx
type                name                label
begin_group         shocks              Shocks
select_multiple shock  shock_types      Shocks experienced in last 12 months
select_one yes_no   coping_used         Used coping strategies?
relevant            ${shock_types} != ''
end_group           shocks
```

Best practices:
- Use relevance to avoid unnecessary questions.
- Keep shock list specific to context.

## Migration and Mobility

Survey structure:
```xlsx
type                name                label
begin_group         migration           Migration
select_one yes_no   migrated            Migrated in last 12 months?
text                migration_from      Moved from where?
relevant            ${migrated} = '1'
text                migration_reason    Main reason for moving
relevant            ${migrated} = '1'
end_group           migration
```

Best practices:
- Use relevance for follow-up fields.
- Consider select_one for common reasons.

## Sector Variants

### WFP Food Security (rCSI-style short)

Survey structure:
```xlsx
type                name                label
begin_group         rcsi                Coping strategies (last 7 days)
integer             rcsi_less_preferred Ate less preferred foods
integer             rcsi_borrow_food    Borrowed food
integer             rcsi_reduce_meals   Reduced meals
integer             rcsi_reduce_adults  Adults reduced to feed children
end_group           rcsi
```

Best practices:
- Use integers for frequency (0-7).
- Keep recall period in labels.

### DHS-style Household Roster (Short)

Survey structure:
```xlsx
type                name                label
begin_repeat        hh_member           Household member
text                hh_name             Name
select_one rel      hh_relation         Relationship to head
integer             hh_age              Age
select_one gender   hh_gender           Sex
end_repeat          hh_member
```

Best practices:
- Use standard relationship codes.
- Keep `hh_name` required.

### LSMS Agriculture (Plot/Crop)

Survey structure:
```xlsx
type                name                label
begin_repeat        plot                Plot
text                plot_id             Plot ID
decimal             plot_area_ha        Plot area (ha)
begin_repeat        crop                Crop
select_one crop     crop_type           Crop type
decimal             crop_area_ha        Crop area (ha)
decimal             harvest_qty         Harvest quantity
end_repeat          crop
end_repeat          plot
```

Best practices:
- Use nested repeats only when needed.
- Keep plot IDs unique.

### MICS Child Health (Short)

Survey structure:
```xlsx
type                name                label
begin_group         child_health        Child health
select_one yes_no   child_diarrhea      Diarrhea in last 2 weeks?
select_one treat    diarrhea_treatment  Treatment sought
relevant            ${child_diarrhea} = '1'
select_one yes_no   child_fever         Fever in last 2 weeks?
end_group           child_health
```

Best practices:
- Keep recall period in labels.
- Use relevance for treatment questions.

### SMART Nutrition (MUAC)

Survey structure:
```xlsx
type                name                label
begin_group         nutrition           Nutrition
decimal             muac_mm             MUAC (mm)
select_one edema    edema               Bilateral pitting edema
end_group           nutrition
```

Best practices:
- Record MUAC in mm for precision.
- Use standard edema codes.

### WHO STEPS (Tobacco/Alcohol)

Survey structure:
```xlsx
type                name                label
begin_group         steps               STEPS risk factors
select_one yes_no   tobacco_use         Current tobacco use?
integer             cigarettes_per_day  Cigarettes per day
relevant            ${tobacco_use} = '1'
select_one freq     alcohol_freq        Alcohol use frequency
end_group           steps
```

Best practices:
- Use relevance for follow-up counts.
- Use frequency scales consistently.

### MICS/WASH (Drinking Water)

Survey structure:
```xlsx
type                name                label
begin_group         water               Drinking water
select_one water    water_source        Main source of drinking water
select_one yes_no   water_treated       Water treated to make safe?
end_group           water
```

Best practices:
- Use standard JMP water source list.

### Immunization / Vaccination (Basic)

Survey structure:
```xlsx
type                name                label
begin_group         immunization        Immunization
select_one yes_no   has_card            Has vaccination card?
select_one yes_no   bcg_received        BCG received?
select_one yes_no   measles_received    Measles received?
end_group           immunization
```

Best practices:
- Ask about card availability first.
- Use standard vaccine names.

### Antenatal Care (ANC)

Survey structure:
```xlsx
type                name                label
begin_group         anc                 Antenatal care
select_one yes_no   anc_visit           Any ANC visit?
integer             anc_visits_count    Number of ANC visits
relevant            ${anc_visit} = '1'
select_one yes_no   anc_tt              Received tetanus toxoid?
relevant            ${anc_visit} = '1'
end_group           anc
```

Best practices:
- Use relevance for follow-ups.
- Keep recall periods in labels.

### Livelihoods (Sources of Income)

Survey structure:
```xlsx
type                    name                label
begin_group             livelihoods         Livelihoods
select_multiple income  income_sources      Main income sources
select_one yes_no       wage_employment     Wage employment?
end_group               livelihoods
```

Best practices:
- Use standardized income source lists.
- Allow multiple selection for mixed livelihoods.

### Market Prices (Simple)

Survey structure:
```xlsx
type                name                label
begin_repeat        market_item         Market item
select_one item     item_name           Item
decimal             price_unit          Price per unit
select_one unit     price_unit_type     Unit
end_repeat          market_item
```

Best practices:
- Use repeat for multiple items.
- Use numeric price with unit selection.

### Food Consumption Score (FCS-style short)

Survey structure:
```xlsx
type                name                label
begin_group         fcs                 Food consumption (last 7 days)
integer             fcs_cereals         Cereals
integer             fcs_pulses          Pulses
integer             fcs_veg             Vegetables
integer             fcs_fruit           Fruits
integer             fcs_meat            Meat/Fish
integer             fcs_dairy           Dairy
integer             fcs_sugar           Sugar
integer             fcs_oil             Oils/Fats
end_group           fcs
```

Best practices:
- Use integer counts (0-7).
- Compute FCS in a calculate field if needed.

### Anthropometric Measurements

Survey structure:
```xlsx
type                name                label
begin_group         anthro              Anthropometry
decimal             height_cm           Height (cm)
decimal             weight_kg           Weight (kg)
decimal             muac_mm             MUAC (mm)
select_one edema    edema               Bilateral pitting edema
end_group           anthro
```

Best practices:
- Use decimal for height/weight and mm for MUAC.
- Add constraints for plausible ranges.

### Health Biomarker Collection

Survey structure:
```xlsx
type                name                label
begin_group         biomarkers          Biomarkers
barcode             sample_id           Sample barcode
select_one specimen specimen_type       Specimen type
date                collection_date     Collection date
time                collection_time     Collection time
end_group           biomarkers
```

Best practices:
- Use barcode for unique sample IDs.
- Use separate date/time fields or dateTime as needed.

### Agriculture DNA Fingerprint Collection

Survey structure:
```xlsx
type                name                label
begin_group         dna                 DNA fingerprint
barcode             dna_sample_id       DNA sample barcode
select_one crop     dna_crop_type       Crop type
text                dna_plot_id         Plot ID
date                dna_collection_date Collection date
end_group           dna
```

Best practices:
- Use barcode to prevent transcription errors.
- Require plot ID if linking to plot repeats.

### Aquaculture DNA Fingerprint Collection

Survey structure:
```xlsx
type                name                label
begin_group         aqua_dna            Aquaculture DNA
barcode             fish_sample_id      Fish sample barcode
select_one species  fish_species        Species
text                pond_id             Pond ID
date                collection_date     Collection date
end_group           aqua_dna
```

Best practices:
- Use barcode to prevent transcription errors.
- Keep pond ID consistent with farm records.

### Chain of Custody (Sample Transfer)

Survey structure:
```xlsx
type                name                label
begin_repeat        custody             Chain of custody
select_one role     custodian_role      Custodian role
text                custodian_name      Custodian name
dateTime            handoff_time        Handoff time
text                handoff_location    Handoff location
end_repeat          custody
```

Best practices:
- Use repeat to capture multiple handoffs.
- Use dateTime for precise tracking.

### Cold Chain Monitoring

Survey structure:
```xlsx
type                name                label
begin_repeat        cold_chain          Cold chain checks
dateTime            temp_time           Measurement time
decimal             temp_c              Temperature (C)
select_one yes_no   temp_out_of_range   Out of range?
end_repeat          cold_chain
```

Best practices:
- Use decimal for temperature.
- Add constraints for expected ranges when applicable.

### Duplicate Samples

Survey structure:
```xlsx
type                name                label
begin_group         duplicate_samples   Duplicate samples
select_one yes_no   has_duplicate       Duplicate collected?
barcode             duplicate_id        Duplicate sample barcode
relevant            ${has_duplicate} = '1'
end_group           duplicate_samples
```

Best practices:
- Only collect duplicate ID when needed.
- Use barcode to prevent mismatches.

### Lab Metadata (Storage and Preservation)

Survey structure:
```xlsx
type                name                label
begin_group         lab_meta            Lab metadata
select_one medium   storage_medium      Storage medium
select_one preserv  preservative_used   Preservative used
text                freezer_id          Freezer ID
text                rack_position       Rack/box position
end_group           lab_meta
```

Best practices:
- Use standardized lists for medium and preservative.
- Capture freezer and rack IDs for traceability.

## Additional Modules

### Child Education

Survey structure:
```xlsx
type                name                label
begin_group         child_education     Child education
select_one yes_no   enrolled            Currently enrolled?
select_one level    grade_level         Current grade
relevant            ${enrolled} = '1'
integer             days_absent_month   Days absent (last 30 days)
relevant            ${enrolled} = '1'
select_one reason   dropout_reason      Main reason for dropout
relevant            ${enrolled} = '0'
end_group           child_education
```

Best practices:
- Use relevance for enrolled vs dropout paths.
- Keep recall period in labels.

### Access to Education

Survey structure:
```xlsx
type                name                label
begin_group         edu_access          Education access
decimal             distance_school_km  Distance to school (km)
select_one mode     transport_mode      Usual transport to school
decimal             transport_cost      Cost per trip
select_one yes_no   fees_paid           School fees paid?
end_group           edu_access
```

Best practices:
- Use decimal for distance and cost.
- Add "none" or "free" in transport mode if needed.

### Environment and Climate

Survey structure:
```xlsx
type                name                label
begin_group         environment         Environment
select_multiple shock  climate_shocks   Shocks in last 12 months
select_one yes_no   land_degraded       Land degradation observed?
select_one yes_no   water_pollution     Water pollution observed?
end_group           environment
```

Best practices:
- Use relevance if follow-ups are required for specific shocks.
- Keep shock list contextual.

### Housing and Shelter

Survey structure:
```xlsx
type                name                label
begin_group         housing             Housing
select_one house    dwelling_type       Dwelling type
select_one tenure   tenure_status       Tenure status
integer             rooms_sleep         Rooms used for sleeping
end_group           housing
```

Best practices:
- Use standard housing categories.
- Use integer for room counts.

### Energy Access

Survey structure:
```xlsx
type                name                label
begin_group         energy              Energy access
select_one fuel     cooking_fuel        Primary cooking fuel
select_one light    lighting_source     Primary lighting source
select_one yes_no   electricity_access  Electricity access?
end_group           energy
```

Best practices:
- Use standard fuel lists.
- Add relevance if electricity follow-ups are needed.

### Disability (WGSS Short Set)

Survey structure:
```xlsx
type                    name            label
begin_group             disability      Disability
select_one wg           seeing          Difficulty seeing?
select_one wg           hearing         Difficulty hearing?
select_one wg           walking         Difficulty walking?
select_one wg           remembering     Difficulty remembering?
select_one wg           self_care        Difficulty with self-care?
select_one wg           communicating   Difficulty communicating?
end_group               disability
```

Best practices:
- Use standard WG response options.
- Keep wording consistent with WG guidelines.

### Social Protection

Survey structure:
```xlsx
type                name                label
begin_group         social_protection   Social protection
select_one yes_no   receives_benefit    Receives any benefit?
select_multiple ben benefit_types       Benefit types
relevant            ${receives_benefit} = '1'
end_group           social_protection
```

Best practices:
- Use relevance for benefit types.
- Keep benefit list short and contextual.

### Gender and Protection (Non-sensitive)

Survey structure:
```xlsx
type                name                label
begin_group         gender              Gender and protection
select_one yes_no   decision_food       Involved in food decisions?
select_one yes_no   decision_spend      Involved in spending decisions?
end_group           gender
```

Best practices:
- Avoid sensitive questions unless protocols exist.
- Use neutral wording.

### Digital Access

Survey structure:
```xlsx
type                name                label
begin_group         digital_access      Digital access
select_one yes_no   owns_phone          Owns a phone?
select_one yes_no   internet_access     Has internet access?
select_one freq     internet_use        Internet use frequency
relevant            ${internet_access} = '1'
end_group           digital_access
```

Best practices:
- Use relevance for frequency.
- Use standardized frequency scales.

### Market Access

Survey structure:
```xlsx
type                name                label
begin_group         market_access       Market access
decimal             market_distance_km  Distance to main market (km)
select_one mode     market_transport    Transport to market
select_one yes_no   price_increase      Prices increased recently?
end_group           market_access
```

Best practices:
- Use decimal for distance.
- Add follow-ups if price_increase is yes.

### Protection and GBV (Sensitive Protocol Template)

Survey structure:
```xlsx
type                name                label
begin_group         protection          Protection
note                consent_intro       We will ask sensitive questions. You can skip any question or stop at any time.
select_one yes_no   consent_given       Do you consent to continue?
relevant            ${consent_given} = '1'
select_one yes_no   safe_to_answer      Is it safe to continue?
relevant            ${consent_given} = '1'
select_one yes_no   experienced_harm    Experienced harm in last 12 months?
relevant            ${safe_to_answer} = '1'
note                referral_note       If needed, provide local referral options. [Customize per country/partner]
relevant            ${experienced_harm} = '1'
end_group           protection
```

Best practices:
- Use safety screening before sensitive questions.
- Provide referral information and local protocols.
- Do not collect identifiable details without approvals.

### Child Protection (Sensitive Protocol Template)

Survey structure:
```xlsx
type                name                label
begin_group         child_protection    Child protection
note                consent_intro       We will ask sensitive questions. You can skip any question or stop at any time.
select_one yes_no   consent_given       Do you consent to continue?
relevant            ${consent_given} = '1'
select_one yes_no   safe_to_answer      Is it safe to continue?
relevant            ${consent_given} = '1'
select_one yes_no   child_risk          Child at risk?
relevant            ${safe_to_answer} = '1'
note                referral_note       If needed, provide local referral options. [Customize per country/partner]
relevant            ${child_risk} = '1'
end_group           child_protection
```

Best practices:
- Use safety screening and follow local protocols.
- Avoid collecting sensitive identifiable details.

### Labor Rights

Survey structure:
```xlsx
type                name                label
begin_group         labor_rights        Labor rights
select_one yes_no   written_contract    Has a written contract?
select_one yes_no   paid_on_time        Paid on time?
select_one yes_no   overtime_paid       Overtime paid?
end_group           labor_rights
```

Best practices:
- Use neutral wording.
- Avoid employer-identifying details.

### Workplace Violence (Sensitive Protocol Template)

Survey structure:
```xlsx
type                name                label
begin_group         workplace_violence  Workplace safety
note                consent_intro       We will ask sensitive questions. You can skip any question or stop at any time.
select_one yes_no   consent_given       Do you consent to continue?
relevant            ${consent_given} = '1'
select_one yes_no   safe_to_answer      Is it safe to continue?
relevant            ${consent_given} = '1'
select_one yes_no   violence_incident   Experienced violence at work?
relevant            ${safe_to_answer} = '1'
note                referral_note       If needed, provide local referral options. [Customize per country/partner]
relevant            ${violence_incident} = '1'
end_group           workplace_violence
```

Best practices:
- Use safety screening and referral guidance.
- Keep questions minimal and non-identifying.
