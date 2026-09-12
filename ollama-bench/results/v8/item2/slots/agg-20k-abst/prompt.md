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
6. What calibration offset does station S-0109 record? -> `calibration_offset`
7. What load does station S-0990 record? -> `absent_station_load`
8. What is the governing load of station S-0128? -> `conflicting_station_load`
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

If the material does not determine the answer to a question -- because the fact is not
recorded anywhere in it, or because the material leaves the question open -- answer that
question with the string `INSUFFICIENT` instead of supplying a value. Answering
`INSUFFICIENT` where the material does determine an answer is a failure of the same kind,
so use it only where the material genuinely does not decide.

## 6. The register

Every return in this quarter's register follows. They are in no particular order.

### S-0101 -- Dapple Reach

The access key for S-0101 is held at the district office and signed out per visit.
Vegetation around Dapple Reach is cut back twice a year under the standing arrangement.
The site plan for Dapple Reach is the ninth revision and supersedes the sketch held in the district folder.
Telemetry from S-0101 arrives on the sixth relay and is batched nightly rather than streamed.
Tier 9 is where Dapple Reach sits on revision 3, whose status is withdrawn.
The load on that revision of S-0101, lodged 2034-09-14, is 980.
A spare sensor head is kept at Dapple Reach against the failure that took out the district in the previous cycle.
The instrument housing at Dapple Reach is the original pattern and its door seal is checked each visit.
An earlier clerk recorded Dapple Reach under a shortened spelling, and both forms still appear in the older indexes.

### S-0102 -- Beacon Pound

A visitor log is kept at Beacon Pound and shows 12 entries for the period.
Revision 3 of the return for Beacon Pound was lodged on 2034-09-07 and stands settled.
That revision places S-0102 in tier 4 and gives its load as 304.
A calibration offset of 21 is recorded for S-0102 against the district standard.
The enclosure at Beacon Pound was rebuilt in timber after the old fencing was taken by the river.
The logbook kept at Beacon Pound runs to 46 pages and the earlier volumes are held off site.
The instrument housing at Beacon Pound is the original pattern and its door seal is checked each visit.
Access to Beacon Pound is by the service road from the south; the gate code was reissued after the eleventh inspection.
Maintenance visits to S-0102 are scheduled quarterly and the twelfth of those was carried out as planned.

### S-0103 -- Auburn Ledge

Calibration gear for S-0103 travels with the district van and is shared with 22 other sites.
The access key for S-0103 is held at the district office and signed out per visit.
The notes for S-0103 mention a disused well inside the compound, capped and recorded but not surveyed.
An earlier clerk recorded Auburn Ledge under a shortened spelling, and both forms still appear in the older indexes.
Auburn Ledge lodged revision 6 on 2034-09-06.
The return for S-0103 is settled, sits at tier 2, and records a load of 275.
Vegetation around Auburn Ledge is cut back twice a year under the standing arrangement.
Weather at Auburn Ledge closed the approach for 4 days during the period under review and no readings were lost.
Signal strength at Auburn Ledge has been marginal since the mast on the ridge was lowered.
S-0103 was one of the sites brought forward in the consolidation and its numbering reflects that order.

### S-0104 -- Basalt Haven

Drainage work near Basalt Haven was completed without interruption to the record.
The approach to Basalt Haven crosses 38 field boundaries and the wayleave is held by the county.
Correspondence shows the tenancy at Basalt Haven was renewed for a further 19 years.
Access to Basalt Haven is by the service road from the south; the gate code was reissued after the ninth inspection.
Basalt Haven lodged revision 5 on 2034-10-27.
The return for S-0104 is settled, sits at tier 2, and records a load of 838.
A housekeeping note against S-0104 asks that the cable run be rewalked before the next dry season.
Weather at Basalt Haven closed the approach for 40 days during the period under review and no readings were lost.
Calibration gear for S-0104 travels with the district van and is shared with 18 other sites.
An earlier clerk recorded Basalt Haven under a shortened spelling, and both forms still appear in the older indexes.
The survey party reached Basalt Haven on the sixth of the month and found the access track passable for light vehicles only.

### S-0105 -- Copper Gate

Calibration gear for S-0105 travels with the district van and is shared with 38 other sites.
The district file for Copper Gate shows revision 4 lodged on 2034-10-04.
For S-0105 the status is open, the tier is 5, and the load is 344.
The approach to Copper Gate crosses 10 field boundaries and the wayleave is held by the county.
The logbook kept at Copper Gate runs to 43 pages and the earlier volumes are held off site.
Drainage work near Copper Gate was completed without interruption to the record.
Telemetry from S-0105 arrives on the fifth relay and is batched nightly rather than streamed.
S-0105 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The enclosure at Copper Gate was rebuilt in timber after the old fencing was taken by the river.
A housekeeping note against S-0105 asks that the cable run be rewalked before the next dry season.
The notes for S-0105 mention a disused well inside the compound, capped and recorded but not surveyed.
An earlier clerk recorded Copper Gate under a shortened spelling, and both forms still appear in the older indexes.

### S-0106 -- Linden Bourne

Maintenance visits to S-0106 are scheduled quarterly and the first of those was carried out as planned.
Linden Bourne shares its power feed with the neighbouring pumping station and has its own cut-out.
Two of the anchors at Linden Bourne were replaced after the frost and the work is recorded in the district ledger.
Access to Linden Bourne is by the service road from the south; the gate code was reissued after the eighth inspection.
Signal strength at Linden Bourne has been marginal since the mast on the ridge was lowered.
Status settled: revision 2 for S-0106, lodged 2034-04-25.
Load 946 at tier 3 is what that revision carries for Linden Bourne.
Weather at Linden Bourne closed the approach for 39 days during the period under review and no readings were lost.
The fence line at Linden Bourne was rerun 14 metres to the east to clear the culvert.

### S-0107 -- Mellow Terrace

Telemetry from S-0107 arrives on the fourth relay and is batched nightly rather than streamed.
The access key for S-0107 is held at the district office and signed out per visit.
The instrument housing at Mellow Terrace is the original pattern and its door seal is checked each visit.
A visitor log is kept at Mellow Terrace and shows 22 entries for the period.
The district file for Mellow Terrace shows revision 1 lodged on 2034-04-16.
For S-0107 the status is settled, the tier is 3, and the load is 443.
A spare sensor head is kept at Mellow Terrace against the failure that took out the district in the previous cycle.
Maintenance visits to S-0107 are scheduled quarterly and the ninth of those was carried out as planned.
The fence line at Mellow Terrace was rerun 4 metres to the east to clear the culvert.
The approach to Mellow Terrace crosses 26 field boundaries and the wayleave is held by the county.

### S-0186 -- Ember Anchorage

Maintenance visits to S-0186 are scheduled quarterly and the eleventh of those was carried out as planned.
Calibration gear for S-0186 travels with the district van and is shared with 22 other sites.
The site plan for Ember Anchorage is the twelfth revision and supersedes the sketch held in the district folder.
A visitor log is kept at Ember Anchorage and shows 85 entries for the period.
On 2034-07-09 the district accepted revision 3 for Ember Anchorage and marked it settled.
S-0186 carries tier 9 on that revision and a load of 999.
The reconciliation sequence mark carried by this revision of S-0186 is 3.
An earlier clerk recorded Ember Anchorage under a shortened spelling, and both forms still appear in the older indexes.
Correspondence about S-0186 is filed under the district rather than under the site, which has caused confusion before.

### S-0109 -- Beacon Yard

Beacon Yard shares its power feed with the neighbouring pumping station and has its own cut-out.
A visitor log is kept at Beacon Yard and shows 40 entries for the period.
A spare sensor head is kept at Beacon Yard against the failure that took out the district in the previous cycle.
Tier 8 is where Beacon Yard sits on revision 5, whose status is settled.
The load on that revision of S-0109, lodged 2034-11-27, is 986.
Beacon Yard carries sequence mark 2 in this quarter's reconciliation.
Maintenance visits to S-0109 are scheduled quarterly and the fifth of those was carried out as planned.

### S-0110 -- Dusk Down

Signal strength at Dusk Down has been marginal since the mast on the ridge was lowered.
Status settled: revision 4 for S-0110, lodged 2034-08-06.
Load 668 at tier 8 is what that revision carries for Dusk Down.
Vegetation around Dusk Down is cut back twice a year under the standing arrangement.
An earlier clerk recorded Dusk Down under a shortened spelling, and both forms still appear in the older indexes.
Telemetry from S-0110 arrives on the thirteenth relay and is batched nightly rather than streamed.
The instrument housing at Dusk Down is the original pattern and its door seal is checked each visit.

### S-0111 -- Mellow Channel

A spare sensor head is kept at Mellow Channel against the failure that took out the district in the previous cycle.
Tier 4 is where Mellow Channel sits on revision 5, whose status is settled.
The load on that revision of S-0111, lodged 2034-05-22, is 258.
A calibration offset of 33 is recorded for S-0111 against the district standard.
The access key for S-0111 is held at the district office and signed out per visit.
The reading shelter at Mellow Channel takes water in heavy weather and the floor was relaid.
The survey party reached Mellow Channel on the first of the month and found the access track passable for light vehicles only.
The notes for S-0111 mention a disused well inside the compound, capped and recorded but not surveyed.
Weather at Mellow Channel closed the approach for 4 days during the period under review and no readings were lost.

### S-0112 -- Hazel Terrace

The logbook kept at Hazel Terrace runs to 29 pages and the earlier volumes are held off site.
Telemetry from S-0112 arrives on the second relay and is batched nightly rather than streamed.
Access to Hazel Terrace is by the service road from the south; the gate code was reissued after the seventh inspection.
The approach to Hazel Terrace crosses 4 field boundaries and the wayleave is held by the county.
A housekeeping note against S-0112 asks that the cable run be rewalked before the next dry season.
An earlier clerk recorded Hazel Terrace under a shortened spelling, and both forms still appear in the older indexes.
Revision 5 of the return for Hazel Terrace was lodged on 2034-10-15 and stands settled.
That revision places S-0112 in tier 7 and gives its load as 270.
A visitor log is kept at Hazel Terrace and shows 55 entries for the period.

### S-0113 -- Hazel Pound

Calibration gear for S-0113 travels with the district van and is shared with 37 other sites.
The district file for Hazel Pound shows revision 3 lodged on 2034-07-21.
For S-0113 the status is settled, the tier is 4, and the load is 393.
Two of the anchors at Hazel Pound were replaced after the frost and the work is recorded in the district ledger.
A spare sensor head is kept at Hazel Pound against the failure that took out the district in the previous cycle.
An earlier clerk recorded Hazel Pound under a shortened spelling, and both forms still appear in the older indexes.
The notes for S-0113 mention a disused well inside the compound, capped and recorded but not surveyed.
Access to Hazel Pound is by the service road from the south; the gate code was reissued after the thirteenth inspection.
The logbook kept at Hazel Pound runs to 73 pages and the earlier volumes are held off site.
The enclosure at Hazel Pound was rebuilt in timber after the old fencing was taken by the river.
The approach to Hazel Pound crosses 22 field boundaries and the wayleave is held by the county.
The instrument housing at Hazel Pound is the original pattern and its door seal is checked each visit.

### S-0114 -- Sedge Gully

A spare sensor head is kept at Sedge Gully against the failure that took out the district in the previous cycle.
Revision 4 of the return for Sedge Gully was lodged on 2034-09-01 and stands returned.
That revision places S-0114 in tier 7 and gives its load as 154.
Access to Sedge Gully is by the service road from the south; the gate code was reissued after the thirteenth inspection.
Sedge Gully shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0115 -- Bronze Delve

Calibration gear for S-0115 travels with the district van and is shared with 14 other sites.
The logbook kept at Bronze Delve runs to 85 pages and the earlier volumes are held off site.
The district file for Bronze Delve shows revision 5 lodged on 2034-05-01.
For S-0115 the status is withdrawn, the tier is 7, and the load is 782.
Maintenance visits to S-0115 are scheduled quarterly and the ninth of those was carried out as planned.
Weather at Bronze Delve closed the approach for 24 days during the period under review and no readings were lost.
A visitor log is kept at Bronze Delve and shows 49 entries for the period.
A spare sensor head is kept at Bronze Delve against the failure that took out the district in the previous cycle.
The notes for S-0115 mention a disused well inside the compound, capped and recorded but not surveyed.

### S-0116 -- Coral Landing

Signal strength at Coral Landing has been marginal since the mast on the ridge was lowered.
Weather at Coral Landing closed the approach for 2 days during the period under review and no readings were lost.
Correspondence shows the tenancy at Coral Landing was renewed for a further 4 years.
Coral Landing lodged revision 3 on 2034-11-25.
The return for S-0116 is withdrawn, sits at tier 5, and records a load of 495.
Maintenance visits to S-0116 are scheduled quarterly and the seventh of those was carried out as planned.
The fence line at Coral Landing was rerun 13 metres to the east to clear the culvert.

### S-0117 -- Nettle Mere

The notes for S-0117 mention a disused well inside the compound, capped and recorded but not surveyed.
The survey party reached Nettle Mere on the fourth of the month and found the access track passable for light vehicles only.
The access key for S-0117 is held at the district office and signed out per visit.
The instrument housing at Nettle Mere is the original pattern and its door seal is checked each visit.
The reading shelter at Nettle Mere takes water in heavy weather and the floor was relaid.
Signal strength at Nettle Mere has been marginal since the mast on the ridge was lowered.
Nettle Mere has been on the register since the first consolidation and its paperwork has never been reconstructed.
Tier 1 is where Nettle Mere sits on revision 6, whose status is withdrawn.
The load on that revision of S-0117, lodged 2034-01-06, is 711.
The offset applied to readings from S-0117 is 26 and has not been revised.
An earlier clerk recorded Nettle Mere under a shortened spelling, and both forms still appear in the older indexes.

### S-0118 -- Spindle Brae

The logbook kept at Spindle Brae runs to 3 pages and the earlier volumes are held off site.
The survey party reached Spindle Brae on the ninth of the month and found the access track passable for light vehicles only.
Signal strength at Spindle Brae has been marginal since the mast on the ridge was lowered.
Access to Spindle Brae is by the service road from the south; the gate code was reissued after the eighth inspection.
The approach to Spindle Brae crosses 6 field boundaries and the wayleave is held by the county.
Correspondence about S-0118 is filed under the district rather than under the site, which has caused confusion before.
The load recorded for S-0118 is 261, on a return at tier 4.
That return for Spindle Brae is revision 5, lodged 2034-10-07, and its status is settled.
A calibration offset of -37 is recorded for S-0118 against the district standard.
Spindle Brae shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0119 -- Ember Barrow

A spare sensor head is kept at Ember Barrow against the failure that took out the district in the previous cycle.
The fence line at Ember Barrow was rerun 37 metres to the east to clear the culvert.
Ember Barrow has been on the register since the first consolidation and its paperwork has never been reconstructed.
Maintenance visits to S-0119 are scheduled quarterly and the eighth of those was carried out as planned.
The enclosure at Ember Barrow was rebuilt in timber after the old fencing was taken by the river.
The load recorded for S-0119 is 828, on a return at tier 5.
That return for Ember Barrow is revision 3, lodged 2034-02-26, and its status is open.
Telemetry from S-0119 arrives on the third relay and is batched nightly rather than streamed.
Correspondence about S-0119 is filed under the district rather than under the site, which has caused confusion before.
S-0119 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Access to Ember Barrow is by the service road from the south; the gate code was reissued after the second inspection.
Calibration gear for S-0119 travels with the district van and is shared with 29 other sites.

### S-0120 -- Lichen Warren

A housekeeping note against S-0120 asks that the cable run be rewalked before the next dry season.
A visitor log is kept at Lichen Warren and shows 63 entries for the period.
The load recorded for S-0120 is 105, on a return at tier 8.
That return for Lichen Warren is revision 2, lodged 2034-10-09, and its status is withdrawn.
Vegetation around Lichen Warren is cut back twice a year under the standing arrangement.
Two of the anchors at Lichen Warren were replaced after the frost and the work is recorded in the district ledger.
The approach to Lichen Warren crosses 30 field boundaries and the wayleave is held by the county.
Maintenance visits to S-0120 are scheduled quarterly and the fourteenth of those was carried out as planned.
Correspondence shows the tenancy at Lichen Warren was renewed for a further 38 years.
The notes for S-0120 mention a disused well inside the compound, capped and recorded but not surveyed.

### S-0121 -- Flint Moor

Vegetation around Flint Moor is cut back twice a year under the standing arrangement.
The enclosure at Flint Moor was rebuilt in timber after the old fencing was taken by the river.
Revision 2 of the return for Flint Moor was lodged on 2034-04-17 and stands settled.
That revision places S-0121 in tier 3 and gives its load as 254.
The site plan for Flint Moor is the twelfth revision and supersedes the sketch held in the district folder.
The logbook kept at Flint Moor runs to 69 pages and the earlier volumes are held off site.
Signal strength at Flint Moor has been marginal since the mast on the ridge was lowered.
Flint Moor has been on the register since the first consolidation and its paperwork has never been reconstructed.
A visitor log is kept at Flint Moor and shows 3 entries for the period.
Correspondence shows the tenancy at Flint Moor was renewed for a further 80 years.

### S-0122 -- Dapple Spur

A visitor log is kept at Dapple Spur and shows 23 entries for the period.
Access to Dapple Spur is by the service road from the south; the gate code was reissued after the seventh inspection.
S-0122 appears at revision 2 with a load of 835.
That revision of Dapple Spur was lodged 2034-12-24, is settled, and places the station in tier 4.
Calibration gear for S-0122 travels with the district van and is shared with 34 other sites.
The instrument housing at Dapple Spur is the original pattern and its door seal is checked each visit.
S-0122 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Correspondence about S-0122 is filed under the district rather than under the site, which has caused confusion before.

### S-0123 -- Jasper Slade

The logbook kept at Jasper Slade runs to 70 pages and the earlier volumes are held off site.
Weather at Jasper Slade closed the approach for 13 days during the period under review and no readings were lost.
The instrument housing at Jasper Slade is the original pattern and its door seal is checked each visit.
The fence line at Jasper Slade was rerun 6 metres to the east to clear the culvert.
The load recorded for S-0123 is 103, on a return at tier 8.
That return for Jasper Slade is revision 4, lodged 2034-09-06, and its status is open.
An earlier clerk recorded Jasper Slade under a shortened spelling, and both forms still appear in the older indexes.
Two of the anchors at Jasper Slade were replaced after the frost and the work is recorded in the district ledger.
The survey party reached Jasper Slade on the third of the month and found the access track passable for light vehicles only.
A visitor log is kept at Jasper Slade and shows 58 entries for the period.
Maintenance visits to S-0123 are scheduled quarterly and the second of those was carried out as planned.

### S-0124 -- Cedar Gully

The survey party reached Cedar Gully on the ninth of the month and found the access track passable for light vehicles only.
Two of the anchors at Cedar Gully were replaced after the frost and the work is recorded in the district ledger.
The fence line at Cedar Gully was rerun 27 metres to the east to clear the culvert.
Correspondence shows the tenancy at Cedar Gully was renewed for a further 20 years.
The instrument housing at Cedar Gully is the original pattern and its door seal is checked each visit.
Weather at Cedar Gully closed the approach for 39 days during the period under review and no readings were lost.
The load recorded for S-0124 is 166, on a return at tier 2.
That return for Cedar Gully is revision 5, lodged 2034-03-11, and its status is settled.
Telemetry from S-0124 arrives on the second relay and is batched nightly rather than streamed.
Drainage work near Cedar Gully was completed without interruption to the record.

### S-0125 -- Osier Staithe

The site plan for Osier Staithe is the seventh revision and supersedes the sketch held in the district folder.
The load recorded for S-0125 is 236, on a return at tier 4.
That return for Osier Staithe is revision 1, lodged 2034-01-04, and its status is settled.
An earlier clerk recorded Osier Staithe under a shortened spelling, and both forms still appear in the older indexes.
A visitor log is kept at Osier Staithe and shows 27 entries for the period.
The access key for S-0125 is held at the district office and signed out per visit.
Correspondence about S-0125 is filed under the district rather than under the site, which has caused confusion before.

### S-0126 -- Fallow Hollow

The reading shelter at Fallow Hollow takes water in heavy weather and the floor was relaid.
Telemetry from S-0126 arrives on the fifth relay and is batched nightly rather than streamed.
Weather at Fallow Hollow closed the approach for 11 days during the period under review and no readings were lost.
Status provisional: revision 6 for S-0126, lodged 2034-01-15.
Load 265 at tier 4 is what that revision carries for Fallow Hollow.
A spare sensor head is kept at Fallow Hollow against the failure that took out the district in the previous cycle.
A visitor log is kept at Fallow Hollow and shows 79 entries for the period.

### S-0127 -- Quarry Copse

An earlier clerk recorded Quarry Copse under a shortened spelling, and both forms still appear in the older indexes.
A spare sensor head is kept at Quarry Copse against the failure that took out the district in the previous cycle.
Revision 1 of the return for Quarry Copse was lodged on 2034-04-22 and stands returned.
That revision places S-0127 in tier 5 and gives its load as 272.
Quarry Copse carries a calibration offset of 5 on the current instrument head.
Telemetry from S-0127 arrives on the tenth relay and is batched nightly rather than streamed.
The notes for S-0127 mention a disused well inside the compound, capped and recorded but not surveyed.
The access key for S-0127 is held at the district office and signed out per visit.
Correspondence about S-0127 is filed under the district rather than under the site, which has caused confusion before.
Drainage work near Quarry Copse was completed without interruption to the record.

### S-0128 -- Verdigris Sand

The access key for S-0128 is held at the district office and signed out per visit.
Calibration gear for S-0128 travels with the district van and is shared with 12 other sites.
Weather at Verdigris Sand closed the approach for 27 days during the period under review and no readings were lost.
The site plan for Verdigris Sand is the tenth revision and supersedes the sketch held in the district folder.
The approach to Verdigris Sand crosses 13 field boundaries and the wayleave is held by the county.
Verdigris Sand lodged revision 5 on 2034-11-19.
The return for S-0128 is settled, sits at tier 6, and records a load of 486.
Access to Verdigris Sand is by the service road from the south; the gate code was reissued after the twelfth inspection.
A visitor log is kept at Verdigris Sand and shows 70 entries for the period.

### S-0129 -- Sorrel Crossing

The survey party reached Sorrel Crossing on the third of the month and found the access track passable for light vehicles only.
The approach to Sorrel Crossing crosses 27 field boundaries and the wayleave is held by the county.
Sorrel Crossing has been on the register since the first consolidation and its paperwork has never been reconstructed.
The site plan for Sorrel Crossing is the tenth revision and supersedes the sketch held in the district folder.
The access key for S-0129 is held at the district office and signed out per visit.
Sorrel Crossing lodged revision 4 on 2034-06-24.
The return for S-0129 is settled, sits at tier 9, and records a load of 610.
The reconciliation sequence mark carried by this revision of S-0129 is 5.
The reading shelter at Sorrel Crossing takes water in heavy weather and the floor was relaid.

### S-0130 -- Kestrel Haven

Two of the anchors at Kestrel Haven were replaced after the frost and the work is recorded in the district ledger.
The reading shelter at Kestrel Haven takes water in heavy weather and the floor was relaid.
Telemetry from S-0130 arrives on the first relay and is batched nightly rather than streamed.
The enclosure at Kestrel Haven was rebuilt in timber after the old fencing was taken by the river.
Correspondence about S-0130 is filed under the district rather than under the site, which has caused confusion before.
S-0130 appears at revision 5 with a load of 342.
That revision of Kestrel Haven was lodged 2034-12-26, is settled, and places the station in tier 7.
A calibration offset of 25 is recorded for S-0130 against the district standard.
The logbook kept at Kestrel Haven runs to 58 pages and the earlier volumes are held off site.
The approach to Kestrel Haven crosses 11 field boundaries and the wayleave is held by the county.
Vegetation around Kestrel Haven is cut back twice a year under the standing arrangement.
The fence line at Kestrel Haven was rerun 34 metres to the east to clear the culvert.
S-0130 was one of the sites brought forward in the consolidation and its numbering reflects that order.

### S-0131 -- Granite Mere

A spare sensor head is kept at Granite Mere against the failure that took out the district in the previous cycle.
On 2034-01-02 the district accepted revision 3 for Granite Mere and marked it settled.
S-0131 carries tier 5 on that revision and a load of 226.
Telemetry from S-0131 arrives on the fifth relay and is batched nightly rather than streamed.
Correspondence about S-0131 is filed under the district rather than under the site, which has caused confusion before.
Signal strength at Granite Mere has been marginal since the mast on the ridge was lowered.

### S-0132 -- Basalt Ripple

The fence line at Basalt Ripple was rerun 35 metres to the east to clear the culvert.
On 2034-04-02 the district accepted revision 5 for Basalt Ripple and marked it withdrawn.
S-0132 carries tier 7 on that revision and a load of 905.
Two of the anchors at Basalt Ripple were replaced after the frost and the work is recorded in the district ledger.
Weather at Basalt Ripple closed the approach for 38 days during the period under review and no readings were lost.
Basalt Ripple has been on the register since the first consolidation and its paperwork has never been reconstructed.
The enclosure at Basalt Ripple was rebuilt in timber after the old fencing was taken by the river.
The logbook kept at Basalt Ripple runs to 41 pages and the earlier volumes are held off site.

### S-0133 -- Marram Coomb

The fence line at Marram Coomb was rerun 5 metres to the east to clear the culvert.
Revision 1 of the return for Marram Coomb was lodged on 2034-07-22 and stands settled.
That revision places S-0133 in tier 3 and gives its load as 660.
A visitor log is kept at Marram Coomb and shows 44 entries for the period.
Access to Marram Coomb is by the service road from the south; the gate code was reissued after the second inspection.
A spare sensor head is kept at Marram Coomb against the failure that took out the district in the previous cycle.
Calibration gear for S-0133 travels with the district van and is shared with 36 other sites.
Two of the anchors at Marram Coomb were replaced after the frost and the work is recorded in the district ledger.
The enclosure at Marram Coomb was rebuilt in timber after the old fencing was taken by the river.

### S-0134 -- Kestrel Weir

Two of the anchors at Kestrel Weir were replaced after the frost and the work is recorded in the district ledger.
The site plan for Kestrel Weir is the second revision and supersedes the sketch held in the district folder.
Calibration gear for S-0134 travels with the district van and is shared with 23 other sites.
On 2034-04-16 the district accepted revision 1 for Kestrel Weir and marked it settled.
S-0134 carries tier 4 on that revision and a load of 697.
The offset applied to readings from S-0134 is 8 and has not been revised.
Maintenance visits to S-0134 are scheduled quarterly and the first of those was carried out as planned.
Weather at Kestrel Weir closed the approach for 17 days during the period under review and no readings were lost.
A visitor log is kept at Kestrel Weir and shows 20 entries for the period.

### S-0135 -- Basalt Furlong

Signal strength at Basalt Furlong has been marginal since the mast on the ridge was lowered.
The site plan for Basalt Furlong is the seventh revision and supersedes the sketch held in the district folder.
Weather at Basalt Furlong closed the approach for 22 days during the period under review and no readings were lost.
Tier 7 is where Basalt Furlong sits on revision 1, whose status is withdrawn.
The load on that revision of S-0135, lodged 2034-05-17, is 262.
Correspondence about S-0135 is filed under the district rather than under the site, which has caused confusion before.
Basalt Furlong has been on the register since the first consolidation and its paperwork has never been reconstructed.
Access to Basalt Furlong is by the service road from the south; the gate code was reissued after the fifth inspection.

### S-0136 -- Garnet Headland

The notes for S-0136 mention a disused well inside the compound, capped and recorded but not surveyed.
Garnet Headland shares its power feed with the neighbouring pumping station and has its own cut-out.
Maintenance visits to S-0136 are scheduled quarterly and the twelfth of those was carried out as planned.
Garnet Headland has been on the register since the first consolidation and its paperwork has never been reconstructed.
S-0136 was one of the sites brought forward in the consolidation and its numbering reflects that order.
S-0136 appears at revision 6 with a load of 533.
That revision of Garnet Headland was lodged 2034-09-05, is settled, and places the station in tier 4.
Garnet Headland carries a calibration offset of -40 on the current instrument head.
Vegetation around Garnet Headland is cut back twice a year under the standing arrangement.
The logbook kept at Garnet Headland runs to 57 pages and the earlier volumes are held off site.

### S-0137 -- Nettle Crossing

The site plan for Nettle Crossing is the third revision and supersedes the sketch held in the district folder.
A spare sensor head is kept at Nettle Crossing against the failure that took out the district in the previous cycle.
The logbook kept at Nettle Crossing runs to 57 pages and the earlier volumes are held off site.
The access key for S-0137 is held at the district office and signed out per visit.
Status settled: revision 4 for S-0137, lodged 2034-12-06.
Load 720 at tier 1 is what that revision carries for Nettle Crossing.
A visitor log is kept at Nettle Crossing and shows 12 entries for the period.
Correspondence about S-0137 is filed under the district rather than under the site, which has caused confusion before.
The enclosure at Nettle Crossing was rebuilt in timber after the old fencing was taken by the river.

### S-0138 -- Cedar Shaw

The access key for S-0138 is held at the district office and signed out per visit.
The site plan for Cedar Shaw is the tenth revision and supersedes the sketch held in the district folder.
Drainage work near Cedar Shaw was completed without interruption to the record.
Cedar Shaw lodged revision 3 on 2034-02-02.
The return for S-0138 is provisional, sits at tier 6, and records a load of 613.
A visitor log is kept at Cedar Shaw and shows 68 entries for the period.
Maintenance visits to S-0138 are scheduled quarterly and the second of those was carried out as planned.
Cedar Shaw has been on the register since the first consolidation and its paperwork has never been reconstructed.
Cedar Shaw shares its power feed with the neighbouring pumping station and has its own cut-out.
Signal strength at Cedar Shaw has been marginal since the mast on the ridge was lowered.

### S-0139 -- Heather Ghyll

An earlier clerk recorded Heather Ghyll under a shortened spelling, and both forms still appear in the older indexes.
The access key for S-0139 is held at the district office and signed out per visit.
On 2034-12-08 the district accepted revision 5 for Heather Ghyll and marked it settled.
S-0139 carries tier 3 on that revision and a load of 867.
The logbook kept at Heather Ghyll runs to 62 pages and the earlier volumes are held off site.
The enclosure at Heather Ghyll was rebuilt in timber after the old fencing was taken by the river.
The reading shelter at Heather Ghyll takes water in heavy weather and the floor was relaid.
Access to Heather Ghyll is by the service road from the south; the gate code was reissued after the third inspection.
Telemetry from S-0139 arrives on the second relay and is batched nightly rather than streamed.
Signal strength at Heather Ghyll has been marginal since the mast on the ridge was lowered.

### S-0140 -- Pebble Rill

Pebble Rill has been on the register since the first consolidation and its paperwork has never been reconstructed.
A spare sensor head is kept at Pebble Rill against the failure that took out the district in the previous cycle.
S-0140 appears at revision 6 with a load of 462.
That revision of Pebble Rill was lodged 2034-01-11, is open, and places the station in tier 1.
Pebble Rill carries a calibration offset of 27 on the current instrument head.
The logbook kept at Pebble Rill runs to 15 pages and the earlier volumes are held off site.
The approach to Pebble Rill crosses 12 field boundaries and the wayleave is held by the county.
The notes for S-0140 mention a disused well inside the compound, capped and recorded but not surveyed.

### S-0141 -- Flint Reach

Telemetry from S-0141 arrives on the fifth relay and is batched nightly rather than streamed.
Correspondence about S-0141 is filed under the district rather than under the site, which has caused confusion before.
The logbook kept at Flint Reach runs to 70 pages and the earlier volumes are held off site.
Tier 3 is where Flint Reach sits on revision 5, whose status is provisional.
The load on that revision of S-0141, lodged 2034-07-16, is 678.
Weather at Flint Reach closed the approach for 26 days during the period under review and no readings were lost.

### S-0142 -- Dusk Anchorage

Dusk Anchorage shares its power feed with the neighbouring pumping station and has its own cut-out.
S-0142 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Access to Dusk Anchorage is by the service road from the south; the gate code was reissued after the ninth inspection.
Status provisional: revision 1 for S-0142, lodged 2034-02-21.
Load 619 at tier 7 is what that revision carries for Dusk Anchorage.
Dusk Anchorage has been on the register since the first consolidation and its paperwork has never been reconstructed.
A visitor log is kept at Dusk Anchorage and shows 39 entries for the period.
An earlier clerk recorded Dusk Anchorage under a shortened spelling, and both forms still appear in the older indexes.
The access key for S-0142 is held at the district office and signed out per visit.

### S-0143 -- Hazel Bight

The approach to Hazel Bight crosses 15 field boundaries and the wayleave is held by the county.
Signal strength at Hazel Bight has been marginal since the mast on the ridge was lowered.
Correspondence shows the tenancy at Hazel Bight was renewed for a further 80 years.
The district file for Hazel Bight shows revision 6 lodged on 2034-04-24.
For S-0143 the status is returned, the tier is 5, and the load is 366.
The enclosure at Hazel Bight was rebuilt in timber after the old fencing was taken by the river.
Hazel Bight shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0144 -- Copper Butte

Telemetry from S-0144 arrives on the eleventh relay and is batched nightly rather than streamed.
S-0144 appears at revision 4 with a load of 716.
That revision of Copper Butte was lodged 2034-02-22, is withdrawn, and places the station in tier 6.
The enclosure at Copper Butte was rebuilt in timber after the old fencing was taken by the river.
Copper Butte shares its power feed with the neighbouring pumping station and has its own cut-out.
Signal strength at Copper Butte has been marginal since the mast on the ridge was lowered.
The logbook kept at Copper Butte runs to 7 pages and the earlier volumes are held off site.
Maintenance visits to S-0144 are scheduled quarterly and the eleventh of those was carried out as planned.

### S-0145 -- Nettle Beck

A spare sensor head is kept at Nettle Beck against the failure that took out the district in the previous cycle.
Drainage work near Nettle Beck was completed without interruption to the record.
Correspondence about S-0145 is filed under the district rather than under the site, which has caused confusion before.
Vegetation around Nettle Beck is cut back twice a year under the standing arrangement.
The notes for S-0145 mention a disused well inside the compound, capped and recorded but not surveyed.
The reading shelter at Nettle Beck takes water in heavy weather and the floor was relaid.
A housekeeping note against S-0145 asks that the cable run be rewalked before the next dry season.
A visitor log is kept at Nettle Beck and shows 48 entries for the period.
Nettle Beck lodged revision 6 on 2034-03-03.
The return for S-0145 is settled, sits at tier 4, and records a load of 426.
The survey party reached Nettle Beck on the third of the month and found the access track passable for light vehicles only.

### S-0146 -- Russet Cleave

Russet Cleave has been on the register since the first consolidation and its paperwork has never been reconstructed.
The instrument housing at Russet Cleave is the original pattern and its door seal is checked each visit.
Calibration gear for S-0146 travels with the district van and is shared with 35 other sites.
An earlier clerk recorded Russet Cleave under a shortened spelling, and both forms still appear in the older indexes.
Vegetation around Russet Cleave is cut back twice a year under the standing arrangement.
Revision 5 of the return for Russet Cleave was lodged on 2034-07-13 and stands settled.
That revision places S-0146 in tier 1 and gives its load as 548.
The notes for S-0146 mention a disused well inside the compound, capped and recorded but not surveyed.

### S-0147 -- Linden Yard

The fence line at Linden Yard was rerun 34 metres to the east to clear the culvert.
The reading shelter at Linden Yard takes water in heavy weather and the floor was relaid.
Tier 1 is where Linden Yard sits on revision 5, whose status is settled.
The load on that revision of S-0147, lodged 2034-04-23, is 529.
Linden Yard has been on the register since the first consolidation and its paperwork has never been reconstructed.
An earlier clerk recorded Linden Yard under a shortened spelling, and both forms still appear in the older indexes.
Correspondence shows the tenancy at Linden Yard was renewed for a further 11 years.

### S-0148 -- Cedar Gate

Access to Cedar Gate is by the service road from the south; the gate code was reissued after the fifth inspection.
Weather at Cedar Gate closed the approach for 38 days during the period under review and no readings were lost.
The load recorded for S-0148 is 314, on a return at tier 8.
That return for Cedar Gate is revision 2, lodged 2034-05-23, and its status is returned.
Cedar Gate has been on the register since the first consolidation and its paperwork has never been reconstructed.
The instrument housing at Cedar Gate is the original pattern and its door seal is checked each visit.
Telemetry from S-0148 arrives on the second relay and is batched nightly rather than streamed.
Vegetation around Cedar Gate is cut back twice a year under the standing arrangement.
Correspondence shows the tenancy at Cedar Gate was renewed for a further 55 years.

### S-0149 -- Clover Hallow

Correspondence shows the tenancy at Clover Hallow was renewed for a further 86 years.
The access key for S-0149 is held at the district office and signed out per visit.
The notes for S-0149 mention a disused well inside the compound, capped and recorded but not surveyed.
A spare sensor head is kept at Clover Hallow against the failure that took out the district in the previous cycle.
Tier 7 is where Clover Hallow sits on revision 6, whose status is settled.
The load on that revision of S-0149, lodged 2034-01-02, is 214.
Clover Hallow carries sequence mark 4 in this quarter's reconciliation.
A housekeeping note against S-0149 asks that the cable run be rewalked before the next dry season.
The enclosure at Clover Hallow was rebuilt in timber after the old fencing was taken by the river.

### S-0150 -- Tamarisk Shoal

Signal strength at Tamarisk Shoal has been marginal since the mast on the ridge was lowered.
The load recorded for S-0150 is 823, on a return at tier 6.
That return for Tamarisk Shoal is revision 5, lodged 2034-01-24, and its status is open.
The return for Tamarisk Shoal replaces an entry formerly held at S-0990, a code retired at the consolidation and never reissued.
Drainage work near Tamarisk Shoal was completed without interruption to the record.
The enclosure at Tamarisk Shoal was rebuilt in timber after the old fencing was taken by the river.
A visitor log is kept at Tamarisk Shoal and shows 26 entries for the period.
Tamarisk Shoal shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0151 -- Linden Terrace

Two of the anchors at Linden Terrace were replaced after the frost and the work is recorded in the district ledger.
A housekeeping note against S-0151 asks that the cable run be rewalked before the next dry season.
Correspondence about S-0151 is filed under the district rather than under the site, which has caused confusion before.
The load recorded for S-0151 is 538, on a return at tier 9.
That return for Linden Terrace is revision 5, lodged 2034-09-07, and its status is settled.
The notes for S-0151 mention a disused well inside the compound, capped and recorded but not surveyed.
The fence line at Linden Terrace was rerun 16 metres to the east to clear the culvert.
The instrument housing at Linden Terrace is the original pattern and its door seal is checked each visit.
Maintenance visits to S-0151 are scheduled quarterly and the second of those was carried out as planned.
The logbook kept at Linden Terrace runs to 5 pages and the earlier volumes are held off site.
Calibration gear for S-0151 travels with the district van and is shared with 40 other sites.
Access to Linden Terrace is by the service road from the south; the gate code was reissued after the seventh inspection.

### S-0152 -- Tamarisk Bank

Drainage work near Tamarisk Bank was completed without interruption to the record.
Two of the anchors at Tamarisk Bank were replaced after the frost and the work is recorded in the district ledger.
An earlier clerk recorded Tamarisk Bank under a shortened spelling, and both forms still appear in the older indexes.
The fence line at Tamarisk Bank was rerun 6 metres to the east to clear the culvert.
Status settled: revision 6 for S-0152, lodged 2034-09-11.
Load 839 at tier 6 is what that revision carries for Tamarisk Bank.
A visitor log is kept at Tamarisk Bank and shows 88 entries for the period.
Signal strength at Tamarisk Bank has been marginal since the mast on the ridge was lowered.

### S-0153 -- Yarrow Pike

Correspondence shows the tenancy at Yarrow Pike was renewed for a further 60 years.
S-0153 was one of the sites brought forward in the consolidation and its numbering reflects that order.
A housekeeping note against S-0153 asks that the cable run be rewalked before the next dry season.
Vegetation around Yarrow Pike is cut back twice a year under the standing arrangement.
The district file for Yarrow Pike shows revision 6 lodged on 2034-11-16.
For S-0153 the status is withdrawn, the tier is 3, and the load is 775.
A spare sensor head is kept at Yarrow Pike against the failure that took out the district in the previous cycle.

### S-0154 -- Midland Shaw

The site plan for Midland Shaw is the seventh revision and supersedes the sketch held in the district folder.
Midland Shaw has been on the register since the first consolidation and its paperwork has never been reconstructed.
A spare sensor head is kept at Midland Shaw against the failure that took out the district in the previous cycle.
The district file for Midland Shaw shows revision 1 lodged on 2034-10-14.
For S-0154 the status is settled, the tier is 2, and the load is 830.
Correspondence about S-0154 is filed under the district rather than under the site, which has caused confusion before.
Calibration gear for S-0154 travels with the district van and is shared with 18 other sites.
Midland Shaw shares its power feed with the neighbouring pumping station and has its own cut-out.
Two of the anchors at Midland Shaw were replaced after the frost and the work is recorded in the district ledger.

### S-0155 -- Rowan Narrows

Maintenance visits to S-0155 are scheduled quarterly and the ninth of those was carried out as planned.
Weather at Rowan Narrows closed the approach for 35 days during the period under review and no readings were lost.
S-0155 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The enclosure at Rowan Narrows was rebuilt in timber after the old fencing was taken by the river.
Drainage work near Rowan Narrows was completed without interruption to the record.
Correspondence shows the tenancy at Rowan Narrows was renewed for a further 67 years.
The site plan for Rowan Narrows is the ninth revision and supersedes the sketch held in the district folder.
The district file for Rowan Narrows shows revision 4 lodged on 2034-11-04.
For S-0155 the status is withdrawn, the tier is 8, and the load is 964.
The access key for S-0155 is held at the district office and signed out per visit.

### S-0156 -- Midland Sand

A housekeeping note against S-0156 asks that the cable run be rewalked before the next dry season.
A visitor log is kept at Midland Sand and shows 10 entries for the period.
The survey party reached Midland Sand on the fourteenth of the month and found the access track passable for light vehicles only.
The enclosure at Midland Sand was rebuilt in timber after the old fencing was taken by the river.
The reading shelter at Midland Sand takes water in heavy weather and the floor was relaid.
Status settled: revision 6 for S-0156, lodged 2034-08-16.
Load 797 at tier 1 is what that revision carries for Midland Sand.
Vegetation around Midland Sand is cut back twice a year under the standing arrangement.
The notes for S-0156 mention a disused well inside the compound, capped and recorded but not surveyed.
The approach to Midland Sand crosses 23 field boundaries and the wayleave is held by the county.
The access key for S-0156 is held at the district office and signed out per visit.

### S-0157 -- Verdigris Bank

Correspondence about S-0157 is filed under the district rather than under the site, which has caused confusion before.
The instrument housing at Verdigris Bank is the original pattern and its door seal is checked each visit.
The reading shelter at Verdigris Bank takes water in heavy weather and the floor was relaid.
The load recorded for S-0157 is 877, on a return at tier 6.
That return for Verdigris Bank is revision 1, lodged 2034-04-17, and its status is open.
Vegetation around Verdigris Bank is cut back twice a year under the standing arrangement.
A visitor log is kept at Verdigris Bank and shows 44 entries for the period.
The fence line at Verdigris Bank was rerun 27 metres to the east to clear the culvert.
A housekeeping note against S-0157 asks that the cable run be rewalked before the next dry season.
Signal strength at Verdigris Bank has been marginal since the mast on the ridge was lowered.
The enclosure at Verdigris Bank was rebuilt in timber after the old fencing was taken by the river.
Telemetry from S-0157 arrives on the first relay and is batched nightly rather than streamed.

### S-0158 -- Saffron Haven

S-0158 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The load recorded for S-0158 is 761, on a return at tier 1.
That return for Saffron Haven is revision 2, lodged 2034-10-25, and its status is returned.
A calibration offset of -11 is recorded for S-0158 against the district standard.
A visitor log is kept at Saffron Haven and shows 44 entries for the period.
The access key for S-0158 is held at the district office and signed out per visit.
Correspondence about S-0158 is filed under the district rather than under the site, which has caused confusion before.
The reading shelter at Saffron Haven takes water in heavy weather and the floor was relaid.

### S-0159 -- Umber Thwaite

The logbook kept at Umber Thwaite runs to 60 pages and the earlier volumes are held off site.
Telemetry from S-0159 arrives on the sixth relay and is batched nightly rather than streamed.
S-0159 was one of the sites brought forward in the consolidation and its numbering reflects that order.
An earlier clerk recorded Umber Thwaite under a shortened spelling, and both forms still appear in the older indexes.
A spare sensor head is kept at Umber Thwaite against the failure that took out the district in the previous cycle.
The notes for S-0159 mention a disused well inside the compound, capped and recorded but not surveyed.
Umber Thwaite has been on the register since the first consolidation and its paperwork has never been reconstructed.
Status settled: revision 3 for S-0159, lodged 2034-07-06.
Load 252 at tier 4 is what that revision carries for Umber Thwaite.
Calibration gear for S-0159 travels with the district van and is shared with 14 other sites.
Two of the anchors at Umber Thwaite were replaced after the frost and the work is recorded in the district ledger.

### S-0160 -- Yarrow Knap

Telemetry from S-0160 arrives on the seventh relay and is batched nightly rather than streamed.
Yarrow Knap shares its power feed with the neighbouring pumping station and has its own cut-out.
Revision 2 of the return for Yarrow Knap was lodged on 2034-02-27 and stands settled.
That revision places S-0160 in tier 3 and gives its load as 536.
An earlier clerk recorded Yarrow Knap under a shortened spelling, and both forms still appear in the older indexes.
Drainage work near Yarrow Knap was completed without interruption to the record.
The enclosure at Yarrow Knap was rebuilt in timber after the old fencing was taken by the river.
Yarrow Knap has been on the register since the first consolidation and its paperwork has never been reconstructed.
The survey party reached Yarrow Knap on the eighth of the month and found the access track passable for light vehicles only.

### S-0161 -- Teasel Slade

The notes for S-0161 mention a disused well inside the compound, capped and recorded but not surveyed.
Two of the anchors at Teasel Slade were replaced after the frost and the work is recorded in the district ledger.
Vegetation around Teasel Slade is cut back twice a year under the standing arrangement.
A housekeeping note against S-0161 asks that the cable run be rewalked before the next dry season.
Weather at Teasel Slade closed the approach for 23 days during the period under review and no readings were lost.
The logbook kept at Teasel Slade runs to 24 pages and the earlier volumes are held off site.
Teasel Slade has been on the register since the first consolidation and its paperwork has never been reconstructed.
The approach to Teasel Slade crosses 11 field boundaries and the wayleave is held by the county.
Maintenance visits to S-0161 are scheduled quarterly and the fourth of those was carried out as planned.
S-0161 appears at revision 5 with a load of 699.
That revision of Teasel Slade was lodged 2034-05-06, is settled, and places the station in tier 3.
Teasel Slade carries a calibration offset of 31 on the current instrument head.
A spare sensor head is kept at Teasel Slade against the failure that took out the district in the previous cycle.

### S-0162 -- Coral Narrows

The logbook kept at Coral Narrows runs to 76 pages and the earlier volumes are held off site.
Coral Narrows shares its power feed with the neighbouring pumping station and has its own cut-out.
S-0162 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Telemetry from S-0162 arrives on the seventh relay and is batched nightly rather than streamed.
Access to Coral Narrows is by the service road from the south; the gate code was reissued after the tenth inspection.
Correspondence about S-0162 is filed under the district rather than under the site, which has caused confusion before.
The load recorded for S-0162 is 544, on a return at tier 2.
That return for Coral Narrows is revision 2, lodged 2034-11-20, and its status is settled.
The offset applied to readings from S-0162 is -8 and has not been revised.
Correspondence shows the tenancy at Coral Narrows was renewed for a further 44 years.

### S-0163 -- Marram Warren

Marram Warren has been on the register since the first consolidation and its paperwork has never been reconstructed.
The survey party reached Marram Warren on the fourteenth of the month and found the access track passable for light vehicles only.
The access key for S-0163 is held at the district office and signed out per visit.
The notes for S-0163 mention a disused well inside the compound, capped and recorded but not surveyed.
Signal strength at Marram Warren has been marginal since the mast on the ridge was lowered.
The load recorded for S-0163 is 731, on a return at tier 1.
That return for Marram Warren is revision 6, lodged 2034-01-06, and its status is open.
The instrument housing at Marram Warren is the original pattern and its door seal is checked each visit.
Vegetation around Marram Warren is cut back twice a year under the standing arrangement.

### S-0164 -- Calder Shaw

Calder Shaw shares its power feed with the neighbouring pumping station and has its own cut-out.
S-0164 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The site plan for Calder Shaw is the seventh revision and supersedes the sketch held in the district folder.
Vegetation around Calder Shaw is cut back twice a year under the standing arrangement.
The instrument housing at Calder Shaw is the original pattern and its door seal is checked each visit.
Correspondence shows the tenancy at Calder Shaw was renewed for a further 82 years.
The district file for Calder Shaw shows revision 4 lodged on 2034-02-11.
For S-0164 the status is provisional, the tier is 5, and the load is 227.
The offset applied to readings from S-0164 is 13 and has not been revised.
Signal strength at Calder Shaw has been marginal since the mast on the ridge was lowered.
An earlier clerk recorded Calder Shaw under a shortened spelling, and both forms still appear in the older indexes.
The reading shelter at Calder Shaw takes water in heavy weather and the floor was relaid.

### S-0165 -- Bramble Pike

A spare sensor head is kept at Bramble Pike against the failure that took out the district in the previous cycle.
The site plan for Bramble Pike is the ninth revision and supersedes the sketch held in the district folder.
The fence line at Bramble Pike was rerun 18 metres to the east to clear the culvert.
Bramble Pike lodged revision 1 on 2034-02-13.
The return for S-0165 is open, sits at tier 7, and records a load of 791.
Access to Bramble Pike is by the service road from the south; the gate code was reissued after the twelfth inspection.
Vegetation around Bramble Pike is cut back twice a year under the standing arrangement.
Signal strength at Bramble Pike has been marginal since the mast on the ridge was lowered.
The enclosure at Bramble Pike was rebuilt in timber after the old fencing was taken by the river.
The survey party reached Bramble Pike on the fourteenth of the month and found the access track passable for light vehicles only.
The approach to Bramble Pike crosses 3 field boundaries and the wayleave is held by the county.

### S-0128 -- Quarry Pound

Signal strength at Quarry Pound has been marginal since the mast on the ridge was lowered.
Revision 5 of the return for Quarry Pound was lodged on 2034-03-17 and stands settled.
That revision places S-0128 in tier 7 and gives its load as 531.
The site plan for Quarry Pound is the sixth revision and supersedes the sketch held in the district folder.
The fence line at Quarry Pound was rerun 17 metres to the east to clear the culvert.
An earlier clerk recorded Quarry Pound under a shortened spelling, and both forms still appear in the older indexes.
The logbook kept at Quarry Pound runs to 25 pages and the earlier volumes are held off site.

### S-0149 -- Spindle Reach

Spindle Reach has been on the register since the first consolidation and its paperwork has never been reconstructed.
Spindle Reach shares its power feed with the neighbouring pumping station and has its own cut-out.
The instrument housing at Spindle Reach is the original pattern and its door seal is checked each visit.
On 2034-01-10 the district accepted revision 4 for Spindle Reach and marked it settled.
S-0149 carries tier 5 on that revision and a load of 846.
The reconciliation sequence mark carried by this revision of S-0149 is 4.
Maintenance visits to S-0149 are scheduled quarterly and the sixth of those was carried out as planned.
Correspondence shows the tenancy at Spindle Reach was renewed for a further 25 years.
Telemetry from S-0149 arrives on the twelfth relay and is batched nightly rather than streamed.
Drainage work near Spindle Reach was completed without interruption to the record.

### S-0168 -- Dusk Glade

Correspondence about S-0168 is filed under the district rather than under the site, which has caused confusion before.
On 2034-12-26 the district accepted revision 5 for Dusk Glade and marked it settled.
S-0168 carries tier 8 on that revision and a load of 856.
Dusk Glade carries sequence mark 1 in this quarter's reconciliation.
The instrument housing at Dusk Glade is the original pattern and its door seal is checked each visit.
Drainage work near Dusk Glade was completed without interruption to the record.
Dusk Glade has been on the register since the first consolidation and its paperwork has never been reconstructed.
A housekeeping note against S-0168 asks that the cable run be rewalked before the next dry season.

### S-0169 -- Indigo Butte

The reading shelter at Indigo Butte takes water in heavy weather and the floor was relaid.
Access to Indigo Butte is by the service road from the south; the gate code was reissued after the sixth inspection.
Indigo Butte has been on the register since the first consolidation and its paperwork has never been reconstructed.
Drainage work near Indigo Butte was completed without interruption to the record.
A spare sensor head is kept at Indigo Butte against the failure that took out the district in the previous cycle.
Status settled: revision 4 for S-0169, lodged 2034-08-11.
Load 280 at tier 8 is what that revision carries for Indigo Butte.
The offset applied to readings from S-0169 is -28 and has not been revised.
This revision of S-0169 is marked 6 in the reconciliation sequence.
Calibration gear for S-0169 travels with the district van and is shared with 38 other sites.
The approach to Indigo Butte crosses 25 field boundaries and the wayleave is held by the county.

### S-0170 -- Hollow Culvert

The instrument housing at Hollow Culvert is the original pattern and its door seal is checked each visit.
Calibration gear for S-0170 travels with the district van and is shared with 15 other sites.
Telemetry from S-0170 arrives on the tenth relay and is batched nightly rather than streamed.
Correspondence about S-0170 is filed under the district rather than under the site, which has caused confusion before.
Hollow Culvert lodged revision 2 on 2034-02-17.
The return for S-0170 is provisional, sits at tier 2, and records a load of 793.
Hollow Culvert shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0171 -- Kestrel Glade

The access key for S-0171 is held at the district office and signed out per visit.
Status settled: revision 6 for S-0171, lodged 2034-02-21.
Load 301 at tier 9 is what that revision carries for Kestrel Glade.
A visitor log is kept at Kestrel Glade and shows 47 entries for the period.
Signal strength at Kestrel Glade has been marginal since the mast on the ridge was lowered.
Drainage work near Kestrel Glade was completed without interruption to the record.
Telemetry from S-0171 arrives on the ninth relay and is batched nightly rather than streamed.

### S-0172 -- Linden Mill

Linden Mill shares its power feed with the neighbouring pumping station and has its own cut-out.
On 2034-01-16 the district accepted revision 1 for Linden Mill and marked it settled.
S-0172 carries tier 2 on that revision and a load of 908.
The survey party reached Linden Mill on the third of the month and found the access track passable for light vehicles only.
The approach to Linden Mill crosses 39 field boundaries and the wayleave is held by the county.
Signal strength at Linden Mill has been marginal since the mast on the ridge was lowered.
Telemetry from S-0172 arrives on the tenth relay and is batched nightly rather than streamed.

### S-0173 -- Brindle Rill

Brindle Rill has been on the register since the first consolidation and its paperwork has never been reconstructed.
Correspondence shows the tenancy at Brindle Rill was renewed for a further 36 years.
S-0173 appears at revision 6 with a load of 938.
That revision of Brindle Rill was lodged 2034-01-13, is settled, and places the station in tier 4.
The instrument housing at Brindle Rill is the original pattern and its door seal is checked each visit.
The reading shelter at Brindle Rill takes water in heavy weather and the floor was relaid.
The site plan for Brindle Rill is the fourth revision and supersedes the sketch held in the district folder.
A visitor log is kept at Brindle Rill and shows 71 entries for the period.
The survey party reached Brindle Rill on the tenth of the month and found the access track passable for light vehicles only.
The notes for S-0173 mention a disused well inside the compound, capped and recorded but not surveyed.
Vegetation around Brindle Rill is cut back twice a year under the standing arrangement.
The access key for S-0173 is held at the district office and signed out per visit.

### S-0174 -- Teasel Strand

Drainage work near Teasel Strand was completed without interruption to the record.
Correspondence shows the tenancy at Teasel Strand was renewed for a further 71 years.
Telemetry from S-0174 arrives on the ninth relay and is batched nightly rather than streamed.
Two of the anchors at Teasel Strand were replaced after the frost and the work is recorded in the district ledger.
Correspondence about S-0174 is filed under the district rather than under the site, which has caused confusion before.
Revision 3 of the return for Teasel Strand was lodged on 2034-11-14 and stands settled.
That revision places S-0174 in tier 4 and gives its load as 855.
The instrument housing at Teasel Strand is the original pattern and its door seal is checked each visit.
The enclosure at Teasel Strand was rebuilt in timber after the old fencing was taken by the river.

### S-0175 -- Nettle Pound

The logbook kept at Nettle Pound runs to 3 pages and the earlier volumes are held off site.
The fence line at Nettle Pound was rerun 11 metres to the east to clear the culvert.
The survey party reached Nettle Pound on the eighth of the month and found the access track passable for light vehicles only.
On 2034-08-18 the district accepted revision 4 for Nettle Pound and marked it returned.
S-0175 carries tier 5 on that revision and a load of 188.
Correspondence shows the tenancy at Nettle Pound was renewed for a further 90 years.
A visitor log is kept at Nettle Pound and shows 40 entries for the period.
Nettle Pound has been on the register since the first consolidation and its paperwork has never been reconstructed.
Calibration gear for S-0175 travels with the district van and is shared with 3 other sites.
Weather at Nettle Pound closed the approach for 19 days during the period under review and no readings were lost.

### S-0176 -- Beacon Wharf

The site plan for Beacon Wharf is the fourteenth revision and supersedes the sketch held in the district folder.
The access key for S-0176 is held at the district office and signed out per visit.
A housekeeping note against S-0176 asks that the cable run be rewalked before the next dry season.
Correspondence about S-0176 is filed under the district rather than under the site, which has caused confusion before.
The district file for Beacon Wharf shows revision 5 lodged on 2034-07-12.
For S-0176 the status is settled, the tier is 3, and the load is 732.
Access to Beacon Wharf is by the service road from the south; the gate code was reissued after the twelfth inspection.
Beacon Wharf has been on the register since the first consolidation and its paperwork has never been reconstructed.
Maintenance visits to S-0176 are scheduled quarterly and the second of those was carried out as planned.
Correspondence shows the tenancy at Beacon Wharf was renewed for a further 20 years.
The notes for S-0176 mention a disused well inside the compound, capped and recorded but not surveyed.

### S-0177 -- Ridge Dingle

Access to Ridge Dingle is by the service road from the south; the gate code was reissued after the sixth inspection.
Ridge Dingle shares its power feed with the neighbouring pumping station and has its own cut-out.
On 2034-07-11 the district accepted revision 1 for Ridge Dingle and marked it settled.
S-0177 carries tier 3 on that revision and a load of 198.
A calibration offset of 39 is recorded for S-0177 against the district standard.
Signal strength at Ridge Dingle has been marginal since the mast on the ridge was lowered.
A spare sensor head is kept at Ridge Dingle against the failure that took out the district in the previous cycle.
A housekeeping note against S-0177 asks that the cable run be rewalked before the next dry season.
Maintenance visits to S-0177 are scheduled quarterly and the sixth of those was carried out as planned.
Two of the anchors at Ridge Dingle were replaced after the frost and the work is recorded in the district ledger.
Correspondence about S-0177 is filed under the district rather than under the site, which has caused confusion before.

### S-0178 -- Tamarisk Ford

Vegetation around Tamarisk Ford is cut back twice a year under the standing arrangement.
The notes for S-0178 mention a disused well inside the compound, capped and recorded but not surveyed.
The load recorded for S-0178 is 820, on a return at tier 3.
That return for Tamarisk Ford is revision 1, lodged 2034-05-17, and its status is returned.
S-0178 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The instrument housing at Tamarisk Ford is the original pattern and its door seal is checked each visit.
Correspondence about S-0178 is filed under the district rather than under the site, which has caused confusion before.
The reading shelter at Tamarisk Ford takes water in heavy weather and the floor was relaid.
Two of the anchors at Tamarisk Ford were replaced after the frost and the work is recorded in the district ledger.
Signal strength at Tamarisk Ford has been marginal since the mast on the ridge was lowered.
A housekeeping note against S-0178 asks that the cable run be rewalked before the next dry season.
Telemetry from S-0178 arrives on the thirteenth relay and is batched nightly rather than streamed.

### S-0179 -- Quince Rill

The enclosure at Quince Rill was rebuilt in timber after the old fencing was taken by the river.
The approach to Quince Rill crosses 25 field boundaries and the wayleave is held by the county.
Signal strength at Quince Rill has been marginal since the mast on the ridge was lowered.
Telemetry from S-0179 arrives on the eighth relay and is batched nightly rather than streamed.
Drainage work near Quince Rill was completed without interruption to the record.
Quince Rill lodged revision 4 on 2034-01-15.
The return for S-0179 is provisional, sits at tier 6, and records a load of 189.
The site plan for Quince Rill is the second revision and supersedes the sketch held in the district folder.
The instrument housing at Quince Rill is the original pattern and its door seal is checked each visit.
Correspondence shows the tenancy at Quince Rill was renewed for a further 68 years.
The fence line at Quince Rill was rerun 39 metres to the east to clear the culvert.
The survey party reached Quince Rill on the seventh of the month and found the access track passable for light vehicles only.

### S-0180 -- Teasel Pound

Telemetry from S-0180 arrives on the fourth relay and is batched nightly rather than streamed.
A spare sensor head is kept at Teasel Pound against the failure that took out the district in the previous cycle.
Drainage work near Teasel Pound was completed without interruption to the record.
Correspondence about S-0180 is filed under the district rather than under the site, which has caused confusion before.
Teasel Pound shares its power feed with the neighbouring pumping station and has its own cut-out.
Weather at Teasel Pound closed the approach for 4 days during the period under review and no readings were lost.
S-0180 was one of the sites brought forward in the consolidation and its numbering reflects that order.
An earlier clerk recorded Teasel Pound under a shortened spelling, and both forms still appear in the older indexes.
The instrument housing at Teasel Pound is the original pattern and its door seal is checked each visit.
Revision 2 of the return for Teasel Pound was lodged on 2034-04-06 and stands returned.
That revision places S-0180 in tier 3 and gives its load as 602.
The access key for S-0180 is held at the district office and signed out per visit.
The enclosure at Teasel Pound was rebuilt in timber after the old fencing was taken by the river.

### S-0181 -- Fallow Knap

The notes for S-0181 mention a disused well inside the compound, capped and recorded but not surveyed.
Correspondence shows the tenancy at Fallow Knap was renewed for a further 34 years.
Tier 5 is where Fallow Knap sits on revision 1, whose status is open.
The load on that revision of S-0181, lodged 2034-03-01, is 338.
Maintenance visits to S-0181 are scheduled quarterly and the thirteenth of those was carried out as planned.
An earlier clerk recorded Fallow Knap under a shortened spelling, and both forms still appear in the older indexes.
The survey party reached Fallow Knap on the second of the month and found the access track passable for light vehicles only.
The site plan for Fallow Knap is the twelfth revision and supersedes the sketch held in the district folder.
Signal strength at Fallow Knap has been marginal since the mast on the ridge was lowered.

### S-0182 -- Dusk Brook

The approach to Dusk Brook crosses 9 field boundaries and the wayleave is held by the county.
Drainage work near Dusk Brook was completed without interruption to the record.
A visitor log is kept at Dusk Brook and shows 4 entries for the period.
The logbook kept at Dusk Brook runs to 37 pages and the earlier volumes are held off site.
The site plan for Dusk Brook is the third revision and supersedes the sketch held in the district folder.
Revision 3 of the return for Dusk Brook was lodged on 2034-06-20 and stands settled.
That revision places S-0182 in tier 4 and gives its load as 806.
Vegetation around Dusk Brook is cut back twice a year under the standing arrangement.
Correspondence about S-0182 is filed under the district rather than under the site, which has caused confusion before.
The instrument housing at Dusk Brook is the original pattern and its door seal is checked each visit.
Dusk Brook shares its power feed with the neighbouring pumping station and has its own cut-out.
A spare sensor head is kept at Dusk Brook against the failure that took out the district in the previous cycle.

### S-0183 -- Nettle Landing

A spare sensor head is kept at Nettle Landing against the failure that took out the district in the previous cycle.
S-0183 appears at revision 1 with a load of 144.
That revision of Nettle Landing was lodged 2034-05-25, is provisional, and places the station in tier 9.
The notes for S-0183 mention a disused well inside the compound, capped and recorded but not surveyed.
The fence line at Nettle Landing was rerun 17 metres to the east to clear the culvert.
Correspondence about S-0183 is filed under the district rather than under the site, which has caused confusion before.
The site plan for Nettle Landing is the thirteenth revision and supersedes the sketch held in the district folder.
Access to Nettle Landing is by the service road from the south; the gate code was reissued after the seventh inspection.

### S-0184 -- Sedge Weir

The access key for S-0184 is held at the district office and signed out per visit.
Correspondence about S-0184 is filed under the district rather than under the site, which has caused confusion before.
The reading shelter at Sedge Weir takes water in heavy weather and the floor was relaid.
Sedge Weir shares its power feed with the neighbouring pumping station and has its own cut-out.
The enclosure at Sedge Weir was rebuilt in timber after the old fencing was taken by the river.
Signal strength at Sedge Weir has been marginal since the mast on the ridge was lowered.
Tier 4 is where Sedge Weir sits on revision 1, whose status is settled.
The load on that revision of S-0184, lodged 2034-06-10, is 710.
Correspondence shows the tenancy at Sedge Weir was renewed for a further 37 years.
Sedge Weir has been on the register since the first consolidation and its paperwork has never been reconstructed.
S-0184 was one of the sites brought forward in the consolidation and its numbering reflects that order.

### S-0129 -- Mellow Warren

The enclosure at Mellow Warren was rebuilt in timber after the old fencing was taken by the river.
Telemetry from S-0129 arrives on the eleventh relay and is batched nightly rather than streamed.
Calibration gear for S-0129 travels with the district van and is shared with 19 other sites.
The fence line at Mellow Warren was rerun 25 metres to the east to clear the culvert.
The reading shelter at Mellow Warren takes water in heavy weather and the floor was relaid.
Tier 8 is where Mellow Warren sits on revision 3, whose status is settled.
The load on that revision of S-0129, lodged 2034-03-24, is 453.
This revision of S-0129 is marked 5 in the reconciliation sequence.
An earlier clerk recorded Mellow Warren under a shortened spelling, and both forms still appear in the older indexes.
The approach to Mellow Warren crosses 24 field boundaries and the wayleave is held by the county.
Correspondence shows the tenancy at Mellow Warren was renewed for a further 27 years.
Mellow Warren has been on the register since the first consolidation and its paperwork has never been reconstructed.
Signal strength at Mellow Warren has been marginal since the mast on the ridge was lowered.

### S-0186 -- Beacon Ferry

Two of the anchors at Beacon Ferry were replaced after the frost and the work is recorded in the district ledger.
The notes for S-0186 mention a disused well inside the compound, capped and recorded but not surveyed.
Status settled: revision 4 for S-0186, lodged 2034-09-09.
Load 880 at tier 5 is what that revision carries for Beacon Ferry.
This revision of S-0186 is marked 3 in the reconciliation sequence.
Calibration gear for S-0186 travels with the district van and is shared with 11 other sites.
Telemetry from S-0186 arrives on the ninth relay and is batched nightly rather than streamed.
The enclosure at Beacon Ferry was rebuilt in timber after the old fencing was taken by the river.
Beacon Ferry shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0187 -- Crag Barrow

An earlier clerk recorded Crag Barrow under a shortened spelling, and both forms still appear in the older indexes.
The reading shelter at Crag Barrow takes water in heavy weather and the floor was relaid.
A visitor log is kept at Crag Barrow and shows 12 entries for the period.
Two of the anchors at Crag Barrow were replaced after the frost and the work is recorded in the district ledger.
The access key for S-0187 is held at the district office and signed out per visit.
Signal strength at Crag Barrow has been marginal since the mast on the ridge was lowered.
The load recorded for S-0187 is 904, on a return at tier 5.
That return for Crag Barrow is revision 4, lodged 2034-07-12, and its status is settled.
A calibration offset of 3 is recorded for S-0187 against the district standard.
Telemetry from S-0187 arrives on the first relay and is batched nightly rather than streamed.
The instrument housing at Crag Barrow is the original pattern and its door seal is checked each visit.
Calibration gear for S-0187 travels with the district van and is shared with 14 other sites.

### S-0188 -- Crag Bourne

The survey party reached Crag Bourne on the ninth of the month and found the access track passable for light vehicles only.
The logbook kept at Crag Bourne runs to 64 pages and the earlier volumes are held off site.
The site plan for Crag Bourne is the sixth revision and supersedes the sketch held in the district folder.
A visitor log is kept at Crag Bourne and shows 63 entries for the period.
The load recorded for S-0188 is 476, on a return at tier 9.
That return for Crag Bourne is revision 6, lodged 2034-09-10, and its status is settled.
The enclosure at Crag Bourne was rebuilt in timber after the old fencing was taken by the river.

### S-0189 -- Auburn Ford

The survey party reached Auburn Ford on the ninth of the month and found the access track passable for light vehicles only.
The fence line at Auburn Ford was rerun 28 metres to the east to clear the culvert.
The district file for Auburn Ford shows revision 1 lodged on 2034-06-24.
For S-0189 the status is returned, the tier is 7, and the load is 466.
The offset applied to readings from S-0189 is 12 and has not been revised.
A spare sensor head is kept at Auburn Ford against the failure that took out the district in the previous cycle.
The enclosure at Auburn Ford was rebuilt in timber after the old fencing was taken by the river.
The instrument housing at Auburn Ford is the original pattern and its door seal is checked each visit.
Access to Auburn Ford is by the service road from the south; the gate code was reissued after the fourteenth inspection.
Calibration gear for S-0189 travels with the district van and is shared with 12 other sites.
Maintenance visits to S-0189 are scheduled quarterly and the sixth of those was carried out as planned.

### S-0190 -- Ridge Terrace

The approach to Ridge Terrace crosses 18 field boundaries and the wayleave is held by the county.
On 2034-07-27 the district accepted revision 4 for Ridge Terrace and marked it returned.
S-0190 carries tier 4 on that revision and a load of 847.
Correspondence shows the tenancy at Ridge Terrace was renewed for a further 68 years.
The instrument housing at Ridge Terrace is the original pattern and its door seal is checked each visit.
The access key for S-0190 is held at the district office and signed out per visit.
Calibration gear for S-0190 travels with the district van and is shared with 25 other sites.

### S-0191 -- Yarrow Landing

Signal strength at Yarrow Landing has been marginal since the mast on the ridge was lowered.
Tier 7 is where Yarrow Landing sits on revision 2, whose status is open.
The load on that revision of S-0191, lodged 2034-01-22, is 832.
The site plan for Yarrow Landing is the sixth revision and supersedes the sketch held in the district folder.
Weather at Yarrow Landing closed the approach for 10 days during the period under review and no readings were lost.
The notes for S-0191 mention a disused well inside the compound, capped and recorded but not surveyed.
The instrument housing at Yarrow Landing is the original pattern and its door seal is checked each visit.
Drainage work near Yarrow Landing was completed without interruption to the record.
The approach to Yarrow Landing crosses 5 field boundaries and the wayleave is held by the county.
Yarrow Landing shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0192 -- Tamarisk Bourne

The notes for S-0192 mention a disused well inside the compound, capped and recorded but not surveyed.
Status provisional: revision 6 for S-0192, lodged 2034-03-06.
Load 747 at tier 1 is what that revision carries for Tamarisk Bourne.
A calibration offset of 38 is recorded for S-0192 against the district standard.
A visitor log is kept at Tamarisk Bourne and shows 52 entries for the period.
The reading shelter at Tamarisk Bourne takes water in heavy weather and the floor was relaid.
The fence line at Tamarisk Bourne was rerun 2 metres to the east to clear the culvert.
S-0192 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Tamarisk Bourne has been on the register since the first consolidation and its paperwork has never been reconstructed.
Weather at Tamarisk Bourne closed the approach for 18 days during the period under review and no readings were lost.

### S-0193 -- Marram Landing

The fence line at Marram Landing was rerun 17 metres to the east to clear the culvert.
The instrument housing at Marram Landing is the original pattern and its door seal is checked each visit.
The logbook kept at Marram Landing runs to 77 pages and the earlier volumes are held off site.
S-0193 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Two of the anchors at Marram Landing were replaced after the frost and the work is recorded in the district ledger.
Weather at Marram Landing closed the approach for 26 days during the period under review and no readings were lost.
The approach to Marram Landing crosses 7 field boundaries and the wayleave is held by the county.
On 2034-06-16 the district accepted revision 3 for Marram Landing and marked it returned.
S-0193 carries tier 6 on that revision and a load of 276.
Maintenance visits to S-0193 are scheduled quarterly and the tenth of those was carried out as planned.

### S-0194 -- Calder Cairn

Correspondence shows the tenancy at Calder Cairn was renewed for a further 32 years.
Drainage work near Calder Cairn was completed without interruption to the record.
Calder Cairn has been on the register since the first consolidation and its paperwork has never been reconstructed.
The district file for Calder Cairn shows revision 5 lodged on 2034-06-23.
For S-0194 the status is settled, the tier is 3, and the load is 374.
A calibration offset of -31 is recorded for S-0194 against the district standard.
Correspondence about S-0194 is filed under the district rather than under the site, which has caused confusion before.
An earlier clerk recorded Calder Cairn under a shortened spelling, and both forms still appear in the older indexes.

### S-0195 -- Gorse Cove

Calibration gear for S-0195 travels with the district van and is shared with 4 other sites.
Weather at Gorse Cove closed the approach for 28 days during the period under review and no readings were lost.
Vegetation around Gorse Cove is cut back twice a year under the standing arrangement.
Gorse Cove has been on the register since the first consolidation and its paperwork has never been reconstructed.
Signal strength at Gorse Cove has been marginal since the mast on the ridge was lowered.
A housekeeping note against S-0195 asks that the cable run be rewalked before the next dry season.
The district file for Gorse Cove shows revision 3 lodged on 2034-05-11.
For S-0195 the status is returned, the tier is 8, and the load is 901.
Telemetry from S-0195 arrives on the twelfth relay and is batched nightly rather than streamed.
The logbook kept at Gorse Cove runs to 48 pages and the earlier volumes are held off site.
The fence line at Gorse Cove was rerun 24 metres to the east to clear the culvert.

### S-0196 -- Indigo Ghyll

The site plan for Indigo Ghyll is the ninth revision and supersedes the sketch held in the district folder.
The approach to Indigo Ghyll crosses 19 field boundaries and the wayleave is held by the county.
The enclosure at Indigo Ghyll was rebuilt in timber after the old fencing was taken by the river.
Access to Indigo Ghyll is by the service road from the south; the gate code was reissued after the ninth inspection.
A visitor log is kept at Indigo Ghyll and shows 33 entries for the period.
On 2034-10-19 the district accepted revision 3 for Indigo Ghyll and marked it provisional.
S-0196 carries tier 5 on that revision and a load of 238.
An earlier clerk recorded Indigo Ghyll under a shortened spelling, and both forms still appear in the older indexes.
Indigo Ghyll shares its power feed with the neighbouring pumping station and has its own cut-out.
Vegetation around Indigo Ghyll is cut back twice a year under the standing arrangement.


## 7. Before you stop

`answer.json` in your working directory, one JSON object, the nine keys above. Do not
modify or delete `NOTICE.txt`. Work until the answer is complete, then stop.
