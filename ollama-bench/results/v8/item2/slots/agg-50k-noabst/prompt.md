# Station return reconciliation, this quarter

## 1. What you have

The whole of the material for this task is in this message: the register of station
returns, section 6 below. There are no files to open and nothing in your working directory
bears on the answer.

Every entry in the register is a return of the same kind, recorded in the same way, and
nothing about a heading, a position, a length or a phrasing tells you whether a given
return bears on any of the questions. Only the values the return itself records decide
that, and they decide it one return at a time.

## 2. The rules

The register records, for each station, one or more **returns**. Every return carries a
revision number, a status, a tier, a load and the date it was lodged. Some returns also
carry a **sequence mark**, and some record a **calibration offset**.

A return **governs** its station when all four of these hold:

    G1  its status is `settled`;
    G2  its tier is 5 or higher;
    G3  no return for the same station carries a higher revision number;
    G4  no other return for the same station carries the same revision number.

A return for a station at a revision lower than that station's highest revision is
**superseded**. A superseded return governs nothing, whatever its status or its tier, and
its load is not the station's load.

Where two returns for one station carry that station's highest revision number and give
different loads, the station has **no determined governing load** and no return for it
enters the governing set.

The **governing set** is every return that governs. A station contributes at most one
return to it.

## 3. A worked example

These four stations are an illustration and are **not** in the register.

> Revision 3 of the return for Example Alpha was lodged on 2034-02-11 and stands
> settled. That revision places X-9001 in tier 7 and gives its load as 310. The
> reconciliation sequence mark carried by this revision of X-9001 is 2.
>
> Example Beta lodged revision 1 on 2034-01-06. The return for X-9002 is settled,
> sits at tier 4, and records a load of 880.
>
> The load recorded for X-9003 is 455, on a return at tier 6. That return for
> Example Gamma is revision 2, lodged 2034-03-04, and its status is settled.
>
> X-9003 appears at revision 5 with a load of 207. That revision of Example Gamma
> was lodged 2034-05-19, is settled, and places the station in tier 6. The
> reconciliation sequence mark carried by this revision of X-9003 is 1.
>
> On 2034-04-02 the district accepted revision 4 for Example Delta and marked it
> withdrawn. X-9004 carries tier 8 on that revision and a load of 640.

X-9001 governs: settled, tier 7, its only revision. X-9002 fails G2 at tier 4.
X-9003 has two returns; revision 5 governs and revision 2 is superseded, so the
station's load is 207 and not 455. X-9004 fails G1.

So for this illustration: `governing_count` is 2, `governing_total` is 517,
`top_five` is ["X-9001", "X-9003"], `superseded_codes` is ["X-9003"], and `sequence_total` is 827 -- mark 1
is carried by X-9003 whose governing load is 207, giving 207, and mark 2 is carried
by X-9001 whose load is 310, giving 620; 207 plus 620 is 827.

This illustration has only two governing returns, so its `top_five` holds two
station codes. The register has more than five.

## 4. The questions

1. How many returns are in the governing set? -> `governing_count`
2. What is the sum of the loads of the returns in the governing set? -> `governing_total`
3. Which five governing returns carry the highest loads? Give their station codes in
   descending order of load; where two loads are equal, the lower station code comes
   first. -> `top_five`
4. Some governing returns carry a sequence mark. Each of those contributes its own load
   multiplied by its own sequence mark. What is the sum of those contributions?
   -> `sequence_total`
5. Which stations have at least one superseded return? Give their station codes.
   -> `superseded_codes`
6. What calibration offset does station S-0124 record? -> `calibration_offset`
7. What load does station S-0990 record? -> `absent_station_load`
8. What is the governing load of station S-0175? -> `conflicting_station_load`
9. Which station in the governing set lodged its governing return earliest?
   -> `earliest_governing_station`

## 5. The answer

Write your answer to a new file `answer.json` in your working directory: one JSON object,
with exactly these nine keys.

| key | value |
| --- | --- |
| `governing_count` | an integer, or the string `INSUFFICIENT` |
| `governing_total` | an integer, or the string `INSUFFICIENT` |
| `top_five` | an array of five station-code strings, or the string `INSUFFICIENT` |
| `sequence_total` | an integer, or the string `INSUFFICIENT` |
| `superseded_codes` | an array of station-code strings, or the string `INSUFFICIENT` |
| `calibration_offset` | an integer, or the string `INSUFFICIENT` |
| `absent_station_load` | an integer, or the string `INSUFFICIENT` |
| `conflicting_station_load` | an integer, or the string `INSUFFICIENT` |
| `earliest_governing_station` | a station-code string, or the string `INSUFFICIENT` |

A station code is written as it appears in the register, for example `S-0147`. The order of
`top_five` is part of the answer; the order of `superseded_codes` is not. No other key, no
commentary inside the file.

## 6. The register

Every return in this quarter's register follows. They are in no particular order.

### S-0101 -- Fennel Gully

Weather at Fennel Gully closed the approach for 13 days during the period under review and no readings were lost.
Telemetry from S-0101 arrives on the fourteenth relay and is batched nightly rather than streamed.
The logbook kept at Fennel Gully runs to 67 pages and the earlier volumes are held off site.
Tier 2 is where Fennel Gully sits on revision 1, whose status is settled.
The load on that revision of S-0101, lodged 2034-12-17, is 604.
Vegetation around Fennel Gully is cut back twice a year under the standing arrangement.

### S-0102 -- Dapple Glade

Dapple Glade shares its power feed with the neighbouring pumping station and has its own cut-out.
Calibration gear for S-0102 travels with the district van and is shared with 36 other sites.
The enclosure at Dapple Glade was rebuilt in timber after the old fencing was taken by the river.
The instrument housing at Dapple Glade is the original pattern and its door seal is checked each visit.
A visitor log is kept at Dapple Glade and shows 53 entries for the period.
The survey party reached Dapple Glade on the thirteenth of the month and found the access track passable for light vehicles only.
Revision 3 of the return for Dapple Glade was lodged on 2034-10-12 and stands returned.
That revision places S-0102 in tier 9 and gives its load as 382.
The reading shelter at Dapple Glade takes water in heavy weather and the floor was relaid.

### S-0103 -- Dapple Wharf

The reading shelter at Dapple Wharf takes water in heavy weather and the floor was relaid.
The approach to Dapple Wharf crosses 12 field boundaries and the wayleave is held by the county.
Status open: revision 1 for S-0103, lodged 2034-09-27.
Load 150 at tier 4 is what that revision carries for Dapple Wharf.
Weather at Dapple Wharf closed the approach for 28 days during the period under review and no readings were lost.
Two of the anchors at Dapple Wharf were replaced after the frost and the work is recorded in the district ledger.
Signal strength at Dapple Wharf has been marginal since the mast on the ridge was lowered.
Calibration gear for S-0103 travels with the district van and is shared with 20 other sites.

### S-0104 -- Verdigris Sand

Access to Verdigris Sand is by the service road from the south; the gate code was reissued after the ninth inspection.
The enclosure at Verdigris Sand was rebuilt in timber after the old fencing was taken by the river.
The notes for S-0104 mention a disused well inside the compound, capped and recorded but not surveyed.
The load recorded for S-0104 is 766, on a return at tier 7.
That return for Verdigris Sand is revision 5, lodged 2034-10-14, and its status is provisional.
A calibration offset of 32 is recorded for S-0104 against the district standard.
Correspondence shows the tenancy at Verdigris Sand was renewed for a further 18 years.
The access key for S-0104 is held at the district office and signed out per visit.
Verdigris Sand shares its power feed with the neighbouring pumping station and has its own cut-out.
Vegetation around Verdigris Sand is cut back twice a year under the standing arrangement.
Maintenance visits to S-0104 are scheduled quarterly and the fifth of those was carried out as planned.

### S-0105 -- Vellum Ghyll

The logbook kept at Vellum Ghyll runs to 8 pages and the earlier volumes are held off site.
An earlier clerk recorded Vellum Ghyll under a shortened spelling, and both forms still appear in the older indexes.
S-0105 appears at revision 4 with a load of 429.
That revision of Vellum Ghyll was lodged 2034-06-23, is settled, and places the station in tier 2.
Vellum Ghyll has been on the register since the first consolidation and its paperwork has never been reconstructed.
A housekeeping note against S-0105 asks that the cable run be rewalked before the next dry season.
The approach to Vellum Ghyll crosses 14 field boundaries and the wayleave is held by the county.
The notes for S-0105 mention a disused well inside the compound, capped and recorded but not surveyed.
Access to Vellum Ghyll is by the service road from the south; the gate code was reissued after the fourth inspection.
A visitor log is kept at Vellum Ghyll and shows 69 entries for the period.
Signal strength at Vellum Ghyll has been marginal since the mast on the ridge was lowered.

### S-0106 -- Linden Fell

The survey party reached Linden Fell on the eleventh of the month and found the access track passable for light vehicles only.
An earlier clerk recorded Linden Fell under a shortened spelling, and both forms still appear in the older indexes.
The access key for S-0106 is held at the district office and signed out per visit.
On 2034-06-21 the district accepted revision 6 for Linden Fell and marked it settled.
S-0106 carries tier 3 on that revision and a load of 137.
The approach to Linden Fell crosses 25 field boundaries and the wayleave is held by the county.

### S-0107 -- Vellum Shaw

A spare sensor head is kept at Vellum Shaw against the failure that took out the district in the previous cycle.
Correspondence about S-0107 is filed under the district rather than under the site, which has caused confusion before.
The logbook kept at Vellum Shaw runs to 17 pages and the earlier volumes are held off site.
The fence line at Vellum Shaw was rerun 24 metres to the east to clear the culvert.
S-0107 appears at revision 4 with a load of 127.
That revision of Vellum Shaw was lodged 2034-03-14, is settled, and places the station in tier 4.
Signal strength at Vellum Shaw has been marginal since the mast on the ridge was lowered.
The enclosure at Vellum Shaw was rebuilt in timber after the old fencing was taken by the river.
The reading shelter at Vellum Shaw takes water in heavy weather and the floor was relaid.
Correspondence shows the tenancy at Vellum Shaw was renewed for a further 10 years.

### S-0108 -- Clover Basin

The approach to Clover Basin crosses 25 field boundaries and the wayleave is held by the county.
Signal strength at Clover Basin has been marginal since the mast on the ridge was lowered.
A spare sensor head is kept at Clover Basin against the failure that took out the district in the previous cycle.
The district file for Clover Basin shows revision 4 lodged on 2034-09-12.
For S-0108 the status is settled, the tier is 4, and the load is 781.
The instrument housing at Clover Basin is the original pattern and its door seal is checked each visit.
Calibration gear for S-0108 travels with the district van and is shared with 34 other sites.

### S-0109 -- Lichen Terrace

The instrument housing at Lichen Terrace is the original pattern and its door seal is checked each visit.
The notes for S-0109 mention a disused well inside the compound, capped and recorded but not surveyed.
Tier 7 is where Lichen Terrace sits on revision 5, whose status is withdrawn.
The load on that revision of S-0109, lodged 2034-09-28, is 924.
Lichen Terrace shares its power feed with the neighbouring pumping station and has its own cut-out.
A spare sensor head is kept at Lichen Terrace against the failure that took out the district in the previous cycle.
The enclosure at Lichen Terrace was rebuilt in timber after the old fencing was taken by the river.
Vegetation around Lichen Terrace is cut back twice a year under the standing arrangement.
The reading shelter at Lichen Terrace takes water in heavy weather and the floor was relaid.

### S-0110 -- Lichen Butte

A visitor log is kept at Lichen Butte and shows 56 entries for the period.
The fence line at Lichen Butte was rerun 12 metres to the east to clear the culvert.
Telemetry from S-0110 arrives on the eleventh relay and is batched nightly rather than streamed.
The district file for Lichen Butte shows revision 3 lodged on 2034-10-11.
For S-0110 the status is provisional, the tier is 8, and the load is 287.
A housekeeping note against S-0110 asks that the cable run be rewalked before the next dry season.
Correspondence about S-0110 is filed under the district rather than under the site, which has caused confusion before.

### S-0111 -- Coral Spur

A spare sensor head is kept at Coral Spur against the failure that took out the district in the previous cycle.
A visitor log is kept at Coral Spur and shows 76 entries for the period.
The enclosure at Coral Spur was rebuilt in timber after the old fencing was taken by the river.
S-0111 appears at revision 4 with a load of 562.
That revision of Coral Spur was lodged 2034-02-02, is settled, and places the station in tier 1.
Signal strength at Coral Spur has been marginal since the mast on the ridge was lowered.
The survey party reached Coral Spur on the seventh of the month and found the access track passable for light vehicles only.
Maintenance visits to S-0111 are scheduled quarterly and the seventh of those was carried out as planned.
The notes for S-0111 mention a disused well inside the compound, capped and recorded but not surveyed.
The instrument housing at Coral Spur is the original pattern and its door seal is checked each visit.
Calibration gear for S-0111 travels with the district van and is shared with 26 other sites.

### S-0112 -- Willow Knoll

The logbook kept at Willow Knoll runs to 33 pages and the earlier volumes are held off site.
A spare sensor head is kept at Willow Knoll against the failure that took out the district in the previous cycle.
The approach to Willow Knoll crosses 27 field boundaries and the wayleave is held by the county.
The district file for Willow Knoll shows revision 1 lodged on 2034-01-12.
For S-0112 the status is withdrawn, the tier is 9, and the load is 439.
Two of the anchors at Willow Knoll were replaced after the frost and the work is recorded in the district ledger.
Correspondence about S-0112 is filed under the district rather than under the site, which has caused confusion before.
Weather at Willow Knoll closed the approach for 6 days during the period under review and no readings were lost.
A housekeeping note against S-0112 asks that the cable run be rewalked before the next dry season.
A visitor log is kept at Willow Knoll and shows 57 entries for the period.
Calibration gear for S-0112 travels with the district van and is shared with 36 other sites.
The instrument housing at Willow Knoll is the original pattern and its door seal is checked each visit.

### S-0113 -- Cedar Channel

Telemetry from S-0113 arrives on the sixth relay and is batched nightly rather than streamed.
The survey party reached Cedar Channel on the fourteenth of the month and found the access track passable for light vehicles only.
The instrument housing at Cedar Channel is the original pattern and its door seal is checked each visit.
The logbook kept at Cedar Channel runs to 7 pages and the earlier volumes are held off site.
The notes for S-0113 mention a disused well inside the compound, capped and recorded but not surveyed.
On 2034-01-25 the district accepted revision 6 for Cedar Channel and marked it open.
S-0113 carries tier 8 on that revision and a load of 235.
A calibration offset of -31 is recorded for S-0113 against the district standard.
A housekeeping note against S-0113 asks that the cable run be rewalked before the next dry season.
The access key for S-0113 is held at the district office and signed out per visit.
Calibration gear for S-0113 travels with the district van and is shared with 16 other sites.
The enclosure at Cedar Channel was rebuilt in timber after the old fencing was taken by the river.

### S-0114 -- Calder Ledge

The logbook kept at Calder Ledge runs to 25 pages and the earlier volumes are held off site.
S-0114 appears at revision 2 with a load of 841.
That revision of Calder Ledge was lodged 2034-12-10, is settled, and places the station in tier 4.
S-0114 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Correspondence about S-0114 is filed under the district rather than under the site, which has caused confusion before.
The notes for S-0114 mention a disused well inside the compound, capped and recorded but not surveyed.
Calder Ledge has been on the register since the first consolidation and its paperwork has never been reconstructed.
The reading shelter at Calder Ledge takes water in heavy weather and the floor was relaid.

### S-0115 -- Willow Tarn

Telemetry from S-0115 arrives on the first relay and is batched nightly rather than streamed.
Status settled: revision 6 for S-0115, lodged 2034-06-28.
Load 449 at tier 3 is what that revision carries for Willow Tarn.
A visitor log is kept at Willow Tarn and shows 18 entries for the period.
Signal strength at Willow Tarn has been marginal since the mast on the ridge was lowered.
The fence line at Willow Tarn was rerun 2 metres to the east to clear the culvert.
The approach to Willow Tarn crosses 32 field boundaries and the wayleave is held by the county.
An earlier clerk recorded Willow Tarn under a shortened spelling, and both forms still appear in the older indexes.
Drainage work near Willow Tarn was completed without interruption to the record.
The survey party reached Willow Tarn on the twelfth of the month and found the access track passable for light vehicles only.
Calibration gear for S-0115 travels with the district van and is shared with 32 other sites.
The access key for S-0115 is held at the district office and signed out per visit.

### S-0116 -- Ochre Gate

Maintenance visits to S-0116 are scheduled quarterly and the ninth of those was carried out as planned.
On 2034-05-18 the district accepted revision 1 for Ochre Gate and marked it settled.
S-0116 carries tier 1 on that revision and a load of 856.
Telemetry from S-0116 arrives on the thirteenth relay and is batched nightly rather than streamed.
The site plan for Ochre Gate is the ninth revision and supersedes the sketch held in the district folder.
The notes for S-0116 mention a disused well inside the compound, capped and recorded but not surveyed.
The access key for S-0116 is held at the district office and signed out per visit.

### S-0117 -- Gorse Haven

The notes for S-0117 mention a disused well inside the compound, capped and recorded but not surveyed.
Calibration gear for S-0117 travels with the district van and is shared with 38 other sites.
The district file for Gorse Haven shows revision 4 lodged on 2034-04-07.
For S-0117 the status is open, the tier is 3, and the load is 274.
Maintenance visits to S-0117 are scheduled quarterly and the first of those was carried out as planned.
The access key for S-0117 is held at the district office and signed out per visit.

### S-0118 -- Quince Combe

Maintenance visits to S-0118 are scheduled quarterly and the first of those was carried out as planned.
Quince Combe has been on the register since the first consolidation and its paperwork has never been reconstructed.
The load recorded for S-0118 is 870, on a return at tier 2.
That return for Quince Combe is revision 2, lodged 2034-03-13, and its status is settled.
A spare sensor head is kept at Quince Combe against the failure that took out the district in the previous cycle.
Access to Quince Combe is by the service road from the south; the gate code was reissued after the sixth inspection.

### S-0119 -- Granite Slade

Maintenance visits to S-0119 are scheduled quarterly and the sixth of those was carried out as planned.
Correspondence about S-0119 is filed under the district rather than under the site, which has caused confusion before.
The enclosure at Granite Slade was rebuilt in timber after the old fencing was taken by the river.
The load recorded for S-0119 is 900, on a return at tier 4.
That return for Granite Slade is revision 5, lodged 2034-06-21, and its status is settled.
A housekeeping note against S-0119 asks that the cable run be rewalked before the next dry season.

### S-0120 -- Ember Warren

Calibration gear for S-0120 travels with the district van and is shared with 39 other sites.
The load recorded for S-0120 is 855, on a return at tier 1.
That return for Ember Warren is revision 5, lodged 2034-07-20, and its status is settled.
A calibration offset of -18 is recorded for S-0120 against the district standard.
A visitor log is kept at Ember Warren and shows 73 entries for the period.
The access key for S-0120 is held at the district office and signed out per visit.
Correspondence shows the tenancy at Ember Warren was renewed for a further 83 years.
The fence line at Ember Warren was rerun 37 metres to the east to clear the culvert.
Signal strength at Ember Warren has been marginal since the mast on the ridge was lowered.

### S-0121 -- Dusk Hollow

An earlier clerk recorded Dusk Hollow under a shortened spelling, and both forms still appear in the older indexes.
The access key for S-0121 is held at the district office and signed out per visit.
The reading shelter at Dusk Hollow takes water in heavy weather and the floor was relaid.
Telemetry from S-0121 arrives on the first relay and is batched nightly rather than streamed.
Dusk Hollow shares its power feed with the neighbouring pumping station and has its own cut-out.
Correspondence about S-0121 is filed under the district rather than under the site, which has caused confusion before.
Access to Dusk Hollow is by the service road from the south; the gate code was reissued after the fourth inspection.
Status settled: revision 4 for S-0121, lodged 2034-04-06.
Load 307 at tier 2 is what that revision carries for Dusk Hollow.
The offset applied to readings from S-0121 is 38 and has not been revised.
The instrument housing at Dusk Hollow is the original pattern and its door seal is checked each visit.
The enclosure at Dusk Hollow was rebuilt in timber after the old fencing was taken by the river.
Dusk Hollow has been on the register since the first consolidation and its paperwork has never been reconstructed.

### S-0122 -- Chalk Moor

Telemetry from S-0122 arrives on the eighth relay and is batched nightly rather than streamed.
A visitor log is kept at Chalk Moor and shows 32 entries for the period.
Vegetation around Chalk Moor is cut back twice a year under the standing arrangement.
The reading shelter at Chalk Moor takes water in heavy weather and the floor was relaid.
S-0122 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The access key for S-0122 is held at the district office and signed out per visit.
Status provisional: revision 2 for S-0122, lodged 2034-02-13.
Load 610 at tier 5 is what that revision carries for Chalk Moor.
Drainage work near Chalk Moor was completed without interruption to the record.
Weather at Chalk Moor closed the approach for 7 days during the period under review and no readings were lost.
Calibration gear for S-0122 travels with the district van and is shared with 5 other sites.

### S-0326 -- Midland Brae

Midland Brae shares its power feed with the neighbouring pumping station and has its own cut-out.
Two of the anchors at Midland Brae were replaced after the frost and the work is recorded in the district ledger.
The district file for Midland Brae shows revision 3 lodged on 2034-06-12.
For S-0326 the status is settled, the tier is 9, and the load is 999.
The reconciliation sequence mark carried by this revision of S-0326 is 3.
The notes for S-0326 mention a disused well inside the compound, capped and recorded but not surveyed.
The fence line at Midland Brae was rerun 16 metres to the east to clear the culvert.
Maintenance visits to S-0326 are scheduled quarterly and the second of those was carried out as planned.
A visitor log is kept at Midland Brae and shows 44 entries for the period.
A spare sensor head is kept at Midland Brae against the failure that took out the district in the previous cycle.
The access key for S-0326 is held at the district office and signed out per visit.

### S-0124 -- Basalt Rill

Weather at Basalt Rill closed the approach for 20 days during the period under review and no readings were lost.
An earlier clerk recorded Basalt Rill under a shortened spelling, and both forms still appear in the older indexes.
Correspondence shows the tenancy at Basalt Rill was renewed for a further 77 years.
Basalt Rill has been on the register since the first consolidation and its paperwork has never been reconstructed.
Vegetation around Basalt Rill is cut back twice a year under the standing arrangement.
Status settled: revision 4 for S-0124, lodged 2034-04-26.
Load 328 at tier 5 is what that revision carries for Basalt Rill.
This revision of S-0124 is marked 2 in the reconciliation sequence.
A housekeeping note against S-0124 asks that the cable run be rewalked before the next dry season.
Telemetry from S-0124 arrives on the tenth relay and is batched nightly rather than streamed.
Maintenance visits to S-0124 are scheduled quarterly and the ninth of those was carried out as planned.
Two of the anchors at Basalt Rill were replaced after the frost and the work is recorded in the district ledger.

### S-0125 -- Dusk Strand

The instrument housing at Dusk Strand is the original pattern and its door seal is checked each visit.
The site plan for Dusk Strand is the seventh revision and supersedes the sketch held in the district folder.
An earlier clerk recorded Dusk Strand under a shortened spelling, and both forms still appear in the older indexes.
The survey party reached Dusk Strand on the fourth of the month and found the access track passable for light vehicles only.
Access to Dusk Strand is by the service road from the south; the gate code was reissued after the fourteenth inspection.
A visitor log is kept at Dusk Strand and shows 20 entries for the period.
S-0125 appears at revision 5 with a load of 408.
That revision of Dusk Strand was lodged 2034-06-14, is withdrawn, and places the station in tier 5.
The offset applied to readings from S-0125 is -37 and has not been revised.
The enclosure at Dusk Strand was rebuilt in timber after the old fencing was taken by the river.
The notes for S-0125 mention a disused well inside the compound, capped and recorded but not surveyed.
The fence line at Dusk Strand was rerun 8 metres to the east to clear the culvert.
Signal strength at Dusk Strand has been marginal since the mast on the ridge was lowered.

### S-0126 -- Gorse Hollow

Correspondence shows the tenancy at Gorse Hollow was renewed for a further 64 years.
Correspondence about S-0126 is filed under the district rather than under the site, which has caused confusion before.
The district file for Gorse Hollow shows revision 5 lodged on 2034-04-26.
For S-0126 the status is settled, the tier is 6, and the load is 686.
Signal strength at Gorse Hollow has been marginal since the mast on the ridge was lowered.
The reading shelter at Gorse Hollow takes water in heavy weather and the floor was relaid.
A housekeeping note against S-0126 asks that the cable run be rewalked before the next dry season.
A visitor log is kept at Gorse Hollow and shows 39 entries for the period.
The fence line at Gorse Hollow was rerun 16 metres to the east to clear the culvert.
Drainage work near Gorse Hollow was completed without interruption to the record.

### S-0127 -- Garnet Warren

Signal strength at Garnet Warren has been marginal since the mast on the ridge was lowered.
The logbook kept at Garnet Warren runs to 58 pages and the earlier volumes are held off site.
The reading shelter at Garnet Warren takes water in heavy weather and the floor was relaid.
Revision 1 of the return for Garnet Warren was lodged on 2034-06-19 and stands withdrawn.
That revision places S-0127 in tier 7 and gives its load as 611.
The offset applied to readings from S-0127 is -13 and has not been revised.
Calibration gear for S-0127 travels with the district van and is shared with 37 other sites.

### S-0128 -- Birch Strand

Access to Birch Strand is by the service road from the south; the gate code was reissued after the second inspection.
Status settled: revision 4 for S-0128, lodged 2034-09-14.
Load 293 at tier 2 is what that revision carries for Birch Strand.
Signal strength at Birch Strand has been marginal since the mast on the ridge was lowered.
The access key for S-0128 is held at the district office and signed out per visit.
The approach to Birch Strand crosses 27 field boundaries and the wayleave is held by the county.

### S-0129 -- Linden Bourne

The notes for S-0129 mention a disused well inside the compound, capped and recorded but not surveyed.
An earlier clerk recorded Linden Bourne under a shortened spelling, and both forms still appear in the older indexes.
Maintenance visits to S-0129 are scheduled quarterly and the eleventh of those was carried out as planned.
Drainage work near Linden Bourne was completed without interruption to the record.
The access key for S-0129 is held at the district office and signed out per visit.
Tier 3 is where Linden Bourne sits on revision 2, whose status is open.
The load on that revision of S-0129, lodged 2034-06-28, is 441.
Correspondence shows the tenancy at Linden Bourne was renewed for a further 26 years.
The approach to Linden Bourne crosses 17 field boundaries and the wayleave is held by the county.
Linden Bourne has been on the register since the first consolidation and its paperwork has never been reconstructed.
A housekeeping note against S-0129 asks that the cable run be rewalked before the next dry season.

### S-0130 -- Granite Shoal

The instrument housing at Granite Shoal is the original pattern and its door seal is checked each visit.
S-0130 appears at revision 5 with a load of 346.
That revision of Granite Shoal was lodged 2034-05-03, is settled, and places the station in tier 7.
A calibration offset of 3 is recorded for S-0130 against the district standard.
The logbook kept at Granite Shoal runs to 6 pages and the earlier volumes are held off site.
Calibration gear for S-0130 travels with the district van and is shared with 40 other sites.
A visitor log is kept at Granite Shoal and shows 54 entries for the period.
A spare sensor head is kept at Granite Shoal against the failure that took out the district in the previous cycle.
The notes for S-0130 mention a disused well inside the compound, capped and recorded but not surveyed.
S-0130 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Weather at Granite Shoal closed the approach for 5 days during the period under review and no readings were lost.

### S-0131 -- Crag Bluff

The survey party reached Crag Bluff on the fourteenth of the month and found the access track passable for light vehicles only.
The logbook kept at Crag Bluff runs to 33 pages and the earlier volumes are held off site.
Vegetation around Crag Bluff is cut back twice a year under the standing arrangement.
Crag Bluff has been on the register since the first consolidation and its paperwork has never been reconstructed.
Two of the anchors at Crag Bluff were replaced after the frost and the work is recorded in the district ledger.
Revision 4 of the return for Crag Bluff was lodged on 2034-07-25 and stands settled.
That revision places S-0131 in tier 2 and gives its load as 602.
The offset applied to readings from S-0131 is -28 and has not been revised.
The approach to Crag Bluff crosses 3 field boundaries and the wayleave is held by the county.
The reading shelter at Crag Bluff takes water in heavy weather and the floor was relaid.

### S-0132 -- Linden Withy

The instrument housing at Linden Withy is the original pattern and its door seal is checked each visit.
Linden Withy has been on the register since the first consolidation and its paperwork has never been reconstructed.
Linden Withy shares its power feed with the neighbouring pumping station and has its own cut-out.
The logbook kept at Linden Withy runs to 25 pages and the earlier volumes are held off site.
The site plan for Linden Withy is the third revision and supersedes the sketch held in the district folder.
Correspondence about S-0132 is filed under the district rather than under the site, which has caused confusion before.
The approach to Linden Withy crosses 32 field boundaries and the wayleave is held by the county.
Telemetry from S-0132 arrives on the second relay and is batched nightly rather than streamed.
Linden Withy lodged revision 5 on 2034-08-09.
The return for S-0132 is provisional, sits at tier 4, and records a load of 309.
Access to Linden Withy is by the service road from the south; the gate code was reissued after the fourteenth inspection.
A housekeeping note against S-0132 asks that the cable run be rewalked before the next dry season.

### S-0133 -- Gorse Yard

A housekeeping note against S-0133 asks that the cable run be rewalked before the next dry season.
Telemetry from S-0133 arrives on the fourteenth relay and is batched nightly rather than streamed.
S-0133 appears at revision 1 with a load of 946.
That revision of Gorse Yard was lodged 2034-10-28, is provisional, and places the station in tier 7.
A calibration offset of 40 is recorded for S-0133 against the district standard.
The fence line at Gorse Yard was rerun 7 metres to the east to clear the culvert.
Two of the anchors at Gorse Yard were replaced after the frost and the work is recorded in the district ledger.
The logbook kept at Gorse Yard runs to 20 pages and the earlier volumes are held off site.
S-0133 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Access to Gorse Yard is by the service road from the south; the gate code was reissued after the eighth inspection.
A visitor log is kept at Gorse Yard and shows 7 entries for the period.
The enclosure at Gorse Yard was rebuilt in timber after the old fencing was taken by the river.

### S-0134 -- Indigo Causeway

The access key for S-0134 is held at the district office and signed out per visit.
The instrument housing at Indigo Causeway is the original pattern and its door seal is checked each visit.
Maintenance visits to S-0134 are scheduled quarterly and the first of those was carried out as planned.
Correspondence shows the tenancy at Indigo Causeway was renewed for a further 21 years.
The load recorded for S-0134 is 874, on a return at tier 4.
That return for Indigo Causeway is revision 6, lodged 2034-06-27, and its status is settled.
Signal strength at Indigo Causeway has been marginal since the mast on the ridge was lowered.
The notes for S-0134 mention a disused well inside the compound, capped and recorded but not surveyed.
Vegetation around Indigo Causeway is cut back twice a year under the standing arrangement.

### S-0135 -- Osier Headland

The enclosure at Osier Headland was rebuilt in timber after the old fencing was taken by the river.
The reading shelter at Osier Headland takes water in heavy weather and the floor was relaid.
Correspondence about S-0135 is filed under the district rather than under the site, which has caused confusion before.
The instrument housing at Osier Headland is the original pattern and its door seal is checked each visit.
Status returned: revision 2 for S-0135, lodged 2034-12-12.
Load 169 at tier 2 is what that revision carries for Osier Headland.
The offset applied to readings from S-0135 is -40 and has not been revised.
A housekeeping note against S-0135 asks that the cable run be rewalked before the next dry season.
Osier Headland shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0136 -- Granite Cove

A spare sensor head is kept at Granite Cove against the failure that took out the district in the previous cycle.
Weather at Granite Cove closed the approach for 17 days during the period under review and no readings were lost.
Status returned: revision 2 for S-0136, lodged 2034-01-28.
Load 385 at tier 1 is what that revision carries for Granite Cove.
Drainage work near Granite Cove was completed without interruption to the record.
The access key for S-0136 is held at the district office and signed out per visit.
The reading shelter at Granite Cove takes water in heavy weather and the floor was relaid.

### S-0137 -- Sorrel Basin

A housekeeping note against S-0137 asks that the cable run be rewalked before the next dry season.
The approach to Sorrel Basin crosses 14 field boundaries and the wayleave is held by the county.
The enclosure at Sorrel Basin was rebuilt in timber after the old fencing was taken by the river.
The instrument housing at Sorrel Basin is the original pattern and its door seal is checked each visit.
Telemetry from S-0137 arrives on the second relay and is batched nightly rather than streamed.
Two of the anchors at Sorrel Basin were replaced after the frost and the work is recorded in the district ledger.
Weather at Sorrel Basin closed the approach for 33 days during the period under review and no readings were lost.
Signal strength at Sorrel Basin has been marginal since the mast on the ridge was lowered.
The district file for Sorrel Basin shows revision 2 lodged on 2034-07-10.
For S-0137 the status is settled, the tier is 1, and the load is 719.
The offset applied to readings from S-0137 is -2 and has not been revised.
Maintenance visits to S-0137 are scheduled quarterly and the second of those was carried out as planned.

### S-0138 -- Garnet Crossing

A spare sensor head is kept at Garnet Crossing against the failure that took out the district in the previous cycle.
Weather at Garnet Crossing closed the approach for 10 days during the period under review and no readings were lost.
An earlier clerk recorded Garnet Crossing under a shortened spelling, and both forms still appear in the older indexes.
Revision 4 of the return for Garnet Crossing was lodged on 2034-03-16 and stands open.
That revision places S-0138 in tier 7 and gives its load as 917.
The access key for S-0138 is held at the district office and signed out per visit.
A housekeeping note against S-0138 asks that the cable run be rewalked before the next dry season.

### S-0139 -- Amber Ferry

The approach to Amber Ferry crosses 15 field boundaries and the wayleave is held by the county.
Signal strength at Amber Ferry has been marginal since the mast on the ridge was lowered.
Status returned: revision 3 for S-0139, lodged 2034-01-04.
Load 799 at tier 2 is what that revision carries for Amber Ferry.
A housekeeping note against S-0139 asks that the cable run be rewalked before the next dry season.
The logbook kept at Amber Ferry runs to 76 pages and the earlier volumes are held off site.
S-0139 was one of the sites brought forward in the consolidation and its numbering reflects that order.

### S-0140 -- Crag Terrace

The approach to Crag Terrace crosses 28 field boundaries and the wayleave is held by the county.
A housekeeping note against S-0140 asks that the cable run be rewalked before the next dry season.
Correspondence about S-0140 is filed under the district rather than under the site, which has caused confusion before.
Access to Crag Terrace is by the service road from the south; the gate code was reissued after the second inspection.
The enclosure at Crag Terrace was rebuilt in timber after the old fencing was taken by the river.
Correspondence shows the tenancy at Crag Terrace was renewed for a further 7 years.
Status withdrawn: revision 3 for S-0140, lodged 2034-08-08.
Load 591 at tier 7 is what that revision carries for Crag Terrace.
The instrument housing at Crag Terrace is the original pattern and its door seal is checked each visit.
Maintenance visits to S-0140 are scheduled quarterly and the second of those was carried out as planned.

### S-0141 -- Clover Knoll

The fence line at Clover Knoll was rerun 28 metres to the east to clear the culvert.
Access to Clover Knoll is by the service road from the south; the gate code was reissued after the sixth inspection.
Clover Knoll has been on the register since the first consolidation and its paperwork has never been reconstructed.
Tier 1 is where Clover Knoll sits on revision 2, whose status is withdrawn.
The load on that revision of S-0141, lodged 2034-10-05, is 173.
Clover Knoll shares its power feed with the neighbouring pumping station and has its own cut-out.
The approach to Clover Knoll crosses 26 field boundaries and the wayleave is held by the county.

### S-0142 -- Dusk Combe

Maintenance visits to S-0142 are scheduled quarterly and the seventh of those was carried out as planned.
Status settled: revision 3 for S-0142, lodged 2034-12-23.
Load 443 at tier 3 is what that revision carries for Dusk Combe.
Dusk Combe shares its power feed with the neighbouring pumping station and has its own cut-out.
The fence line at Dusk Combe was rerun 35 metres to the east to clear the culvert.
The site plan for Dusk Combe is the thirteenth revision and supersedes the sketch held in the district folder.
S-0142 was one of the sites brought forward in the consolidation and its numbering reflects that order.
A visitor log is kept at Dusk Combe and shows 9 entries for the period.
A housekeeping note against S-0142 asks that the cable run be rewalked before the next dry season.

### S-0143 -- Willow Cairn

A housekeeping note against S-0143 asks that the cable run be rewalked before the next dry season.
Maintenance visits to S-0143 are scheduled quarterly and the twelfth of those was carried out as planned.
The survey party reached Willow Cairn on the thirteenth of the month and found the access track passable for light vehicles only.
An earlier clerk recorded Willow Cairn under a shortened spelling, and both forms still appear in the older indexes.
A spare sensor head is kept at Willow Cairn against the failure that took out the district in the previous cycle.
On 2034-06-04 the district accepted revision 2 for Willow Cairn and marked it settled.
S-0143 carries tier 2 on that revision and a load of 607.
Willow Cairn has been on the register since the first consolidation and its paperwork has never been reconstructed.
The reading shelter at Willow Cairn takes water in heavy weather and the floor was relaid.

### S-0144 -- Birch Thwaite

Two of the anchors at Birch Thwaite were replaced after the frost and the work is recorded in the district ledger.
The survey party reached Birch Thwaite on the first of the month and found the access track passable for light vehicles only.
Tier 2 is where Birch Thwaite sits on revision 3, whose status is settled.
The load on that revision of S-0144, lodged 2034-02-02, is 432.
A calibration offset of 39 is recorded for S-0144 against the district standard.
Signal strength at Birch Thwaite has been marginal since the mast on the ridge was lowered.
The instrument housing at Birch Thwaite is the original pattern and its door seal is checked each visit.
A housekeeping note against S-0144 asks that the cable run be rewalked before the next dry season.

### S-0145 -- Sorrel Shoal

The approach to Sorrel Shoal crosses 30 field boundaries and the wayleave is held by the county.
Weather at Sorrel Shoal closed the approach for 12 days during the period under review and no readings were lost.
Tier 2 is where Sorrel Shoal sits on revision 4, whose status is settled.
The load on that revision of S-0145, lodged 2034-07-07, is 177.
The site plan for Sorrel Shoal is the fourteenth revision and supersedes the sketch held in the district folder.
A spare sensor head is kept at Sorrel Shoal against the failure that took out the district in the previous cycle.
Sorrel Shoal shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0146 -- Mellow Wharf

Maintenance visits to S-0146 are scheduled quarterly and the fourteenth of those was carried out as planned.
Correspondence shows the tenancy at Mellow Wharf was renewed for a further 63 years.
Mellow Wharf shares its power feed with the neighbouring pumping station and has its own cut-out.
An earlier clerk recorded Mellow Wharf under a shortened spelling, and both forms still appear in the older indexes.
Mellow Wharf has been on the register since the first consolidation and its paperwork has never been reconstructed.
Revision 5 of the return for Mellow Wharf was lodged on 2034-06-10 and stands settled.
That revision places S-0146 in tier 3 and gives its load as 362.
The enclosure at Mellow Wharf was rebuilt in timber after the old fencing was taken by the river.
The notes for S-0146 mention a disused well inside the compound, capped and recorded but not surveyed.
Signal strength at Mellow Wharf has been marginal since the mast on the ridge was lowered.
The survey party reached Mellow Wharf on the tenth of the month and found the access track passable for light vehicles only.

### S-0147 -- Ridge Withy

Two of the anchors at Ridge Withy were replaced after the frost and the work is recorded in the district ledger.
Access to Ridge Withy is by the service road from the south; the gate code was reissued after the eighth inspection.
Telemetry from S-0147 arrives on the fifth relay and is batched nightly rather than streamed.
The access key for S-0147 is held at the district office and signed out per visit.
Vegetation around Ridge Withy is cut back twice a year under the standing arrangement.
A visitor log is kept at Ridge Withy and shows 79 entries for the period.
On 2034-07-17 the district accepted revision 2 for Ridge Withy and marked it provisional.
S-0147 carries tier 9 on that revision and a load of 412.
The logbook kept at Ridge Withy runs to 25 pages and the earlier volumes are held off site.
S-0147 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Correspondence shows the tenancy at Ridge Withy was renewed for a further 87 years.
The survey party reached Ridge Withy on the sixth of the month and found the access track passable for light vehicles only.

### S-0148 -- Teasel Wharf

Maintenance visits to S-0148 are scheduled quarterly and the tenth of those was carried out as planned.
Telemetry from S-0148 arrives on the thirteenth relay and is batched nightly rather than streamed.
S-0148 appears at revision 2 with a load of 914.
That revision of Teasel Wharf was lodged 2034-12-11, is settled, and places the station in tier 2.
A calibration offset of 7 is recorded for S-0148 against the district standard.
The logbook kept at Teasel Wharf runs to 47 pages and the earlier volumes are held off site.
Two of the anchors at Teasel Wharf were replaced after the frost and the work is recorded in the district ledger.
The access key for S-0148 is held at the district office and signed out per visit.
Calibration gear for S-0148 travels with the district van and is shared with 2 other sites.

### S-0149 -- Osier Yard

Osier Yard shares its power feed with the neighbouring pumping station and has its own cut-out.
The fence line at Osier Yard was rerun 19 metres to the east to clear the culvert.
A spare sensor head is kept at Osier Yard against the failure that took out the district in the previous cycle.
On 2034-09-10 the district accepted revision 4 for Osier Yard and marked it settled.
S-0149 carries tier 2 on that revision and a load of 528.
Telemetry from S-0149 arrives on the tenth relay and is batched nightly rather than streamed.
Maintenance visits to S-0149 are scheduled quarterly and the second of those was carried out as planned.
Two of the anchors at Osier Yard were replaced after the frost and the work is recorded in the district ledger.
Signal strength at Osier Yard has been marginal since the mast on the ridge was lowered.

### S-0150 -- Gorse Withy

S-0150 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Vegetation around Gorse Withy is cut back twice a year under the standing arrangement.
Maintenance visits to S-0150 are scheduled quarterly and the fourteenth of those was carried out as planned.
An earlier clerk recorded Gorse Withy under a shortened spelling, and both forms still appear in the older indexes.
The site plan for Gorse Withy is the fourth revision and supersedes the sketch held in the district folder.
A visitor log is kept at Gorse Withy and shows 76 entries for the period.
The district file for Gorse Withy shows revision 5 lodged on 2034-10-26.
For S-0150 the status is provisional, the tier is 5, and the load is 899.
The survey party reached Gorse Withy on the seventh of the month and found the access track passable for light vehicles only.
Weather at Gorse Withy closed the approach for 17 days during the period under review and no readings were lost.

### S-0151 -- Sorrel Down

The access key for S-0151 is held at the district office and signed out per visit.
Weather at Sorrel Down closed the approach for 31 days during the period under review and no readings were lost.
Tier 9 is where Sorrel Down sits on revision 1, whose status is returned.
The load on that revision of S-0151, lodged 2034-10-21, is 293.
The notes for S-0151 mention a disused well inside the compound, capped and recorded but not surveyed.
An earlier clerk recorded Sorrel Down under a shortened spelling, and both forms still appear in the older indexes.
The reading shelter at Sorrel Down takes water in heavy weather and the floor was relaid.

### S-0152 -- Birch Drift

The fence line at Birch Drift was rerun 22 metres to the east to clear the culvert.
The site plan for Birch Drift is the tenth revision and supersedes the sketch held in the district folder.
Correspondence about S-0152 is filed under the district rather than under the site, which has caused confusion before.
Signal strength at Birch Drift has been marginal since the mast on the ridge was lowered.
On 2034-10-20 the district accepted revision 6 for Birch Drift and marked it withdrawn.
S-0152 carries tier 3 on that revision and a load of 702.
Weather at Birch Drift closed the approach for 4 days during the period under review and no readings were lost.
The notes for S-0152 mention a disused well inside the compound, capped and recorded but not surveyed.
Drainage work near Birch Drift was completed without interruption to the record.
Correspondence shows the tenancy at Birch Drift was renewed for a further 5 years.

### S-0153 -- Pewter Channel

The enclosure at Pewter Channel was rebuilt in timber after the old fencing was taken by the river.
Pewter Channel lodged revision 2 on 2034-03-14.
The return for S-0153 is withdrawn, sits at tier 6, and records a load of 470.
Telemetry from S-0153 arrives on the ninth relay and is batched nightly rather than streamed.
An earlier clerk recorded Pewter Channel under a shortened spelling, and both forms still appear in the older indexes.
Weather at Pewter Channel closed the approach for 12 days during the period under review and no readings were lost.

### S-0154 -- Crag Hallow

The access key for S-0154 is held at the district office and signed out per visit.
S-0154 was one of the sites brought forward in the consolidation and its numbering reflects that order.
On 2034-11-27 the district accepted revision 1 for Crag Hallow and marked it settled.
S-0154 carries tier 2 on that revision and a load of 528.
A calibration offset of -29 is recorded for S-0154 against the district standard.
The logbook kept at Crag Hallow runs to 85 pages and the earlier volumes are held off site.
Access to Crag Hallow is by the service road from the south; the gate code was reissued after the eighth inspection.

### S-0155 -- Copper Pike

Access to Copper Pike is by the service road from the south; the gate code was reissued after the eighth inspection.
Signal strength at Copper Pike has been marginal since the mast on the ridge was lowered.
Two of the anchors at Copper Pike were replaced after the frost and the work is recorded in the district ledger.
Maintenance visits to S-0155 are scheduled quarterly and the sixth of those was carried out as planned.
Copper Pike shares its power feed with the neighbouring pumping station and has its own cut-out.
The survey party reached Copper Pike on the tenth of the month and found the access track passable for light vehicles only.
The district file for Copper Pike shows revision 6 lodged on 2034-07-13.
For S-0155 the status is provisional, the tier is 6, and the load is 447.
The offset applied to readings from S-0155 is 24 and has not been revised.
The instrument housing at Copper Pike is the original pattern and its door seal is checked each visit.

### S-0156 -- Sedge Bight

A housekeeping note against S-0156 asks that the cable run be rewalked before the next dry season.
S-0156 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Status settled: revision 1 for S-0156, lodged 2034-11-10.
Load 680 at tier 3 is what that revision carries for Sedge Bight.
A visitor log is kept at Sedge Bight and shows 50 entries for the period.
The notes for S-0156 mention a disused well inside the compound, capped and recorded but not surveyed.

### S-0157 -- Garnet Pasture

The enclosure at Garnet Pasture was rebuilt in timber after the old fencing was taken by the river.
A housekeeping note against S-0157 asks that the cable run be rewalked before the next dry season.
Garnet Pasture shares its power feed with the neighbouring pumping station and has its own cut-out.
A spare sensor head is kept at Garnet Pasture against the failure that took out the district in the previous cycle.
Telemetry from S-0157 arrives on the first relay and is batched nightly rather than streamed.
On 2034-01-11 the district accepted revision 3 for Garnet Pasture and marked it settled.
S-0157 carries tier 4 on that revision and a load of 438.
Garnet Pasture carries a calibration offset of -17 on the current instrument head.
The access key for S-0157 is held at the district office and signed out per visit.
The instrument housing at Garnet Pasture is the original pattern and its door seal is checked each visit.
The logbook kept at Garnet Pasture runs to 86 pages and the earlier volumes are held off site.

### S-0158 -- Bramble Channel

The instrument housing at Bramble Channel is the original pattern and its door seal is checked each visit.
The survey party reached Bramble Channel on the fourteenth of the month and found the access track passable for light vehicles only.
The enclosure at Bramble Channel was rebuilt in timber after the old fencing was taken by the river.
Tier 3 is where Bramble Channel sits on revision 2, whose status is settled.
The load on that revision of S-0158, lodged 2034-03-09, is 437.
Signal strength at Bramble Channel has been marginal since the mast on the ridge was lowered.
Vegetation around Bramble Channel is cut back twice a year under the standing arrangement.

### S-0159 -- Hazel Yard

The approach to Hazel Yard crosses 37 field boundaries and the wayleave is held by the county.
Hazel Yard has been on the register since the first consolidation and its paperwork has never been reconstructed.
The district file for Hazel Yard shows revision 5 lodged on 2034-04-25.
For S-0159 the status is settled, the tier is 1, and the load is 406.
Hazel Yard carries a calibration offset of 19 on the current instrument head.
An earlier clerk recorded Hazel Yard under a shortened spelling, and both forms still appear in the older indexes.
Access to Hazel Yard is by the service road from the south; the gate code was reissued after the twelfth inspection.
A spare sensor head is kept at Hazel Yard against the failure that took out the district in the previous cycle.
Weather at Hazel Yard closed the approach for 13 days during the period under review and no readings were lost.
A housekeeping note against S-0159 asks that the cable run be rewalked before the next dry season.
The fence line at Hazel Yard was rerun 23 metres to the east to clear the culvert.
The logbook kept at Hazel Yard runs to 21 pages and the earlier volumes are held off site.

### S-0160 -- Yarrow Haven

S-0160 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The load recorded for S-0160 is 212, on a return at tier 3.
That return for Yarrow Haven is revision 3, lodged 2034-07-10, and its status is settled.
Vegetation around Yarrow Haven is cut back twice a year under the standing arrangement.
Maintenance visits to S-0160 are scheduled quarterly and the seventh of those was carried out as planned.
Correspondence about S-0160 is filed under the district rather than under the site, which has caused confusion before.
The notes for S-0160 mention a disused well inside the compound, capped and recorded but not surveyed.
A spare sensor head is kept at Yarrow Haven against the failure that took out the district in the previous cycle.
Correspondence shows the tenancy at Yarrow Haven was renewed for a further 77 years.
A housekeeping note against S-0160 asks that the cable run be rewalked before the next dry season.

### S-0161 -- Basalt Reach

A visitor log is kept at Basalt Reach and shows 30 entries for the period.
Two of the anchors at Basalt Reach were replaced after the frost and the work is recorded in the district ledger.
Tier 4 is where Basalt Reach sits on revision 6, whose status is returned.
The load on that revision of S-0161, lodged 2034-02-24, is 620.
The access key for S-0161 is held at the district office and signed out per visit.
Correspondence about S-0161 is filed under the district rather than under the site, which has caused confusion before.
The enclosure at Basalt Reach was rebuilt in timber after the old fencing was taken by the river.
Signal strength at Basalt Reach has been marginal since the mast on the ridge was lowered.
The reading shelter at Basalt Reach takes water in heavy weather and the floor was relaid.
Vegetation around Basalt Reach is cut back twice a year under the standing arrangement.

### S-0162 -- Amber Withy

A spare sensor head is kept at Amber Withy against the failure that took out the district in the previous cycle.
Vegetation around Amber Withy is cut back twice a year under the standing arrangement.
Drainage work near Amber Withy was completed without interruption to the record.
On 2034-01-19 the district accepted revision 4 for Amber Withy and marked it withdrawn.
S-0162 carries tier 3 on that revision and a load of 125.
The offset applied to readings from S-0162 is 17 and has not been revised.
The notes for S-0162 mention a disused well inside the compound, capped and recorded but not surveyed.
S-0162 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Amber Withy has been on the register since the first consolidation and its paperwork has never been reconstructed.
An earlier clerk recorded Amber Withy under a shortened spelling, and both forms still appear in the older indexes.
Amber Withy shares its power feed with the neighbouring pumping station and has its own cut-out.
The logbook kept at Amber Withy runs to 31 pages and the earlier volumes are held off site.

### S-0163 -- Willow Gate

The reading shelter at Willow Gate takes water in heavy weather and the floor was relaid.
A housekeeping note against S-0163 asks that the cable run be rewalked before the next dry season.
The notes for S-0163 mention a disused well inside the compound, capped and recorded but not surveyed.
S-0163 was one of the sites brought forward in the consolidation and its numbering reflects that order.
A spare sensor head is kept at Willow Gate against the failure that took out the district in the previous cycle.
Two of the anchors at Willow Gate were replaced after the frost and the work is recorded in the district ledger.
Maintenance visits to S-0163 are scheduled quarterly and the eleventh of those was carried out as planned.
On 2034-10-24 the district accepted revision 5 for Willow Gate and marked it withdrawn.
S-0163 carries tier 7 on that revision and a load of 114.
The offset applied to readings from S-0163 is 38 and has not been revised.
Weather at Willow Gate closed the approach for 19 days during the period under review and no readings were lost.

### S-0164 -- Indigo Staithe

Indigo Staithe has been on the register since the first consolidation and its paperwork has never been reconstructed.
Drainage work near Indigo Staithe was completed without interruption to the record.
The instrument housing at Indigo Staithe is the original pattern and its door seal is checked each visit.
Status settled: revision 5 for S-0164, lodged 2034-05-06.
Load 679 at tier 1 is what that revision carries for Indigo Staithe.
Two of the anchors at Indigo Staithe were replaced after the frost and the work is recorded in the district ledger.
Signal strength at Indigo Staithe has been marginal since the mast on the ridge was lowered.
An earlier clerk recorded Indigo Staithe under a shortened spelling, and both forms still appear in the older indexes.

### S-0165 -- Sable Mill

The enclosure at Sable Mill was rebuilt in timber after the old fencing was taken by the river.
Sable Mill shares its power feed with the neighbouring pumping station and has its own cut-out.
The logbook kept at Sable Mill runs to 10 pages and the earlier volumes are held off site.
The district file for Sable Mill shows revision 6 lodged on 2034-11-26.
For S-0165 the status is provisional, the tier is 8, and the load is 376.
A visitor log is kept at Sable Mill and shows 27 entries for the period.
Drainage work near Sable Mill was completed without interruption to the record.
An earlier clerk recorded Sable Mill under a shortened spelling, and both forms still appear in the older indexes.
Telemetry from S-0165 arrives on the fifth relay and is batched nightly rather than streamed.
The survey party reached Sable Mill on the fourteenth of the month and found the access track passable for light vehicles only.

### S-0166 -- Garnet Furlong

The instrument housing at Garnet Furlong is the original pattern and its door seal is checked each visit.
S-0166 was one of the sites brought forward in the consolidation and its numbering reflects that order.
A visitor log is kept at Garnet Furlong and shows 85 entries for the period.
The approach to Garnet Furlong crosses 24 field boundaries and the wayleave is held by the county.
The reading shelter at Garnet Furlong takes water in heavy weather and the floor was relaid.
Correspondence about S-0166 is filed under the district rather than under the site, which has caused confusion before.
On 2034-08-10 the district accepted revision 2 for Garnet Furlong and marked it withdrawn.
S-0166 carries tier 8 on that revision and a load of 987.
Garnet Furlong carries a calibration offset of -28 on the current instrument head.
Correspondence shows the tenancy at Garnet Furlong was renewed for a further 89 years.

### S-0167 -- Birch Hallow

A housekeeping note against S-0167 asks that the cable run be rewalked before the next dry season.
The access key for S-0167 is held at the district office and signed out per visit.
The enclosure at Birch Hallow was rebuilt in timber after the old fencing was taken by the river.
Revision 5 of the return for Birch Hallow was lodged on 2034-03-28 and stands provisional.
That revision places S-0167 in tier 1 and gives its load as 138.
Signal strength at Birch Hallow has been marginal since the mast on the ridge was lowered.
Calibration gear for S-0167 travels with the district van and is shared with 7 other sites.
Birch Hallow shares its power feed with the neighbouring pumping station and has its own cut-out.
Two of the anchors at Birch Hallow were replaced after the frost and the work is recorded in the district ledger.

### S-0168 -- Birch Quay

The notes for S-0168 mention a disused well inside the compound, capped and recorded but not surveyed.
The approach to Birch Quay crosses 4 field boundaries and the wayleave is held by the county.
An earlier clerk recorded Birch Quay under a shortened spelling, and both forms still appear in the older indexes.
S-0168 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The fence line at Birch Quay was rerun 36 metres to the east to clear the culvert.
Birch Quay lodged revision 5 on 2034-07-14.
The return for S-0168 is settled, sits at tier 2, and records a load of 318.
Signal strength at Birch Quay has been marginal since the mast on the ridge was lowered.
Maintenance visits to S-0168 are scheduled quarterly and the fourteenth of those was carried out as planned.
Correspondence shows the tenancy at Birch Quay was renewed for a further 11 years.

### S-0169 -- Quince Dale

The access key for S-0169 is held at the district office and signed out per visit.
The load recorded for S-0169 is 288, on a return at tier 4.
That return for Quince Dale is revision 3, lodged 2034-08-09, and its status is settled.
The instrument housing at Quince Dale is the original pattern and its door seal is checked each visit.
Weather at Quince Dale closed the approach for 11 days during the period under review and no readings were lost.
Drainage work near Quince Dale was completed without interruption to the record.
Maintenance visits to S-0169 are scheduled quarterly and the ninth of those was carried out as planned.
A visitor log is kept at Quince Dale and shows 66 entries for the period.

### S-0170 -- Osier Ripple

Weather at Osier Ripple closed the approach for 40 days during the period under review and no readings were lost.
The instrument housing at Osier Ripple is the original pattern and its door seal is checked each visit.
Osier Ripple lodged revision 6 on 2034-02-18.
The return for S-0170 is settled, sits at tier 2, and records a load of 752.
A calibration offset of -6 is recorded for S-0170 against the district standard.
The access key for S-0170 is held at the district office and signed out per visit.
A housekeeping note against S-0170 asks that the cable run be rewalked before the next dry season.
Two of the anchors at Osier Ripple were replaced after the frost and the work is recorded in the district ledger.

### S-0171 -- Nettle Gully

A visitor log is kept at Nettle Gully and shows 44 entries for the period.
Nettle Gully shares its power feed with the neighbouring pumping station and has its own cut-out.
The load recorded for S-0171 is 874, on a return at tier 4.
That return for Nettle Gully is revision 5, lodged 2034-08-10, and its status is withdrawn.
The offset applied to readings from S-0171 is 1 and has not been revised.
Correspondence about S-0171 is filed under the district rather than under the site, which has caused confusion before.
Two of the anchors at Nettle Gully were replaced after the frost and the work is recorded in the district ledger.
The instrument housing at Nettle Gully is the original pattern and its door seal is checked each visit.
Weather at Nettle Gully closed the approach for 9 days during the period under review and no readings were lost.

### S-0172 -- Ochre Ferry

A housekeeping note against S-0172 asks that the cable run be rewalked before the next dry season.
Calibration gear for S-0172 travels with the district van and is shared with 15 other sites.
The site plan for Ochre Ferry is the third revision and supersedes the sketch held in the district folder.
Vegetation around Ochre Ferry is cut back twice a year under the standing arrangement.
Revision 4 of the return for Ochre Ferry was lodged on 2034-03-16 and stands open.
That revision places S-0172 in tier 8 and gives its load as 505.
The notes for S-0172 mention a disused well inside the compound, capped and recorded but not surveyed.
The reading shelter at Ochre Ferry takes water in heavy weather and the floor was relaid.
The logbook kept at Ochre Ferry runs to 21 pages and the earlier volumes are held off site.
Correspondence about S-0172 is filed under the district rather than under the site, which has caused confusion before.
A spare sensor head is kept at Ochre Ferry against the failure that took out the district in the previous cycle.

### S-0173 -- Harrow Basin

The site plan for Harrow Basin is the thirteenth revision and supersedes the sketch held in the district folder.
The logbook kept at Harrow Basin runs to 90 pages and the earlier volumes are held off site.
Revision 1 of the return for Harrow Basin was lodged on 2034-07-08 and stands settled.
That revision places S-0173 in tier 1 and gives its load as 640.
Telemetry from S-0173 arrives on the seventh relay and is batched nightly rather than streamed.
A visitor log is kept at Harrow Basin and shows 58 entries for the period.
Harrow Basin has been on the register since the first consolidation and its paperwork has never been reconstructed.
Access to Harrow Basin is by the service road from the south; the gate code was reissued after the eleventh inspection.
The survey party reached Harrow Basin on the eighth of the month and found the access track passable for light vehicles only.

### S-0174 -- Bronze Glade

An earlier clerk recorded Bronze Glade under a shortened spelling, and both forms still appear in the older indexes.
A spare sensor head is kept at Bronze Glade against the failure that took out the district in the previous cycle.
The district file for Bronze Glade shows revision 4 lodged on 2034-01-02.
For S-0174 the status is settled, the tier is 5, and the load is 419.
Bronze Glade carries sequence mark 5 in this quarter's reconciliation.
Access to Bronze Glade is by the service road from the south; the gate code was reissued after the tenth inspection.
S-0174 was one of the sites brought forward in the consolidation and its numbering reflects that order.

### S-0175 -- Dapple Cove

Drainage work near Dapple Cove was completed without interruption to the record.
The reading shelter at Dapple Cove takes water in heavy weather and the floor was relaid.
Tier 5 is where Dapple Cove sits on revision 5, whose status is settled.
The load on that revision of S-0175, lodged 2034-03-03, is 486.
Two of the anchors at Dapple Cove were replaced after the frost and the work is recorded in the district ledger.
Correspondence about S-0175 is filed under the district rather than under the site, which has caused confusion before.
Access to Dapple Cove is by the service road from the south; the gate code was reissued after the fourth inspection.
Vegetation around Dapple Cove is cut back twice a year under the standing arrangement.
A spare sensor head is kept at Dapple Cove against the failure that took out the district in the previous cycle.
The notes for S-0175 mention a disused well inside the compound, capped and recorded but not surveyed.
Correspondence shows the tenancy at Dapple Cove was renewed for a further 83 years.

### S-0176 -- Bronze Cleave

A housekeeping note against S-0176 asks that the cable run be rewalked before the next dry season.
The district file for Bronze Cleave shows revision 5 lodged on 2034-07-07.
For S-0176 the status is settled, the tier is 2, and the load is 621.
The enclosure at Bronze Cleave was rebuilt in timber after the old fencing was taken by the river.
Bronze Cleave shares its power feed with the neighbouring pumping station and has its own cut-out.
Telemetry from S-0176 arrives on the tenth relay and is batched nightly rather than streamed.

### S-0177 -- Jasper Down

Correspondence about S-0177 is filed under the district rather than under the site, which has caused confusion before.
The site plan for Jasper Down is the first revision and supersedes the sketch held in the district folder.
Vegetation around Jasper Down is cut back twice a year under the standing arrangement.
The enclosure at Jasper Down was rebuilt in timber after the old fencing was taken by the river.
Jasper Down shares its power feed with the neighbouring pumping station and has its own cut-out.
Revision 4 of the return for Jasper Down was lodged on 2034-01-02 and stands settled.
That revision places S-0177 in tier 8 and gives its load as 246.
Weather at Jasper Down closed the approach for 8 days during the period under review and no readings were lost.
The instrument housing at Jasper Down is the original pattern and its door seal is checked each visit.
S-0177 was one of the sites brought forward in the consolidation and its numbering reflects that order.

### S-0178 -- Flint Cairn

Signal strength at Flint Cairn has been marginal since the mast on the ridge was lowered.
Vegetation around Flint Cairn is cut back twice a year under the standing arrangement.
Correspondence shows the tenancy at Flint Cairn was renewed for a further 40 years.
Drainage work near Flint Cairn was completed without interruption to the record.
Telemetry from S-0178 arrives on the eleventh relay and is batched nightly rather than streamed.
Status settled: revision 4 for S-0178, lodged 2034-04-09.
Load 250 at tier 4 is what that revision carries for Flint Cairn.
A calibration offset of 21 is recorded for S-0178 against the district standard.
Two of the anchors at Flint Cairn were replaced after the frost and the work is recorded in the district ledger.
Weather at Flint Cairn closed the approach for 7 days during the period under review and no readings were lost.
S-0178 was one of the sites brought forward in the consolidation and its numbering reflects that order.
A spare sensor head is kept at Flint Cairn against the failure that took out the district in the previous cycle.

### S-0179 -- Cinder Pasture

The site plan for Cinder Pasture is the tenth revision and supersedes the sketch held in the district folder.
Vegetation around Cinder Pasture is cut back twice a year under the standing arrangement.
Telemetry from S-0179 arrives on the ninth relay and is batched nightly rather than streamed.
The survey party reached Cinder Pasture on the fourth of the month and found the access track passable for light vehicles only.
Revision 5 of the return for Cinder Pasture was lodged on 2034-09-19 and stands provisional.
That revision places S-0179 in tier 4 and gives its load as 623.
The offset applied to readings from S-0179 is -13 and has not been revised.
The fence line at Cinder Pasture was rerun 32 metres to the east to clear the culvert.
An earlier clerk recorded Cinder Pasture under a shortened spelling, and both forms still appear in the older indexes.
Access to Cinder Pasture is by the service road from the south; the gate code was reissued after the ninth inspection.

### S-0180 -- Linden Cove

Two of the anchors at Linden Cove were replaced after the frost and the work is recorded in the district ledger.
Vegetation around Linden Cove is cut back twice a year under the standing arrangement.
The instrument housing at Linden Cove is the original pattern and its door seal is checked each visit.
Status settled: revision 4 for S-0180, lodged 2034-05-19.
Load 950 at tier 8 is what that revision carries for Linden Cove.
Correspondence about S-0180 is filed under the district rather than under the site, which has caused confusion before.
The notes for S-0180 mention a disused well inside the compound, capped and recorded but not surveyed.

### S-0181 -- Heather Slade

Heather Slade has been on the register since the first consolidation and its paperwork has never been reconstructed.
An earlier clerk recorded Heather Slade under a shortened spelling, and both forms still appear in the older indexes.
Two of the anchors at Heather Slade were replaced after the frost and the work is recorded in the district ledger.
Weather at Heather Slade closed the approach for 22 days during the period under review and no readings were lost.
Heather Slade lodged revision 2 on 2034-11-24.
The return for S-0181 is settled, sits at tier 1, and records a load of 808.
The notes for S-0181 mention a disused well inside the compound, capped and recorded but not surveyed.
Vegetation around Heather Slade is cut back twice a year under the standing arrangement.
The survey party reached Heather Slade on the ninth of the month and found the access track passable for light vehicles only.
The logbook kept at Heather Slade runs to 5 pages and the earlier volumes are held off site.
Calibration gear for S-0181 travels with the district van and is shared with 38 other sites.

### S-0182 -- Yarrow Thwaite

Drainage work near Yarrow Thwaite was completed without interruption to the record.
The district file for Yarrow Thwaite shows revision 3 lodged on 2034-12-01.
For S-0182 the status is settled, the tier is 1, and the load is 570.
Signal strength at Yarrow Thwaite has been marginal since the mast on the ridge was lowered.
The notes for S-0182 mention a disused well inside the compound, capped and recorded but not surveyed.
Vegetation around Yarrow Thwaite is cut back twice a year under the standing arrangement.
Weather at Yarrow Thwaite closed the approach for 17 days during the period under review and no readings were lost.
The reading shelter at Yarrow Thwaite takes water in heavy weather and the floor was relaid.
S-0182 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The instrument housing at Yarrow Thwaite is the original pattern and its door seal is checked each visit.
The logbook kept at Yarrow Thwaite runs to 29 pages and the earlier volumes are held off site.

### S-0183 -- Vellum Pound

The notes for S-0183 mention a disused well inside the compound, capped and recorded but not surveyed.
The fence line at Vellum Pound was rerun 33 metres to the east to clear the culvert.
Vellum Pound lodged revision 2 on 2034-12-22.
The return for S-0183 is settled, sits at tier 4, and records a load of 829.
The site plan for Vellum Pound is the second revision and supersedes the sketch held in the district folder.
Vellum Pound has been on the register since the first consolidation and its paperwork has never been reconstructed.
Vegetation around Vellum Pound is cut back twice a year under the standing arrangement.
S-0183 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The approach to Vellum Pound crosses 22 field boundaries and the wayleave is held by the county.

### S-0184 -- Rowan Dale

Rowan Dale shares its power feed with the neighbouring pumping station and has its own cut-out.
The access key for S-0184 is held at the district office and signed out per visit.
The approach to Rowan Dale crosses 25 field boundaries and the wayleave is held by the county.
A housekeeping note against S-0184 asks that the cable run be rewalked before the next dry season.
Two of the anchors at Rowan Dale were replaced after the frost and the work is recorded in the district ledger.
The enclosure at Rowan Dale was rebuilt in timber after the old fencing was taken by the river.
Rowan Dale lodged revision 1 on 2034-04-21.
The return for S-0184 is settled, sits at tier 4, and records a load of 790.
S-0184 was one of the sites brought forward in the consolidation and its numbering reflects that order.

### S-0185 -- Kestrel Mill

S-0185 was one of the sites brought forward in the consolidation and its numbering reflects that order.
A visitor log is kept at Kestrel Mill and shows 65 entries for the period.
On 2034-03-26 the district accepted revision 5 for Kestrel Mill and marked it provisional.
S-0185 carries tier 6 on that revision and a load of 787.
Access to Kestrel Mill is by the service road from the south; the gate code was reissued after the eleventh inspection.
An earlier clerk recorded Kestrel Mill under a shortened spelling, and both forms still appear in the older indexes.
Two of the anchors at Kestrel Mill were replaced after the frost and the work is recorded in the district ledger.

### S-0186 -- Birch Ferry

Two of the anchors at Birch Ferry were replaced after the frost and the work is recorded in the district ledger.
Birch Ferry shares its power feed with the neighbouring pumping station and has its own cut-out.
Birch Ferry lodged revision 1 on 2034-08-12.
The return for S-0186 is settled, sits at tier 3, and records a load of 196.
A calibration offset of -24 is recorded for S-0186 against the district standard.
Correspondence about S-0186 is filed under the district rather than under the site, which has caused confusion before.
Drainage work near Birch Ferry was completed without interruption to the record.
Calibration gear for S-0186 travels with the district van and is shared with 18 other sites.
The logbook kept at Birch Ferry runs to 13 pages and the earlier volumes are held off site.
Correspondence shows the tenancy at Birch Ferry was renewed for a further 50 years.
Access to Birch Ferry is by the service road from the south; the gate code was reissued after the seventh inspection.
Signal strength at Birch Ferry has been marginal since the mast on the ridge was lowered.

### S-0187 -- Quarry Reach

The survey party reached Quarry Reach on the eleventh of the month and found the access track passable for light vehicles only.
Calibration gear for S-0187 travels with the district van and is shared with 8 other sites.
Status settled: revision 6 for S-0187, lodged 2034-12-27.
Load 334 at tier 4 is what that revision carries for Quarry Reach.
The notes for S-0187 mention a disused well inside the compound, capped and recorded but not surveyed.
Telemetry from S-0187 arrives on the eleventh relay and is batched nightly rather than streamed.

### S-0188 -- Thistle Hallow

S-0188 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Telemetry from S-0188 arrives on the twelfth relay and is batched nightly rather than streamed.
Thistle Hallow has been on the register since the first consolidation and its paperwork has never been reconstructed.
The load recorded for S-0188 is 345, on a return at tier 3.
That return for Thistle Hallow is revision 3, lodged 2034-05-27, and its status is settled.
The logbook kept at Thistle Hallow runs to 38 pages and the earlier volumes are held off site.

### S-0189 -- Russet Reach

The fence line at Russet Reach was rerun 28 metres to the east to clear the culvert.
The load recorded for S-0189 is 260, on a return at tier 5.
That return for Russet Reach is revision 1, lodged 2034-09-04, and its status is open.
Telemetry from S-0189 arrives on the fourteenth relay and is batched nightly rather than streamed.
Calibration gear for S-0189 travels with the district van and is shared with 37 other sites.
Russet Reach has been on the register since the first consolidation and its paperwork has never been reconstructed.
Correspondence about S-0189 is filed under the district rather than under the site, which has caused confusion before.
Access to Russet Reach is by the service road from the south; the gate code was reissued after the fourth inspection.
The access key for S-0189 is held at the district office and signed out per visit.
The notes for S-0189 mention a disused well inside the compound, capped and recorded but not surveyed.
A housekeeping note against S-0189 asks that the cable run be rewalked before the next dry season.

### S-0190 -- Shale Knap

Shale Knap has been on the register since the first consolidation and its paperwork has never been reconstructed.
A visitor log is kept at Shale Knap and shows 78 entries for the period.
S-0190 appears at revision 4 with a load of 933.
That revision of Shale Knap was lodged 2034-07-15, is settled, and places the station in tier 3.
Shale Knap carries a calibration offset of 11 on the current instrument head.
Weather at Shale Knap closed the approach for 29 days during the period under review and no readings were lost.
Calibration gear for S-0190 travels with the district van and is shared with 18 other sites.
The access key for S-0190 is held at the district office and signed out per visit.
Correspondence about S-0190 is filed under the district rather than under the site, which has caused confusion before.
The site plan for Shale Knap is the ninth revision and supersedes the sketch held in the district folder.

### S-0191 -- Marram Crossing

Maintenance visits to S-0191 are scheduled quarterly and the fourth of those was carried out as planned.
The access key for S-0191 is held at the district office and signed out per visit.
Vegetation around Marram Crossing is cut back twice a year under the standing arrangement.
Weather at Marram Crossing closed the approach for 15 days during the period under review and no readings were lost.
An earlier clerk recorded Marram Crossing under a shortened spelling, and both forms still appear in the older indexes.
Marram Crossing lodged revision 5 on 2034-12-27.
The return for S-0191 is returned, sits at tier 2, and records a load of 524.
Marram Crossing has been on the register since the first consolidation and its paperwork has never been reconstructed.
A visitor log is kept at Marram Crossing and shows 77 entries for the period.
The fence line at Marram Crossing was rerun 35 metres to the east to clear the culvert.

### S-0192 -- Ember Quay

A visitor log is kept at Ember Quay and shows 65 entries for the period.
The access key for S-0192 is held at the district office and signed out per visit.
Two of the anchors at Ember Quay were replaced after the frost and the work is recorded in the district ledger.
Tier 5 is where Ember Quay sits on revision 2, whose status is withdrawn.
The load on that revision of S-0192, lodged 2034-10-15, is 136.
A calibration offset of -17 is recorded for S-0192 against the district standard.
Ember Quay has been on the register since the first consolidation and its paperwork has never been reconstructed.
The approach to Ember Quay crosses 35 field boundaries and the wayleave is held by the county.

### S-0193 -- Linden Moor

A housekeeping note against S-0193 asks that the cable run be rewalked before the next dry season.
The survey party reached Linden Moor on the fourteenth of the month and found the access track passable for light vehicles only.
Calibration gear for S-0193 travels with the district van and is shared with 12 other sites.
The enclosure at Linden Moor was rebuilt in timber after the old fencing was taken by the river.
Linden Moor lodged revision 2 on 2034-12-01.
The return for S-0193 is settled, sits at tier 4, and records a load of 215.
The instrument housing at Linden Moor is the original pattern and its door seal is checked each visit.
Signal strength at Linden Moor has been marginal since the mast on the ridge was lowered.

### S-0194 -- Linden Tarn

The survey party reached Linden Tarn on the twelfth of the month and found the access track passable for light vehicles only.
The instrument housing at Linden Tarn is the original pattern and its door seal is checked each visit.
A visitor log is kept at Linden Tarn and shows 80 entries for the period.
Signal strength at Linden Tarn has been marginal since the mast on the ridge was lowered.
Revision 3 of the return for Linden Tarn was lodged on 2034-12-20 and stands settled.
That revision places S-0194 in tier 1 and gives its load as 242.
Drainage work near Linden Tarn was completed without interruption to the record.
Vegetation around Linden Tarn is cut back twice a year under the standing arrangement.
The notes for S-0194 mention a disused well inside the compound, capped and recorded but not surveyed.
S-0194 was one of the sites brought forward in the consolidation and its numbering reflects that order.

### S-0195 -- Quarry Scarp

Maintenance visits to S-0195 are scheduled quarterly and the second of those was carried out as planned.
Correspondence shows the tenancy at Quarry Scarp was renewed for a further 47 years.
An earlier clerk recorded Quarry Scarp under a shortened spelling, and both forms still appear in the older indexes.
Signal strength at Quarry Scarp has been marginal since the mast on the ridge was lowered.
The instrument housing at Quarry Scarp is the original pattern and its door seal is checked each visit.
Quarry Scarp has been on the register since the first consolidation and its paperwork has never been reconstructed.
The district file for Quarry Scarp shows revision 5 lodged on 2034-03-07.
For S-0195 the status is settled, the tier is 2, and the load is 469.
Correspondence about S-0195 is filed under the district rather than under the site, which has caused confusion before.
Weather at Quarry Scarp closed the approach for 16 days during the period under review and no readings were lost.

### S-0196 -- Chalk Delve

S-0196 was one of the sites brought forward in the consolidation and its numbering reflects that order.
S-0196 appears at revision 6 with a load of 743.
That revision of Chalk Delve was lodged 2034-02-04, is returned, and places the station in tier 7.
The offset applied to readings from S-0196 is -19 and has not been revised.
Correspondence shows the tenancy at Chalk Delve was renewed for a further 17 years.
An earlier clerk recorded Chalk Delve under a shortened spelling, and both forms still appear in the older indexes.
The instrument housing at Chalk Delve is the original pattern and its door seal is checked each visit.
Drainage work near Chalk Delve was completed without interruption to the record.
Two of the anchors at Chalk Delve were replaced after the frost and the work is recorded in the district ledger.
Maintenance visits to S-0196 are scheduled quarterly and the thirteenth of those was carried out as planned.
Correspondence about S-0196 is filed under the district rather than under the site, which has caused confusion before.

### S-0197 -- Hollow Hollow

The approach to Hollow Hollow crosses 6 field boundaries and the wayleave is held by the county.
The district file for Hollow Hollow shows revision 6 lodged on 2034-08-08.
For S-0197 the status is settled, the tier is 4, and the load is 232.
Hollow Hollow carries a calibration offset of 35 on the current instrument head.
The notes for S-0197 mention a disused well inside the compound, capped and recorded but not surveyed.
The fence line at Hollow Hollow was rerun 8 metres to the east to clear the culvert.
The enclosure at Hollow Hollow was rebuilt in timber after the old fencing was taken by the river.
The site plan for Hollow Hollow is the fourteenth revision and supersedes the sketch held in the district folder.
The reading shelter at Hollow Hollow takes water in heavy weather and the floor was relaid.
The instrument housing at Hollow Hollow is the original pattern and its door seal is checked each visit.
Weather at Hollow Hollow closed the approach for 20 days during the period under review and no readings were lost.
S-0197 was one of the sites brought forward in the consolidation and its numbering reflects that order.

### S-0198 -- Dapple Knoll

An earlier clerk recorded Dapple Knoll under a shortened spelling, and both forms still appear in the older indexes.
Dapple Knoll lodged revision 6 on 2034-12-02.
The return for S-0198 is settled, sits at tier 4, and records a load of 686.
A spare sensor head is kept at Dapple Knoll against the failure that took out the district in the previous cycle.
Dapple Knoll shares its power feed with the neighbouring pumping station and has its own cut-out.
The instrument housing at Dapple Knoll is the original pattern and its door seal is checked each visit.
The fence line at Dapple Knoll was rerun 29 metres to the east to clear the culvert.
The survey party reached Dapple Knoll on the fourth of the month and found the access track passable for light vehicles only.
Correspondence shows the tenancy at Dapple Knoll was renewed for a further 45 years.
Vegetation around Dapple Knoll is cut back twice a year under the standing arrangement.
S-0198 was one of the sites brought forward in the consolidation and its numbering reflects that order.

### S-0199 -- Dusk Terrace

S-0199 was one of the sites brought forward in the consolidation and its numbering reflects that order.
A visitor log is kept at Dusk Terrace and shows 24 entries for the period.
On 2034-07-11 the district accepted revision 3 for Dusk Terrace and marked it provisional.
S-0199 carries tier 8 on that revision and a load of 492.
A calibration offset of -6 is recorded for S-0199 against the district standard.
A housekeeping note against S-0199 asks that the cable run be rewalked before the next dry season.
The site plan for Dusk Terrace is the twelfth revision and supersedes the sketch held in the district folder.

### S-0200 -- Garnet Ferry

A housekeeping note against S-0200 asks that the cable run be rewalked before the next dry season.
Two of the anchors at Garnet Ferry were replaced after the frost and the work is recorded in the district ledger.
S-0200 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The enclosure at Garnet Ferry was rebuilt in timber after the old fencing was taken by the river.
The fence line at Garnet Ferry was rerun 19 metres to the east to clear the culvert.
Correspondence shows the tenancy at Garnet Ferry was renewed for a further 80 years.
A spare sensor head is kept at Garnet Ferry against the failure that took out the district in the previous cycle.
The survey party reached Garnet Ferry on the eighth of the month and found the access track passable for light vehicles only.
Telemetry from S-0200 arrives on the thirteenth relay and is batched nightly rather than streamed.
The load recorded for S-0200 is 981, on a return at tier 4.
That return for Garnet Ferry is revision 6, lodged 2034-02-20, and its status is open.
The reading shelter at Garnet Ferry takes water in heavy weather and the floor was relaid.

### S-0201 -- Lichen Ripple

Telemetry from S-0201 arrives on the eighth relay and is batched nightly rather than streamed.
The access key for S-0201 is held at the district office and signed out per visit.
The site plan for Lichen Ripple is the fourth revision and supersedes the sketch held in the district folder.
The notes for S-0201 mention a disused well inside the compound, capped and recorded but not surveyed.
Two of the anchors at Lichen Ripple were replaced after the frost and the work is recorded in the district ledger.
The survey party reached Lichen Ripple on the twelfth of the month and found the access track passable for light vehicles only.
Tier 3 is where Lichen Ripple sits on revision 6, whose status is open.
The load on that revision of S-0201, lodged 2034-02-14, is 688.
Maintenance visits to S-0201 are scheduled quarterly and the fourth of those was carried out as planned.
An earlier clerk recorded Lichen Ripple under a shortened spelling, and both forms still appear in the older indexes.
Correspondence about S-0201 is filed under the district rather than under the site, which has caused confusion before.

### S-0202 -- Russet Dingle

Correspondence about S-0202 is filed under the district rather than under the site, which has caused confusion before.
Vegetation around Russet Dingle is cut back twice a year under the standing arrangement.
The instrument housing at Russet Dingle is the original pattern and its door seal is checked each visit.
An earlier clerk recorded Russet Dingle under a shortened spelling, and both forms still appear in the older indexes.
On 2034-11-18 the district accepted revision 4 for Russet Dingle and marked it open.
S-0202 carries tier 1 on that revision and a load of 118.
A housekeeping note against S-0202 asks that the cable run be rewalked before the next dry season.
The approach to Russet Dingle crosses 33 field boundaries and the wayleave is held by the county.
The survey party reached Russet Dingle on the eighth of the month and found the access track passable for light vehicles only.
The reading shelter at Russet Dingle takes water in heavy weather and the floor was relaid.
Two of the anchors at Russet Dingle were replaced after the frost and the work is recorded in the district ledger.

### S-0203 -- Nettle Tarn

The access key for S-0203 is held at the district office and signed out per visit.
An earlier clerk recorded Nettle Tarn under a shortened spelling, and both forms still appear in the older indexes.
Tier 1 is where Nettle Tarn sits on revision 1, whose status is settled.
The load on that revision of S-0203, lodged 2034-03-28, is 387.
S-0203 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The instrument housing at Nettle Tarn is the original pattern and its door seal is checked each visit.
The logbook kept at Nettle Tarn runs to 14 pages and the earlier volumes are held off site.
The enclosure at Nettle Tarn was rebuilt in timber after the old fencing was taken by the river.
The fence line at Nettle Tarn was rerun 14 metres to the east to clear the culvert.
Two of the anchors at Nettle Tarn were replaced after the frost and the work is recorded in the district ledger.

### S-0204 -- Copper Moor

The fence line at Copper Moor was rerun 18 metres to the east to clear the culvert.
The site plan for Copper Moor is the seventh revision and supersedes the sketch held in the district folder.
Calibration gear for S-0204 travels with the district van and is shared with 16 other sites.
The reading shelter at Copper Moor takes water in heavy weather and the floor was relaid.
Revision 3 of the return for Copper Moor was lodged on 2034-07-07 and stands provisional.
That revision places S-0204 in tier 6 and gives its load as 530.
Copper Moor has been on the register since the first consolidation and its paperwork has never been reconstructed.
Correspondence about S-0204 is filed under the district rather than under the site, which has caused confusion before.

### S-0205 -- Shale Reach

Shale Reach has been on the register since the first consolidation and its paperwork has never been reconstructed.
The district file for Shale Reach shows revision 6 lodged on 2034-09-04.
For S-0205 the status is provisional, the tier is 5, and the load is 203.
The approach to Shale Reach crosses 38 field boundaries and the wayleave is held by the county.
The reading shelter at Shale Reach takes water in heavy weather and the floor was relaid.
The access key for S-0205 is held at the district office and signed out per visit.

### S-0206 -- Tamarisk Spur

A housekeeping note against S-0206 asks that the cable run be rewalked before the next dry season.
Status settled: revision 5 for S-0206, lodged 2034-08-18.
Load 851 at tier 3 is what that revision carries for Tamarisk Spur.
Tamarisk Spur carries a calibration offset of 7 on the current instrument head.
Correspondence shows the tenancy at Tamarisk Spur was renewed for a further 29 years.
Two of the anchors at Tamarisk Spur were replaced after the frost and the work is recorded in the district ledger.
S-0206 was one of the sites brought forward in the consolidation and its numbering reflects that order.

### S-0207 -- Spindle Delve

A visitor log is kept at Spindle Delve and shows 58 entries for the period.
Tier 4 is where Spindle Delve sits on revision 4, whose status is open.
The load on that revision of S-0207, lodged 2034-12-09, is 921.
Spindle Delve shares its power feed with the neighbouring pumping station and has its own cut-out.
Weather at Spindle Delve closed the approach for 10 days during the period under review and no readings were lost.
Correspondence shows the tenancy at Spindle Delve was renewed for a further 44 years.

### S-0208 -- Granite Quay

Telemetry from S-0208 arrives on the twelfth relay and is batched nightly rather than streamed.
The survey party reached Granite Quay on the fourteenth of the month and found the access track passable for light vehicles only.
Revision 1 of the return for Granite Quay was lodged on 2034-12-02 and stands settled.
That revision places S-0208 in tier 3 and gives its load as 345.
Two of the anchors at Granite Quay were replaced after the frost and the work is recorded in the district ledger.
The access key for S-0208 is held at the district office and signed out per visit.
A visitor log is kept at Granite Quay and shows 36 entries for the period.
Granite Quay has been on the register since the first consolidation and its paperwork has never been reconstructed.
A spare sensor head is kept at Granite Quay against the failure that took out the district in the previous cycle.
Maintenance visits to S-0208 are scheduled quarterly and the third of those was carried out as planned.
A housekeeping note against S-0208 asks that the cable run be rewalked before the next dry season.
The instrument housing at Granite Quay is the original pattern and its door seal is checked each visit.

### S-0209 -- Tamarisk Brae

The access key for S-0209 is held at the district office and signed out per visit.
The district file for Tamarisk Brae shows revision 1 lodged on 2034-05-19.
For S-0209 the status is settled, the tier is 1, and the load is 560.
Calibration gear for S-0209 travels with the district van and is shared with 12 other sites.
The reading shelter at Tamarisk Brae takes water in heavy weather and the floor was relaid.
Two of the anchors at Tamarisk Brae were replaced after the frost and the work is recorded in the district ledger.
S-0209 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The instrument housing at Tamarisk Brae is the original pattern and its door seal is checked each visit.
The fence line at Tamarisk Brae was rerun 37 metres to the east to clear the culvert.
The enclosure at Tamarisk Brae was rebuilt in timber after the old fencing was taken by the river.
Correspondence about S-0209 is filed under the district rather than under the site, which has caused confusion before.

### S-0210 -- Nettle Mere

Nettle Mere shares its power feed with the neighbouring pumping station and has its own cut-out.
S-0210 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Signal strength at Nettle Mere has been marginal since the mast on the ridge was lowered.
Nettle Mere lodged revision 5 on 2034-08-05.
The return for S-0210 is settled, sits at tier 1, and records a load of 528.
The enclosure at Nettle Mere was rebuilt in timber after the old fencing was taken by the river.
The approach to Nettle Mere crosses 22 field boundaries and the wayleave is held by the county.
Access to Nettle Mere is by the service road from the south; the gate code was reissued after the fourth inspection.
The access key for S-0210 is held at the district office and signed out per visit.
The fence line at Nettle Mere was rerun 3 metres to the east to clear the culvert.

### S-0211 -- Marram Basin

A housekeeping note against S-0211 asks that the cable run be rewalked before the next dry season.
The site plan for Marram Basin is the eleventh revision and supersedes the sketch held in the district folder.
The logbook kept at Marram Basin runs to 52 pages and the earlier volumes are held off site.
The fence line at Marram Basin was rerun 35 metres to the east to clear the culvert.
Revision 4 of the return for Marram Basin was lodged on 2034-12-01 and stands settled.
That revision places S-0211 in tier 3 and gives its load as 190.
S-0211 was one of the sites brought forward in the consolidation and its numbering reflects that order.

### S-0212 -- Osier Weir

An earlier clerk recorded Osier Weir under a shortened spelling, and both forms still appear in the older indexes.
Tier 3 is where Osier Weir sits on revision 4, whose status is settled.
The load on that revision of S-0212, lodged 2034-06-12, is 487.
Access to Osier Weir is by the service road from the south; the gate code was reissued after the third inspection.
The survey party reached Osier Weir on the tenth of the month and found the access track passable for light vehicles only.
The reading shelter at Osier Weir takes water in heavy weather and the floor was relaid.
Correspondence shows the tenancy at Osier Weir was renewed for a further 63 years.

### S-0213 -- Linden Staithe

Weather at Linden Staithe closed the approach for 15 days during the period under review and no readings were lost.
Maintenance visits to S-0213 are scheduled quarterly and the ninth of those was carried out as planned.
The access key for S-0213 is held at the district office and signed out per visit.
The load recorded for S-0213 is 169, on a return at tier 2.
That return for Linden Staithe is revision 4, lodged 2034-01-15, and its status is settled.
Access to Linden Staithe is by the service road from the south; the gate code was reissued after the sixth inspection.
The logbook kept at Linden Staithe runs to 8 pages and the earlier volumes are held off site.
Telemetry from S-0213 arrives on the eleventh relay and is batched nightly rather than streamed.
A visitor log is kept at Linden Staithe and shows 36 entries for the period.
The notes for S-0213 mention a disused well inside the compound, capped and recorded but not surveyed.

### S-0214 -- Meadow Mere

A spare sensor head is kept at Meadow Mere against the failure that took out the district in the previous cycle.
The notes for S-0214 mention a disused well inside the compound, capped and recorded but not surveyed.
Correspondence shows the tenancy at Meadow Mere was renewed for a further 57 years.
The site plan for Meadow Mere is the fourteenth revision and supersedes the sketch held in the district folder.
An earlier clerk recorded Meadow Mere under a shortened spelling, and both forms still appear in the older indexes.
Meadow Mere has been on the register since the first consolidation and its paperwork has never been reconstructed.
Tier 4 is where Meadow Mere sits on revision 4, whose status is returned.
The load on that revision of S-0214, lodged 2034-01-02, is 740.
Correspondence about S-0214 is filed under the district rather than under the site, which has caused confusion before.
The logbook kept at Meadow Mere runs to 8 pages and the earlier volumes are held off site.

### S-0215 -- Clover Shaw

The reading shelter at Clover Shaw takes water in heavy weather and the floor was relaid.
Access to Clover Shaw is by the service road from the south; the gate code was reissued after the first inspection.
An earlier clerk recorded Clover Shaw under a shortened spelling, and both forms still appear in the older indexes.
S-0215 was one of the sites brought forward in the consolidation and its numbering reflects that order.
S-0215 appears at revision 6 with a load of 365.
That revision of Clover Shaw was lodged 2034-04-27, is open, and places the station in tier 2.
The notes for S-0215 mention a disused well inside the compound, capped and recorded but not surveyed.
Vegetation around Clover Shaw is cut back twice a year under the standing arrangement.

### S-0216 -- Yarrow Hollow

Vegetation around Yarrow Hollow is cut back twice a year under the standing arrangement.
The enclosure at Yarrow Hollow was rebuilt in timber after the old fencing was taken by the river.
The survey party reached Yarrow Hollow on the third of the month and found the access track passable for light vehicles only.
A spare sensor head is kept at Yarrow Hollow against the failure that took out the district in the previous cycle.
The load recorded for S-0216 is 753, on a return at tier 2.
That return for Yarrow Hollow is revision 1, lodged 2034-02-09, and its status is settled.
The offset applied to readings from S-0216 is -39 and has not been revised.
Two of the anchors at Yarrow Hollow were replaced after the frost and the work is recorded in the district ledger.
A visitor log is kept at Yarrow Hollow and shows 46 entries for the period.

### S-0217 -- Shale Sand

The logbook kept at Shale Sand runs to 86 pages and the earlier volumes are held off site.
An earlier clerk recorded Shale Sand under a shortened spelling, and both forms still appear in the older indexes.
Maintenance visits to S-0217 are scheduled quarterly and the fifth of those was carried out as planned.
Calibration gear for S-0217 travels with the district van and is shared with 14 other sites.
The site plan for Shale Sand is the first revision and supersedes the sketch held in the district folder.
The district file for Shale Sand shows revision 5 lodged on 2034-10-18.
For S-0217 the status is withdrawn, the tier is 2, and the load is 378.
A calibration offset of 21 is recorded for S-0217 against the district standard.
The approach to Shale Sand crosses 31 field boundaries and the wayleave is held by the county.
Vegetation around Shale Sand is cut back twice a year under the standing arrangement.

### S-0218 -- Fennel Reach

Weather at Fennel Reach closed the approach for 18 days during the period under review and no readings were lost.
An earlier clerk recorded Fennel Reach under a shortened spelling, and both forms still appear in the older indexes.
The reading shelter at Fennel Reach takes water in heavy weather and the floor was relaid.
Status settled: revision 6 for S-0218, lodged 2034-12-23.
Load 992 at tier 4 is what that revision carries for Fennel Reach.
Fennel Reach carries a calibration offset of -12 on the current instrument head.
Fennel Reach shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0219 -- Willow Scarp

Maintenance visits to S-0219 are scheduled quarterly and the fourth of those was carried out as planned.
Calibration gear for S-0219 travels with the district van and is shared with 29 other sites.
The site plan for Willow Scarp is the fifth revision and supersedes the sketch held in the district folder.
Correspondence about S-0219 is filed under the district rather than under the site, which has caused confusion before.
Drainage work near Willow Scarp was completed without interruption to the record.
Vegetation around Willow Scarp is cut back twice a year under the standing arrangement.
Willow Scarp lodged revision 2 on 2034-11-04.
The return for S-0219 is settled, sits at tier 2, and records a load of 476.
The fence line at Willow Scarp was rerun 3 metres to the east to clear the culvert.
The notes for S-0219 mention a disused well inside the compound, capped and recorded but not surveyed.
S-0219 was one of the sites brought forward in the consolidation and its numbering reflects that order.

### S-0220 -- Sable Copse

The enclosure at Sable Copse was rebuilt in timber after the old fencing was taken by the river.
Access to Sable Copse is by the service road from the south; the gate code was reissued after the fifth inspection.
Sable Copse shares its power feed with the neighbouring pumping station and has its own cut-out.
Two of the anchors at Sable Copse were replaced after the frost and the work is recorded in the district ledger.
The district file for Sable Copse shows revision 6 lodged on 2034-10-02.
For S-0220 the status is settled, the tier is 2, and the load is 990.
An earlier clerk recorded Sable Copse under a shortened spelling, and both forms still appear in the older indexes.
Telemetry from S-0220 arrives on the seventh relay and is batched nightly rather than streamed.
The access key for S-0220 is held at the district office and signed out per visit.

### S-0221 -- Thistle Coomb

Thistle Coomb shares its power feed with the neighbouring pumping station and has its own cut-out.
Correspondence shows the tenancy at Thistle Coomb was renewed for a further 31 years.
Tier 2 is where Thistle Coomb sits on revision 6, whose status is open.
The load on that revision of S-0221, lodged 2034-10-13, is 942.
The site plan for Thistle Coomb is the second revision and supersedes the sketch held in the district folder.
The enclosure at Thistle Coomb was rebuilt in timber after the old fencing was taken by the river.

### S-0222 -- Hazel Ledge

The enclosure at Hazel Ledge was rebuilt in timber after the old fencing was taken by the river.
The survey party reached Hazel Ledge on the fifth of the month and found the access track passable for light vehicles only.
Maintenance visits to S-0222 are scheduled quarterly and the second of those was carried out as planned.
Revision 4 of the return for Hazel Ledge was lodged on 2034-04-21 and stands returned.
That revision places S-0222 in tier 5 and gives its load as 425.
The reading shelter at Hazel Ledge takes water in heavy weather and the floor was relaid.
The approach to Hazel Ledge crosses 11 field boundaries and the wayleave is held by the county.

### S-0223 -- Pewter Brae

The notes for S-0223 mention a disused well inside the compound, capped and recorded but not surveyed.
The district file for Pewter Brae shows revision 6 lodged on 2034-06-20.
For S-0223 the status is settled, the tier is 2, and the load is 616.
Pewter Brae carries a calibration offset of -6 on the current instrument head.
Access to Pewter Brae is by the service road from the south; the gate code was reissued after the thirteenth inspection.
A housekeeping note against S-0223 asks that the cable run be rewalked before the next dry season.
Vegetation around Pewter Brae is cut back twice a year under the standing arrangement.
Pewter Brae has been on the register since the first consolidation and its paperwork has never been reconstructed.
Drainage work near Pewter Brae was completed without interruption to the record.
The enclosure at Pewter Brae was rebuilt in timber after the old fencing was taken by the river.
The instrument housing at Pewter Brae is the original pattern and its door seal is checked each visit.

### S-0224 -- Meadow Knap

Signal strength at Meadow Knap has been marginal since the mast on the ridge was lowered.
A spare sensor head is kept at Meadow Knap against the failure that took out the district in the previous cycle.
Weather at Meadow Knap closed the approach for 18 days during the period under review and no readings were lost.
Status settled: revision 5 for S-0224, lodged 2034-10-23.
Load 798 at tier 3 is what that revision carries for Meadow Knap.
A calibration offset of -32 is recorded for S-0224 against the district standard.
Meadow Knap shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0225 -- Ochre Vale

Calibration gear for S-0225 travels with the district van and is shared with 8 other sites.
Correspondence about S-0225 is filed under the district rather than under the site, which has caused confusion before.
On 2034-04-05 the district accepted revision 3 for Ochre Vale and marked it settled.
S-0225 carries tier 9 on that revision and a load of 549.
The reconciliation sequence mark carried by this revision of S-0225 is 4.
The fence line at Ochre Vale was rerun 3 metres to the east to clear the culvert.
Vegetation around Ochre Vale is cut back twice a year under the standing arrangement.
The approach to Ochre Vale crosses 32 field boundaries and the wayleave is held by the county.
A visitor log is kept at Ochre Vale and shows 20 entries for the period.
The survey party reached Ochre Vale on the twelfth of the month and found the access track passable for light vehicles only.
The instrument housing at Ochre Vale is the original pattern and its door seal is checked each visit.
Weather at Ochre Vale closed the approach for 19 days during the period under review and no readings were lost.

### S-0226 -- Tamarisk Slade

Maintenance visits to S-0226 are scheduled quarterly and the fifth of those was carried out as planned.
An earlier clerk recorded Tamarisk Slade under a shortened spelling, and both forms still appear in the older indexes.
The enclosure at Tamarisk Slade was rebuilt in timber after the old fencing was taken by the river.
The district file for Tamarisk Slade shows revision 2 lodged on 2034-10-25.
For S-0226 the status is settled, the tier is 1, and the load is 507.
Signal strength at Tamarisk Slade has been marginal since the mast on the ridge was lowered.
Tamarisk Slade shares its power feed with the neighbouring pumping station and has its own cut-out.
Vegetation around Tamarisk Slade is cut back twice a year under the standing arrangement.
The reading shelter at Tamarisk Slade takes water in heavy weather and the floor was relaid.
Correspondence shows the tenancy at Tamarisk Slade was renewed for a further 12 years.

### S-0227 -- Willow Dingle

The logbook kept at Willow Dingle runs to 50 pages and the earlier volumes are held off site.
S-0227 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The site plan for Willow Dingle is the sixth revision and supersedes the sketch held in the district folder.
The district file for Willow Dingle shows revision 5 lodged on 2034-10-21.
For S-0227 the status is open, the tier is 6, and the load is 851.
The return for Willow Dingle replaces an entry formerly held at S-0990, a code retired at the consolidation and never reissued.
A visitor log is kept at Willow Dingle and shows 36 entries for the period.
Willow Dingle shares its power feed with the neighbouring pumping station and has its own cut-out.
The fence line at Willow Dingle was rerun 19 metres to the east to clear the culvert.
Weather at Willow Dingle closed the approach for 18 days during the period under review and no readings were lost.
Signal strength at Willow Dingle has been marginal since the mast on the ridge was lowered.
The enclosure at Willow Dingle was rebuilt in timber after the old fencing was taken by the river.

### S-0228 -- Willow Basin

Vegetation around Willow Basin is cut back twice a year under the standing arrangement.
The approach to Willow Basin crosses 27 field boundaries and the wayleave is held by the county.
Signal strength at Willow Basin has been marginal since the mast on the ridge was lowered.
Status settled: revision 6 for S-0228, lodged 2034-07-11.
Load 819 at tier 8 is what that revision carries for Willow Basin.
The offset applied to readings from S-0228 is -14 and has not been revised.
The enclosure at Willow Basin was rebuilt in timber after the old fencing was taken by the river.
The survey party reached Willow Basin on the first of the month and found the access track passable for light vehicles only.
The logbook kept at Willow Basin runs to 44 pages and the earlier volumes are held off site.
The instrument housing at Willow Basin is the original pattern and its door seal is checked each visit.

### S-0229 -- Fallow Knoll

The enclosure at Fallow Knoll was rebuilt in timber after the old fencing was taken by the river.
The site plan for Fallow Knoll is the seventh revision and supersedes the sketch held in the district folder.
The approach to Fallow Knoll crosses 8 field boundaries and the wayleave is held by the county.
The instrument housing at Fallow Knoll is the original pattern and its door seal is checked each visit.
The load recorded for S-0229 is 523, on a return at tier 2.
That return for Fallow Knoll is revision 1, lodged 2034-11-05, and its status is withdrawn.
Drainage work near Fallow Knoll was completed without interruption to the record.
An earlier clerk recorded Fallow Knoll under a shortened spelling, and both forms still appear in the older indexes.

### S-0230 -- Copper Bourne

An earlier clerk recorded Copper Bourne under a shortened spelling, and both forms still appear in the older indexes.
Copper Bourne shares its power feed with the neighbouring pumping station and has its own cut-out.
Signal strength at Copper Bourne has been marginal since the mast on the ridge was lowered.
S-0230 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The enclosure at Copper Bourne was rebuilt in timber after the old fencing was taken by the river.
Weather at Copper Bourne closed the approach for 2 days during the period under review and no readings were lost.
Access to Copper Bourne is by the service road from the south; the gate code was reissued after the sixth inspection.
The load recorded for S-0230 is 652, on a return at tier 1.
That return for Copper Bourne is revision 5, lodged 2034-02-08, and its status is settled.
Maintenance visits to S-0230 are scheduled quarterly and the eighth of those was carried out as planned.
The survey party reached Copper Bourne on the eighth of the month and found the access track passable for light vehicles only.
The fence line at Copper Bourne was rerun 29 metres to the east to clear the culvert.

### S-0231 -- Ochre Coomb

A visitor log is kept at Ochre Coomb and shows 22 entries for the period.
Vegetation around Ochre Coomb is cut back twice a year under the standing arrangement.
Drainage work near Ochre Coomb was completed without interruption to the record.
A housekeeping note against S-0231 asks that the cable run be rewalked before the next dry season.
Status settled: revision 5 for S-0231, lodged 2034-03-08.
Load 988 at tier 5 is what that revision carries for Ochre Coomb.
S-0231 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Two of the anchors at Ochre Coomb were replaced after the frost and the work is recorded in the district ledger.
The instrument housing at Ochre Coomb is the original pattern and its door seal is checked each visit.

### S-0232 -- Nettle Bourne

Weather at Nettle Bourne closed the approach for 12 days during the period under review and no readings were lost.
Maintenance visits to S-0232 are scheduled quarterly and the third of those was carried out as planned.
S-0232 appears at revision 6 with a load of 434.
That revision of Nettle Bourne was lodged 2034-05-06, is settled, and places the station in tier 2.
Signal strength at Nettle Bourne has been marginal since the mast on the ridge was lowered.
Nettle Bourne shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0233 -- Teasel Ferry

Correspondence shows the tenancy at Teasel Ferry was renewed for a further 86 years.
Teasel Ferry has been on the register since the first consolidation and its paperwork has never been reconstructed.
S-0233 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The survey party reached Teasel Ferry on the thirteenth of the month and found the access track passable for light vehicles only.
On 2034-03-18 the district accepted revision 4 for Teasel Ferry and marked it open.
S-0233 carries tier 8 on that revision and a load of 194.
The logbook kept at Teasel Ferry runs to 23 pages and the earlier volumes are held off site.
The access key for S-0233 is held at the district office and signed out per visit.
Access to Teasel Ferry is by the service road from the south; the gate code was reissued after the eleventh inspection.
Two of the anchors at Teasel Ferry were replaced after the frost and the work is recorded in the district ledger.

### S-0234 -- Ochre Ripple

The access key for S-0234 is held at the district office and signed out per visit.
Ochre Ripple lodged revision 6 on 2034-12-07.
The return for S-0234 is provisional, sits at tier 7, and records a load of 402.
Two of the anchors at Ochre Ripple were replaced after the frost and the work is recorded in the district ledger.
The reading shelter at Ochre Ripple takes water in heavy weather and the floor was relaid.
Calibration gear for S-0234 travels with the district van and is shared with 23 other sites.
Drainage work near Ochre Ripple was completed without interruption to the record.
The notes for S-0234 mention a disused well inside the compound, capped and recorded but not surveyed.
A visitor log is kept at Ochre Ripple and shows 28 entries for the period.
Ochre Ripple shares its power feed with the neighbouring pumping station and has its own cut-out.
The enclosure at Ochre Ripple was rebuilt in timber after the old fencing was taken by the river.
Maintenance visits to S-0234 are scheduled quarterly and the first of those was carried out as planned.

### S-0235 -- Heather Tarn

The reading shelter at Heather Tarn takes water in heavy weather and the floor was relaid.
The survey party reached Heather Tarn on the fourteenth of the month and found the access track passable for light vehicles only.
The load recorded for S-0235 is 510, on a return at tier 2.
That return for Heather Tarn is revision 2, lodged 2034-12-07, and its status is settled.
A spare sensor head is kept at Heather Tarn against the failure that took out the district in the previous cycle.
Drainage work near Heather Tarn was completed without interruption to the record.
The logbook kept at Heather Tarn runs to 63 pages and the earlier volumes are held off site.

### S-0236 -- Flint Ledge

The fence line at Flint Ledge was rerun 10 metres to the east to clear the culvert.
The load recorded for S-0236 is 490, on a return at tier 3.
That return for Flint Ledge is revision 2, lodged 2034-11-01, and its status is provisional.
Vegetation around Flint Ledge is cut back twice a year under the standing arrangement.
The notes for S-0236 mention a disused well inside the compound, capped and recorded but not surveyed.
The access key for S-0236 is held at the district office and signed out per visit.
Access to Flint Ledge is by the service road from the south; the gate code was reissued after the eighth inspection.
The reading shelter at Flint Ledge takes water in heavy weather and the floor was relaid.
Drainage work near Flint Ledge was completed without interruption to the record.

### S-0237 -- Amber Bight

An earlier clerk recorded Amber Bight under a shortened spelling, and both forms still appear in the older indexes.
Two of the anchors at Amber Bight were replaced after the frost and the work is recorded in the district ledger.
Amber Bight shares its power feed with the neighbouring pumping station and has its own cut-out.
The reading shelter at Amber Bight takes water in heavy weather and the floor was relaid.
On 2034-06-22 the district accepted revision 4 for Amber Bight and marked it returned.
S-0237 carries tier 7 on that revision and a load of 273.
Access to Amber Bight is by the service road from the south; the gate code was reissued after the twelfth inspection.
Drainage work near Amber Bight was completed without interruption to the record.
Maintenance visits to S-0237 are scheduled quarterly and the tenth of those was carried out as planned.

### S-0238 -- Sable Ford

An earlier clerk recorded Sable Ford under a shortened spelling, and both forms still appear in the older indexes.
The approach to Sable Ford crosses 23 field boundaries and the wayleave is held by the county.
Maintenance visits to S-0238 are scheduled quarterly and the first of those was carried out as planned.
A housekeeping note against S-0238 asks that the cable run be rewalked before the next dry season.
Sable Ford lodged revision 6 on 2034-09-27.
The return for S-0238 is withdrawn, sits at tier 3, and records a load of 670.
Correspondence shows the tenancy at Sable Ford was renewed for a further 44 years.
Signal strength at Sable Ford has been marginal since the mast on the ridge was lowered.
Vegetation around Sable Ford is cut back twice a year under the standing arrangement.
S-0238 was one of the sites brought forward in the consolidation and its numbering reflects that order.
A spare sensor head is kept at Sable Ford against the failure that took out the district in the previous cycle.

### S-0239 -- Lichen Ferry

Telemetry from S-0239 arrives on the twelfth relay and is batched nightly rather than streamed.
A spare sensor head is kept at Lichen Ferry against the failure that took out the district in the previous cycle.
Maintenance visits to S-0239 are scheduled quarterly and the first of those was carried out as planned.
Tier 1 is where Lichen Ferry sits on revision 5, whose status is settled.
The load on that revision of S-0239, lodged 2034-05-05, is 865.
A calibration offset of -31 is recorded for S-0239 against the district standard.
Correspondence shows the tenancy at Lichen Ferry was renewed for a further 52 years.
Calibration gear for S-0239 travels with the district van and is shared with 29 other sites.
Two of the anchors at Lichen Ferry were replaced after the frost and the work is recorded in the district ledger.

### S-0240 -- Copper Slade

The survey party reached Copper Slade on the first of the month and found the access track passable for light vehicles only.
S-0240 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Access to Copper Slade is by the service road from the south; the gate code was reissued after the fifth inspection.
The approach to Copper Slade crosses 39 field boundaries and the wayleave is held by the county.
Correspondence shows the tenancy at Copper Slade was renewed for a further 51 years.
Telemetry from S-0240 arrives on the fourth relay and is batched nightly rather than streamed.
Signal strength at Copper Slade has been marginal since the mast on the ridge was lowered.
The district file for Copper Slade shows revision 3 lodged on 2034-03-10.
For S-0240 the status is settled, the tier is 1, and the load is 854.
Calibration gear for S-0240 travels with the district van and is shared with 4 other sites.

### S-0241 -- Fennel Down

An earlier clerk recorded Fennel Down under a shortened spelling, and both forms still appear in the older indexes.
A housekeeping note against S-0241 asks that the cable run be rewalked before the next dry season.
A visitor log is kept at Fennel Down and shows 37 entries for the period.
Tier 3 is where Fennel Down sits on revision 4, whose status is settled.
The load on that revision of S-0241, lodged 2034-10-08, is 503.
The offset applied to readings from S-0241 is -37 and has not been revised.
Correspondence about S-0241 is filed under the district rather than under the site, which has caused confusion before.
Two of the anchors at Fennel Down were replaced after the frost and the work is recorded in the district ledger.
Correspondence shows the tenancy at Fennel Down was renewed for a further 32 years.

### S-0242 -- Russet Terrace

The site plan for Russet Terrace is the eleventh revision and supersedes the sketch held in the district folder.
The notes for S-0242 mention a disused well inside the compound, capped and recorded but not surveyed.
Tier 1 is where Russet Terrace sits on revision 3, whose status is returned.
The load on that revision of S-0242, lodged 2034-03-16, is 409.
A calibration offset of -2 is recorded for S-0242 against the district standard.
Access to Russet Terrace is by the service road from the south; the gate code was reissued after the eighth inspection.
The approach to Russet Terrace crosses 8 field boundaries and the wayleave is held by the county.
Weather at Russet Terrace closed the approach for 23 days during the period under review and no readings were lost.
A visitor log is kept at Russet Terrace and shows 48 entries for the period.
Correspondence shows the tenancy at Russet Terrace was renewed for a further 19 years.

### S-0243 -- Verdigris Fell

Telemetry from S-0243 arrives on the sixth relay and is batched nightly rather than streamed.
The fence line at Verdigris Fell was rerun 32 metres to the east to clear the culvert.
The district file for Verdigris Fell shows revision 3 lodged on 2034-03-15.
For S-0243 the status is settled, the tier is 2, and the load is 539.
Access to Verdigris Fell is by the service road from the south; the gate code was reissued after the eighth inspection.
The site plan for Verdigris Fell is the third revision and supersedes the sketch held in the district folder.
Vegetation around Verdigris Fell is cut back twice a year under the standing arrangement.

### S-0244 -- Verdigris Anchorage

Correspondence shows the tenancy at Verdigris Anchorage was renewed for a further 77 years.
Verdigris Anchorage has been on the register since the first consolidation and its paperwork has never been reconstructed.
Vegetation around Verdigris Anchorage is cut back twice a year under the standing arrangement.
S-0244 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Status open: revision 6 for S-0244, lodged 2034-10-09.
Load 871 at tier 9 is what that revision carries for Verdigris Anchorage.
The access key for S-0244 is held at the district office and signed out per visit.
The notes for S-0244 mention a disused well inside the compound, capped and recorded but not surveyed.
The enclosure at Verdigris Anchorage was rebuilt in timber after the old fencing was taken by the river.
Telemetry from S-0244 arrives on the eighth relay and is batched nightly rather than streamed.
Two of the anchors at Verdigris Anchorage were replaced after the frost and the work is recorded in the district ledger.
Signal strength at Verdigris Anchorage has been marginal since the mast on the ridge was lowered.

### S-0245 -- Granite Pasture

Correspondence shows the tenancy at Granite Pasture was renewed for a further 80 years.
Maintenance visits to S-0245 are scheduled quarterly and the second of those was carried out as planned.
S-0245 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Access to Granite Pasture is by the service road from the south; the gate code was reissued after the ninth inspection.
Calibration gear for S-0245 travels with the district van and is shared with 33 other sites.
The district file for Granite Pasture shows revision 2 lodged on 2034-08-12.
For S-0245 the status is returned, the tier is 6, and the load is 517.
The reading shelter at Granite Pasture takes water in heavy weather and the floor was relaid.
A spare sensor head is kept at Granite Pasture against the failure that took out the district in the previous cycle.

### S-0246 -- Sedge Scarp

Telemetry from S-0246 arrives on the fourth relay and is batched nightly rather than streamed.
Sedge Scarp lodged revision 1 on 2034-01-21.
The return for S-0246 is settled, sits at tier 1, and records a load of 769.
The instrument housing at Sedge Scarp is the original pattern and its door seal is checked each visit.
Correspondence shows the tenancy at Sedge Scarp was renewed for a further 63 years.
The notes for S-0246 mention a disused well inside the compound, capped and recorded but not surveyed.
A visitor log is kept at Sedge Scarp and shows 59 entries for the period.
Access to Sedge Scarp is by the service road from the south; the gate code was reissued after the thirteenth inspection.
A spare sensor head is kept at Sedge Scarp against the failure that took out the district in the previous cycle.

### S-0247 -- Pewter Brook

The reading shelter at Pewter Brook takes water in heavy weather and the floor was relaid.
Signal strength at Pewter Brook has been marginal since the mast on the ridge was lowered.
A visitor log is kept at Pewter Brook and shows 8 entries for the period.
Tier 1 is where Pewter Brook sits on revision 1, whose status is withdrawn.
The load on that revision of S-0247, lodged 2034-11-03, is 458.
Access to Pewter Brook is by the service road from the south; the gate code was reissued after the eighth inspection.

### S-0248 -- Fennel Vale

The survey party reached Fennel Vale on the eighth of the month and found the access track passable for light vehicles only.
Correspondence about S-0248 is filed under the district rather than under the site, which has caused confusion before.
An earlier clerk recorded Fennel Vale under a shortened spelling, and both forms still appear in the older indexes.
Fennel Vale has been on the register since the first consolidation and its paperwork has never been reconstructed.
Maintenance visits to S-0248 are scheduled quarterly and the tenth of those was carried out as planned.
The load recorded for S-0248 is 487, on a return at tier 3.
That return for Fennel Vale is revision 5, lodged 2034-01-25, and its status is settled.
A spare sensor head is kept at Fennel Vale against the failure that took out the district in the previous cycle.
The approach to Fennel Vale crosses 32 field boundaries and the wayleave is held by the county.

### S-0249 -- Calder Spur

The fence line at Calder Spur was rerun 40 metres to the east to clear the culvert.
An earlier clerk recorded Calder Spur under a shortened spelling, and both forms still appear in the older indexes.
S-0249 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Maintenance visits to S-0249 are scheduled quarterly and the second of those was carried out as planned.
Tier 3 is where Calder Spur sits on revision 2, whose status is settled.
The load on that revision of S-0249, lodged 2034-03-12, is 432.
Two of the anchors at Calder Spur were replaced after the frost and the work is recorded in the district ledger.

### S-0250 -- Hollow Haven

Signal strength at Hollow Haven has been marginal since the mast on the ridge was lowered.
The logbook kept at Hollow Haven runs to 17 pages and the earlier volumes are held off site.
Vegetation around Hollow Haven is cut back twice a year under the standing arrangement.
Access to Hollow Haven is by the service road from the south; the gate code was reissued after the seventh inspection.
Drainage work near Hollow Haven was completed without interruption to the record.
A housekeeping note against S-0250 asks that the cable run be rewalked before the next dry season.
Hollow Haven lodged revision 6 on 2034-09-28.
The return for S-0250 is withdrawn, sits at tier 2, and records a load of 680.
A calibration offset of -14 is recorded for S-0250 against the district standard.
The approach to Hollow Haven crosses 20 field boundaries and the wayleave is held by the county.
Calibration gear for S-0250 travels with the district van and is shared with 29 other sites.

### S-0251 -- Dapple Holt

The site plan for Dapple Holt is the tenth revision and supersedes the sketch held in the district folder.
Maintenance visits to S-0251 are scheduled quarterly and the seventh of those was carried out as planned.
A housekeeping note against S-0251 asks that the cable run be rewalked before the next dry season.
An earlier clerk recorded Dapple Holt under a shortened spelling, and both forms still appear in the older indexes.
Dapple Holt lodged revision 3 on 2034-06-25.
The return for S-0251 is provisional, sits at tier 5, and records a load of 477.
Dapple Holt has been on the register since the first consolidation and its paperwork has never been reconstructed.
The approach to Dapple Holt crosses 33 field boundaries and the wayleave is held by the county.
Weather at Dapple Holt closed the approach for 26 days during the period under review and no readings were lost.
The notes for S-0251 mention a disused well inside the compound, capped and recorded but not surveyed.

### S-0252 -- Yarrow Rill

Correspondence about S-0252 is filed under the district rather than under the site, which has caused confusion before.
Vegetation around Yarrow Rill is cut back twice a year under the standing arrangement.
S-0252 appears at revision 1 with a load of 709.
That revision of Yarrow Rill was lodged 2034-08-10, is settled, and places the station in tier 2.
Telemetry from S-0252 arrives on the fourteenth relay and is batched nightly rather than streamed.
A visitor log is kept at Yarrow Rill and shows 67 entries for the period.
Yarrow Rill has been on the register since the first consolidation and its paperwork has never been reconstructed.
Maintenance visits to S-0252 are scheduled quarterly and the fifth of those was carried out as planned.
The notes for S-0252 mention a disused well inside the compound, capped and recorded but not surveyed.

### S-0253 -- Meadow Wharf

Signal strength at Meadow Wharf has been marginal since the mast on the ridge was lowered.
Meadow Wharf shares its power feed with the neighbouring pumping station and has its own cut-out.
An earlier clerk recorded Meadow Wharf under a shortened spelling, and both forms still appear in the older indexes.
The reading shelter at Meadow Wharf takes water in heavy weather and the floor was relaid.
The district file for Meadow Wharf shows revision 5 lodged on 2034-07-18.
For S-0253 the status is open, the tier is 7, and the load is 643.
The survey party reached Meadow Wharf on the thirteenth of the month and found the access track passable for light vehicles only.
Drainage work near Meadow Wharf was completed without interruption to the record.
Weather at Meadow Wharf closed the approach for 2 days during the period under review and no readings were lost.
Calibration gear for S-0253 travels with the district van and is shared with 14 other sites.
The site plan for Meadow Wharf is the twelfth revision and supersedes the sketch held in the district folder.

### S-0254 -- Bronze Sand

Signal strength at Bronze Sand has been marginal since the mast on the ridge was lowered.
Access to Bronze Sand is by the service road from the south; the gate code was reissued after the tenth inspection.
Bronze Sand lodged revision 5 on 2034-07-17.
The return for S-0254 is returned, sits at tier 6, and records a load of 569.
Weather at Bronze Sand closed the approach for 4 days during the period under review and no readings were lost.
A visitor log is kept at Bronze Sand and shows 79 entries for the period.
An earlier clerk recorded Bronze Sand under a shortened spelling, and both forms still appear in the older indexes.

### S-0255 -- Garnet Ledge

S-0255 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Garnet Ledge has been on the register since the first consolidation and its paperwork has never been reconstructed.
Correspondence about S-0255 is filed under the district rather than under the site, which has caused confusion before.
On 2034-06-08 the district accepted revision 3 for Garnet Ledge and marked it returned.
S-0255 carries tier 8 on that revision and a load of 381.
Telemetry from S-0255 arrives on the fourteenth relay and is batched nightly rather than streamed.
The approach to Garnet Ledge crosses 15 field boundaries and the wayleave is held by the county.
The enclosure at Garnet Ledge was rebuilt in timber after the old fencing was taken by the river.
The logbook kept at Garnet Ledge runs to 72 pages and the earlier volumes are held off site.
The instrument housing at Garnet Ledge is the original pattern and its door seal is checked each visit.

### S-0256 -- Nettle Yard

The instrument housing at Nettle Yard is the original pattern and its door seal is checked each visit.
The reading shelter at Nettle Yard takes water in heavy weather and the floor was relaid.
A visitor log is kept at Nettle Yard and shows 17 entries for the period.
Tier 3 is where Nettle Yard sits on revision 4, whose status is withdrawn.
The load on that revision of S-0256, lodged 2034-06-18, is 247.
Calibration gear for S-0256 travels with the district van and is shared with 8 other sites.
Correspondence shows the tenancy at Nettle Yard was renewed for a further 76 years.
Access to Nettle Yard is by the service road from the south; the gate code was reissued after the fourteenth inspection.
Two of the anchors at Nettle Yard were replaced after the frost and the work is recorded in the district ledger.

### S-0257 -- Linden Coomb

The instrument housing at Linden Coomb is the original pattern and its door seal is checked each visit.
Drainage work near Linden Coomb was completed without interruption to the record.
The notes for S-0257 mention a disused well inside the compound, capped and recorded but not surveyed.
On 2034-08-20 the district accepted revision 3 for Linden Coomb and marked it settled.
S-0257 carries tier 2 on that revision and a load of 576.
The offset applied to readings from S-0257 is -5 and has not been revised.
Correspondence about S-0257 is filed under the district rather than under the site, which has caused confusion before.
S-0257 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Calibration gear for S-0257 travels with the district van and is shared with 6 other sites.
The enclosure at Linden Coomb was rebuilt in timber after the old fencing was taken by the river.
Correspondence shows the tenancy at Linden Coomb was renewed for a further 54 years.

### S-0258 -- Indigo Mere

The logbook kept at Indigo Mere runs to 23 pages and the earlier volumes are held off site.
Indigo Mere lodged revision 3 on 2034-12-15.
The return for S-0258 is settled, sits at tier 2, and records a load of 786.
Two of the anchors at Indigo Mere were replaced after the frost and the work is recorded in the district ledger.
The reading shelter at Indigo Mere takes water in heavy weather and the floor was relaid.
Correspondence about S-0258 is filed under the district rather than under the site, which has caused confusion before.
Vegetation around Indigo Mere is cut back twice a year under the standing arrangement.
Indigo Mere has been on the register since the first consolidation and its paperwork has never been reconstructed.
Signal strength at Indigo Mere has been marginal since the mast on the ridge was lowered.

### S-0259 -- Indigo Drift

Two of the anchors at Indigo Drift were replaced after the frost and the work is recorded in the district ledger.
The notes for S-0259 mention a disused well inside the compound, capped and recorded but not surveyed.
Status settled: revision 4 for S-0259, lodged 2034-03-08.
Load 120 at tier 4 is what that revision carries for Indigo Drift.
Signal strength at Indigo Drift has been marginal since the mast on the ridge was lowered.
A spare sensor head is kept at Indigo Drift against the failure that took out the district in the previous cycle.
The instrument housing at Indigo Drift is the original pattern and its door seal is checked each visit.
A visitor log is kept at Indigo Drift and shows 57 entries for the period.
Weather at Indigo Drift closed the approach for 10 days during the period under review and no readings were lost.
Correspondence about S-0259 is filed under the district rather than under the site, which has caused confusion before.

### S-0260 -- Dusk Vale

An earlier clerk recorded Dusk Vale under a shortened spelling, and both forms still appear in the older indexes.
Correspondence about S-0260 is filed under the district rather than under the site, which has caused confusion before.
Dusk Vale lodged revision 6 on 2034-06-22.
The return for S-0260 is open, sits at tier 6, and records a load of 877.
Two of the anchors at Dusk Vale were replaced after the frost and the work is recorded in the district ledger.
Telemetry from S-0260 arrives on the fifth relay and is batched nightly rather than streamed.
The fence line at Dusk Vale was rerun 24 metres to the east to clear the culvert.

### S-0261 -- Russet Withy

Telemetry from S-0261 arrives on the first relay and is batched nightly rather than streamed.
Correspondence about S-0261 is filed under the district rather than under the site, which has caused confusion before.
Status returned: revision 6 for S-0261, lodged 2034-08-26.
Load 597 at tier 2 is what that revision carries for Russet Withy.
The offset applied to readings from S-0261 is 31 and has not been revised.
Weather at Russet Withy closed the approach for 16 days during the period under review and no readings were lost.
An earlier clerk recorded Russet Withy under a shortened spelling, and both forms still appear in the older indexes.
Access to Russet Withy is by the service road from the south; the gate code was reissued after the eleventh inspection.
The reading shelter at Russet Withy takes water in heavy weather and the floor was relaid.
The survey party reached Russet Withy on the sixth of the month and found the access track passable for light vehicles only.
A visitor log is kept at Russet Withy and shows 34 entries for the period.

### S-0262 -- Basalt Terrace

The fence line at Basalt Terrace was rerun 19 metres to the east to clear the culvert.
Revision 4 of the return for Basalt Terrace was lodged on 2034-12-26 and stands withdrawn.
That revision places S-0262 in tier 8 and gives its load as 864.
Maintenance visits to S-0262 are scheduled quarterly and the ninth of those was carried out as planned.
Signal strength at Basalt Terrace has been marginal since the mast on the ridge was lowered.
The enclosure at Basalt Terrace was rebuilt in timber after the old fencing was taken by the river.

### S-0263 -- Sable Brae

A spare sensor head is kept at Sable Brae against the failure that took out the district in the previous cycle.
Two of the anchors at Sable Brae were replaced after the frost and the work is recorded in the district ledger.
Calibration gear for S-0263 travels with the district van and is shared with 25 other sites.
Signal strength at Sable Brae has been marginal since the mast on the ridge was lowered.
Maintenance visits to S-0263 are scheduled quarterly and the thirteenth of those was carried out as planned.
On 2034-04-15 the district accepted revision 4 for Sable Brae and marked it returned.
S-0263 carries tier 6 on that revision and a load of 132.
Sable Brae carries a calibration offset of -22 on the current instrument head.
The site plan for Sable Brae is the first revision and supersedes the sketch held in the district folder.
Sable Brae shares its power feed with the neighbouring pumping station and has its own cut-out.
Telemetry from S-0263 arrives on the first relay and is batched nightly rather than streamed.

### S-0264 -- Ochre Pike

S-0264 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The instrument housing at Ochre Pike is the original pattern and its door seal is checked each visit.
Status settled: revision 2 for S-0264, lodged 2034-11-21.
Load 383 at tier 3 is what that revision carries for Ochre Pike.
A calibration offset of -36 is recorded for S-0264 against the district standard.
Maintenance visits to S-0264 are scheduled quarterly and the fourteenth of those was carried out as planned.
A housekeeping note against S-0264 asks that the cable run be rewalked before the next dry season.
The site plan for Ochre Pike is the ninth revision and supersedes the sketch held in the district folder.
Ochre Pike shares its power feed with the neighbouring pumping station and has its own cut-out.
The reading shelter at Ochre Pike takes water in heavy weather and the floor was relaid.
Access to Ochre Pike is by the service road from the south; the gate code was reissued after the thirteenth inspection.
The fence line at Ochre Pike was rerun 39 metres to the east to clear the culvert.
Calibration gear for S-0264 travels with the district van and is shared with 26 other sites.

### S-0265 -- Thistle Delve

The enclosure at Thistle Delve was rebuilt in timber after the old fencing was taken by the river.
The approach to Thistle Delve crosses 24 field boundaries and the wayleave is held by the county.
Telemetry from S-0265 arrives on the eleventh relay and is batched nightly rather than streamed.
The logbook kept at Thistle Delve runs to 52 pages and the earlier volumes are held off site.
Revision 4 of the return for Thistle Delve was lodged on 2034-04-07 and stands withdrawn.
That revision places S-0265 in tier 6 and gives its load as 843.
Thistle Delve shares its power feed with the neighbouring pumping station and has its own cut-out.
The instrument housing at Thistle Delve is the original pattern and its door seal is checked each visit.
Two of the anchors at Thistle Delve were replaced after the frost and the work is recorded in the district ledger.
Correspondence shows the tenancy at Thistle Delve was renewed for a further 56 years.

### S-0266 -- Indigo Sand

The survey party reached Indigo Sand on the fourth of the month and found the access track passable for light vehicles only.
The district file for Indigo Sand shows revision 3 lodged on 2034-03-05.
For S-0266 the status is settled, the tier is 2, and the load is 858.
A spare sensor head is kept at Indigo Sand against the failure that took out the district in the previous cycle.
S-0266 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Indigo Sand shares its power feed with the neighbouring pumping station and has its own cut-out.
The access key for S-0266 is held at the district office and signed out per visit.
Calibration gear for S-0266 travels with the district van and is shared with 37 other sites.
The reading shelter at Indigo Sand takes water in heavy weather and the floor was relaid.

### S-0267 -- Indigo Wharf

A spare sensor head is kept at Indigo Wharf against the failure that took out the district in the previous cycle.
An earlier clerk recorded Indigo Wharf under a shortened spelling, and both forms still appear in the older indexes.
A visitor log is kept at Indigo Wharf and shows 55 entries for the period.
A housekeeping note against S-0267 asks that the cable run be rewalked before the next dry season.
The access key for S-0267 is held at the district office and signed out per visit.
S-0267 appears at revision 6 with a load of 139.
That revision of Indigo Wharf was lodged 2034-11-14, is provisional, and places the station in tier 8.
The fence line at Indigo Wharf was rerun 12 metres to the east to clear the culvert.

### S-0268 -- Birch Down

Maintenance visits to S-0268 are scheduled quarterly and the fourteenth of those was carried out as planned.
The fence line at Birch Down was rerun 33 metres to the east to clear the culvert.
Birch Down has been on the register since the first consolidation and its paperwork has never been reconstructed.
The instrument housing at Birch Down is the original pattern and its door seal is checked each visit.
Vegetation around Birch Down is cut back twice a year under the standing arrangement.
The load recorded for S-0268 is 638, on a return at tier 7.
That return for Birch Down is revision 2, lodged 2034-12-17, and its status is provisional.
Telemetry from S-0268 arrives on the thirteenth relay and is batched nightly rather than streamed.
The enclosure at Birch Down was rebuilt in timber after the old fencing was taken by the river.

### S-0269 -- Cedar Ripple

Weather at Cedar Ripple closed the approach for 25 days during the period under review and no readings were lost.
The enclosure at Cedar Ripple was rebuilt in timber after the old fencing was taken by the river.
The instrument housing at Cedar Ripple is the original pattern and its door seal is checked each visit.
Access to Cedar Ripple is by the service road from the south; the gate code was reissued after the third inspection.
A spare sensor head is kept at Cedar Ripple against the failure that took out the district in the previous cycle.
The fence line at Cedar Ripple was rerun 10 metres to the east to clear the culvert.
The notes for S-0269 mention a disused well inside the compound, capped and recorded but not surveyed.
Cedar Ripple has been on the register since the first consolidation and its paperwork has never been reconstructed.
The load recorded for S-0269 is 379, on a return at tier 1.
That return for Cedar Ripple is revision 3, lodged 2034-02-04, and its status is settled.
The logbook kept at Cedar Ripple runs to 80 pages and the earlier volumes are held off site.

### S-0270 -- Bronze Landing

The instrument housing at Bronze Landing is the original pattern and its door seal is checked each visit.
The enclosure at Bronze Landing was rebuilt in timber after the old fencing was taken by the river.
The notes for S-0270 mention a disused well inside the compound, capped and recorded but not surveyed.
Status withdrawn: revision 3 for S-0270, lodged 2034-11-25.
Load 166 at tier 8 is what that revision carries for Bronze Landing.
The site plan for Bronze Landing is the twelfth revision and supersedes the sketch held in the district folder.

### S-0271 -- Calder Landing

Two of the anchors at Calder Landing were replaced after the frost and the work is recorded in the district ledger.
Correspondence shows the tenancy at Calder Landing was renewed for a further 62 years.
A visitor log is kept at Calder Landing and shows 54 entries for the period.
S-0271 appears at revision 1 with a load of 378.
That revision of Calder Landing was lodged 2034-03-20, is settled, and places the station in tier 1.
The notes for S-0271 mention a disused well inside the compound, capped and recorded but not surveyed.
The survey party reached Calder Landing on the fourth of the month and found the access track passable for light vehicles only.
The site plan for Calder Landing is the tenth revision and supersedes the sketch held in the district folder.
Calibration gear for S-0271 travels with the district van and is shared with 39 other sites.

### S-0272 -- Basalt Spur

The approach to Basalt Spur crosses 22 field boundaries and the wayleave is held by the county.
Signal strength at Basalt Spur has been marginal since the mast on the ridge was lowered.
Vegetation around Basalt Spur is cut back twice a year under the standing arrangement.
Weather at Basalt Spur closed the approach for 4 days during the period under review and no readings were lost.
The district file for Basalt Spur shows revision 4 lodged on 2034-09-10.
For S-0272 the status is withdrawn, the tier is 8, and the load is 364.
A housekeeping note against S-0272 asks that the cable run be rewalked before the next dry season.
A spare sensor head is kept at Basalt Spur against the failure that took out the district in the previous cycle.

### S-0273 -- Vellum Terrace

The fence line at Vellum Terrace was rerun 3 metres to the east to clear the culvert.
An earlier clerk recorded Vellum Terrace under a shortened spelling, and both forms still appear in the older indexes.
Calibration gear for S-0273 travels with the district van and is shared with 29 other sites.
Tier 2 is where Vellum Terrace sits on revision 1, whose status is settled.
The load on that revision of S-0273, lodged 2034-09-17, is 715.
A housekeeping note against S-0273 asks that the cable run be rewalked before the next dry season.
Drainage work near Vellum Terrace was completed without interruption to the record.
Maintenance visits to S-0273 are scheduled quarterly and the fourteenth of those was carried out as planned.
The enclosure at Vellum Terrace was rebuilt in timber after the old fencing was taken by the river.

### S-0274 -- Calder Glade

Correspondence about S-0274 is filed under the district rather than under the site, which has caused confusion before.
The survey party reached Calder Glade on the fifth of the month and found the access track passable for light vehicles only.
Drainage work near Calder Glade was completed without interruption to the record.
Signal strength at Calder Glade has been marginal since the mast on the ridge was lowered.
S-0274 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Calibration gear for S-0274 travels with the district van and is shared with 4 other sites.
Status settled: revision 4 for S-0274, lodged 2034-03-27.
Load 282 at tier 4 is what that revision carries for Calder Glade.
Calder Glade carries a calibration offset of 12 on the current instrument head.
The access key for S-0274 is held at the district office and signed out per visit.

### S-0225 -- Calder Barrow

A visitor log is kept at Calder Barrow and shows 44 entries for the period.
The logbook kept at Calder Barrow runs to 77 pages and the earlier volumes are held off site.
A housekeeping note against S-0225 asks that the cable run be rewalked before the next dry season.
Signal strength at Calder Barrow has been marginal since the mast on the ridge was lowered.
The fence line at Calder Barrow was rerun 6 metres to the east to clear the culvert.
Status settled: revision 1 for S-0225, lodged 2034-01-05.
Load 670 at tier 8 is what that revision carries for Calder Barrow.
This revision of S-0225 is marked 4 in the reconciliation sequence.
Correspondence about S-0225 is filed under the district rather than under the site, which has caused confusion before.
The survey party reached Calder Barrow on the twelfth of the month and found the access track passable for light vehicles only.
Two of the anchors at Calder Barrow were replaced after the frost and the work is recorded in the district ledger.

### S-0276 -- Shale Withy

Signal strength at Shale Withy has been marginal since the mast on the ridge was lowered.
The approach to Shale Withy crosses 37 field boundaries and the wayleave is held by the county.
Telemetry from S-0276 arrives on the seventh relay and is batched nightly rather than streamed.
Drainage work near Shale Withy was completed without interruption to the record.
Maintenance visits to S-0276 are scheduled quarterly and the tenth of those was carried out as planned.
Tier 6 is where Shale Withy sits on revision 6, whose status is settled.
The load on that revision of S-0276, lodged 2034-12-25, is 876.
Shale Withy carries a calibration offset of -9 on the current instrument head.
This revision of S-0276 is marked 1 in the reconciliation sequence.
The logbook kept at Shale Withy runs to 47 pages and the earlier volumes are held off site.
Access to Shale Withy is by the service road from the south; the gate code was reissued after the twelfth inspection.
A spare sensor head is kept at Shale Withy against the failure that took out the district in the previous cycle.

### S-0175 -- Crag Culvert

Access to Crag Culvert is by the service road from the south; the gate code was reissued after the eleventh inspection.
A visitor log is kept at Crag Culvert and shows 85 entries for the period.
Signal strength at Crag Culvert has been marginal since the mast on the ridge was lowered.
The site plan for Crag Culvert is the ninth revision and supersedes the sketch held in the district folder.
Two of the anchors at Crag Culvert were replaced after the frost and the work is recorded in the district ledger.
S-0175 appears at revision 5 with a load of 531.
That revision of Crag Culvert was lodged 2034-10-18, is settled, and places the station in tier 8.
Correspondence shows the tenancy at Crag Culvert was renewed for a further 82 years.
The notes for S-0175 mention a disused well inside the compound, capped and recorded but not surveyed.
The fence line at Crag Culvert was rerun 22 metres to the east to clear the culvert.
Calibration gear for S-0175 travels with the district van and is shared with 19 other sites.

### S-0278 -- Basalt Knoll

The logbook kept at Basalt Knoll runs to 21 pages and the earlier volumes are held off site.
Basalt Knoll lodged revision 6 on 2034-04-19.
The return for S-0278 is settled, sits at tier 1, and records a load of 390.
Maintenance visits to S-0278 are scheduled quarterly and the eighth of those was carried out as planned.
The survey party reached Basalt Knoll on the third of the month and found the access track passable for light vehicles only.
Correspondence about S-0278 is filed under the district rather than under the site, which has caused confusion before.
The enclosure at Basalt Knoll was rebuilt in timber after the old fencing was taken by the river.

### S-0279 -- Dapple Sand

Correspondence about S-0279 is filed under the district rather than under the site, which has caused confusion before.
Signal strength at Dapple Sand has been marginal since the mast on the ridge was lowered.
A visitor log is kept at Dapple Sand and shows 83 entries for the period.
Maintenance visits to S-0279 are scheduled quarterly and the eleventh of those was carried out as planned.
The fence line at Dapple Sand was rerun 4 metres to the east to clear the culvert.
Weather at Dapple Sand closed the approach for 16 days during the period under review and no readings were lost.
Calibration gear for S-0279 travels with the district van and is shared with 13 other sites.
Status settled: revision 3 for S-0279, lodged 2034-06-02.
Load 222 at tier 9 is what that revision carries for Dapple Sand.
Dapple Sand carries sequence mark 6 in this quarter's reconciliation.
Telemetry from S-0279 arrives on the ninth relay and is batched nightly rather than streamed.
An earlier clerk recorded Dapple Sand under a shortened spelling, and both forms still appear in the older indexes.
The access key for S-0279 is held at the district office and signed out per visit.

### S-0280 -- Bronze Headland

An earlier clerk recorded Bronze Headland under a shortened spelling, and both forms still appear in the older indexes.
Maintenance visits to S-0280 are scheduled quarterly and the tenth of those was carried out as planned.
Telemetry from S-0280 arrives on the first relay and is batched nightly rather than streamed.
Bronze Headland shares its power feed with the neighbouring pumping station and has its own cut-out.
Drainage work near Bronze Headland was completed without interruption to the record.
Bronze Headland lodged revision 6 on 2034-03-21.
The return for S-0280 is settled, sits at tier 1, and records a load of 146.
Correspondence shows the tenancy at Bronze Headland was renewed for a further 72 years.

### S-0281 -- Cinder Rill

The survey party reached Cinder Rill on the sixth of the month and found the access track passable for light vehicles only.
A housekeeping note against S-0281 asks that the cable run be rewalked before the next dry season.
Signal strength at Cinder Rill has been marginal since the mast on the ridge was lowered.
Revision 3 of the return for Cinder Rill was lodged on 2034-04-12 and stands settled.
That revision places S-0281 in tier 1 and gives its load as 373.
S-0281 was one of the sites brought forward in the consolidation and its numbering reflects that order.
An earlier clerk recorded Cinder Rill under a shortened spelling, and both forms still appear in the older indexes.

### S-0282 -- Copper Butte

Two of the anchors at Copper Butte were replaced after the frost and the work is recorded in the district ledger.
An earlier clerk recorded Copper Butte under a shortened spelling, and both forms still appear in the older indexes.
The logbook kept at Copper Butte runs to 49 pages and the earlier volumes are held off site.
S-0282 appears at revision 4 with a load of 768.
That revision of Copper Butte was lodged 2034-02-11, is settled, and places the station in tier 5.
The fence line at Copper Butte was rerun 23 metres to the east to clear the culvert.
Calibration gear for S-0282 travels with the district van and is shared with 28 other sites.
The approach to Copper Butte crosses 23 field boundaries and the wayleave is held by the county.
The survey party reached Copper Butte on the eleventh of the month and found the access track passable for light vehicles only.
Copper Butte has been on the register since the first consolidation and its paperwork has never been reconstructed.
Signal strength at Copper Butte has been marginal since the mast on the ridge was lowered.

### S-0283 -- Dusk Brae

The survey party reached Dusk Brae on the twelfth of the month and found the access track passable for light vehicles only.
Calibration gear for S-0283 travels with the district van and is shared with 2 other sites.
Vegetation around Dusk Brae is cut back twice a year under the standing arrangement.
On 2034-09-16 the district accepted revision 6 for Dusk Brae and marked it provisional.
S-0283 carries tier 4 on that revision and a load of 514.
Drainage work near Dusk Brae was completed without interruption to the record.
Signal strength at Dusk Brae has been marginal since the mast on the ridge was lowered.
Telemetry from S-0283 arrives on the first relay and is batched nightly rather than streamed.

### S-0284 -- Indigo Terrace

Two of the anchors at Indigo Terrace were replaced after the frost and the work is recorded in the district ledger.
Indigo Terrace has been on the register since the first consolidation and its paperwork has never been reconstructed.
Drainage work near Indigo Terrace was completed without interruption to the record.
The load recorded for S-0284 is 691, on a return at tier 7.
That return for Indigo Terrace is revision 1, lodged 2034-03-22, and its status is returned.
S-0284 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The reading shelter at Indigo Terrace takes water in heavy weather and the floor was relaid.
A spare sensor head is kept at Indigo Terrace against the failure that took out the district in the previous cycle.
Indigo Terrace shares its power feed with the neighbouring pumping station and has its own cut-out.
The access key for S-0284 is held at the district office and signed out per visit.

### S-0285 -- Birch Glade

The enclosure at Birch Glade was rebuilt in timber after the old fencing was taken by the river.
An earlier clerk recorded Birch Glade under a shortened spelling, and both forms still appear in the older indexes.
The fence line at Birch Glade was rerun 35 metres to the east to clear the culvert.
Status settled: revision 6 for S-0285, lodged 2034-10-01.
Load 972 at tier 1 is what that revision carries for Birch Glade.
A calibration offset of -13 is recorded for S-0285 against the district standard.
Birch Glade shares its power feed with the neighbouring pumping station and has its own cut-out.
Access to Birch Glade is by the service road from the south; the gate code was reissued after the fourteenth inspection.
Two of the anchors at Birch Glade were replaced after the frost and the work is recorded in the district ledger.
Signal strength at Birch Glade has been marginal since the mast on the ridge was lowered.

### S-0286 -- Tamarisk Coomb

The reading shelter at Tamarisk Coomb takes water in heavy weather and the floor was relaid.
Revision 3 of the return for Tamarisk Coomb was lodged on 2034-01-12 and stands provisional.
That revision places S-0286 in tier 4 and gives its load as 406.
Tamarisk Coomb shares its power feed with the neighbouring pumping station and has its own cut-out.
Telemetry from S-0286 arrives on the first relay and is batched nightly rather than streamed.
Two of the anchors at Tamarisk Coomb were replaced after the frost and the work is recorded in the district ledger.
A spare sensor head is kept at Tamarisk Coomb against the failure that took out the district in the previous cycle.

### S-0287 -- Heather Cove

The approach to Heather Cove crosses 31 field boundaries and the wayleave is held by the county.
The logbook kept at Heather Cove runs to 45 pages and the earlier volumes are held off site.
Vegetation around Heather Cove is cut back twice a year under the standing arrangement.
Correspondence about S-0287 is filed under the district rather than under the site, which has caused confusion before.
S-0287 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Weather at Heather Cove closed the approach for 4 days during the period under review and no readings were lost.
Access to Heather Cove is by the service road from the south; the gate code was reissued after the eleventh inspection.
Status settled: revision 4 for S-0287, lodged 2034-08-23.
Load 394 at tier 1 is what that revision carries for Heather Cove.
Correspondence shows the tenancy at Heather Cove was renewed for a further 16 years.
Signal strength at Heather Cove has been marginal since the mast on the ridge was lowered.

### S-0288 -- Spindle Ghyll

Calibration gear for S-0288 travels with the district van and is shared with 15 other sites.
An earlier clerk recorded Spindle Ghyll under a shortened spelling, and both forms still appear in the older indexes.
Vegetation around Spindle Ghyll is cut back twice a year under the standing arrangement.
Status open: revision 6 for S-0288, lodged 2034-06-20.
Load 158 at tier 5 is what that revision carries for Spindle Ghyll.
The notes for S-0288 mention a disused well inside the compound, capped and recorded but not surveyed.
Telemetry from S-0288 arrives on the eleventh relay and is batched nightly rather than streamed.
The logbook kept at Spindle Ghyll runs to 78 pages and the earlier volumes are held off site.
Two of the anchors at Spindle Ghyll were replaced after the frost and the work is recorded in the district ledger.

### S-0289 -- Quince Staithe

Correspondence about S-0289 is filed under the district rather than under the site, which has caused confusion before.
Weather at Quince Staithe closed the approach for 16 days during the period under review and no readings were lost.
The load recorded for S-0289 is 427, on a return at tier 2.
That return for Quince Staithe is revision 3, lodged 2034-04-03, and its status is settled.
Telemetry from S-0289 arrives on the second relay and is batched nightly rather than streamed.
S-0289 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The access key for S-0289 is held at the district office and signed out per visit.
The fence line at Quince Staithe was rerun 19 metres to the east to clear the culvert.
A visitor log is kept at Quince Staithe and shows 62 entries for the period.
Access to Quince Staithe is by the service road from the south; the gate code was reissued after the twelfth inspection.
Two of the anchors at Quince Staithe were replaced after the frost and the work is recorded in the district ledger.
An earlier clerk recorded Quince Staithe under a shortened spelling, and both forms still appear in the older indexes.

### S-0290 -- Dusk Ford

The approach to Dusk Ford crosses 30 field boundaries and the wayleave is held by the county.
The reading shelter at Dusk Ford takes water in heavy weather and the floor was relaid.
S-0290 appears at revision 3 with a load of 783.
That revision of Dusk Ford was lodged 2034-03-11, is returned, and places the station in tier 4.
The fence line at Dusk Ford was rerun 22 metres to the east to clear the culvert.
S-0290 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Maintenance visits to S-0290 are scheduled quarterly and the fourteenth of those was carried out as planned.

### S-0291 -- Ember Ghyll

Ember Ghyll has been on the register since the first consolidation and its paperwork has never been reconstructed.
Signal strength at Ember Ghyll has been marginal since the mast on the ridge was lowered.
The approach to Ember Ghyll crosses 30 field boundaries and the wayleave is held by the county.
On 2034-12-19 the district accepted revision 3 for Ember Ghyll and marked it withdrawn.
S-0291 carries tier 9 on that revision and a load of 897.
The offset applied to readings from S-0291 is 22 and has not been revised.
The notes for S-0291 mention a disused well inside the compound, capped and recorded but not surveyed.
Weather at Ember Ghyll closed the approach for 37 days during the period under review and no readings were lost.
The site plan for Ember Ghyll is the eighth revision and supersedes the sketch held in the district folder.
The access key for S-0291 is held at the district office and signed out per visit.
Calibration gear for S-0291 travels with the district van and is shared with 14 other sites.

### S-0292 -- Meadow Copse

A spare sensor head is kept at Meadow Copse against the failure that took out the district in the previous cycle.
Weather at Meadow Copse closed the approach for 26 days during the period under review and no readings were lost.
Access to Meadow Copse is by the service road from the south; the gate code was reissued after the fourteenth inspection.
The access key for S-0292 is held at the district office and signed out per visit.
Status provisional: revision 5 for S-0292, lodged 2034-10-03.
Load 712 at tier 4 is what that revision carries for Meadow Copse.
The approach to Meadow Copse crosses 9 field boundaries and the wayleave is held by the county.
Meadow Copse has been on the register since the first consolidation and its paperwork has never been reconstructed.

### S-0293 -- Bramble Knoll

The instrument housing at Bramble Knoll is the original pattern and its door seal is checked each visit.
The enclosure at Bramble Knoll was rebuilt in timber after the old fencing was taken by the river.
Correspondence about S-0293 is filed under the district rather than under the site, which has caused confusion before.
The reading shelter at Bramble Knoll takes water in heavy weather and the floor was relaid.
Bramble Knoll shares its power feed with the neighbouring pumping station and has its own cut-out.
Access to Bramble Knoll is by the service road from the south; the gate code was reissued after the second inspection.
The access key for S-0293 is held at the district office and signed out per visit.
The notes for S-0293 mention a disused well inside the compound, capped and recorded but not surveyed.
Status withdrawn: revision 2 for S-0293, lodged 2034-05-10.
Load 311 at tier 3 is what that revision carries for Bramble Knoll.
Drainage work near Bramble Knoll was completed without interruption to the record.

### S-0294 -- Fennel Culvert

Correspondence shows the tenancy at Fennel Culvert was renewed for a further 29 years.
The site plan for Fennel Culvert is the tenth revision and supersedes the sketch held in the district folder.
Tier 5 is where Fennel Culvert sits on revision 5, whose status is returned.
The load on that revision of S-0294, lodged 2034-08-06, is 935.
The fence line at Fennel Culvert was rerun 7 metres to the east to clear the culvert.
An earlier clerk recorded Fennel Culvert under a shortened spelling, and both forms still appear in the older indexes.
A housekeeping note against S-0294 asks that the cable run be rewalked before the next dry season.

### S-0295 -- Bronze Thwaite

Correspondence shows the tenancy at Bronze Thwaite was renewed for a further 88 years.
S-0295 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The district file for Bronze Thwaite shows revision 6 lodged on 2034-06-15.
For S-0295 the status is provisional, the tier is 9, and the load is 779.
The access key for S-0295 is held at the district office and signed out per visit.
Bronze Thwaite has been on the register since the first consolidation and its paperwork has never been reconstructed.
Vegetation around Bronze Thwaite is cut back twice a year under the standing arrangement.
The enclosure at Bronze Thwaite was rebuilt in timber after the old fencing was taken by the river.
Signal strength at Bronze Thwaite has been marginal since the mast on the ridge was lowered.
The survey party reached Bronze Thwaite on the fifth of the month and found the access track passable for light vehicles only.

### S-0296 -- Yarrow Reach

Two of the anchors at Yarrow Reach were replaced after the frost and the work is recorded in the district ledger.
The logbook kept at Yarrow Reach runs to 70 pages and the earlier volumes are held off site.
Yarrow Reach shares its power feed with the neighbouring pumping station and has its own cut-out.
Correspondence shows the tenancy at Yarrow Reach was renewed for a further 76 years.
Tier 1 is where Yarrow Reach sits on revision 5, whose status is open.
The load on that revision of S-0296, lodged 2034-10-19, is 800.
Maintenance visits to S-0296 are scheduled quarterly and the fourteenth of those was carried out as planned.
A visitor log is kept at Yarrow Reach and shows 44 entries for the period.

### S-0297 -- Quince Withy

A visitor log is kept at Quince Withy and shows 68 entries for the period.
Quince Withy has been on the register since the first consolidation and its paperwork has never been reconstructed.
Quince Withy lodged revision 4 on 2034-04-16.
The return for S-0297 is settled, sits at tier 2, and records a load of 132.
The reading shelter at Quince Withy takes water in heavy weather and the floor was relaid.
Two of the anchors at Quince Withy were replaced after the frost and the work is recorded in the district ledger.
Drainage work near Quince Withy was completed without interruption to the record.
An earlier clerk recorded Quince Withy under a shortened spelling, and both forms still appear in the older indexes.

### S-0298 -- Yarrow Warren

Signal strength at Yarrow Warren has been marginal since the mast on the ridge was lowered.
The approach to Yarrow Warren crosses 23 field boundaries and the wayleave is held by the county.
The instrument housing at Yarrow Warren is the original pattern and its door seal is checked each visit.
The reading shelter at Yarrow Warren takes water in heavy weather and the floor was relaid.
A housekeeping note against S-0298 asks that the cable run be rewalked before the next dry season.
Yarrow Warren lodged revision 1 on 2034-02-27.
The return for S-0298 is settled, sits at tier 2, and records a load of 493.
Yarrow Warren carries a calibration offset of 12 on the current instrument head.
Weather at Yarrow Warren closed the approach for 11 days during the period under review and no readings were lost.
Access to Yarrow Warren is by the service road from the south; the gate code was reissued after the fourth inspection.

### S-0299 -- Chalk Fell

Correspondence about S-0299 is filed under the district rather than under the site, which has caused confusion before.
Weather at Chalk Fell closed the approach for 6 days during the period under review and no readings were lost.
On 2034-08-18 the district accepted revision 3 for Chalk Fell and marked it settled.
S-0299 carries tier 2 on that revision and a load of 557.
A calibration offset of -31 is recorded for S-0299 against the district standard.
Signal strength at Chalk Fell has been marginal since the mast on the ridge was lowered.
Maintenance visits to S-0299 are scheduled quarterly and the seventh of those was carried out as planned.
The reading shelter at Chalk Fell takes water in heavy weather and the floor was relaid.
A housekeeping note against S-0299 asks that the cable run be rewalked before the next dry season.
Vegetation around Chalk Fell is cut back twice a year under the standing arrangement.
The access key for S-0299 is held at the district office and signed out per visit.

### S-0300 -- Umber Holt

The reading shelter at Umber Holt takes water in heavy weather and the floor was relaid.
The survey party reached Umber Holt on the third of the month and found the access track passable for light vehicles only.
S-0300 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The access key for S-0300 is held at the district office and signed out per visit.
Revision 5 of the return for Umber Holt was lodged on 2034-03-09 and stands settled.
That revision places S-0300 in tier 3 and gives its load as 454.
Vegetation around Umber Holt is cut back twice a year under the standing arrangement.
Two of the anchors at Umber Holt were replaced after the frost and the work is recorded in the district ledger.

### S-0301 -- Umber Cairn

The enclosure at Umber Cairn was rebuilt in timber after the old fencing was taken by the river.
Correspondence about S-0301 is filed under the district rather than under the site, which has caused confusion before.
Revision 1 of the return for Umber Cairn was lodged on 2034-05-12 and stands open.
That revision places S-0301 in tier 8 and gives its load as 811.
Umber Cairn carries a calibration offset of -15 on the current instrument head.
A spare sensor head is kept at Umber Cairn against the failure that took out the district in the previous cycle.
The fence line at Umber Cairn was rerun 10 metres to the east to clear the culvert.
The survey party reached Umber Cairn on the first of the month and found the access track passable for light vehicles only.

### S-0302 -- Shale Gully

Signal strength at Shale Gully has been marginal since the mast on the ridge was lowered.
Shale Gully shares its power feed with the neighbouring pumping station and has its own cut-out.
Correspondence about S-0302 is filed under the district rather than under the site, which has caused confusion before.
The district file for Shale Gully shows revision 5 lodged on 2034-12-27.
For S-0302 the status is settled, the tier is 3, and the load is 289.
The fence line at Shale Gully was rerun 8 metres to the east to clear the culvert.

### S-0303 -- Cinder Furlong

Signal strength at Cinder Furlong has been marginal since the mast on the ridge was lowered.
Revision 6 of the return for Cinder Furlong was lodged on 2034-04-23 and stands settled.
That revision places S-0303 in tier 3 and gives its load as 369.
S-0303 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The approach to Cinder Furlong crosses 14 field boundaries and the wayleave is held by the county.
An earlier clerk recorded Cinder Furlong under a shortened spelling, and both forms still appear in the older indexes.
The enclosure at Cinder Furlong was rebuilt in timber after the old fencing was taken by the river.
The instrument housing at Cinder Furlong is the original pattern and its door seal is checked each visit.

### S-0304 -- Midland Dingle

The enclosure at Midland Dingle was rebuilt in timber after the old fencing was taken by the river.
Weather at Midland Dingle closed the approach for 34 days during the period under review and no readings were lost.
Status open: revision 1 for S-0304, lodged 2034-01-08.
Load 513 at tier 9 is what that revision carries for Midland Dingle.
The instrument housing at Midland Dingle is the original pattern and its door seal is checked each visit.
Vegetation around Midland Dingle is cut back twice a year under the standing arrangement.
The logbook kept at Midland Dingle runs to 20 pages and the earlier volumes are held off site.
Drainage work near Midland Dingle was completed without interruption to the record.

### S-0305 -- Flint Causeway

Flint Causeway shares its power feed with the neighbouring pumping station and has its own cut-out.
On 2034-10-08 the district accepted revision 6 for Flint Causeway and marked it withdrawn.
S-0305 carries tier 8 on that revision and a load of 418.
The offset applied to readings from S-0305 is 29 and has not been revised.
Vegetation around Flint Causeway is cut back twice a year under the standing arrangement.
Signal strength at Flint Causeway has been marginal since the mast on the ridge was lowered.
Two of the anchors at Flint Causeway were replaced after the frost and the work is recorded in the district ledger.

### S-0306 -- Sorrel Yard

S-0306 was one of the sites brought forward in the consolidation and its numbering reflects that order.
A housekeeping note against S-0306 asks that the cable run be rewalked before the next dry season.
Status settled: revision 3 for S-0306, lodged 2034-09-20.
Load 254 at tier 3 is what that revision carries for Sorrel Yard.
The access key for S-0306 is held at the district office and signed out per visit.
A spare sensor head is kept at Sorrel Yard against the failure that took out the district in the previous cycle.
The notes for S-0306 mention a disused well inside the compound, capped and recorded but not surveyed.
The site plan for Sorrel Yard is the tenth revision and supersedes the sketch held in the district folder.
Two of the anchors at Sorrel Yard were replaced after the frost and the work is recorded in the district ledger.
The logbook kept at Sorrel Yard runs to 40 pages and the earlier volumes are held off site.

### S-0307 -- Ember Shoal

A visitor log is kept at Ember Shoal and shows 6 entries for the period.
A housekeeping note against S-0307 asks that the cable run be rewalked before the next dry season.
The survey party reached Ember Shoal on the fifth of the month and found the access track passable for light vehicles only.
S-0307 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Signal strength at Ember Shoal has been marginal since the mast on the ridge was lowered.
Drainage work near Ember Shoal was completed without interruption to the record.
The load recorded for S-0307 is 415, on a return at tier 3.
That return for Ember Shoal is revision 6, lodged 2034-01-16, and its status is settled.
A spare sensor head is kept at Ember Shoal against the failure that took out the district in the previous cycle.
An earlier clerk recorded Ember Shoal under a shortened spelling, and both forms still appear in the older indexes.
The reading shelter at Ember Shoal takes water in heavy weather and the floor was relaid.
Ember Shoal has been on the register since the first consolidation and its paperwork has never been reconstructed.

### S-0308 -- Kestrel Drift

Telemetry from S-0308 arrives on the seventh relay and is batched nightly rather than streamed.
The notes for S-0308 mention a disused well inside the compound, capped and recorded but not surveyed.
Access to Kestrel Drift is by the service road from the south; the gate code was reissued after the first inspection.
Correspondence shows the tenancy at Kestrel Drift was renewed for a further 31 years.
The enclosure at Kestrel Drift was rebuilt in timber after the old fencing was taken by the river.
Revision 3 of the return for Kestrel Drift was lodged on 2034-09-14 and stands withdrawn.
That revision places S-0308 in tier 6 and gives its load as 627.
A calibration offset of 4 is recorded for S-0308 against the district standard.
Signal strength at Kestrel Drift has been marginal since the mast on the ridge was lowered.

### S-0309 -- Mellow Weir

Mellow Weir has been on the register since the first consolidation and its paperwork has never been reconstructed.
The survey party reached Mellow Weir on the eleventh of the month and found the access track passable for light vehicles only.
Drainage work near Mellow Weir was completed without interruption to the record.
The load recorded for S-0309 is 688, on a return at tier 7.
That return for Mellow Weir is revision 3, lodged 2034-08-01, and its status is returned.
The offset applied to readings from S-0309 is 15 and has not been revised.
Two of the anchors at Mellow Weir were replaced after the frost and the work is recorded in the district ledger.
Mellow Weir shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0310 -- Fennel Gate

The survey party reached Fennel Gate on the fourteenth of the month and found the access track passable for light vehicles only.
Drainage work near Fennel Gate was completed without interruption to the record.
The logbook kept at Fennel Gate runs to 47 pages and the earlier volumes are held off site.
Vegetation around Fennel Gate is cut back twice a year under the standing arrangement.
S-0310 appears at revision 3 with a load of 348.
That revision of Fennel Gate was lodged 2034-12-16, is settled, and places the station in tier 2.
Fennel Gate carries a calibration offset of -3 on the current instrument head.
Telemetry from S-0310 arrives on the eighth relay and is batched nightly rather than streamed.

### S-0311 -- Basalt Mill

S-0311 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Access to Basalt Mill is by the service road from the south; the gate code was reissued after the fourth inspection.
Drainage work near Basalt Mill was completed without interruption to the record.
S-0311 appears at revision 5 with a load of 957.
That revision of Basalt Mill was lodged 2034-02-23, is provisional, and places the station in tier 1.
The offset applied to readings from S-0311 is 21 and has not been revised.
Weather at Basalt Mill closed the approach for 11 days during the period under review and no readings were lost.

### S-0312 -- Mellow Scarp

Correspondence about S-0312 is filed under the district rather than under the site, which has caused confusion before.
The enclosure at Mellow Scarp was rebuilt in timber after the old fencing was taken by the river.
The reading shelter at Mellow Scarp takes water in heavy weather and the floor was relaid.
Tier 3 is where Mellow Scarp sits on revision 3, whose status is open.
The load on that revision of S-0312, lodged 2034-04-08, is 808.
Mellow Scarp carries a calibration offset of 8 on the current instrument head.
Access to Mellow Scarp is by the service road from the south; the gate code was reissued after the twelfth inspection.
Signal strength at Mellow Scarp has been marginal since the mast on the ridge was lowered.

### S-0313 -- Coral Yard

Calibration gear for S-0313 travels with the district van and is shared with 4 other sites.
Telemetry from S-0313 arrives on the sixth relay and is batched nightly rather than streamed.
An earlier clerk recorded Coral Yard under a shortened spelling, and both forms still appear in the older indexes.
The load recorded for S-0313 is 445, on a return at tier 4.
That return for Coral Yard is revision 3, lodged 2034-04-01, and its status is settled.
A visitor log is kept at Coral Yard and shows 29 entries for the period.
Access to Coral Yard is by the service road from the south; the gate code was reissued after the thirteenth inspection.
A housekeeping note against S-0313 asks that the cable run be rewalked before the next dry season.
The access key for S-0313 is held at the district office and signed out per visit.
Drainage work near Coral Yard was completed without interruption to the record.
The fence line at Coral Yard was rerun 18 metres to the east to clear the culvert.

### S-0314 -- Pewter Causeway

Correspondence about S-0314 is filed under the district rather than under the site, which has caused confusion before.
Maintenance visits to S-0314 are scheduled quarterly and the fourteenth of those was carried out as planned.
On 2034-06-17 the district accepted revision 1 for Pewter Causeway and marked it returned.
S-0314 carries tier 8 on that revision and a load of 406.
The logbook kept at Pewter Causeway runs to 16 pages and the earlier volumes are held off site.
The notes for S-0314 mention a disused well inside the compound, capped and recorded but not surveyed.
S-0314 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Signal strength at Pewter Causeway has been marginal since the mast on the ridge was lowered.
Access to Pewter Causeway is by the service road from the south; the gate code was reissued after the first inspection.
Correspondence shows the tenancy at Pewter Causeway was renewed for a further 79 years.
The survey party reached Pewter Causeway on the seventh of the month and found the access track passable for light vehicles only.

### S-0315 -- Amber Culvert

A spare sensor head is kept at Amber Culvert against the failure that took out the district in the previous cycle.
Access to Amber Culvert is by the service road from the south; the gate code was reissued after the thirteenth inspection.
S-0315 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Telemetry from S-0315 arrives on the fourteenth relay and is batched nightly rather than streamed.
Status open: revision 3 for S-0315, lodged 2034-08-01.
Load 349 at tier 3 is what that revision carries for Amber Culvert.
Vegetation around Amber Culvert is cut back twice a year under the standing arrangement.
The enclosure at Amber Culvert was rebuilt in timber after the old fencing was taken by the river.
Correspondence about S-0315 is filed under the district rather than under the site, which has caused confusion before.
Signal strength at Amber Culvert has been marginal since the mast on the ridge was lowered.

### S-0316 -- Lichen Staithe

A spare sensor head is kept at Lichen Staithe against the failure that took out the district in the previous cycle.
Maintenance visits to S-0316 are scheduled quarterly and the eighth of those was carried out as planned.
The survey party reached Lichen Staithe on the twelfth of the month and found the access track passable for light vehicles only.
The logbook kept at Lichen Staithe runs to 9 pages and the earlier volumes are held off site.
The site plan for Lichen Staithe is the eighth revision and supersedes the sketch held in the district folder.
An earlier clerk recorded Lichen Staithe under a shortened spelling, and both forms still appear in the older indexes.
Drainage work near Lichen Staithe was completed without interruption to the record.
The instrument housing at Lichen Staithe is the original pattern and its door seal is checked each visit.
Tier 5 is where Lichen Staithe sits on revision 2, whose status is provisional.
The load on that revision of S-0316, lodged 2034-08-05, is 843.
The reading shelter at Lichen Staithe takes water in heavy weather and the floor was relaid.

### S-0317 -- Willow Thwaite

Willow Thwaite has been on the register since the first consolidation and its paperwork has never been reconstructed.
On 2034-04-21 the district accepted revision 2 for Willow Thwaite and marked it settled.
S-0317 carries tier 2 on that revision and a load of 418.
Willow Thwaite carries a calibration offset of -13 on the current instrument head.
A spare sensor head is kept at Willow Thwaite against the failure that took out the district in the previous cycle.
Two of the anchors at Willow Thwaite were replaced after the frost and the work is recorded in the district ledger.
Willow Thwaite shares its power feed with the neighbouring pumping station and has its own cut-out.
The logbook kept at Willow Thwaite runs to 65 pages and the earlier volumes are held off site.
Access to Willow Thwaite is by the service road from the south; the gate code was reissued after the third inspection.
Drainage work near Willow Thwaite was completed without interruption to the record.
A visitor log is kept at Willow Thwaite and shows 80 entries for the period.

### S-0318 -- Indigo Shaw

The site plan for Indigo Shaw is the eighth revision and supersedes the sketch held in the district folder.
A visitor log is kept at Indigo Shaw and shows 14 entries for the period.
The load recorded for S-0318 is 899, on a return at tier 4.
That return for Indigo Shaw is revision 1, lodged 2034-08-19, and its status is settled.
A calibration offset of 4 is recorded for S-0318 against the district standard.
Vegetation around Indigo Shaw is cut back twice a year under the standing arrangement.
Maintenance visits to S-0318 are scheduled quarterly and the third of those was carried out as planned.

### S-0319 -- Willow Brae

Two of the anchors at Willow Brae were replaced after the frost and the work is recorded in the district ledger.
Telemetry from S-0319 arrives on the fourth relay and is batched nightly rather than streamed.
Drainage work near Willow Brae was completed without interruption to the record.
Tier 8 is where Willow Brae sits on revision 1, whose status is withdrawn.
The load on that revision of S-0319, lodged 2034-05-02, is 477.
The survey party reached Willow Brae on the fourth of the month and found the access track passable for light vehicles only.
A spare sensor head is kept at Willow Brae against the failure that took out the district in the previous cycle.
S-0319 was one of the sites brought forward in the consolidation and its numbering reflects that order.

### S-0320 -- Quarry Haven

Two of the anchors at Quarry Haven were replaced after the frost and the work is recorded in the district ledger.
Drainage work near Quarry Haven was completed without interruption to the record.
Revision 3 of the return for Quarry Haven was lodged on 2034-08-09 and stands withdrawn.
That revision places S-0320 in tier 6 and gives its load as 642.
The offset applied to readings from S-0320 is -26 and has not been revised.
A spare sensor head is kept at Quarry Haven against the failure that took out the district in the previous cycle.
A visitor log is kept at Quarry Haven and shows 11 entries for the period.
Telemetry from S-0320 arrives on the ninth relay and is batched nightly rather than streamed.
Quarry Haven shares its power feed with the neighbouring pumping station and has its own cut-out.
The notes for S-0320 mention a disused well inside the compound, capped and recorded but not surveyed.
Calibration gear for S-0320 travels with the district van and is shared with 29 other sites.
Correspondence shows the tenancy at Quarry Haven was renewed for a further 81 years.
The approach to Quarry Haven crosses 30 field boundaries and the wayleave is held by the county.

### S-0321 -- Chalk Knap

Signal strength at Chalk Knap has been marginal since the mast on the ridge was lowered.
The notes for S-0321 mention a disused well inside the compound, capped and recorded but not surveyed.
Revision 5 of the return for Chalk Knap was lodged on 2034-05-24 and stands settled.
That revision places S-0321 in tier 4 and gives its load as 184.
Weather at Chalk Knap closed the approach for 31 days during the period under review and no readings were lost.
The reading shelter at Chalk Knap takes water in heavy weather and the floor was relaid.

### S-0322 -- Mellow Knoll

The reading shelter at Mellow Knoll takes water in heavy weather and the floor was relaid.
The load recorded for S-0322 is 989, on a return at tier 4.
That return for Mellow Knoll is revision 4, lodged 2034-03-05, and its status is settled.
A calibration offset of -2 is recorded for S-0322 against the district standard.
Telemetry from S-0322 arrives on the sixth relay and is batched nightly rather than streamed.
The enclosure at Mellow Knoll was rebuilt in timber after the old fencing was taken by the river.
The notes for S-0322 mention a disused well inside the compound, capped and recorded but not surveyed.
Signal strength at Mellow Knoll has been marginal since the mast on the ridge was lowered.
The approach to Mellow Knoll crosses 14 field boundaries and the wayleave is held by the county.
A spare sensor head is kept at Mellow Knoll against the failure that took out the district in the previous cycle.
A visitor log is kept at Mellow Knoll and shows 37 entries for the period.

### S-0323 -- Linden Yard

Linden Yard shares its power feed with the neighbouring pumping station and has its own cut-out.
The reading shelter at Linden Yard takes water in heavy weather and the floor was relaid.
Two of the anchors at Linden Yard were replaced after the frost and the work is recorded in the district ledger.
Linden Yard lodged revision 5 on 2034-02-26.
The return for S-0323 is settled, sits at tier 1, and records a load of 236.
A calibration offset of -30 is recorded for S-0323 against the district standard.
Linden Yard has been on the register since the first consolidation and its paperwork has never been reconstructed.
Vegetation around Linden Yard is cut back twice a year under the standing arrangement.
A housekeeping note against S-0323 asks that the cable run be rewalked before the next dry season.
A visitor log is kept at Linden Yard and shows 59 entries for the period.
Maintenance visits to S-0323 are scheduled quarterly and the third of those was carried out as planned.
The survey party reached Linden Yard on the sixth of the month and found the access track passable for light vehicles only.

### S-0324 -- Kestrel Ghyll

The survey party reached Kestrel Ghyll on the eighth of the month and found the access track passable for light vehicles only.
The site plan for Kestrel Ghyll is the fifth revision and supersedes the sketch held in the district folder.
Drainage work near Kestrel Ghyll was completed without interruption to the record.
Kestrel Ghyll shares its power feed with the neighbouring pumping station and has its own cut-out.
The enclosure at Kestrel Ghyll was rebuilt in timber after the old fencing was taken by the river.
Correspondence shows the tenancy at Kestrel Ghyll was renewed for a further 49 years.
Revision 1 of the return for Kestrel Ghyll was lodged on 2034-05-15 and stands settled.
That revision places S-0324 in tier 1 and gives its load as 431.
The offset applied to readings from S-0324 is 18 and has not been revised.
Kestrel Ghyll has been on the register since the first consolidation and its paperwork has never been reconstructed.
The logbook kept at Kestrel Ghyll runs to 47 pages and the earlier volumes are held off site.

### S-0325 -- Cedar Mill

Cedar Mill has been on the register since the first consolidation and its paperwork has never been reconstructed.
Telemetry from S-0325 arrives on the sixth relay and is batched nightly rather than streamed.
Correspondence shows the tenancy at Cedar Mill was renewed for a further 34 years.
The instrument housing at Cedar Mill is the original pattern and its door seal is checked each visit.
Vegetation around Cedar Mill is cut back twice a year under the standing arrangement.
The fence line at Cedar Mill was rerun 4 metres to the east to clear the culvert.
Maintenance visits to S-0325 are scheduled quarterly and the seventh of those was carried out as planned.
A spare sensor head is kept at Cedar Mill against the failure that took out the district in the previous cycle.
Revision 5 of the return for Cedar Mill was lodged on 2034-05-04 and stands settled.
That revision places S-0325 in tier 2 and gives its load as 822.
The site plan for Cedar Mill is the thirteenth revision and supersedes the sketch held in the district folder.
Weather at Cedar Mill closed the approach for 9 days during the period under review and no readings were lost.

### S-0326 -- Bramble Combe

An earlier clerk recorded Bramble Combe under a shortened spelling, and both forms still appear in the older indexes.
On 2034-07-12 the district accepted revision 4 for Bramble Combe and marked it settled.
S-0326 carries tier 7 on that revision and a load of 834.
The reconciliation sequence mark carried by this revision of S-0326 is 3.
A housekeeping note against S-0326 asks that the cable run be rewalked before the next dry season.
Bramble Combe has been on the register since the first consolidation and its paperwork has never been reconstructed.
Correspondence shows the tenancy at Bramble Combe was renewed for a further 85 years.
The reading shelter at Bramble Combe takes water in heavy weather and the floor was relaid.
The survey party reached Bramble Combe on the seventh of the month and found the access track passable for light vehicles only.
Drainage work near Bramble Combe was completed without interruption to the record.

### S-0174 -- Heather Holt

Vegetation around Heather Holt is cut back twice a year under the standing arrangement.
The instrument housing at Heather Holt is the original pattern and its door seal is checked each visit.
A housekeeping note against S-0174 asks that the cable run be rewalked before the next dry season.
Maintenance visits to S-0174 are scheduled quarterly and the second of those was carried out as planned.
Two of the anchors at Heather Holt were replaced after the frost and the work is recorded in the district ledger.
Tier 7 is where Heather Holt sits on revision 2, whose status is settled.
The load on that revision of S-0174, lodged 2034-01-22, is 643.
The reconciliation sequence mark carried by this revision of S-0174 is 5.
The access key for S-0174 is held at the district office and signed out per visit.
The fence line at Heather Holt was rerun 38 metres to the east to clear the culvert.
Access to Heather Holt is by the service road from the south; the gate code was reissued after the ninth inspection.
Correspondence about S-0174 is filed under the district rather than under the site, which has caused confusion before.

### S-0328 -- Pewter Quay

Correspondence shows the tenancy at Pewter Quay was renewed for a further 68 years.
A spare sensor head is kept at Pewter Quay against the failure that took out the district in the previous cycle.
The enclosure at Pewter Quay was rebuilt in timber after the old fencing was taken by the river.
On 2034-06-01 the district accepted revision 1 for Pewter Quay and marked it returned.
S-0328 carries tier 3 on that revision and a load of 246.
The site plan for Pewter Quay is the fourteenth revision and supersedes the sketch held in the district folder.

### S-0329 -- Saffron Channel

The survey party reached Saffron Channel on the eighth of the month and found the access track passable for light vehicles only.
A visitor log is kept at Saffron Channel and shows 23 entries for the period.
Weather at Saffron Channel closed the approach for 27 days during the period under review and no readings were lost.
Telemetry from S-0329 arrives on the second relay and is batched nightly rather than streamed.
The approach to Saffron Channel crosses 23 field boundaries and the wayleave is held by the county.
The fence line at Saffron Channel was rerun 12 metres to the east to clear the culvert.
A housekeeping note against S-0329 asks that the cable run be rewalked before the next dry season.
The notes for S-0329 mention a disused well inside the compound, capped and recorded but not surveyed.
Revision 4 of the return for Saffron Channel was lodged on 2034-07-04 and stands settled.
That revision places S-0329 in tier 9 and gives its load as 763.
The offset applied to readings from S-0329 is 26 and has not been revised.
Access to Saffron Channel is by the service road from the south; the gate code was reissued after the eighth inspection.

### S-0330 -- Teasel Hallow

Correspondence about S-0330 is filed under the district rather than under the site, which has caused confusion before.
A housekeeping note against S-0330 asks that the cable run be rewalked before the next dry season.
S-0330 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Teasel Hallow lodged revision 3 on 2034-02-18.
The return for S-0330 is provisional, sits at tier 1, and records a load of 823.
Teasel Hallow has been on the register since the first consolidation and its paperwork has never been reconstructed.

### S-0331 -- Rowan Sand

The enclosure at Rowan Sand was rebuilt in timber after the old fencing was taken by the river.
On 2034-04-09 the district accepted revision 4 for Rowan Sand and marked it withdrawn.
S-0331 carries tier 9 on that revision and a load of 403.
Rowan Sand has been on the register since the first consolidation and its paperwork has never been reconstructed.
Drainage work near Rowan Sand was completed without interruption to the record.
The notes for S-0331 mention a disused well inside the compound, capped and recorded but not surveyed.
Telemetry from S-0331 arrives on the fifth relay and is batched nightly rather than streamed.

### S-0332 -- Spindle Anchorage

Correspondence about S-0332 is filed under the district rather than under the site, which has caused confusion before.
Spindle Anchorage lodged revision 3 on 2034-12-18.
The return for S-0332 is provisional, sits at tier 6, and records a load of 298.
The offset applied to readings from S-0332 is 37 and has not been revised.
The access key for S-0332 is held at the district office and signed out per visit.
The notes for S-0332 mention a disused well inside the compound, capped and recorded but not surveyed.
A housekeeping note against S-0332 asks that the cable run be rewalked before the next dry season.
Calibration gear for S-0332 travels with the district van and is shared with 37 other sites.
The instrument housing at Spindle Anchorage is the original pattern and its door seal is checked each visit.
Signal strength at Spindle Anchorage has been marginal since the mast on the ridge was lowered.
Weather at Spindle Anchorage closed the approach for 18 days during the period under review and no readings were lost.

### S-0333 -- Beacon Warren

The fence line at Beacon Warren was rerun 14 metres to the east to clear the culvert.
Drainage work near Beacon Warren was completed without interruption to the record.
S-0333 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The load recorded for S-0333 is 975, on a return at tier 9.
That return for Beacon Warren is revision 6, lodged 2034-03-28, and its status is settled.
The reading shelter at Beacon Warren takes water in heavy weather and the floor was relaid.

### S-0334 -- Gorse Mere

A spare sensor head is kept at Gorse Mere against the failure that took out the district in the previous cycle.
The load recorded for S-0334 is 231, on a return at tier 1.
That return for Gorse Mere is revision 1, lodged 2034-02-28, and its status is settled.
Gorse Mere has been on the register since the first consolidation and its paperwork has never been reconstructed.
The notes for S-0334 mention a disused well inside the compound, capped and recorded but not surveyed.
S-0334 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Maintenance visits to S-0334 are scheduled quarterly and the tenth of those was carried out as planned.
Drainage work near Gorse Mere was completed without interruption to the record.
Correspondence about S-0334 is filed under the district rather than under the site, which has caused confusion before.

### S-0335 -- Fennel Furlong

The approach to Fennel Furlong crosses 40 field boundaries and the wayleave is held by the county.
An earlier clerk recorded Fennel Furlong under a shortened spelling, and both forms still appear in the older indexes.
Access to Fennel Furlong is by the service road from the south; the gate code was reissued after the twelfth inspection.
The fence line at Fennel Furlong was rerun 24 metres to the east to clear the culvert.
Tier 6 is where Fennel Furlong sits on revision 6, whose status is provisional.
The load on that revision of S-0335, lodged 2034-03-06, is 913.
A calibration offset of -7 is recorded for S-0335 against the district standard.
Vegetation around Fennel Furlong is cut back twice a year under the standing arrangement.

### S-0336 -- Hazel Cleave

The survey party reached Hazel Cleave on the fourth of the month and found the access track passable for light vehicles only.
Telemetry from S-0336 arrives on the fourth relay and is batched nightly rather than streamed.
Weather at Hazel Cleave closed the approach for 4 days during the period under review and no readings were lost.
Calibration gear for S-0336 travels with the district van and is shared with 6 other sites.
The fence line at Hazel Cleave was rerun 40 metres to the east to clear the culvert.
Hazel Cleave has been on the register since the first consolidation and its paperwork has never been reconstructed.
Status settled: revision 3 for S-0336, lodged 2034-07-13.
Load 599 at tier 4 is what that revision carries for Hazel Cleave.
Correspondence shows the tenancy at Hazel Cleave was renewed for a further 5 years.
The notes for S-0336 mention a disused well inside the compound, capped and recorded but not surveyed.

### S-0337 -- Saffron Knoll

A visitor log is kept at Saffron Knoll and shows 50 entries for the period.
The access key for S-0337 is held at the district office and signed out per visit.
Saffron Knoll has been on the register since the first consolidation and its paperwork has never been reconstructed.
Tier 3 is where Saffron Knoll sits on revision 6, whose status is settled.
The load on that revision of S-0337, lodged 2034-10-19, is 590.
Saffron Knoll shares its power feed with the neighbouring pumping station and has its own cut-out.
A spare sensor head is kept at Saffron Knoll against the failure that took out the district in the previous cycle.

### S-0338 -- Midland Dale

The instrument housing at Midland Dale is the original pattern and its door seal is checked each visit.
The load recorded for S-0338 is 410, on a return at tier 2.
That return for Midland Dale is revision 5, lodged 2034-07-24, and its status is settled.
A housekeeping note against S-0338 asks that the cable run be rewalked before the next dry season.
Midland Dale shares its power feed with the neighbouring pumping station and has its own cut-out.
Telemetry from S-0338 arrives on the eleventh relay and is batched nightly rather than streamed.
S-0338 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The enclosure at Midland Dale was rebuilt in timber after the old fencing was taken by the river.
Access to Midland Dale is by the service road from the south; the gate code was reissued after the fourth inspection.

### S-0339 -- Fallow Strand

Fallow Strand has been on the register since the first consolidation and its paperwork has never been reconstructed.
The district file for Fallow Strand shows revision 6 lodged on 2034-02-24.
For S-0339 the status is provisional, the tier is 8, and the load is 153.
Drainage work near Fallow Strand was completed without interruption to the record.
Maintenance visits to S-0339 are scheduled quarterly and the sixth of those was carried out as planned.
Correspondence shows the tenancy at Fallow Strand was renewed for a further 75 years.
The approach to Fallow Strand crosses 25 field boundaries and the wayleave is held by the county.
The enclosure at Fallow Strand was rebuilt in timber after the old fencing was taken by the river.

### S-0340 -- Midland Pound

Weather at Midland Pound closed the approach for 17 days during the period under review and no readings were lost.
The survey party reached Midland Pound on the eighth of the month and found the access track passable for light vehicles only.
Telemetry from S-0340 arrives on the second relay and is batched nightly rather than streamed.
Status returned: revision 1 for S-0340, lodged 2034-06-03.
Load 374 at tier 4 is what that revision carries for Midland Pound.
The offset applied to readings from S-0340 is 24 and has not been revised.
Access to Midland Pound is by the service road from the south; the gate code was reissued after the fifth inspection.
Correspondence about S-0340 is filed under the district rather than under the site, which has caused confusion before.
Two of the anchors at Midland Pound were replaced after the frost and the work is recorded in the district ledger.

### S-0341 -- Birch Yard

The reading shelter at Birch Yard takes water in heavy weather and the floor was relaid.
The fence line at Birch Yard was rerun 12 metres to the east to clear the culvert.
Telemetry from S-0341 arrives on the eleventh relay and is batched nightly rather than streamed.
Drainage work near Birch Yard was completed without interruption to the record.
The instrument housing at Birch Yard is the original pattern and its door seal is checked each visit.
Birch Yard lodged revision 5 on 2034-08-09.
The return for S-0341 is returned, sits at tier 8, and records a load of 387.
Birch Yard carries a calibration offset of -9 on the current instrument head.
Two of the anchors at Birch Yard were replaced after the frost and the work is recorded in the district ledger.

### S-0342 -- Linden Brook

Weather at Linden Brook closed the approach for 18 days during the period under review and no readings were lost.
Linden Brook has been on the register since the first consolidation and its paperwork has never been reconstructed.
Signal strength at Linden Brook has been marginal since the mast on the ridge was lowered.
The access key for S-0342 is held at the district office and signed out per visit.
Linden Brook lodged revision 4 on 2034-12-15.
The return for S-0342 is settled, sits at tier 4, and records a load of 380.
S-0342 was one of the sites brought forward in the consolidation and its numbering reflects that order.
A visitor log is kept at Linden Brook and shows 19 entries for the period.
Correspondence shows the tenancy at Linden Brook was renewed for a further 23 years.

### S-0343 -- Saffron Copse

Calibration gear for S-0343 travels with the district van and is shared with 10 other sites.
The instrument housing at Saffron Copse is the original pattern and its door seal is checked each visit.
A visitor log is kept at Saffron Copse and shows 20 entries for the period.
Telemetry from S-0343 arrives on the first relay and is batched nightly rather than streamed.
Signal strength at Saffron Copse has been marginal since the mast on the ridge was lowered.
On 2034-12-09 the district accepted revision 3 for Saffron Copse and marked it provisional.
S-0343 carries tier 8 on that revision and a load of 222.
The notes for S-0343 mention a disused well inside the compound, capped and recorded but not surveyed.
The site plan for Saffron Copse is the sixth revision and supersedes the sketch held in the district folder.

### S-0344 -- Chalk Beck

A spare sensor head is kept at Chalk Beck against the failure that took out the district in the previous cycle.
Chalk Beck shares its power feed with the neighbouring pumping station and has its own cut-out.
Two of the anchors at Chalk Beck were replaced after the frost and the work is recorded in the district ledger.
A housekeeping note against S-0344 asks that the cable run be rewalked before the next dry season.
On 2034-08-22 the district accepted revision 6 for Chalk Beck and marked it settled.
S-0344 carries tier 4 on that revision and a load of 904.
Access to Chalk Beck is by the service road from the south; the gate code was reissued after the tenth inspection.

### S-0345 -- Garnet Coomb

Calibration gear for S-0345 travels with the district van and is shared with 2 other sites.
Vegetation around Garnet Coomb is cut back twice a year under the standing arrangement.
Tier 3 is where Garnet Coomb sits on revision 1, whose status is settled.
The load on that revision of S-0345, lodged 2034-09-04, is 514.
The notes for S-0345 mention a disused well inside the compound, capped and recorded but not surveyed.
Correspondence shows the tenancy at Garnet Coomb was renewed for a further 46 years.
Drainage work near Garnet Coomb was completed without interruption to the record.
The reading shelter at Garnet Coomb takes water in heavy weather and the floor was relaid.
A spare sensor head is kept at Garnet Coomb against the failure that took out the district in the previous cycle.

### S-0346 -- Tamarisk Barrow

A spare sensor head is kept at Tamarisk Barrow against the failure that took out the district in the previous cycle.
Correspondence about S-0346 is filed under the district rather than under the site, which has caused confusion before.
Maintenance visits to S-0346 are scheduled quarterly and the eleventh of those was carried out as planned.
A housekeeping note against S-0346 asks that the cable run be rewalked before the next dry season.
On 2034-03-09 the district accepted revision 4 for Tamarisk Barrow and marked it returned.
S-0346 carries tier 8 on that revision and a load of 292.
The logbook kept at Tamarisk Barrow runs to 15 pages and the earlier volumes are held off site.
The reading shelter at Tamarisk Barrow takes water in heavy weather and the floor was relaid.
Tamarisk Barrow shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0347 -- Flint Bight

The logbook kept at Flint Bight runs to 28 pages and the earlier volumes are held off site.
Flint Bight has been on the register since the first consolidation and its paperwork has never been reconstructed.
Two of the anchors at Flint Bight were replaced after the frost and the work is recorded in the district ledger.
Flint Bight shares its power feed with the neighbouring pumping station and has its own cut-out.
S-0347 appears at revision 6 with a load of 649.
That revision of Flint Bight was lodged 2034-07-07, is settled, and places the station in tier 4.
Maintenance visits to S-0347 are scheduled quarterly and the tenth of those was carried out as planned.

### S-0348 -- Pebble Brook

The survey party reached Pebble Brook on the sixth of the month and found the access track passable for light vehicles only.
Vegetation around Pebble Brook is cut back twice a year under the standing arrangement.
Two of the anchors at Pebble Brook were replaced after the frost and the work is recorded in the district ledger.
Maintenance visits to S-0348 are scheduled quarterly and the fourth of those was carried out as planned.
Correspondence shows the tenancy at Pebble Brook was renewed for a further 64 years.
The fence line at Pebble Brook was rerun 26 metres to the east to clear the culvert.
Status settled: revision 4 for S-0348, lodged 2034-07-10.
Load 898 at tier 4 is what that revision carries for Pebble Brook.
A calibration offset of -26 is recorded for S-0348 against the district standard.
A housekeeping note against S-0348 asks that the cable run be rewalked before the next dry season.

### S-0349 -- Russet Bourne

The reading shelter at Russet Bourne takes water in heavy weather and the floor was relaid.
Calibration gear for S-0349 travels with the district van and is shared with 6 other sites.
Russet Bourne shares its power feed with the neighbouring pumping station and has its own cut-out.
Russet Bourne lodged revision 2 on 2034-06-08.
The return for S-0349 is open, sits at tier 7, and records a load of 192.
The offset applied to readings from S-0349 is -39 and has not been revised.
Two of the anchors at Russet Bourne were replaced after the frost and the work is recorded in the district ledger.
Russet Bourne has been on the register since the first consolidation and its paperwork has never been reconstructed.
Weather at Russet Bourne closed the approach for 13 days during the period under review and no readings were lost.
A visitor log is kept at Russet Bourne and shows 13 entries for the period.
The notes for S-0349 mention a disused well inside the compound, capped and recorded but not surveyed.
Access to Russet Bourne is by the service road from the south; the gate code was reissued after the tenth inspection.

### S-0350 -- Osier Ferry

An earlier clerk recorded Osier Ferry under a shortened spelling, and both forms still appear in the older indexes.
The survey party reached Osier Ferry on the fifth of the month and found the access track passable for light vehicles only.
Tier 5 is where Osier Ferry sits on revision 4, whose status is provisional.
The load on that revision of S-0350, lodged 2034-11-23, is 330.
The reading shelter at Osier Ferry takes water in heavy weather and the floor was relaid.
A visitor log is kept at Osier Ferry and shows 28 entries for the period.
The fence line at Osier Ferry was rerun 35 metres to the east to clear the culvert.
Calibration gear for S-0350 travels with the district van and is shared with 15 other sites.
Drainage work near Osier Ferry was completed without interruption to the record.
Access to Osier Ferry is by the service road from the south; the gate code was reissued after the fourth inspection.
The instrument housing at Osier Ferry is the original pattern and its door seal is checked each visit.

### S-0351 -- Ridge Thwaite

Maintenance visits to S-0351 are scheduled quarterly and the first of those was carried out as planned.
Revision 5 of the return for Ridge Thwaite was lodged on 2034-02-09 and stands withdrawn.
That revision places S-0351 in tier 9 and gives its load as 414.
The offset applied to readings from S-0351 is 34 and has not been revised.
The instrument housing at Ridge Thwaite is the original pattern and its door seal is checked each visit.
Ridge Thwaite shares its power feed with the neighbouring pumping station and has its own cut-out.
Calibration gear for S-0351 travels with the district van and is shared with 5 other sites.
Telemetry from S-0351 arrives on the fourteenth relay and is batched nightly rather than streamed.
Correspondence shows the tenancy at Ridge Thwaite was renewed for a further 59 years.
Access to Ridge Thwaite is by the service road from the south; the gate code was reissued after the eighth inspection.
The approach to Ridge Thwaite crosses 17 field boundaries and the wayleave is held by the county.

### S-0352 -- Russet Crossing

Maintenance visits to S-0352 are scheduled quarterly and the thirteenth of those was carried out as planned.
The reading shelter at Russet Crossing takes water in heavy weather and the floor was relaid.
Revision 4 of the return for Russet Crossing was lodged on 2034-05-06 and stands provisional.
That revision places S-0352 in tier 4 and gives its load as 716.
The notes for S-0352 mention a disused well inside the compound, capped and recorded but not surveyed.
Access to Russet Crossing is by the service road from the south; the gate code was reissued after the twelfth inspection.
A spare sensor head is kept at Russet Crossing against the failure that took out the district in the previous cycle.
The survey party reached Russet Crossing on the second of the month and found the access track passable for light vehicles only.
S-0352 was one of the sites brought forward in the consolidation and its numbering reflects that order.

### S-0353 -- Quarry Vale

A visitor log is kept at Quarry Vale and shows 49 entries for the period.
Correspondence about S-0353 is filed under the district rather than under the site, which has caused confusion before.
Telemetry from S-0353 arrives on the second relay and is batched nightly rather than streamed.
The district file for Quarry Vale shows revision 3 lodged on 2034-10-01.
For S-0353 the status is open, the tier is 4, and the load is 933.
The fence line at Quarry Vale was rerun 35 metres to the east to clear the culvert.
S-0353 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Vegetation around Quarry Vale is cut back twice a year under the standing arrangement.
Calibration gear for S-0353 travels with the district van and is shared with 21 other sites.

### S-0354 -- Cedar Anchorage

A spare sensor head is kept at Cedar Anchorage against the failure that took out the district in the previous cycle.
The fence line at Cedar Anchorage was rerun 38 metres to the east to clear the culvert.
Cedar Anchorage lodged revision 3 on 2034-04-25.
The return for S-0354 is settled, sits at tier 4, and records a load of 767.
Cedar Anchorage carries a calibration offset of -19 on the current instrument head.
S-0354 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Maintenance visits to S-0354 are scheduled quarterly and the sixth of those was carried out as planned.
Cedar Anchorage shares its power feed with the neighbouring pumping station and has its own cut-out.
The notes for S-0354 mention a disused well inside the compound, capped and recorded but not surveyed.
Calibration gear for S-0354 travels with the district van and is shared with 8 other sites.

### S-0355 -- Sedge Copse

Correspondence shows the tenancy at Sedge Copse was renewed for a further 41 years.
Sedge Copse lodged revision 2 on 2034-11-17.
The return for S-0355 is settled, sits at tier 1, and records a load of 236.
Sedge Copse carries a calibration offset of -2 on the current instrument head.
Signal strength at Sedge Copse has been marginal since the mast on the ridge was lowered.
The approach to Sedge Copse crosses 8 field boundaries and the wayleave is held by the county.
Telemetry from S-0355 arrives on the ninth relay and is batched nightly rather than streamed.
The survey party reached Sedge Copse on the eighth of the month and found the access track passable for light vehicles only.
Calibration gear for S-0355 travels with the district van and is shared with 20 other sites.
A visitor log is kept at Sedge Copse and shows 48 entries for the period.
The site plan for Sedge Copse is the seventh revision and supersedes the sketch held in the district folder.


## 7. Before you stop

`answer.json` in your working directory, one JSON object, the nine keys above. Do not
modify or delete `NOTICE.txt`. Work until the answer is complete, then stop.
