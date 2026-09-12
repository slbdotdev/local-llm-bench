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
6. What calibration offset does station S-0225 record? -> `calibration_offset`
7. What load does station S-0990 record? -> `absent_station_load`
8. What is the governing load of station S-0222? -> `conflicting_station_load`
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

### S-0101 -- Linden Glade

An earlier clerk recorded Linden Glade under a shortened spelling, and both forms still appear in the older indexes.
The survey party reached Linden Glade on the eighth of the month and found the access track passable for light vehicles only.
A visitor log is kept at Linden Glade and shows 29 entries for the period.
Status provisional: revision 2 for S-0101, lodged 2034-03-28.
Load 136 at tier 9 is what that revision carries for Linden Glade.
The offset applied to readings from S-0101 is 14 and has not been revised.
A housekeeping note against S-0101 asks that the cable run be rewalked before the next dry season.
Calibration gear for S-0101 travels with the district van and is shared with 17 other sites.
Drainage work near Linden Glade was completed without interruption to the record.
Correspondence about S-0101 is filed under the district rather than under the site, which has caused confusion before.

### S-0102 -- Cinder Anchorage

The reading shelter at Cinder Anchorage takes water in heavy weather and the floor was relaid.
Drainage work near Cinder Anchorage was completed without interruption to the record.
Cinder Anchorage has been on the register since the first consolidation and its paperwork has never been reconstructed.
Correspondence about S-0102 is filed under the district rather than under the site, which has caused confusion before.
The site plan for Cinder Anchorage is the fourteenth revision and supersedes the sketch held in the district folder.
S-0102 appears at revision 1 with a load of 391.
That revision of Cinder Anchorage was lodged 2034-08-23, is open, and places the station in tier 6.
A spare sensor head is kept at Cinder Anchorage against the failure that took out the district in the previous cycle.
Signal strength at Cinder Anchorage has been marginal since the mast on the ridge was lowered.
Maintenance visits to S-0102 are scheduled quarterly and the eleventh of those was carried out as planned.

### S-0103 -- Verdigris Pound

A visitor log is kept at Verdigris Pound and shows 15 entries for the period.
The access key for S-0103 is held at the district office and signed out per visit.
The load recorded for S-0103 is 494, on a return at tier 1.
That return for Verdigris Pound is revision 5, lodged 2034-08-04, and its status is settled.
S-0103 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Verdigris Pound shares its power feed with the neighbouring pumping station and has its own cut-out.
The enclosure at Verdigris Pound was rebuilt in timber after the old fencing was taken by the river.
Signal strength at Verdigris Pound has been marginal since the mast on the ridge was lowered.
The instrument housing at Verdigris Pound is the original pattern and its door seal is checked each visit.

### S-0104 -- Flint Wharf

Vegetation around Flint Wharf is cut back twice a year under the standing arrangement.
S-0104 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Signal strength at Flint Wharf has been marginal since the mast on the ridge was lowered.
A visitor log is kept at Flint Wharf and shows 81 entries for the period.
The instrument housing at Flint Wharf is the original pattern and its door seal is checked each visit.
S-0104 appears at revision 6 with a load of 946.
That revision of Flint Wharf was lodged 2034-11-04, is settled, and places the station in tier 4.
Two of the anchors at Flint Wharf were replaced after the frost and the work is recorded in the district ledger.
The approach to Flint Wharf crosses 2 field boundaries and the wayleave is held by the county.
The fence line at Flint Wharf was rerun 40 metres to the east to clear the culvert.

### S-0105 -- Calder Ripple

Weather at Calder Ripple closed the approach for 33 days during the period under review and no readings were lost.
Correspondence about S-0105 is filed under the district rather than under the site, which has caused confusion before.
Calibration gear for S-0105 travels with the district van and is shared with 11 other sites.
The enclosure at Calder Ripple was rebuilt in timber after the old fencing was taken by the river.
An earlier clerk recorded Calder Ripple under a shortened spelling, and both forms still appear in the older indexes.
Tier 8 is where Calder Ripple sits on revision 6, whose status is returned.
The load on that revision of S-0105, lodged 2034-05-23, is 155.
The offset applied to readings from S-0105 is -26 and has not been revised.
The survey party reached Calder Ripple on the tenth of the month and found the access track passable for light vehicles only.
The reading shelter at Calder Ripple takes water in heavy weather and the floor was relaid.

### S-0106 -- Meadow Pike

The approach to Meadow Pike crosses 32 field boundaries and the wayleave is held by the county.
Telemetry from S-0106 arrives on the ninth relay and is batched nightly rather than streamed.
Tier 6 is where Meadow Pike sits on revision 4, whose status is open.
The load on that revision of S-0106, lodged 2034-07-23, is 708.
The access key for S-0106 is held at the district office and signed out per visit.
The reading shelter at Meadow Pike takes water in heavy weather and the floor was relaid.
Vegetation around Meadow Pike is cut back twice a year under the standing arrangement.

### S-0107 -- Russet Weir

The fence line at Russet Weir was rerun 7 metres to the east to clear the culvert.
S-0107 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The survey party reached Russet Weir on the seventh of the month and found the access track passable for light vehicles only.
The district file for Russet Weir shows revision 1 lodged on 2034-11-27.
For S-0107 the status is settled, the tier is 4, and the load is 457.
Correspondence about S-0107 is filed under the district rather than under the site, which has caused confusion before.

### S-0108 -- Thistle Cairn

Signal strength at Thistle Cairn has been marginal since the mast on the ridge was lowered.
On 2034-11-19 the district accepted revision 6 for Thistle Cairn and marked it settled.
S-0108 carries tier 4 on that revision and a load of 333.
Correspondence about S-0108 is filed under the district rather than under the site, which has caused confusion before.
The enclosure at Thistle Cairn was rebuilt in timber after the old fencing was taken by the river.
Two of the anchors at Thistle Cairn were replaced after the frost and the work is recorded in the district ledger.
The site plan for Thistle Cairn is the eighth revision and supersedes the sketch held in the district folder.

### S-0109 -- Garnet Haven

S-0109 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The reading shelter at Garnet Haven takes water in heavy weather and the floor was relaid.
Two of the anchors at Garnet Haven were replaced after the frost and the work is recorded in the district ledger.
An earlier clerk recorded Garnet Haven under a shortened spelling, and both forms still appear in the older indexes.
On 2034-10-09 the district accepted revision 4 for Garnet Haven and marked it settled.
S-0109 carries tier 1 on that revision and a load of 532.
The notes for S-0109 mention a disused well inside the compound, capped and recorded but not surveyed.
Vegetation around Garnet Haven is cut back twice a year under the standing arrangement.
Signal strength at Garnet Haven has been marginal since the mast on the ridge was lowered.
The site plan for Garnet Haven is the second revision and supersedes the sketch held in the district folder.
Garnet Haven has been on the register since the first consolidation and its paperwork has never been reconstructed.

### S-0110 -- Fallow Vale

The access key for S-0110 is held at the district office and signed out per visit.
S-0110 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The survey party reached Fallow Vale on the first of the month and found the access track passable for light vehicles only.
Fallow Vale lodged revision 1 on 2034-01-06.
The return for S-0110 is settled, sits at tier 2, and records a load of 607.
An earlier clerk recorded Fallow Vale under a shortened spelling, and both forms still appear in the older indexes.

### S-0111 -- Crag Mill

Crag Mill has been on the register since the first consolidation and its paperwork has never been reconstructed.
Maintenance visits to S-0111 are scheduled quarterly and the fifth of those was carried out as planned.
Status settled: revision 1 for S-0111, lodged 2034-04-16.
Load 137 at tier 3 is what that revision carries for Crag Mill.
Access to Crag Mill is by the service road from the south; the gate code was reissued after the fifth inspection.
The reading shelter at Crag Mill takes water in heavy weather and the floor was relaid.

### S-0112 -- Brindle Wharf

Two of the anchors at Brindle Wharf were replaced after the frost and the work is recorded in the district ledger.
The reading shelter at Brindle Wharf takes water in heavy weather and the floor was relaid.
The instrument housing at Brindle Wharf is the original pattern and its door seal is checked each visit.
S-0112 was one of the sites brought forward in the consolidation and its numbering reflects that order.
On 2034-12-16 the district accepted revision 1 for Brindle Wharf and marked it withdrawn.
S-0112 carries tier 4 on that revision and a load of 621.
A housekeeping note against S-0112 asks that the cable run be rewalked before the next dry season.

### S-0113 -- Harrow Headland

A spare sensor head is kept at Harrow Headland against the failure that took out the district in the previous cycle.
S-0113 appears at revision 3 with a load of 288.
That revision of Harrow Headland was lodged 2034-06-06, is returned, and places the station in tier 3.
Harrow Headland shares its power feed with the neighbouring pumping station and has its own cut-out.
Correspondence shows the tenancy at Harrow Headland was renewed for a further 90 years.
The notes for S-0113 mention a disused well inside the compound, capped and recorded but not surveyed.
The instrument housing at Harrow Headland is the original pattern and its door seal is checked each visit.
Calibration gear for S-0113 travels with the district van and is shared with 25 other sites.

### S-0114 -- Ember Furlong

The notes for S-0114 mention a disused well inside the compound, capped and recorded but not surveyed.
The instrument housing at Ember Furlong is the original pattern and its door seal is checked each visit.
Revision 4 of the return for Ember Furlong was lodged on 2034-10-18 and stands provisional.
That revision places S-0114 in tier 2 and gives its load as 437.
A calibration offset of 30 is recorded for S-0114 against the district standard.
The site plan for Ember Furlong is the first revision and supersedes the sketch held in the district folder.
Correspondence shows the tenancy at Ember Furlong was renewed for a further 8 years.
Signal strength at Ember Furlong has been marginal since the mast on the ridge was lowered.
Drainage work near Ember Furlong was completed without interruption to the record.

### S-0115 -- Nettle Spur

The site plan for Nettle Spur is the second revision and supersedes the sketch held in the district folder.
The notes for S-0115 mention a disused well inside the compound, capped and recorded but not surveyed.
Nettle Spur shares its power feed with the neighbouring pumping station and has its own cut-out.
A visitor log is kept at Nettle Spur and shows 59 entries for the period.
Tier 8 is where Nettle Spur sits on revision 2, whose status is provisional.
The load on that revision of S-0115, lodged 2034-03-07, is 720.
The approach to Nettle Spur crosses 37 field boundaries and the wayleave is held by the county.
Signal strength at Nettle Spur has been marginal since the mast on the ridge was lowered.

### S-0116 -- Quarry Barrow

The fence line at Quarry Barrow was rerun 10 metres to the east to clear the culvert.
Drainage work near Quarry Barrow was completed without interruption to the record.
Revision 1 of the return for Quarry Barrow was lodged on 2034-02-15 and stands settled.
That revision places S-0116 in tier 2 and gives its load as 611.
A housekeeping note against S-0116 asks that the cable run be rewalked before the next dry season.
The approach to Quarry Barrow crosses 12 field boundaries and the wayleave is held by the county.
Calibration gear for S-0116 travels with the district van and is shared with 11 other sites.
Quarry Barrow has been on the register since the first consolidation and its paperwork has never been reconstructed.

### S-0117 -- Chalk Narrows

A spare sensor head is kept at Chalk Narrows against the failure that took out the district in the previous cycle.
On 2034-04-28 the district accepted revision 3 for Chalk Narrows and marked it open.
S-0117 carries tier 4 on that revision and a load of 556.
Chalk Narrows shares its power feed with the neighbouring pumping station and has its own cut-out.
S-0117 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The reading shelter at Chalk Narrows takes water in heavy weather and the floor was relaid.
The site plan for Chalk Narrows is the first revision and supersedes the sketch held in the district folder.
An earlier clerk recorded Chalk Narrows under a shortened spelling, and both forms still appear in the older indexes.

### S-0118 -- Fennel Causeway

S-0118 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Fennel Causeway shares its power feed with the neighbouring pumping station and has its own cut-out.
Telemetry from S-0118 arrives on the ninth relay and is batched nightly rather than streamed.
Maintenance visits to S-0118 are scheduled quarterly and the fourteenth of those was carried out as planned.
The access key for S-0118 is held at the district office and signed out per visit.
Status settled: revision 1 for S-0118, lodged 2034-05-04.
Load 470 at tier 4 is what that revision carries for Fennel Causeway.
Correspondence about S-0118 is filed under the district rather than under the site, which has caused confusion before.
The approach to Fennel Causeway crosses 33 field boundaries and the wayleave is held by the county.

### S-0119 -- Crag Cove

The instrument housing at Crag Cove is the original pattern and its door seal is checked each visit.
Vegetation around Crag Cove is cut back twice a year under the standing arrangement.
The district file for Crag Cove shows revision 2 lodged on 2034-10-10.
For S-0119 the status is settled, the tier is 4, and the load is 920.
Weather at Crag Cove closed the approach for 37 days during the period under review and no readings were lost.
A spare sensor head is kept at Crag Cove against the failure that took out the district in the previous cycle.
The survey party reached Crag Cove on the first of the month and found the access track passable for light vehicles only.
The fence line at Crag Cove was rerun 9 metres to the east to clear the culvert.
The notes for S-0119 mention a disused well inside the compound, capped and recorded but not surveyed.

### S-0120 -- Kestrel Brook

A visitor log is kept at Kestrel Brook and shows 4 entries for the period.
Telemetry from S-0120 arrives on the thirteenth relay and is batched nightly rather than streamed.
Tier 1 is where Kestrel Brook sits on revision 5, whose status is returned.
The load on that revision of S-0120, lodged 2034-05-28, is 194.
The access key for S-0120 is held at the district office and signed out per visit.
Kestrel Brook shares its power feed with the neighbouring pumping station and has its own cut-out.
The enclosure at Kestrel Brook was rebuilt in timber after the old fencing was taken by the river.

### S-0121 -- Rowan Knap

A spare sensor head is kept at Rowan Knap against the failure that took out the district in the previous cycle.
The reading shelter at Rowan Knap takes water in heavy weather and the floor was relaid.
Telemetry from S-0121 arrives on the first relay and is batched nightly rather than streamed.
The district file for Rowan Knap shows revision 2 lodged on 2034-11-04.
For S-0121 the status is settled, the tier is 4, and the load is 784.
The instrument housing at Rowan Knap is the original pattern and its door seal is checked each visit.
The fence line at Rowan Knap was rerun 13 metres to the east to clear the culvert.
Signal strength at Rowan Knap has been marginal since the mast on the ridge was lowered.
Correspondence about S-0121 is filed under the district rather than under the site, which has caused confusion before.

### S-0122 -- Rowan Staithe

Telemetry from S-0122 arrives on the sixth relay and is batched nightly rather than streamed.
A visitor log is kept at Rowan Staithe and shows 39 entries for the period.
On 2034-04-02 the district accepted revision 3 for Rowan Staithe and marked it settled.
S-0122 carries tier 1 on that revision and a load of 219.
A calibration offset of 6 is recorded for S-0122 against the district standard.
A housekeeping note against S-0122 asks that the cable run be rewalked before the next dry season.
S-0122 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Rowan Staithe shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0123 -- Auburn Cleave

Weather at Auburn Cleave closed the approach for 22 days during the period under review and no readings were lost.
The reading shelter at Auburn Cleave takes water in heavy weather and the floor was relaid.
The logbook kept at Auburn Cleave runs to 10 pages and the earlier volumes are held off site.
The instrument housing at Auburn Cleave is the original pattern and its door seal is checked each visit.
The load recorded for S-0123 is 489, on a return at tier 1.
That return for Auburn Cleave is revision 6, lodged 2034-04-14, and its status is provisional.
Vegetation around Auburn Cleave is cut back twice a year under the standing arrangement.

### S-0124 -- Copper Butte

The site plan for Copper Butte is the twelfth revision and supersedes the sketch held in the district folder.
Correspondence about S-0124 is filed under the district rather than under the site, which has caused confusion before.
The fence line at Copper Butte was rerun 33 metres to the east to clear the culvert.
S-0124 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The instrument housing at Copper Butte is the original pattern and its door seal is checked each visit.
Weather at Copper Butte closed the approach for 10 days during the period under review and no readings were lost.
Copper Butte has been on the register since the first consolidation and its paperwork has never been reconstructed.
The district file for Copper Butte shows revision 1 lodged on 2034-06-21.
For S-0124 the status is settled, the tier is 2, and the load is 892.
Two of the anchors at Copper Butte were replaced after the frost and the work is recorded in the district ledger.
A housekeeping note against S-0124 asks that the cable run be rewalked before the next dry season.

### S-0125 -- Chalk Dingle

S-0125 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Two of the anchors at Chalk Dingle were replaced after the frost and the work is recorded in the district ledger.
On 2034-02-06 the district accepted revision 6 for Chalk Dingle and marked it open.
S-0125 carries tier 6 on that revision and a load of 381.
Chalk Dingle carries a calibration offset of -16 on the current instrument head.
Chalk Dingle has been on the register since the first consolidation and its paperwork has never been reconstructed.
An earlier clerk recorded Chalk Dingle under a shortened spelling, and both forms still appear in the older indexes.
A visitor log is kept at Chalk Dingle and shows 37 entries for the period.

### S-0126 -- Sedge Spur

S-0126 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Tier 4 is where Sedge Spur sits on revision 2, whose status is settled.
The load on that revision of S-0126, lodged 2034-11-24, is 354.
Access to Sedge Spur is by the service road from the south; the gate code was reissued after the tenth inspection.
The enclosure at Sedge Spur was rebuilt in timber after the old fencing was taken by the river.
Calibration gear for S-0126 travels with the district van and is shared with 34 other sites.
Correspondence shows the tenancy at Sedge Spur was renewed for a further 42 years.
The logbook kept at Sedge Spur runs to 19 pages and the earlier volumes are held off site.

### S-0127 -- Shale Cairn

The notes for S-0127 mention a disused well inside the compound, capped and recorded but not surveyed.
The load recorded for S-0127 is 337, on a return at tier 1.
That return for Shale Cairn is revision 6, lodged 2034-02-09, and its status is settled.
Shale Cairn carries a calibration offset of -6 on the current instrument head.
Shale Cairn shares its power feed with the neighbouring pumping station and has its own cut-out.
The reading shelter at Shale Cairn takes water in heavy weather and the floor was relaid.
Weather at Shale Cairn closed the approach for 8 days during the period under review and no readings were lost.
The instrument housing at Shale Cairn is the original pattern and its door seal is checked each visit.

### S-0128 -- Flint Vale

Telemetry from S-0128 arrives on the twelfth relay and is batched nightly rather than streamed.
Weather at Flint Vale closed the approach for 4 days during the period under review and no readings were lost.
An earlier clerk recorded Flint Vale under a shortened spelling, and both forms still appear in the older indexes.
Maintenance visits to S-0128 are scheduled quarterly and the fourteenth of those was carried out as planned.
Correspondence about S-0128 is filed under the district rather than under the site, which has caused confusion before.
Tier 4 is where Flint Vale sits on revision 2, whose status is settled.
The load on that revision of S-0128, lodged 2034-11-04, is 422.
Signal strength at Flint Vale has been marginal since the mast on the ridge was lowered.
Correspondence shows the tenancy at Flint Vale was renewed for a further 23 years.

### S-0129 -- Clover Strand

A visitor log is kept at Clover Strand and shows 74 entries for the period.
The load recorded for S-0129 is 171, on a return at tier 3.
That return for Clover Strand is revision 1, lodged 2034-11-19, and its status is settled.
Clover Strand carries a calibration offset of -21 on the current instrument head.
Correspondence shows the tenancy at Clover Strand was renewed for a further 20 years.
Calibration gear for S-0129 travels with the district van and is shared with 14 other sites.
The logbook kept at Clover Strand runs to 65 pages and the earlier volumes are held off site.
The site plan for Clover Strand is the fourteenth revision and supersedes the sketch held in the district folder.
The instrument housing at Clover Strand is the original pattern and its door seal is checked each visit.

### S-0130 -- Ember Hollow

A spare sensor head is kept at Ember Hollow against the failure that took out the district in the previous cycle.
The load recorded for S-0130 is 365, on a return at tier 4.
That return for Ember Hollow is revision 5, lodged 2034-06-19, and its status is settled.
A calibration offset of 16 is recorded for S-0130 against the district standard.
Ember Hollow has been on the register since the first consolidation and its paperwork has never been reconstructed.
The site plan for Ember Hollow is the fourteenth revision and supersedes the sketch held in the district folder.
Telemetry from S-0130 arrives on the second relay and is batched nightly rather than streamed.
The reading shelter at Ember Hollow takes water in heavy weather and the floor was relaid.
The approach to Ember Hollow crosses 22 field boundaries and the wayleave is held by the county.
S-0130 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Vegetation around Ember Hollow is cut back twice a year under the standing arrangement.
Correspondence about S-0130 is filed under the district rather than under the site, which has caused confusion before.
A housekeeping note against S-0130 asks that the cable run be rewalked before the next dry season.

### S-0131 -- Sorrel Warren

A visitor log is kept at Sorrel Warren and shows 60 entries for the period.
An earlier clerk recorded Sorrel Warren under a shortened spelling, and both forms still appear in the older indexes.
Status open: revision 4 for S-0131, lodged 2034-06-24.
Load 927 at tier 6 is what that revision carries for Sorrel Warren.
The site plan for Sorrel Warren is the seventh revision and supersedes the sketch held in the district folder.
A housekeeping note against S-0131 asks that the cable run be rewalked before the next dry season.
The logbook kept at Sorrel Warren runs to 56 pages and the earlier volumes are held off site.
Telemetry from S-0131 arrives on the fourth relay and is batched nightly rather than streamed.
Two of the anchors at Sorrel Warren were replaced after the frost and the work is recorded in the district ledger.

### S-0132 -- Rowan Glade

Rowan Glade has been on the register since the first consolidation and its paperwork has never been reconstructed.
The reading shelter at Rowan Glade takes water in heavy weather and the floor was relaid.
Tier 5 is where Rowan Glade sits on revision 2, whose status is returned.
The load on that revision of S-0132, lodged 2034-07-04, is 728.
A housekeeping note against S-0132 asks that the cable run be rewalked before the next dry season.
Correspondence shows the tenancy at Rowan Glade was renewed for a further 61 years.
Access to Rowan Glade is by the service road from the south; the gate code was reissued after the fourth inspection.
The fence line at Rowan Glade was rerun 20 metres to the east to clear the culvert.
A spare sensor head is kept at Rowan Glade against the failure that took out the district in the previous cycle.
The survey party reached Rowan Glade on the sixth of the month and found the access track passable for light vehicles only.
The access key for S-0132 is held at the district office and signed out per visit.
The notes for S-0132 mention a disused well inside the compound, capped and recorded but not surveyed.

### S-0133 -- Ochre Ripple

S-0133 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Ochre Ripple has been on the register since the first consolidation and its paperwork has never been reconstructed.
The access key for S-0133 is held at the district office and signed out per visit.
The logbook kept at Ochre Ripple runs to 3 pages and the earlier volumes are held off site.
Ochre Ripple lodged revision 3 on 2034-06-15.
The return for S-0133 is returned, sits at tier 7, and records a load of 415.
Ochre Ripple carries a calibration offset of 4 on the current instrument head.
Telemetry from S-0133 arrives on the tenth relay and is batched nightly rather than streamed.
Ochre Ripple shares its power feed with the neighbouring pumping station and has its own cut-out.
Signal strength at Ochre Ripple has been marginal since the mast on the ridge was lowered.
The site plan for Ochre Ripple is the twelfth revision and supersedes the sketch held in the district folder.
Maintenance visits to S-0133 are scheduled quarterly and the ninth of those was carried out as planned.
A visitor log is kept at Ochre Ripple and shows 90 entries for the period.

### S-0134 -- Linden Bank

Correspondence shows the tenancy at Linden Bank was renewed for a further 79 years.
Signal strength at Linden Bank has been marginal since the mast on the ridge was lowered.
S-0134 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The reading shelter at Linden Bank takes water in heavy weather and the floor was relaid.
The load recorded for S-0134 is 362, on a return at tier 3.
That return for Linden Bank is revision 1, lodged 2034-02-14, and its status is settled.
Correspondence about S-0134 is filed under the district rather than under the site, which has caused confusion before.

### S-0135 -- Kestrel Cove

The access key for S-0135 is held at the district office and signed out per visit.
Vegetation around Kestrel Cove is cut back twice a year under the standing arrangement.
Two of the anchors at Kestrel Cove were replaced after the frost and the work is recorded in the district ledger.
Access to Kestrel Cove is by the service road from the south; the gate code was reissued after the seventh inspection.
Status settled: revision 4 for S-0135, lodged 2034-09-07.
Load 600 at tier 4 is what that revision carries for Kestrel Cove.
Telemetry from S-0135 arrives on the eleventh relay and is batched nightly rather than streamed.
S-0135 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The site plan for Kestrel Cove is the sixth revision and supersedes the sketch held in the district folder.
An earlier clerk recorded Kestrel Cove under a shortened spelling, and both forms still appear in the older indexes.
The instrument housing at Kestrel Cove is the original pattern and its door seal is checked each visit.

### S-0136 -- Amber Sand

The fence line at Amber Sand was rerun 19 metres to the east to clear the culvert.
The load recorded for S-0136 is 287, on a return at tier 2.
That return for Amber Sand is revision 6, lodged 2034-08-23, and its status is provisional.
A calibration offset of -3 is recorded for S-0136 against the district standard.
A visitor log is kept at Amber Sand and shows 56 entries for the period.
The approach to Amber Sand crosses 26 field boundaries and the wayleave is held by the county.
Weather at Amber Sand closed the approach for 14 days during the period under review and no readings were lost.
The notes for S-0136 mention a disused well inside the compound, capped and recorded but not surveyed.
An earlier clerk recorded Amber Sand under a shortened spelling, and both forms still appear in the older indexes.
The survey party reached Amber Sand on the sixth of the month and found the access track passable for light vehicles only.

### S-0137 -- Ember Mill

The instrument housing at Ember Mill is the original pattern and its door seal is checked each visit.
Ember Mill lodged revision 4 on 2034-03-28.
The return for S-0137 is settled, sits at tier 3, and records a load of 875.
The site plan for Ember Mill is the second revision and supersedes the sketch held in the district folder.
The reading shelter at Ember Mill takes water in heavy weather and the floor was relaid.
A visitor log is kept at Ember Mill and shows 87 entries for the period.
Drainage work near Ember Mill was completed without interruption to the record.
A spare sensor head is kept at Ember Mill against the failure that took out the district in the previous cycle.
Correspondence shows the tenancy at Ember Mill was renewed for a further 61 years.
Ember Mill has been on the register since the first consolidation and its paperwork has never been reconstructed.

### S-0138 -- Birch Staithe

The logbook kept at Birch Staithe runs to 30 pages and the earlier volumes are held off site.
Tier 5 is where Birch Staithe sits on revision 6, whose status is settled.
The load on that revision of S-0138, lodged 2034-05-24, is 938.
The offset applied to readings from S-0138 is 22 and has not been revised.
This revision of S-0138 is marked 2 in the reconciliation sequence.
The survey party reached Birch Staithe on the fourteenth of the month and found the access track passable for light vehicles only.
The reading shelter at Birch Staithe takes water in heavy weather and the floor was relaid.
Correspondence shows the tenancy at Birch Staithe was renewed for a further 82 years.
Weather at Birch Staithe closed the approach for 5 days during the period under review and no readings were lost.
The access key for S-0138 is held at the district office and signed out per visit.
The fence line at Birch Staithe was rerun 25 metres to the east to clear the culvert.
Maintenance visits to S-0138 are scheduled quarterly and the second of those was carried out as planned.

### S-0467 -- Indigo Sand

Drainage work near Indigo Sand was completed without interruption to the record.
The logbook kept at Indigo Sand runs to 11 pages and the earlier volumes are held off site.
Calibration gear for S-0467 travels with the district van and is shared with 33 other sites.
The instrument housing at Indigo Sand is the original pattern and its door seal is checked each visit.
The reading shelter at Indigo Sand takes water in heavy weather and the floor was relaid.
The site plan for Indigo Sand is the seventh revision and supersedes the sketch held in the district folder.
The approach to Indigo Sand crosses 17 field boundaries and the wayleave is held by the county.
A visitor log is kept at Indigo Sand and shows 80 entries for the period.
S-0467 appears at revision 2 with a load of 999.
That revision of Indigo Sand was lodged 2034-09-05, is settled, and places the station in tier 9.
Indigo Sand carries sequence mark 3 in this quarter's reconciliation.
Signal strength at Indigo Sand has been marginal since the mast on the ridge was lowered.

### S-0140 -- Garnet Terrace

The notes for S-0140 mention a disused well inside the compound, capped and recorded but not surveyed.
The district file for Garnet Terrace shows revision 6 lodged on 2034-03-23.
For S-0140 the status is returned, the tier is 7, and the load is 948.
S-0140 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The instrument housing at Garnet Terrace is the original pattern and its door seal is checked each visit.
Weather at Garnet Terrace closed the approach for 23 days during the period under review and no readings were lost.
Drainage work near Garnet Terrace was completed without interruption to the record.
The survey party reached Garnet Terrace on the tenth of the month and found the access track passable for light vehicles only.
Telemetry from S-0140 arrives on the first relay and is batched nightly rather than streamed.

### S-0141 -- Midland Cove

The approach to Midland Cove crosses 15 field boundaries and the wayleave is held by the county.
Calibration gear for S-0141 travels with the district van and is shared with 9 other sites.
Signal strength at Midland Cove has been marginal since the mast on the ridge was lowered.
Midland Cove lodged revision 6 on 2034-06-22.
The return for S-0141 is withdrawn, sits at tier 3, and records a load of 381.
Midland Cove carries a calibration offset of -36 on the current instrument head.
Access to Midland Cove is by the service road from the south; the gate code was reissued after the fourth inspection.
Telemetry from S-0141 arrives on the sixth relay and is batched nightly rather than streamed.
The instrument housing at Midland Cove is the original pattern and its door seal is checked each visit.
A housekeeping note against S-0141 asks that the cable run be rewalked before the next dry season.
The logbook kept at Midland Cove runs to 90 pages and the earlier volumes are held off site.
Maintenance visits to S-0141 are scheduled quarterly and the twelfth of those was carried out as planned.

### S-0142 -- Flint Bluff

A visitor log is kept at Flint Bluff and shows 13 entries for the period.
The access key for S-0142 is held at the district office and signed out per visit.
The logbook kept at Flint Bluff runs to 25 pages and the earlier volumes are held off site.
Flint Bluff has been on the register since the first consolidation and its paperwork has never been reconstructed.
The survey party reached Flint Bluff on the third of the month and found the access track passable for light vehicles only.
A spare sensor head is kept at Flint Bluff against the failure that took out the district in the previous cycle.
Weather at Flint Bluff closed the approach for 35 days during the period under review and no readings were lost.
Drainage work near Flint Bluff was completed without interruption to the record.
The district file for Flint Bluff shows revision 1 lodged on 2034-02-14.
For S-0142 the status is provisional, the tier is 2, and the load is 197.
Access to Flint Bluff is by the service road from the south; the gate code was reissued after the fourth inspection.
The fence line at Flint Bluff was rerun 5 metres to the east to clear the culvert.

### S-0143 -- Copper Anchorage

Correspondence about S-0143 is filed under the district rather than under the site, which has caused confusion before.
The district file for Copper Anchorage shows revision 5 lodged on 2034-05-28.
For S-0143 the status is settled, the tier is 6, and the load is 770.
The offset applied to readings from S-0143 is 38 and has not been revised.
Correspondence shows the tenancy at Copper Anchorage was renewed for a further 86 years.
The logbook kept at Copper Anchorage runs to 17 pages and the earlier volumes are held off site.
Copper Anchorage has been on the register since the first consolidation and its paperwork has never been reconstructed.

### S-0144 -- Midland Ford

A spare sensor head is kept at Midland Ford against the failure that took out the district in the previous cycle.
Status withdrawn: revision 1 for S-0144, lodged 2034-03-03.
Load 677 at tier 3 is what that revision carries for Midland Ford.
The offset applied to readings from S-0144 is -18 and has not been revised.
Access to Midland Ford is by the service road from the south; the gate code was reissued after the eleventh inspection.
Weather at Midland Ford closed the approach for 19 days during the period under review and no readings were lost.
The fence line at Midland Ford was rerun 33 metres to the east to clear the culvert.
Signal strength at Midland Ford has been marginal since the mast on the ridge was lowered.
Maintenance visits to S-0144 are scheduled quarterly and the eleventh of those was carried out as planned.

### S-0145 -- Hazel Combe

Vegetation around Hazel Combe is cut back twice a year under the standing arrangement.
Signal strength at Hazel Combe has been marginal since the mast on the ridge was lowered.
The access key for S-0145 is held at the district office and signed out per visit.
Revision 2 of the return for Hazel Combe was lodged on 2034-05-14 and stands provisional.
That revision places S-0145 in tier 9 and gives its load as 318.
A calibration offset of 5 is recorded for S-0145 against the district standard.
A visitor log is kept at Hazel Combe and shows 66 entries for the period.
An earlier clerk recorded Hazel Combe under a shortened spelling, and both forms still appear in the older indexes.
Calibration gear for S-0145 travels with the district van and is shared with 19 other sites.
Two of the anchors at Hazel Combe were replaced after the frost and the work is recorded in the district ledger.
A spare sensor head is kept at Hazel Combe against the failure that took out the district in the previous cycle.
Access to Hazel Combe is by the service road from the south; the gate code was reissued after the eleventh inspection.

### S-0146 -- Calder Shaw

Correspondence shows the tenancy at Calder Shaw was renewed for a further 19 years.
Calibration gear for S-0146 travels with the district van and is shared with 38 other sites.
The fence line at Calder Shaw was rerun 17 metres to the east to clear the culvert.
Vegetation around Calder Shaw is cut back twice a year under the standing arrangement.
A housekeeping note against S-0146 asks that the cable run be rewalked before the next dry season.
The access key for S-0146 is held at the district office and signed out per visit.
The logbook kept at Calder Shaw runs to 30 pages and the earlier volumes are held off site.
Correspondence about S-0146 is filed under the district rather than under the site, which has caused confusion before.
Status settled: revision 2 for S-0146, lodged 2034-10-11.
Load 893 at tier 3 is what that revision carries for Calder Shaw.
A calibration offset of -36 is recorded for S-0146 against the district standard.
The approach to Calder Shaw crosses 17 field boundaries and the wayleave is held by the county.
Calder Shaw shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0147 -- Umber Combe

Correspondence about S-0147 is filed under the district rather than under the site, which has caused confusion before.
The notes for S-0147 mention a disused well inside the compound, capped and recorded but not surveyed.
Calibration gear for S-0147 travels with the district van and is shared with 15 other sites.
The logbook kept at Umber Combe runs to 82 pages and the earlier volumes are held off site.
Umber Combe shares its power feed with the neighbouring pumping station and has its own cut-out.
Umber Combe has been on the register since the first consolidation and its paperwork has never been reconstructed.
Weather at Umber Combe closed the approach for 19 days during the period under review and no readings were lost.
The district file for Umber Combe shows revision 6 lodged on 2034-12-17.
For S-0147 the status is settled, the tier is 9, and the load is 757.
The offset applied to readings from S-0147 is -18 and has not been revised.
The enclosure at Umber Combe was rebuilt in timber after the old fencing was taken by the river.
The fence line at Umber Combe was rerun 33 metres to the east to clear the culvert.
Access to Umber Combe is by the service road from the south; the gate code was reissued after the eleventh inspection.

### S-0148 -- Crag Barrow

The approach to Crag Barrow crosses 30 field boundaries and the wayleave is held by the county.
The district file for Crag Barrow shows revision 6 lodged on 2034-03-23.
For S-0148 the status is settled, the tier is 4, and the load is 638.
The enclosure at Crag Barrow was rebuilt in timber after the old fencing was taken by the river.
S-0148 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The logbook kept at Crag Barrow runs to 27 pages and the earlier volumes are held off site.
Signal strength at Crag Barrow has been marginal since the mast on the ridge was lowered.
The site plan for Crag Barrow is the third revision and supersedes the sketch held in the district folder.

### S-0149 -- Thistle Copse

Thistle Copse has been on the register since the first consolidation and its paperwork has never been reconstructed.
The enclosure at Thistle Copse was rebuilt in timber after the old fencing was taken by the river.
The load recorded for S-0149 is 863, on a return at tier 2.
That return for Thistle Copse is revision 4, lodged 2034-10-10, and its status is withdrawn.
The fence line at Thistle Copse was rerun 16 metres to the east to clear the culvert.
Signal strength at Thistle Copse has been marginal since the mast on the ridge was lowered.

### S-0150 -- Thistle Sand

Calibration gear for S-0150 travels with the district van and is shared with 24 other sites.
The load recorded for S-0150 is 958, on a return at tier 3.
That return for Thistle Sand is revision 4, lodged 2034-10-11, and its status is settled.
S-0150 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Correspondence shows the tenancy at Thistle Sand was renewed for a further 23 years.
A housekeeping note against S-0150 asks that the cable run be rewalked before the next dry season.
The reading shelter at Thistle Sand takes water in heavy weather and the floor was relaid.
Vegetation around Thistle Sand is cut back twice a year under the standing arrangement.
Weather at Thistle Sand closed the approach for 19 days during the period under review and no readings were lost.

### S-0151 -- Cedar Wharf

Cedar Wharf has been on the register since the first consolidation and its paperwork has never been reconstructed.
An earlier clerk recorded Cedar Wharf under a shortened spelling, and both forms still appear in the older indexes.
The logbook kept at Cedar Wharf runs to 59 pages and the earlier volumes are held off site.
Revision 5 of the return for Cedar Wharf was lodged on 2034-08-09 and stands settled.
That revision places S-0151 in tier 4 and gives its load as 965.
The instrument housing at Cedar Wharf is the original pattern and its door seal is checked each visit.

### S-0152 -- Heather Causeway

S-0152 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The instrument housing at Heather Causeway is the original pattern and its door seal is checked each visit.
The reading shelter at Heather Causeway takes water in heavy weather and the floor was relaid.
A housekeeping note against S-0152 asks that the cable run be rewalked before the next dry season.
Heather Causeway shares its power feed with the neighbouring pumping station and has its own cut-out.
Tier 1 is where Heather Causeway sits on revision 2, whose status is settled.
The load on that revision of S-0152, lodged 2034-05-01, is 958.
The site plan for Heather Causeway is the eleventh revision and supersedes the sketch held in the district folder.
The approach to Heather Causeway crosses 19 field boundaries and the wayleave is held by the county.
Signal strength at Heather Causeway has been marginal since the mast on the ridge was lowered.

### S-0153 -- Ridge Fell

The approach to Ridge Fell crosses 2 field boundaries and the wayleave is held by the county.
The load recorded for S-0153 is 394, on a return at tier 1.
That return for Ridge Fell is revision 4, lodged 2034-05-14, and its status is settled.
S-0153 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Ridge Fell shares its power feed with the neighbouring pumping station and has its own cut-out.
Weather at Ridge Fell closed the approach for 35 days during the period under review and no readings were lost.
The fence line at Ridge Fell was rerun 20 metres to the east to clear the culvert.
Calibration gear for S-0153 travels with the district van and is shared with 5 other sites.
Correspondence shows the tenancy at Ridge Fell was renewed for a further 56 years.
A housekeeping note against S-0153 asks that the cable run be rewalked before the next dry season.
The logbook kept at Ridge Fell runs to 38 pages and the earlier volumes are held off site.

### S-0154 -- Rowan Butte

The survey party reached Rowan Butte on the ninth of the month and found the access track passable for light vehicles only.
Drainage work near Rowan Butte was completed without interruption to the record.
The district file for Rowan Butte shows revision 1 lodged on 2034-01-11.
For S-0154 the status is settled, the tier is 4, and the load is 665.
The instrument housing at Rowan Butte is the original pattern and its door seal is checked each visit.
Vegetation around Rowan Butte is cut back twice a year under the standing arrangement.
The enclosure at Rowan Butte was rebuilt in timber after the old fencing was taken by the river.
Correspondence shows the tenancy at Rowan Butte was renewed for a further 47 years.

### S-0155 -- Vellum Pound

Signal strength at Vellum Pound has been marginal since the mast on the ridge was lowered.
A housekeeping note against S-0155 asks that the cable run be rewalked before the next dry season.
A spare sensor head is kept at Vellum Pound against the failure that took out the district in the previous cycle.
Access to Vellum Pound is by the service road from the south; the gate code was reissued after the second inspection.
On 2034-10-10 the district accepted revision 6 for Vellum Pound and marked it settled.
S-0155 carries tier 1 on that revision and a load of 245.
The site plan for Vellum Pound is the third revision and supersedes the sketch held in the district folder.
Correspondence about S-0155 is filed under the district rather than under the site, which has caused confusion before.

### S-0156 -- Willow Wharf

The access key for S-0156 is held at the district office and signed out per visit.
Two of the anchors at Willow Wharf were replaced after the frost and the work is recorded in the district ledger.
Maintenance visits to S-0156 are scheduled quarterly and the seventh of those was carried out as planned.
Status provisional: revision 4 for S-0156, lodged 2034-08-08.
Load 313 at tier 5 is what that revision carries for Willow Wharf.
Willow Wharf has been on the register since the first consolidation and its paperwork has never been reconstructed.
The logbook kept at Willow Wharf runs to 63 pages and the earlier volumes are held off site.
The instrument housing at Willow Wharf is the original pattern and its door seal is checked each visit.
S-0156 was one of the sites brought forward in the consolidation and its numbering reflects that order.
A visitor log is kept at Willow Wharf and shows 80 entries for the period.
A housekeeping note against S-0156 asks that the cable run be rewalked before the next dry season.

### S-0157 -- Fallow Yard

A housekeeping note against S-0157 asks that the cable run be rewalked before the next dry season.
Tier 4 is where Fallow Yard sits on revision 2, whose status is settled.
The load on that revision of S-0157, lodged 2034-04-03, is 440.
The approach to Fallow Yard crosses 22 field boundaries and the wayleave is held by the county.
The notes for S-0157 mention a disused well inside the compound, capped and recorded but not surveyed.
The instrument housing at Fallow Yard is the original pattern and its door seal is checked each visit.
Calibration gear for S-0157 travels with the district van and is shared with 24 other sites.
Telemetry from S-0157 arrives on the twelfth relay and is batched nightly rather than streamed.
S-0157 was one of the sites brought forward in the consolidation and its numbering reflects that order.

### S-0158 -- Flint Mere

The reading shelter at Flint Mere takes water in heavy weather and the floor was relaid.
Two of the anchors at Flint Mere were replaced after the frost and the work is recorded in the district ledger.
The access key for S-0158 is held at the district office and signed out per visit.
A spare sensor head is kept at Flint Mere against the failure that took out the district in the previous cycle.
The approach to Flint Mere crosses 15 field boundaries and the wayleave is held by the county.
Flint Mere has been on the register since the first consolidation and its paperwork has never been reconstructed.
A housekeeping note against S-0158 asks that the cable run be rewalked before the next dry season.
The instrument housing at Flint Mere is the original pattern and its door seal is checked each visit.
Correspondence about S-0158 is filed under the district rather than under the site, which has caused confusion before.
Tier 4 is where Flint Mere sits on revision 4, whose status is settled.
The load on that revision of S-0158, lodged 2034-06-21, is 379.
The offset applied to readings from S-0158 is 38 and has not been revised.
Flint Mere shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0159 -- Hazel Rill

A spare sensor head is kept at Hazel Rill against the failure that took out the district in the previous cycle.
A visitor log is kept at Hazel Rill and shows 76 entries for the period.
Tier 4 is where Hazel Rill sits on revision 2, whose status is settled.
The load on that revision of S-0159, lodged 2034-07-11, is 420.
The approach to Hazel Rill crosses 24 field boundaries and the wayleave is held by the county.
Maintenance visits to S-0159 are scheduled quarterly and the second of those was carried out as planned.
The survey party reached Hazel Rill on the ninth of the month and found the access track passable for light vehicles only.
Calibration gear for S-0159 travels with the district van and is shared with 24 other sites.

### S-0160 -- Sorrel Shoal

The enclosure at Sorrel Shoal was rebuilt in timber after the old fencing was taken by the river.
The approach to Sorrel Shoal crosses 9 field boundaries and the wayleave is held by the county.
Sorrel Shoal has been on the register since the first consolidation and its paperwork has never been reconstructed.
Signal strength at Sorrel Shoal has been marginal since the mast on the ridge was lowered.
Sorrel Shoal lodged revision 6 on 2034-08-22.
The return for S-0160 is withdrawn, sits at tier 5, and records a load of 158.
Calibration gear for S-0160 travels with the district van and is shared with 11 other sites.
Correspondence shows the tenancy at Sorrel Shoal was renewed for a further 77 years.
Correspondence about S-0160 is filed under the district rather than under the site, which has caused confusion before.
Maintenance visits to S-0160 are scheduled quarterly and the fourth of those was carried out as planned.
A visitor log is kept at Sorrel Shoal and shows 24 entries for the period.
Drainage work near Sorrel Shoal was completed without interruption to the record.

### S-0161 -- Sorrel Landing

The reading shelter at Sorrel Landing takes water in heavy weather and the floor was relaid.
A spare sensor head is kept at Sorrel Landing against the failure that took out the district in the previous cycle.
Calibration gear for S-0161 travels with the district van and is shared with 33 other sites.
Drainage work near Sorrel Landing was completed without interruption to the record.
On 2034-06-02 the district accepted revision 5 for Sorrel Landing and marked it settled.
S-0161 carries tier 1 on that revision and a load of 477.
The instrument housing at Sorrel Landing is the original pattern and its door seal is checked each visit.
An earlier clerk recorded Sorrel Landing under a shortened spelling, and both forms still appear in the older indexes.
Access to Sorrel Landing is by the service road from the south; the gate code was reissued after the fifth inspection.
The site plan for Sorrel Landing is the third revision and supersedes the sketch held in the district folder.

### S-0162 -- Bramble Ledge

The access key for S-0162 is held at the district office and signed out per visit.
The district file for Bramble Ledge shows revision 2 lodged on 2034-12-21.
For S-0162 the status is settled, the tier is 4, and the load is 494.
The enclosure at Bramble Ledge was rebuilt in timber after the old fencing was taken by the river.
The instrument housing at Bramble Ledge is the original pattern and its door seal is checked each visit.
A visitor log is kept at Bramble Ledge and shows 70 entries for the period.

### S-0163 -- Thistle Glade

The access key for S-0163 is held at the district office and signed out per visit.
Revision 5 of the return for Thistle Glade was lodged on 2034-06-07 and stands settled.
That revision places S-0163 in tier 2 and gives its load as 609.
A calibration offset of 3 is recorded for S-0163 against the district standard.
Maintenance visits to S-0163 are scheduled quarterly and the tenth of those was carried out as planned.
The notes for S-0163 mention a disused well inside the compound, capped and recorded but not surveyed.
The logbook kept at Thistle Glade runs to 73 pages and the earlier volumes are held off site.

### S-0164 -- Spindle Rill

The instrument housing at Spindle Rill is the original pattern and its door seal is checked each visit.
A visitor log is kept at Spindle Rill and shows 44 entries for the period.
Calibration gear for S-0164 travels with the district van and is shared with 16 other sites.
Spindle Rill lodged revision 2 on 2034-11-01.
The return for S-0164 is settled, sits at tier 2, and records a load of 430.
S-0164 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Vegetation around Spindle Rill is cut back twice a year under the standing arrangement.

### S-0165 -- Bramble Gully

The instrument housing at Bramble Gully is the original pattern and its door seal is checked each visit.
Weather at Bramble Gully closed the approach for 16 days during the period under review and no readings were lost.
The notes for S-0165 mention a disused well inside the compound, capped and recorded but not surveyed.
S-0165 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The district file for Bramble Gully shows revision 6 lodged on 2034-05-04.
For S-0165 the status is withdrawn, the tier is 3, and the load is 158.
Bramble Gully carries a calibration offset of 28 on the current instrument head.
Bramble Gully has been on the register since the first consolidation and its paperwork has never been reconstructed.

### S-0166 -- Fallow Sand

Signal strength at Fallow Sand has been marginal since the mast on the ridge was lowered.
Telemetry from S-0166 arrives on the twelfth relay and is batched nightly rather than streamed.
The survey party reached Fallow Sand on the eighth of the month and found the access track passable for light vehicles only.
On 2034-10-11 the district accepted revision 2 for Fallow Sand and marked it settled.
S-0166 carries tier 3 on that revision and a load of 807.
Maintenance visits to S-0166 are scheduled quarterly and the fourteenth of those was carried out as planned.
The notes for S-0166 mention a disused well inside the compound, capped and recorded but not surveyed.
Correspondence shows the tenancy at Fallow Sand was renewed for a further 5 years.
A visitor log is kept at Fallow Sand and shows 49 entries for the period.
The access key for S-0166 is held at the district office and signed out per visit.
Weather at Fallow Sand closed the approach for 15 days during the period under review and no readings were lost.

### S-0167 -- Mellow Quay

Calibration gear for S-0167 travels with the district van and is shared with 16 other sites.
The site plan for Mellow Quay is the second revision and supersedes the sketch held in the district folder.
Mellow Quay has been on the register since the first consolidation and its paperwork has never been reconstructed.
Mellow Quay lodged revision 2 on 2034-05-24.
The return for S-0167 is settled, sits at tier 2, and records a load of 160.
S-0167 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The enclosure at Mellow Quay was rebuilt in timber after the old fencing was taken by the river.
A spare sensor head is kept at Mellow Quay against the failure that took out the district in the previous cycle.
The logbook kept at Mellow Quay runs to 25 pages and the earlier volumes are held off site.

### S-0168 -- Harrow Butte

Harrow Butte shares its power feed with the neighbouring pumping station and has its own cut-out.
Status provisional: revision 1 for S-0168, lodged 2034-02-18.
Load 115 at tier 4 is what that revision carries for Harrow Butte.
S-0168 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Vegetation around Harrow Butte is cut back twice a year under the standing arrangement.
Access to Harrow Butte is by the service road from the south; the gate code was reissued after the fifth inspection.
A visitor log is kept at Harrow Butte and shows 43 entries for the period.

### S-0169 -- Sedge Dale

Drainage work near Sedge Dale was completed without interruption to the record.
The district file for Sedge Dale shows revision 4 lodged on 2034-07-14.
For S-0169 the status is settled, the tier is 4, and the load is 872.
Weather at Sedge Dale closed the approach for 26 days during the period under review and no readings were lost.
A housekeeping note against S-0169 asks that the cable run be rewalked before the next dry season.
The site plan for Sedge Dale is the twelfth revision and supersedes the sketch held in the district folder.
The reading shelter at Sedge Dale takes water in heavy weather and the floor was relaid.
The survey party reached Sedge Dale on the tenth of the month and found the access track passable for light vehicles only.
S-0169 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The notes for S-0169 mention a disused well inside the compound, capped and recorded but not surveyed.
Sedge Dale has been on the register since the first consolidation and its paperwork has never been reconstructed.

### S-0170 -- Auburn Cairn

Access to Auburn Cairn is by the service road from the south; the gate code was reissued after the twelfth inspection.
A housekeeping note against S-0170 asks that the cable run be rewalked before the next dry season.
The survey party reached Auburn Cairn on the ninth of the month and found the access track passable for light vehicles only.
Auburn Cairn shares its power feed with the neighbouring pumping station and has its own cut-out.
An earlier clerk recorded Auburn Cairn under a shortened spelling, and both forms still appear in the older indexes.
The district file for Auburn Cairn shows revision 5 lodged on 2034-11-27.
For S-0170 the status is provisional, the tier is 6, and the load is 802.
Telemetry from S-0170 arrives on the twelfth relay and is batched nightly rather than streamed.
A visitor log is kept at Auburn Cairn and shows 72 entries for the period.
The reading shelter at Auburn Cairn takes water in heavy weather and the floor was relaid.
The logbook kept at Auburn Cairn runs to 86 pages and the earlier volumes are held off site.

### S-0171 -- Copper Drift

Drainage work near Copper Drift was completed without interruption to the record.
Vegetation around Copper Drift is cut back twice a year under the standing arrangement.
Signal strength at Copper Drift has been marginal since the mast on the ridge was lowered.
The load recorded for S-0171 is 766, on a return at tier 1.
That return for Copper Drift is revision 1, lodged 2034-11-07, and its status is withdrawn.
Copper Drift carries a calibration offset of -8 on the current instrument head.
Copper Drift shares its power feed with the neighbouring pumping station and has its own cut-out.
The fence line at Copper Drift was rerun 8 metres to the east to clear the culvert.

### S-0172 -- Ochre Pasture

An earlier clerk recorded Ochre Pasture under a shortened spelling, and both forms still appear in the older indexes.
The site plan for Ochre Pasture is the fifth revision and supersedes the sketch held in the district folder.
The load recorded for S-0172 is 166, on a return at tier 2.
That return for Ochre Pasture is revision 1, lodged 2034-03-13, and its status is settled.
Vegetation around Ochre Pasture is cut back twice a year under the standing arrangement.
A spare sensor head is kept at Ochre Pasture against the failure that took out the district in the previous cycle.

### S-0173 -- Jasper Delve

The enclosure at Jasper Delve was rebuilt in timber after the old fencing was taken by the river.
S-0173 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Revision 6 of the return for Jasper Delve was lodged on 2034-04-17 and stands withdrawn.
That revision places S-0173 in tier 9 and gives its load as 363.
Maintenance visits to S-0173 are scheduled quarterly and the twelfth of those was carried out as planned.
Drainage work near Jasper Delve was completed without interruption to the record.
The fence line at Jasper Delve was rerun 14 metres to the east to clear the culvert.
Weather at Jasper Delve closed the approach for 22 days during the period under review and no readings were lost.
Signal strength at Jasper Delve has been marginal since the mast on the ridge was lowered.
Access to Jasper Delve is by the service road from the south; the gate code was reissued after the fourth inspection.
Correspondence shows the tenancy at Jasper Delve was renewed for a further 59 years.

### S-0174 -- Quarry Gate

The instrument housing at Quarry Gate is the original pattern and its door seal is checked each visit.
An earlier clerk recorded Quarry Gate under a shortened spelling, and both forms still appear in the older indexes.
Drainage work near Quarry Gate was completed without interruption to the record.
Quarry Gate has been on the register since the first consolidation and its paperwork has never been reconstructed.
The access key for S-0174 is held at the district office and signed out per visit.
Correspondence about S-0174 is filed under the district rather than under the site, which has caused confusion before.
Signal strength at Quarry Gate has been marginal since the mast on the ridge was lowered.
The survey party reached Quarry Gate on the eleventh of the month and found the access track passable for light vehicles only.
Status settled: revision 3 for S-0174, lodged 2034-12-21.
Load 330 at tier 4 is what that revision carries for Quarry Gate.
Quarry Gate carries a calibration offset of -16 on the current instrument head.
A housekeeping note against S-0174 asks that the cable run be rewalked before the next dry season.

### S-0175 -- Calder Staithe

An earlier clerk recorded Calder Staithe under a shortened spelling, and both forms still appear in the older indexes.
A housekeeping note against S-0175 asks that the cable run be rewalked before the next dry season.
A spare sensor head is kept at Calder Staithe against the failure that took out the district in the previous cycle.
S-0175 appears at revision 4 with a load of 718.
That revision of Calder Staithe was lodged 2034-10-14, is open, and places the station in tier 6.
A calibration offset of 6 is recorded for S-0175 against the district standard.
Calder Staithe shares its power feed with the neighbouring pumping station and has its own cut-out.
The approach to Calder Staithe crosses 15 field boundaries and the wayleave is held by the county.
The enclosure at Calder Staithe was rebuilt in timber after the old fencing was taken by the river.
The logbook kept at Calder Staithe runs to 30 pages and the earlier volumes are held off site.

### S-0176 -- Kestrel Pike

The instrument housing at Kestrel Pike is the original pattern and its door seal is checked each visit.
Drainage work near Kestrel Pike was completed without interruption to the record.
Vegetation around Kestrel Pike is cut back twice a year under the standing arrangement.
Two of the anchors at Kestrel Pike were replaced after the frost and the work is recorded in the district ledger.
The fence line at Kestrel Pike was rerun 26 metres to the east to clear the culvert.
S-0176 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The reading shelter at Kestrel Pike takes water in heavy weather and the floor was relaid.
S-0176 appears at revision 2 with a load of 330.
That revision of Kestrel Pike was lodged 2034-02-06, is settled, and places the station in tier 2.
The enclosure at Kestrel Pike was rebuilt in timber after the old fencing was taken by the river.
Maintenance visits to S-0176 are scheduled quarterly and the second of those was carried out as planned.

### S-0177 -- Ochre Fell

Correspondence shows the tenancy at Ochre Fell was renewed for a further 37 years.
Access to Ochre Fell is by the service road from the south; the gate code was reissued after the first inspection.
The survey party reached Ochre Fell on the second of the month and found the access track passable for light vehicles only.
Revision 3 of the return for Ochre Fell was lodged on 2034-04-04 and stands settled.
That revision places S-0177 in tier 3 and gives its load as 604.
Ochre Fell carries a calibration offset of 23 on the current instrument head.
Signal strength at Ochre Fell has been marginal since the mast on the ridge was lowered.
A housekeeping note against S-0177 asks that the cable run be rewalked before the next dry season.

### S-0178 -- Crag Brook

Crag Brook shares its power feed with the neighbouring pumping station and has its own cut-out.
The approach to Crag Brook crosses 31 field boundaries and the wayleave is held by the county.
Correspondence about S-0178 is filed under the district rather than under the site, which has caused confusion before.
Status settled: revision 1 for S-0178, lodged 2034-08-20.
Load 838 at tier 1 is what that revision carries for Crag Brook.
A calibration offset of 18 is recorded for S-0178 against the district standard.
Vegetation around Crag Brook is cut back twice a year under the standing arrangement.
Maintenance visits to S-0178 are scheduled quarterly and the twelfth of those was carried out as planned.

### S-0179 -- Spindle Ledge

Two of the anchors at Spindle Ledge were replaced after the frost and the work is recorded in the district ledger.
The notes for S-0179 mention a disused well inside the compound, capped and recorded but not surveyed.
The district file for Spindle Ledge shows revision 5 lodged on 2034-12-02.
For S-0179 the status is settled, the tier is 3, and the load is 119.
An earlier clerk recorded Spindle Ledge under a shortened spelling, and both forms still appear in the older indexes.
The enclosure at Spindle Ledge was rebuilt in timber after the old fencing was taken by the river.

### S-0180 -- Quarry Brook

Signal strength at Quarry Brook has been marginal since the mast on the ridge was lowered.
Tier 1 is where Quarry Brook sits on revision 2, whose status is settled.
The load on that revision of S-0180, lodged 2034-08-15, is 176.
Correspondence shows the tenancy at Quarry Brook was renewed for a further 67 years.
The survey party reached Quarry Brook on the fourteenth of the month and found the access track passable for light vehicles only.
Quarry Brook shares its power feed with the neighbouring pumping station and has its own cut-out.
The approach to Quarry Brook crosses 14 field boundaries and the wayleave is held by the county.
A visitor log is kept at Quarry Brook and shows 20 entries for the period.
The instrument housing at Quarry Brook is the original pattern and its door seal is checked each visit.

### S-0181 -- Cinder Barrow

Signal strength at Cinder Barrow has been marginal since the mast on the ridge was lowered.
S-0181 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Cinder Barrow lodged revision 3 on 2034-04-28.
The return for S-0181 is returned, sits at tier 7, and records a load of 189.
The offset applied to readings from S-0181 is 39 and has not been revised.
Calibration gear for S-0181 travels with the district van and is shared with 10 other sites.
Two of the anchors at Cinder Barrow were replaced after the frost and the work is recorded in the district ledger.
An earlier clerk recorded Cinder Barrow under a shortened spelling, and both forms still appear in the older indexes.
Drainage work near Cinder Barrow was completed without interruption to the record.
A visitor log is kept at Cinder Barrow and shows 77 entries for the period.

### S-0182 -- Ember Withy

An earlier clerk recorded Ember Withy under a shortened spelling, and both forms still appear in the older indexes.
Weather at Ember Withy closed the approach for 6 days during the period under review and no readings were lost.
A spare sensor head is kept at Ember Withy against the failure that took out the district in the previous cycle.
Tier 2 is where Ember Withy sits on revision 6, whose status is settled.
The load on that revision of S-0182, lodged 2034-07-20, is 954.
The reading shelter at Ember Withy takes water in heavy weather and the floor was relaid.
Signal strength at Ember Withy has been marginal since the mast on the ridge was lowered.

### S-0183 -- Flint Withy

Flint Withy shares its power feed with the neighbouring pumping station and has its own cut-out.
The load recorded for S-0183 is 324, on a return at tier 3.
That return for Flint Withy is revision 5, lodged 2034-07-03, and its status is settled.
An earlier clerk recorded Flint Withy under a shortened spelling, and both forms still appear in the older indexes.
The logbook kept at Flint Withy runs to 28 pages and the earlier volumes are held off site.
Correspondence shows the tenancy at Flint Withy was renewed for a further 9 years.
The approach to Flint Withy crosses 34 field boundaries and the wayleave is held by the county.

### S-0184 -- Thistle Mill

Thistle Mill has been on the register since the first consolidation and its paperwork has never been reconstructed.
Signal strength at Thistle Mill has been marginal since the mast on the ridge was lowered.
Calibration gear for S-0184 travels with the district van and is shared with 3 other sites.
The notes for S-0184 mention a disused well inside the compound, capped and recorded but not surveyed.
A housekeeping note against S-0184 asks that the cable run be rewalked before the next dry season.
Status returned: revision 2 for S-0184, lodged 2034-12-01.
Load 224 at tier 7 is what that revision carries for Thistle Mill.
A visitor log is kept at Thistle Mill and shows 66 entries for the period.
Correspondence about S-0184 is filed under the district rather than under the site, which has caused confusion before.
The reading shelter at Thistle Mill takes water in heavy weather and the floor was relaid.
Access to Thistle Mill is by the service road from the south; the gate code was reissued after the third inspection.

### S-0185 -- Linden Gate

A visitor log is kept at Linden Gate and shows 18 entries for the period.
Tier 3 is where Linden Gate sits on revision 2, whose status is settled.
The load on that revision of S-0185, lodged 2034-06-20, is 777.
Linden Gate has been on the register since the first consolidation and its paperwork has never been reconstructed.
Vegetation around Linden Gate is cut back twice a year under the standing arrangement.
The site plan for Linden Gate is the eleventh revision and supersedes the sketch held in the district folder.
The access key for S-0185 is held at the district office and signed out per visit.

### S-0186 -- Copper Mill

Weather at Copper Mill closed the approach for 30 days during the period under review and no readings were lost.
Revision 6 of the return for Copper Mill was lodged on 2034-09-21 and stands provisional.
That revision places S-0186 in tier 1 and gives its load as 436.
A spare sensor head is kept at Copper Mill against the failure that took out the district in the previous cycle.
Access to Copper Mill is by the service road from the south; the gate code was reissued after the first inspection.
Copper Mill shares its power feed with the neighbouring pumping station and has its own cut-out.
A housekeeping note against S-0186 asks that the cable run be rewalked before the next dry season.

### S-0187 -- Fallow Pasture

Weather at Fallow Pasture closed the approach for 35 days during the period under review and no readings were lost.
The survey party reached Fallow Pasture on the eleventh of the month and found the access track passable for light vehicles only.
A spare sensor head is kept at Fallow Pasture against the failure that took out the district in the previous cycle.
The notes for S-0187 mention a disused well inside the compound, capped and recorded but not surveyed.
The access key for S-0187 is held at the district office and signed out per visit.
The load recorded for S-0187 is 368, on a return at tier 1.
That return for Fallow Pasture is revision 5, lodged 2034-12-09, and its status is settled.
Drainage work near Fallow Pasture was completed without interruption to the record.

### S-0188 -- Fennel Furlong

Signal strength at Fennel Furlong has been marginal since the mast on the ridge was lowered.
Two of the anchors at Fennel Furlong were replaced after the frost and the work is recorded in the district ledger.
The survey party reached Fennel Furlong on the first of the month and found the access track passable for light vehicles only.
On 2034-05-10 the district accepted revision 4 for Fennel Furlong and marked it settled.
S-0188 carries tier 1 on that revision and a load of 772.
The reading shelter at Fennel Furlong takes water in heavy weather and the floor was relaid.
Calibration gear for S-0188 travels with the district van and is shared with 10 other sites.

### S-0189 -- Quarry Bank

The notes for S-0189 mention a disused well inside the compound, capped and recorded but not surveyed.
Maintenance visits to S-0189 are scheduled quarterly and the sixth of those was carried out as planned.
Signal strength at Quarry Bank has been marginal since the mast on the ridge was lowered.
A spare sensor head is kept at Quarry Bank against the failure that took out the district in the previous cycle.
S-0189 appears at revision 4 with a load of 385.
That revision of Quarry Bank was lodged 2034-04-19, is open, and places the station in tier 3.
Correspondence shows the tenancy at Quarry Bank was renewed for a further 48 years.
Correspondence about S-0189 is filed under the district rather than under the site, which has caused confusion before.
Access to Quarry Bank is by the service road from the south; the gate code was reissued after the tenth inspection.
S-0189 was one of the sites brought forward in the consolidation and its numbering reflects that order.

### S-0190 -- Calder Mere

The survey party reached Calder Mere on the ninth of the month and found the access track passable for light vehicles only.
The instrument housing at Calder Mere is the original pattern and its door seal is checked each visit.
An earlier clerk recorded Calder Mere under a shortened spelling, and both forms still appear in the older indexes.
The district file for Calder Mere shows revision 3 lodged on 2034-02-08.
For S-0190 the status is settled, the tier is 3, and the load is 160.
Calibration gear for S-0190 travels with the district van and is shared with 16 other sites.
The access key for S-0190 is held at the district office and signed out per visit.
A visitor log is kept at Calder Mere and shows 40 entries for the period.
Access to Calder Mere is by the service road from the south; the gate code was reissued after the eighth inspection.

### S-0191 -- Quarry Knap

Correspondence about S-0191 is filed under the district rather than under the site, which has caused confusion before.
The approach to Quarry Knap crosses 5 field boundaries and the wayleave is held by the county.
Vegetation around Quarry Knap is cut back twice a year under the standing arrangement.
An earlier clerk recorded Quarry Knap under a shortened spelling, and both forms still appear in the older indexes.
Tier 4 is where Quarry Knap sits on revision 4, whose status is returned.
The load on that revision of S-0191, lodged 2034-09-26, is 985.
Quarry Knap carries a calibration offset of -12 on the current instrument head.
The site plan for Quarry Knap is the third revision and supersedes the sketch held in the district folder.
The access key for S-0191 is held at the district office and signed out per visit.
A spare sensor head is kept at Quarry Knap against the failure that took out the district in the previous cycle.

### S-0192 -- Heather Hallow

Calibration gear for S-0192 travels with the district van and is shared with 37 other sites.
Heather Hallow has been on the register since the first consolidation and its paperwork has never been reconstructed.
Drainage work near Heather Hallow was completed without interruption to the record.
A visitor log is kept at Heather Hallow and shows 74 entries for the period.
The approach to Heather Hallow crosses 25 field boundaries and the wayleave is held by the county.
The reading shelter at Heather Hallow takes water in heavy weather and the floor was relaid.
On 2034-12-06 the district accepted revision 4 for Heather Hallow and marked it settled.
S-0192 carries tier 1 on that revision and a load of 906.
An earlier clerk recorded Heather Hallow under a shortened spelling, and both forms still appear in the older indexes.

### S-0193 -- Calder Pike

The notes for S-0193 mention a disused well inside the compound, capped and recorded but not surveyed.
The district file for Calder Pike shows revision 6 lodged on 2034-02-02.
For S-0193 the status is settled, the tier is 1, and the load is 598.
A visitor log is kept at Calder Pike and shows 25 entries for the period.
An earlier clerk recorded Calder Pike under a shortened spelling, and both forms still appear in the older indexes.
The enclosure at Calder Pike was rebuilt in timber after the old fencing was taken by the river.
Calder Pike shares its power feed with the neighbouring pumping station and has its own cut-out.
The access key for S-0193 is held at the district office and signed out per visit.
Telemetry from S-0193 arrives on the eleventh relay and is batched nightly rather than streamed.
Signal strength at Calder Pike has been marginal since the mast on the ridge was lowered.

### S-0194 -- Thistle Warren

Telemetry from S-0194 arrives on the eighth relay and is batched nightly rather than streamed.
Thistle Warren shares its power feed with the neighbouring pumping station and has its own cut-out.
The enclosure at Thistle Warren was rebuilt in timber after the old fencing was taken by the river.
S-0194 appears at revision 6 with a load of 223.
That revision of Thistle Warren was lodged 2034-12-01, is withdrawn, and places the station in tier 6.
The site plan for Thistle Warren is the first revision and supersedes the sketch held in the district folder.
S-0194 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Drainage work near Thistle Warren was completed without interruption to the record.
Calibration gear for S-0194 travels with the district van and is shared with 20 other sites.
The instrument housing at Thistle Warren is the original pattern and its door seal is checked each visit.
Weather at Thistle Warren closed the approach for 35 days during the period under review and no readings were lost.
A spare sensor head is kept at Thistle Warren against the failure that took out the district in the previous cycle.

### S-0195 -- Ridge Yard

Calibration gear for S-0195 travels with the district van and is shared with 3 other sites.
Telemetry from S-0195 arrives on the thirteenth relay and is batched nightly rather than streamed.
Two of the anchors at Ridge Yard were replaced after the frost and the work is recorded in the district ledger.
Access to Ridge Yard is by the service road from the south; the gate code was reissued after the fourteenth inspection.
The instrument housing at Ridge Yard is the original pattern and its door seal is checked each visit.
The reading shelter at Ridge Yard takes water in heavy weather and the floor was relaid.
The load recorded for S-0195 is 946, on a return at tier 6.
That return for Ridge Yard is revision 1, lodged 2034-01-03, and its status is open.
Correspondence about S-0195 is filed under the district rather than under the site, which has caused confusion before.

### S-0196 -- Cedar Landing

The survey party reached Cedar Landing on the eleventh of the month and found the access track passable for light vehicles only.
Correspondence about S-0196 is filed under the district rather than under the site, which has caused confusion before.
S-0196 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The access key for S-0196 is held at the district office and signed out per visit.
Drainage work near Cedar Landing was completed without interruption to the record.
The reading shelter at Cedar Landing takes water in heavy weather and the floor was relaid.
The fence line at Cedar Landing was rerun 5 metres to the east to clear the culvert.
The district file for Cedar Landing shows revision 4 lodged on 2034-05-18.
For S-0196 the status is open, the tier is 2, and the load is 493.
Maintenance visits to S-0196 are scheduled quarterly and the third of those was carried out as planned.
Telemetry from S-0196 arrives on the eighth relay and is batched nightly rather than streamed.
Two of the anchors at Cedar Landing were replaced after the frost and the work is recorded in the district ledger.

### S-0197 -- Tamarisk Shaw

Two of the anchors at Tamarisk Shaw were replaced after the frost and the work is recorded in the district ledger.
Signal strength at Tamarisk Shaw has been marginal since the mast on the ridge was lowered.
The instrument housing at Tamarisk Shaw is the original pattern and its door seal is checked each visit.
The survey party reached Tamarisk Shaw on the tenth of the month and found the access track passable for light vehicles only.
Vegetation around Tamarisk Shaw is cut back twice a year under the standing arrangement.
The load recorded for S-0197 is 278, on a return at tier 4.
That return for Tamarisk Shaw is revision 2, lodged 2034-06-10, and its status is settled.
The offset applied to readings from S-0197 is 31 and has not been revised.
Calibration gear for S-0197 travels with the district van and is shared with 27 other sites.
Correspondence about S-0197 is filed under the district rather than under the site, which has caused confusion before.
Tamarisk Shaw shares its power feed with the neighbouring pumping station and has its own cut-out.
A visitor log is kept at Tamarisk Shaw and shows 83 entries for the period.

### S-0198 -- Saffron Pike

Access to Saffron Pike is by the service road from the south; the gate code was reissued after the fourth inspection.
The reading shelter at Saffron Pike takes water in heavy weather and the floor was relaid.
Saffron Pike shares its power feed with the neighbouring pumping station and has its own cut-out.
On 2034-12-02 the district accepted revision 6 for Saffron Pike and marked it withdrawn.
S-0198 carries tier 1 on that revision and a load of 567.
Saffron Pike carries a calibration offset of 36 on the current instrument head.
S-0198 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Telemetry from S-0198 arrives on the fifth relay and is batched nightly rather than streamed.

### S-0199 -- Calder Withy

The notes for S-0199 mention a disused well inside the compound, capped and recorded but not surveyed.
The site plan for Calder Withy is the eleventh revision and supersedes the sketch held in the district folder.
An earlier clerk recorded Calder Withy under a shortened spelling, and both forms still appear in the older indexes.
The fence line at Calder Withy was rerun 37 metres to the east to clear the culvert.
S-0199 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The approach to Calder Withy crosses 36 field boundaries and the wayleave is held by the county.
On 2034-04-27 the district accepted revision 6 for Calder Withy and marked it settled.
S-0199 carries tier 2 on that revision and a load of 746.
Correspondence about S-0199 is filed under the district rather than under the site, which has caused confusion before.
Access to Calder Withy is by the service road from the south; the gate code was reissued after the twelfth inspection.
The instrument housing at Calder Withy is the original pattern and its door seal is checked each visit.

### S-0200 -- Linden Strand

A visitor log is kept at Linden Strand and shows 41 entries for the period.
A housekeeping note against S-0200 asks that the cable run be rewalked before the next dry season.
The fence line at Linden Strand was rerun 18 metres to the east to clear the culvert.
Calibration gear for S-0200 travels with the district van and is shared with 24 other sites.
Correspondence about S-0200 is filed under the district rather than under the site, which has caused confusion before.
S-0200 appears at revision 3 with a load of 264.
That revision of Linden Strand was lodged 2034-06-19, is withdrawn, and places the station in tier 3.
Signal strength at Linden Strand has been marginal since the mast on the ridge was lowered.
A spare sensor head is kept at Linden Strand against the failure that took out the district in the previous cycle.
The access key for S-0200 is held at the district office and signed out per visit.
Drainage work near Linden Strand was completed without interruption to the record.

### S-0201 -- Calder Yard

A housekeeping note against S-0201 asks that the cable run be rewalked before the next dry season.
Access to Calder Yard is by the service road from the south; the gate code was reissued after the first inspection.
A visitor log is kept at Calder Yard and shows 47 entries for the period.
On 2034-07-25 the district accepted revision 6 for Calder Yard and marked it returned.
S-0201 carries tier 1 on that revision and a load of 527.
Telemetry from S-0201 arrives on the sixth relay and is batched nightly rather than streamed.
The survey party reached Calder Yard on the fifth of the month and found the access track passable for light vehicles only.
Calder Yard has been on the register since the first consolidation and its paperwork has never been reconstructed.
The site plan for Calder Yard is the tenth revision and supersedes the sketch held in the district folder.
The fence line at Calder Yard was rerun 40 metres to the east to clear the culvert.

### S-0202 -- Osier Mere

The enclosure at Osier Mere was rebuilt in timber after the old fencing was taken by the river.
Telemetry from S-0202 arrives on the first relay and is batched nightly rather than streamed.
The logbook kept at Osier Mere runs to 52 pages and the earlier volumes are held off site.
Drainage work near Osier Mere was completed without interruption to the record.
Weather at Osier Mere closed the approach for 29 days during the period under review and no readings were lost.
Tier 5 is where Osier Mere sits on revision 3, whose status is open.
The load on that revision of S-0202, lodged 2034-05-20, is 982.
The fence line at Osier Mere was rerun 2 metres to the east to clear the culvert.

### S-0203 -- Vellum Glade

An earlier clerk recorded Vellum Glade under a shortened spelling, and both forms still appear in the older indexes.
A visitor log is kept at Vellum Glade and shows 37 entries for the period.
The reading shelter at Vellum Glade takes water in heavy weather and the floor was relaid.
Vellum Glade lodged revision 6 on 2034-06-07.
The return for S-0203 is withdrawn, sits at tier 9, and records a load of 802.
Correspondence about S-0203 is filed under the district rather than under the site, which has caused confusion before.
The logbook kept at Vellum Glade runs to 44 pages and the earlier volumes are held off site.

### S-0204 -- Fennel Vale

Vegetation around Fennel Vale is cut back twice a year under the standing arrangement.
Fennel Vale lodged revision 4 on 2034-08-02.
The return for S-0204 is settled, sits at tier 4, and records a load of 625.
The enclosure at Fennel Vale was rebuilt in timber after the old fencing was taken by the river.
The logbook kept at Fennel Vale runs to 4 pages and the earlier volumes are held off site.
A housekeeping note against S-0204 asks that the cable run be rewalked before the next dry season.
The site plan for Fennel Vale is the twelfth revision and supersedes the sketch held in the district folder.
Telemetry from S-0204 arrives on the fourteenth relay and is batched nightly rather than streamed.
Maintenance visits to S-0204 are scheduled quarterly and the eighth of those was carried out as planned.

### S-0205 -- Ember Staithe

The instrument housing at Ember Staithe is the original pattern and its door seal is checked each visit.
Ember Staithe has been on the register since the first consolidation and its paperwork has never been reconstructed.
Drainage work near Ember Staithe was completed without interruption to the record.
S-0205 appears at revision 3 with a load of 145.
That revision of Ember Staithe was lodged 2034-08-27, is settled, and places the station in tier 3.
Telemetry from S-0205 arrives on the twelfth relay and is batched nightly rather than streamed.
The notes for S-0205 mention a disused well inside the compound, capped and recorded but not surveyed.
Vegetation around Ember Staithe is cut back twice a year under the standing arrangement.
A housekeeping note against S-0205 asks that the cable run be rewalked before the next dry season.
Calibration gear for S-0205 travels with the district van and is shared with 20 other sites.
The survey party reached Ember Staithe on the twelfth of the month and found the access track passable for light vehicles only.
Correspondence about S-0205 is filed under the district rather than under the site, which has caused confusion before.

### S-0206 -- Ridge Strand

Correspondence shows the tenancy at Ridge Strand was renewed for a further 8 years.
Correspondence about S-0206 is filed under the district rather than under the site, which has caused confusion before.
The access key for S-0206 is held at the district office and signed out per visit.
Two of the anchors at Ridge Strand were replaced after the frost and the work is recorded in the district ledger.
The fence line at Ridge Strand was rerun 15 metres to the east to clear the culvert.
Ridge Strand has been on the register since the first consolidation and its paperwork has never been reconstructed.
Revision 3 of the return for Ridge Strand was lodged on 2034-06-17 and stands settled.
That revision places S-0206 in tier 1 and gives its load as 426.
The notes for S-0206 mention a disused well inside the compound, capped and recorded but not surveyed.
The site plan for Ridge Strand is the sixth revision and supersedes the sketch held in the district folder.
S-0206 was one of the sites brought forward in the consolidation and its numbering reflects that order.

### S-0207 -- Quince Brook

Quince Brook has been on the register since the first consolidation and its paperwork has never been reconstructed.
The reading shelter at Quince Brook takes water in heavy weather and the floor was relaid.
S-0207 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Correspondence about S-0207 is filed under the district rather than under the site, which has caused confusion before.
Two of the anchors at Quince Brook were replaced after the frost and the work is recorded in the district ledger.
A spare sensor head is kept at Quince Brook against the failure that took out the district in the previous cycle.
Signal strength at Quince Brook has been marginal since the mast on the ridge was lowered.
A housekeeping note against S-0207 asks that the cable run be rewalked before the next dry season.
The logbook kept at Quince Brook runs to 56 pages and the earlier volumes are held off site.
Quince Brook lodged revision 4 on 2034-12-05.
The return for S-0207 is provisional, sits at tier 6, and records a load of 791.
The instrument housing at Quince Brook is the original pattern and its door seal is checked each visit.

### S-0208 -- Granite Scarp

Maintenance visits to S-0208 are scheduled quarterly and the sixth of those was carried out as planned.
Revision 1 of the return for Granite Scarp was lodged on 2034-12-08 and stands settled.
That revision places S-0208 in tier 1 and gives its load as 897.
The offset applied to readings from S-0208 is -38 and has not been revised.
Granite Scarp has been on the register since the first consolidation and its paperwork has never been reconstructed.
The instrument housing at Granite Scarp is the original pattern and its door seal is checked each visit.
Drainage work near Granite Scarp was completed without interruption to the record.
The access key for S-0208 is held at the district office and signed out per visit.

### S-0209 -- Dapple Knap

The instrument housing at Dapple Knap is the original pattern and its door seal is checked each visit.
Weather at Dapple Knap closed the approach for 13 days during the period under review and no readings were lost.
S-0209 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The load recorded for S-0209 is 922, on a return at tier 1.
That return for Dapple Knap is revision 4, lodged 2034-07-24, and its status is settled.
The notes for S-0209 mention a disused well inside the compound, capped and recorded but not surveyed.

### S-0210 -- Clover Terrace

A visitor log is kept at Clover Terrace and shows 81 entries for the period.
On 2034-04-28 the district accepted revision 6 for Clover Terrace and marked it provisional.
S-0210 carries tier 3 on that revision and a load of 891.
The access key for S-0210 is held at the district office and signed out per visit.
The logbook kept at Clover Terrace runs to 20 pages and the earlier volumes are held off site.
Clover Terrace has been on the register since the first consolidation and its paperwork has never been reconstructed.
Correspondence about S-0210 is filed under the district rather than under the site, which has caused confusion before.
Maintenance visits to S-0210 are scheduled quarterly and the tenth of those was carried out as planned.

### S-0211 -- Ochre Butte

Ochre Butte has been on the register since the first consolidation and its paperwork has never been reconstructed.
The access key for S-0211 is held at the district office and signed out per visit.
Revision 5 of the return for Ochre Butte was lodged on 2034-05-15 and stands open.
That revision places S-0211 in tier 5 and gives its load as 119.
The offset applied to readings from S-0211 is -22 and has not been revised.
The site plan for Ochre Butte is the fourth revision and supersedes the sketch held in the district folder.
The notes for S-0211 mention a disused well inside the compound, capped and recorded but not surveyed.

### S-0212 -- Sorrel Anchorage

The logbook kept at Sorrel Anchorage runs to 89 pages and the earlier volumes are held off site.
Correspondence about S-0212 is filed under the district rather than under the site, which has caused confusion before.
S-0212 appears at revision 6 with a load of 461.
That revision of Sorrel Anchorage was lodged 2034-10-19, is returned, and places the station in tier 2.
Sorrel Anchorage has been on the register since the first consolidation and its paperwork has never been reconstructed.
Drainage work near Sorrel Anchorage was completed without interruption to the record.
The access key for S-0212 is held at the district office and signed out per visit.

### S-0213 -- Granite Causeway

Vegetation around Granite Causeway is cut back twice a year under the standing arrangement.
The survey party reached Granite Causeway on the fourteenth of the month and found the access track passable for light vehicles only.
The logbook kept at Granite Causeway runs to 6 pages and the earlier volumes are held off site.
An earlier clerk recorded Granite Causeway under a shortened spelling, and both forms still appear in the older indexes.
Granite Causeway lodged revision 5 on 2034-08-07.
The return for S-0213 is withdrawn, sits at tier 1, and records a load of 818.
Drainage work near Granite Causeway was completed without interruption to the record.
A visitor log is kept at Granite Causeway and shows 85 entries for the period.
Signal strength at Granite Causeway has been marginal since the mast on the ridge was lowered.
The enclosure at Granite Causeway was rebuilt in timber after the old fencing was taken by the river.

### S-0214 -- Teasel Strand

Correspondence shows the tenancy at Teasel Strand was renewed for a further 38 years.
S-0214 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The notes for S-0214 mention a disused well inside the compound, capped and recorded but not surveyed.
The district file for Teasel Strand shows revision 4 lodged on 2034-10-14.
For S-0214 the status is provisional, the tier is 2, and the load is 263.
Teasel Strand shares its power feed with the neighbouring pumping station and has its own cut-out.
Vegetation around Teasel Strand is cut back twice a year under the standing arrangement.
The enclosure at Teasel Strand was rebuilt in timber after the old fencing was taken by the river.

### S-0215 -- Fennel Fell

A spare sensor head is kept at Fennel Fell against the failure that took out the district in the previous cycle.
A housekeeping note against S-0215 asks that the cable run be rewalked before the next dry season.
The notes for S-0215 mention a disused well inside the compound, capped and recorded but not surveyed.
Revision 6 of the return for Fennel Fell was lodged on 2034-09-28 and stands withdrawn.
That revision places S-0215 in tier 1 and gives its load as 272.
Fennel Fell carries a calibration offset of -20 on the current instrument head.
An earlier clerk recorded Fennel Fell under a shortened spelling, and both forms still appear in the older indexes.
Calibration gear for S-0215 travels with the district van and is shared with 4 other sites.
Two of the anchors at Fennel Fell were replaced after the frost and the work is recorded in the district ledger.

### S-0216 -- Linden Moor

A spare sensor head is kept at Linden Moor against the failure that took out the district in the previous cycle.
The notes for S-0216 mention a disused well inside the compound, capped and recorded but not surveyed.
The logbook kept at Linden Moor runs to 57 pages and the earlier volumes are held off site.
Revision 3 of the return for Linden Moor was lodged on 2034-07-13 and stands settled.
That revision places S-0216 in tier 2 and gives its load as 139.
Linden Moor carries a calibration offset of 10 on the current instrument head.
A housekeeping note against S-0216 asks that the cable run be rewalked before the next dry season.
The enclosure at Linden Moor was rebuilt in timber after the old fencing was taken by the river.
A visitor log is kept at Linden Moor and shows 49 entries for the period.

### S-0217 -- Hazel Mill

Drainage work near Hazel Mill was completed without interruption to the record.
The fence line at Hazel Mill was rerun 8 metres to the east to clear the culvert.
The load recorded for S-0217 is 890, on a return at tier 4.
That return for Hazel Mill is revision 6, lodged 2034-05-17, and its status is open.
Hazel Mill carries a calibration offset of -38 on the current instrument head.
Vegetation around Hazel Mill is cut back twice a year under the standing arrangement.
Correspondence about S-0217 is filed under the district rather than under the site, which has caused confusion before.
Hazel Mill shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0218 -- Garnet Fell

The site plan for Garnet Fell is the sixth revision and supersedes the sketch held in the district folder.
The district file for Garnet Fell shows revision 4 lodged on 2034-05-12.
For S-0218 the status is settled, the tier is 2, and the load is 996.
A spare sensor head is kept at Garnet Fell against the failure that took out the district in the previous cycle.
Maintenance visits to S-0218 are scheduled quarterly and the eleventh of those was carried out as planned.
The logbook kept at Garnet Fell runs to 4 pages and the earlier volumes are held off site.
Correspondence shows the tenancy at Garnet Fell was renewed for a further 72 years.

### S-0219 -- Dapple Pike

The approach to Dapple Pike crosses 11 field boundaries and the wayleave is held by the county.
Drainage work near Dapple Pike was completed without interruption to the record.
The fence line at Dapple Pike was rerun 34 metres to the east to clear the culvert.
The enclosure at Dapple Pike was rebuilt in timber after the old fencing was taken by the river.
A housekeeping note against S-0219 asks that the cable run be rewalked before the next dry season.
The survey party reached Dapple Pike on the tenth of the month and found the access track passable for light vehicles only.
On 2034-09-27 the district accepted revision 6 for Dapple Pike and marked it settled.
S-0219 carries tier 3 on that revision and a load of 854.
The reading shelter at Dapple Pike takes water in heavy weather and the floor was relaid.
A spare sensor head is kept at Dapple Pike against the failure that took out the district in the previous cycle.

### S-0220 -- Quarry Copse

A spare sensor head is kept at Quarry Copse against the failure that took out the district in the previous cycle.
The approach to Quarry Copse crosses 40 field boundaries and the wayleave is held by the county.
Tier 2 is where Quarry Copse sits on revision 3, whose status is settled.
The load on that revision of S-0220, lodged 2034-05-10, is 513.
The enclosure at Quarry Copse was rebuilt in timber after the old fencing was taken by the river.
The logbook kept at Quarry Copse runs to 3 pages and the earlier volumes are held off site.
The reading shelter at Quarry Copse takes water in heavy weather and the floor was relaid.
Two of the anchors at Quarry Copse were replaced after the frost and the work is recorded in the district ledger.

### S-0221 -- Bronze Landing

Weather at Bronze Landing closed the approach for 33 days during the period under review and no readings were lost.
Bronze Landing has been on the register since the first consolidation and its paperwork has never been reconstructed.
The site plan for Bronze Landing is the fourth revision and supersedes the sketch held in the district folder.
The reading shelter at Bronze Landing takes water in heavy weather and the floor was relaid.
Telemetry from S-0221 arrives on the tenth relay and is batched nightly rather than streamed.
The instrument housing at Bronze Landing is the original pattern and its door seal is checked each visit.
Signal strength at Bronze Landing has been marginal since the mast on the ridge was lowered.
Tier 6 is where Bronze Landing sits on revision 3, whose status is settled.
The load on that revision of S-0221, lodged 2034-05-13, is 509.
The offset applied to readings from S-0221 is -19 and has not been revised.
This revision of S-0221 is marked 5 in the reconciliation sequence.
The fence line at Bronze Landing was rerun 34 metres to the east to clear the culvert.

### S-0222 -- Midland Dale

The survey party reached Midland Dale on the second of the month and found the access track passable for light vehicles only.
The logbook kept at Midland Dale runs to 52 pages and the earlier volumes are held off site.
Midland Dale has been on the register since the first consolidation and its paperwork has never been reconstructed.
Vegetation around Midland Dale is cut back twice a year under the standing arrangement.
The fence line at Midland Dale was rerun 35 metres to the east to clear the culvert.
Calibration gear for S-0222 travels with the district van and is shared with 31 other sites.
Tier 9 is where Midland Dale sits on revision 5, whose status is settled.
The load on that revision of S-0222, lodged 2034-03-16, is 486.
The reading shelter at Midland Dale takes water in heavy weather and the floor was relaid.
The approach to Midland Dale crosses 5 field boundaries and the wayleave is held by the county.
Access to Midland Dale is by the service road from the south; the gate code was reissued after the first inspection.
Telemetry from S-0222 arrives on the sixth relay and is batched nightly rather than streamed.

### S-0223 -- Gorse Culvert

Signal strength at Gorse Culvert has been marginal since the mast on the ridge was lowered.
The survey party reached Gorse Culvert on the thirteenth of the month and found the access track passable for light vehicles only.
The logbook kept at Gorse Culvert runs to 71 pages and the earlier volumes are held off site.
The load recorded for S-0223 is 485, on a return at tier 1.
That return for Gorse Culvert is revision 5, lodged 2034-03-19, and its status is settled.
Drainage work near Gorse Culvert was completed without interruption to the record.
The site plan for Gorse Culvert is the eighth revision and supersedes the sketch held in the district folder.

### S-0224 -- Osier Delve

The access key for S-0224 is held at the district office and signed out per visit.
Osier Delve has been on the register since the first consolidation and its paperwork has never been reconstructed.
The notes for S-0224 mention a disused well inside the compound, capped and recorded but not surveyed.
An earlier clerk recorded Osier Delve under a shortened spelling, and both forms still appear in the older indexes.
S-0224 appears at revision 5 with a load of 880.
That revision of Osier Delve was lodged 2034-06-21, is open, and places the station in tier 5.
The survey party reached Osier Delve on the fourteenth of the month and found the access track passable for light vehicles only.
A housekeeping note against S-0224 asks that the cable run be rewalked before the next dry season.
The reading shelter at Osier Delve takes water in heavy weather and the floor was relaid.
Signal strength at Osier Delve has been marginal since the mast on the ridge was lowered.
The fence line at Osier Delve was rerun 26 metres to the east to clear the culvert.

### S-0225 -- Birch Dingle

Calibration gear for S-0225 travels with the district van and is shared with 22 other sites.
S-0225 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The instrument housing at Birch Dingle is the original pattern and its door seal is checked each visit.
The survey party reached Birch Dingle on the eleventh of the month and found the access track passable for light vehicles only.
Two of the anchors at Birch Dingle were replaced after the frost and the work is recorded in the district ledger.
The district file for Birch Dingle shows revision 3 lodged on 2034-12-04.
For S-0225 the status is settled, the tier is 7, and the load is 814.
Correspondence about S-0225 is filed under the district rather than under the site, which has caused confusion before.
The access key for S-0225 is held at the district office and signed out per visit.
The reading shelter at Birch Dingle takes water in heavy weather and the floor was relaid.
Vegetation around Birch Dingle is cut back twice a year under the standing arrangement.

### S-0226 -- Flint Staithe

Vegetation around Flint Staithe is cut back twice a year under the standing arrangement.
The access key for S-0226 is held at the district office and signed out per visit.
Access to Flint Staithe is by the service road from the south; the gate code was reissued after the ninth inspection.
Flint Staithe shares its power feed with the neighbouring pumping station and has its own cut-out.
Calibration gear for S-0226 travels with the district van and is shared with 24 other sites.
The enclosure at Flint Staithe was rebuilt in timber after the old fencing was taken by the river.
Correspondence about S-0226 is filed under the district rather than under the site, which has caused confusion before.
A spare sensor head is kept at Flint Staithe against the failure that took out the district in the previous cycle.
The load recorded for S-0226 is 254, on a return at tier 1.
That return for Flint Staithe is revision 1, lodged 2034-06-23, and its status is open.
The notes for S-0226 mention a disused well inside the compound, capped and recorded but not surveyed.
Telemetry from S-0226 arrives on the fourteenth relay and is batched nightly rather than streamed.

### S-0227 -- Chalk Slade

The access key for S-0227 is held at the district office and signed out per visit.
S-0227 appears at revision 1 with a load of 597.
That revision of Chalk Slade was lodged 2034-09-03, is settled, and places the station in tier 2.
Vegetation around Chalk Slade is cut back twice a year under the standing arrangement.
A visitor log is kept at Chalk Slade and shows 30 entries for the period.
Calibration gear for S-0227 travels with the district van and is shared with 4 other sites.
S-0227 was one of the sites brought forward in the consolidation and its numbering reflects that order.

### S-0228 -- Auburn Dale

Drainage work near Auburn Dale was completed without interruption to the record.
The district file for Auburn Dale shows revision 5 lodged on 2034-04-06.
For S-0228 the status is settled, the tier is 4, and the load is 618.
The survey party reached Auburn Dale on the tenth of the month and found the access track passable for light vehicles only.
A housekeeping note against S-0228 asks that the cable run be rewalked before the next dry season.
The enclosure at Auburn Dale was rebuilt in timber after the old fencing was taken by the river.
A spare sensor head is kept at Auburn Dale against the failure that took out the district in the previous cycle.

### S-0229 -- Umber Ripple

The survey party reached Umber Ripple on the fourteenth of the month and found the access track passable for light vehicles only.
A spare sensor head is kept at Umber Ripple against the failure that took out the district in the previous cycle.
The logbook kept at Umber Ripple runs to 84 pages and the earlier volumes are held off site.
The instrument housing at Umber Ripple is the original pattern and its door seal is checked each visit.
A visitor log is kept at Umber Ripple and shows 81 entries for the period.
S-0229 appears at revision 4 with a load of 598.
That revision of Umber Ripple was lodged 2034-12-25, is settled, and places the station in tier 3.
The offset applied to readings from S-0229 is -6 and has not been revised.
An earlier clerk recorded Umber Ripple under a shortened spelling, and both forms still appear in the older indexes.
Maintenance visits to S-0229 are scheduled quarterly and the eleventh of those was carried out as planned.
Weather at Umber Ripple closed the approach for 9 days during the period under review and no readings were lost.

### S-0230 -- Umber Rill

The notes for S-0230 mention a disused well inside the compound, capped and recorded but not surveyed.
Weather at Umber Rill closed the approach for 11 days during the period under review and no readings were lost.
The logbook kept at Umber Rill runs to 86 pages and the earlier volumes are held off site.
Vegetation around Umber Rill is cut back twice a year under the standing arrangement.
The approach to Umber Rill crosses 18 field boundaries and the wayleave is held by the county.
Status settled: revision 3 for S-0230, lodged 2034-11-22.
Load 987 at tier 8 is what that revision carries for Umber Rill.
Access to Umber Rill is by the service road from the south; the gate code was reissued after the tenth inspection.
Maintenance visits to S-0230 are scheduled quarterly and the second of those was carried out as planned.
An earlier clerk recorded Umber Rill under a shortened spelling, and both forms still appear in the older indexes.
The fence line at Umber Rill was rerun 4 metres to the east to clear the culvert.

### S-0231 -- Dusk Vale

Correspondence about S-0231 is filed under the district rather than under the site, which has caused confusion before.
Drainage work near Dusk Vale was completed without interruption to the record.
Calibration gear for S-0231 travels with the district van and is shared with 30 other sites.
The enclosure at Dusk Vale was rebuilt in timber after the old fencing was taken by the river.
The notes for S-0231 mention a disused well inside the compound, capped and recorded but not surveyed.
The district file for Dusk Vale shows revision 6 lodged on 2034-03-06.
For S-0231 the status is settled, the tier is 3, and the load is 232.
Dusk Vale has been on the register since the first consolidation and its paperwork has never been reconstructed.

### S-0232 -- Ochre Rill

Two of the anchors at Ochre Rill were replaced after the frost and the work is recorded in the district ledger.
The notes for S-0232 mention a disused well inside the compound, capped and recorded but not surveyed.
Vegetation around Ochre Rill is cut back twice a year under the standing arrangement.
The reading shelter at Ochre Rill takes water in heavy weather and the floor was relaid.
Access to Ochre Rill is by the service road from the south; the gate code was reissued after the ninth inspection.
Status withdrawn: revision 2 for S-0232, lodged 2034-10-13.
Load 606 at tier 6 is what that revision carries for Ochre Rill.
Telemetry from S-0232 arrives on the second relay and is batched nightly rather than streamed.
Maintenance visits to S-0232 are scheduled quarterly and the tenth of those was carried out as planned.

### S-0233 -- Garnet Moor

A spare sensor head is kept at Garnet Moor against the failure that took out the district in the previous cycle.
Revision 5 of the return for Garnet Moor was lodged on 2034-05-13 and stands settled.
That revision places S-0233 in tier 4 and gives its load as 878.
The instrument housing at Garnet Moor is the original pattern and its door seal is checked each visit.
Calibration gear for S-0233 travels with the district van and is shared with 35 other sites.
The site plan for Garnet Moor is the tenth revision and supersedes the sketch held in the district folder.
The survey party reached Garnet Moor on the third of the month and found the access track passable for light vehicles only.
S-0233 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Garnet Moor shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0234 -- Hazel Furlong

Correspondence shows the tenancy at Hazel Furlong was renewed for a further 67 years.
The district file for Hazel Furlong shows revision 6 lodged on 2034-09-05.
For S-0234 the status is withdrawn, the tier is 6, and the load is 268.
The site plan for Hazel Furlong is the seventh revision and supersedes the sketch held in the district folder.
Weather at Hazel Furlong closed the approach for 11 days during the period under review and no readings were lost.
A visitor log is kept at Hazel Furlong and shows 8 entries for the period.
The survey party reached Hazel Furlong on the eleventh of the month and found the access track passable for light vehicles only.
Drainage work near Hazel Furlong was completed without interruption to the record.

### S-0235 -- Fennel Scarp

The survey party reached Fennel Scarp on the twelfth of the month and found the access track passable for light vehicles only.
Maintenance visits to S-0235 are scheduled quarterly and the tenth of those was carried out as planned.
The access key for S-0235 is held at the district office and signed out per visit.
The fence line at Fennel Scarp was rerun 6 metres to the east to clear the culvert.
Fennel Scarp lodged revision 5 on 2034-11-06.
The return for S-0235 is provisional, sits at tier 3, and records a load of 269.
A housekeeping note against S-0235 asks that the cable run be rewalked before the next dry season.
The instrument housing at Fennel Scarp is the original pattern and its door seal is checked each visit.

### S-0236 -- Sorrel Causeway

Sorrel Causeway shares its power feed with the neighbouring pumping station and has its own cut-out.
Calibration gear for S-0236 travels with the district van and is shared with 5 other sites.
The instrument housing at Sorrel Causeway is the original pattern and its door seal is checked each visit.
Revision 5 of the return for Sorrel Causeway was lodged on 2034-11-16 and stands settled.
That revision places S-0236 in tier 4 and gives its load as 965.
The logbook kept at Sorrel Causeway runs to 18 pages and the earlier volumes are held off site.
The survey party reached Sorrel Causeway on the sixth of the month and found the access track passable for light vehicles only.

### S-0237 -- Beacon Haven

The reading shelter at Beacon Haven takes water in heavy weather and the floor was relaid.
Beacon Haven lodged revision 4 on 2034-08-19.
The return for S-0237 is withdrawn, sits at tier 3, and records a load of 427.
A spare sensor head is kept at Beacon Haven against the failure that took out the district in the previous cycle.
An earlier clerk recorded Beacon Haven under a shortened spelling, and both forms still appear in the older indexes.
Correspondence about S-0237 is filed under the district rather than under the site, which has caused confusion before.
The access key for S-0237 is held at the district office and signed out per visit.
Drainage work near Beacon Haven was completed without interruption to the record.
The notes for S-0237 mention a disused well inside the compound, capped and recorded but not surveyed.
Beacon Haven has been on the register since the first consolidation and its paperwork has never been reconstructed.
The enclosure at Beacon Haven was rebuilt in timber after the old fencing was taken by the river.

### S-0238 -- Mellow Headland

Correspondence shows the tenancy at Mellow Headland was renewed for a further 50 years.
The survey party reached Mellow Headland on the twelfth of the month and found the access track passable for light vehicles only.
Tier 4 is where Mellow Headland sits on revision 1, whose status is settled.
The load on that revision of S-0238, lodged 2034-06-17, is 812.
The instrument housing at Mellow Headland is the original pattern and its door seal is checked each visit.
The enclosure at Mellow Headland was rebuilt in timber after the old fencing was taken by the river.
The fence line at Mellow Headland was rerun 6 metres to the east to clear the culvert.
Drainage work near Mellow Headland was completed without interruption to the record.

### S-0239 -- Thistle Knoll

Maintenance visits to S-0239 are scheduled quarterly and the sixth of those was carried out as planned.
Thistle Knoll lodged revision 6 on 2034-12-18.
The return for S-0239 is provisional, sits at tier 8, and records a load of 551.
S-0239 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Drainage work near Thistle Knoll was completed without interruption to the record.
The notes for S-0239 mention a disused well inside the compound, capped and recorded but not surveyed.
The approach to Thistle Knoll crosses 37 field boundaries and the wayleave is held by the county.
The reading shelter at Thistle Knoll takes water in heavy weather and the floor was relaid.
Signal strength at Thistle Knoll has been marginal since the mast on the ridge was lowered.

### S-0240 -- Dusk Spur

Maintenance visits to S-0240 are scheduled quarterly and the sixth of those was carried out as planned.
Calibration gear for S-0240 travels with the district van and is shared with 15 other sites.
S-0240 appears at revision 6 with a load of 511.
That revision of Dusk Spur was lodged 2034-09-03, is open, and places the station in tier 7.
Dusk Spur carries a calibration offset of 9 on the current instrument head.
Correspondence shows the tenancy at Dusk Spur was renewed for a further 6 years.
Drainage work near Dusk Spur was completed without interruption to the record.

### S-0241 -- Meadow Ripple

The notes for S-0241 mention a disused well inside the compound, capped and recorded but not surveyed.
The access key for S-0241 is held at the district office and signed out per visit.
A housekeeping note against S-0241 asks that the cable run be rewalked before the next dry season.
The approach to Meadow Ripple crosses 19 field boundaries and the wayleave is held by the county.
Correspondence shows the tenancy at Meadow Ripple was renewed for a further 37 years.
Meadow Ripple shares its power feed with the neighbouring pumping station and has its own cut-out.
Telemetry from S-0241 arrives on the fourteenth relay and is batched nightly rather than streamed.
Meadow Ripple has been on the register since the first consolidation and its paperwork has never been reconstructed.
On 2034-12-21 the district accepted revision 2 for Meadow Ripple and marked it settled.
S-0241 carries tier 4 on that revision and a load of 241.
An earlier clerk recorded Meadow Ripple under a shortened spelling, and both forms still appear in the older indexes.

### S-0242 -- Osier Terrace

The fence line at Osier Terrace was rerun 34 metres to the east to clear the culvert.
Maintenance visits to S-0242 are scheduled quarterly and the eighth of those was carried out as planned.
Telemetry from S-0242 arrives on the fourteenth relay and is batched nightly rather than streamed.
Status returned: revision 3 for S-0242, lodged 2034-08-13.
Load 581 at tier 7 is what that revision carries for Osier Terrace.
A spare sensor head is kept at Osier Terrace against the failure that took out the district in the previous cycle.
A housekeeping note against S-0242 asks that the cable run be rewalked before the next dry season.

### S-0243 -- Pebble Brae

Correspondence shows the tenancy at Pebble Brae was renewed for a further 43 years.
Calibration gear for S-0243 travels with the district van and is shared with 26 other sites.
The enclosure at Pebble Brae was rebuilt in timber after the old fencing was taken by the river.
The notes for S-0243 mention a disused well inside the compound, capped and recorded but not surveyed.
S-0243 appears at revision 2 with a load of 787.
That revision of Pebble Brae was lodged 2034-05-23, is settled, and places the station in tier 3.
A spare sensor head is kept at Pebble Brae against the failure that took out the district in the previous cycle.

### S-0244 -- Crag Hollow

Crag Hollow has been on the register since the first consolidation and its paperwork has never been reconstructed.
S-0244 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Correspondence shows the tenancy at Crag Hollow was renewed for a further 39 years.
Vegetation around Crag Hollow is cut back twice a year under the standing arrangement.
Tier 4 is where Crag Hollow sits on revision 5, whose status is provisional.
The load on that revision of S-0244, lodged 2034-12-21, is 442.
Telemetry from S-0244 arrives on the eighth relay and is batched nightly rather than streamed.

### S-0245 -- Quarry Weir

Quarry Weir has been on the register since the first consolidation and its paperwork has never been reconstructed.
The logbook kept at Quarry Weir runs to 52 pages and the earlier volumes are held off site.
Access to Quarry Weir is by the service road from the south; the gate code was reissued after the tenth inspection.
Correspondence about S-0245 is filed under the district rather than under the site, which has caused confusion before.
The survey party reached Quarry Weir on the seventh of the month and found the access track passable for light vehicles only.
The fence line at Quarry Weir was rerun 23 metres to the east to clear the culvert.
S-0245 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The enclosure at Quarry Weir was rebuilt in timber after the old fencing was taken by the river.
The load recorded for S-0245 is 321, on a return at tier 9.
That return for Quarry Weir is revision 2, lodged 2034-10-26, and its status is withdrawn.
Maintenance visits to S-0245 are scheduled quarterly and the twelfth of those was carried out as planned.

### S-0246 -- Osier Culvert

Correspondence about S-0246 is filed under the district rather than under the site, which has caused confusion before.
Osier Culvert lodged revision 5 on 2034-06-07.
The return for S-0246 is settled, sits at tier 3, and records a load of 399.
The notes for S-0246 mention a disused well inside the compound, capped and recorded but not surveyed.
Osier Culvert shares its power feed with the neighbouring pumping station and has its own cut-out.
The survey party reached Osier Culvert on the eighth of the month and found the access track passable for light vehicles only.
The approach to Osier Culvert crosses 27 field boundaries and the wayleave is held by the county.
A spare sensor head is kept at Osier Culvert against the failure that took out the district in the previous cycle.
The enclosure at Osier Culvert was rebuilt in timber after the old fencing was taken by the river.
A visitor log is kept at Osier Culvert and shows 3 entries for the period.
The instrument housing at Osier Culvert is the original pattern and its door seal is checked each visit.

### S-0247 -- Marram Vale

Access to Marram Vale is by the service road from the south; the gate code was reissued after the eighth inspection.
The survey party reached Marram Vale on the first of the month and found the access track passable for light vehicles only.
Marram Vale has been on the register since the first consolidation and its paperwork has never been reconstructed.
The district file for Marram Vale shows revision 4 lodged on 2034-02-07.
For S-0247 the status is open, the tier is 1, and the load is 160.
The reading shelter at Marram Vale takes water in heavy weather and the floor was relaid.
Correspondence shows the tenancy at Marram Vale was renewed for a further 48 years.
Calibration gear for S-0247 travels with the district van and is shared with 12 other sites.
Telemetry from S-0247 arrives on the eighth relay and is batched nightly rather than streamed.
A spare sensor head is kept at Marram Vale against the failure that took out the district in the previous cycle.

### S-0248 -- Bramble Withy

The site plan for Bramble Withy is the fourteenth revision and supersedes the sketch held in the district folder.
The access key for S-0248 is held at the district office and signed out per visit.
Calibration gear for S-0248 travels with the district van and is shared with 37 other sites.
The survey party reached Bramble Withy on the second of the month and found the access track passable for light vehicles only.
Tier 2 is where Bramble Withy sits on revision 5, whose status is provisional.
The load on that revision of S-0248, lodged 2034-05-25, is 785.
Bramble Withy carries a calibration offset of -32 on the current instrument head.
A visitor log is kept at Bramble Withy and shows 36 entries for the period.

### S-0249 -- Osier Slade

Vegetation around Osier Slade is cut back twice a year under the standing arrangement.
The survey party reached Osier Slade on the ninth of the month and found the access track passable for light vehicles only.
A housekeeping note against S-0249 asks that the cable run be rewalked before the next dry season.
Osier Slade lodged revision 1 on 2034-03-22.
The return for S-0249 is returned, sits at tier 5, and records a load of 771.
The offset applied to readings from S-0249 is 4 and has not been revised.
Correspondence about S-0249 is filed under the district rather than under the site, which has caused confusion before.

### S-0250 -- Garnet Culvert

Access to Garnet Culvert is by the service road from the south; the gate code was reissued after the thirteenth inspection.
Vegetation around Garnet Culvert is cut back twice a year under the standing arrangement.
Correspondence shows the tenancy at Garnet Culvert was renewed for a further 67 years.
The enclosure at Garnet Culvert was rebuilt in timber after the old fencing was taken by the river.
Tier 2 is where Garnet Culvert sits on revision 1, whose status is settled.
The load on that revision of S-0250, lodged 2034-06-10, is 244.
Garnet Culvert carries a calibration offset of 4 on the current instrument head.
Telemetry from S-0250 arrives on the ninth relay and is batched nightly rather than streamed.
Garnet Culvert shares its power feed with the neighbouring pumping station and has its own cut-out.
A spare sensor head is kept at Garnet Culvert against the failure that took out the district in the previous cycle.
A housekeeping note against S-0250 asks that the cable run be rewalked before the next dry season.

### S-0251 -- Amber Strand

Telemetry from S-0251 arrives on the thirteenth relay and is batched nightly rather than streamed.
A visitor log is kept at Amber Strand and shows 87 entries for the period.
The enclosure at Amber Strand was rebuilt in timber after the old fencing was taken by the river.
The site plan for Amber Strand is the sixth revision and supersedes the sketch held in the district folder.
The instrument housing at Amber Strand is the original pattern and its door seal is checked each visit.
Maintenance visits to S-0251 are scheduled quarterly and the ninth of those was carried out as planned.
Revision 6 of the return for Amber Strand was lodged on 2034-03-05 and stands settled.
That revision places S-0251 in tier 3 and gives its load as 977.
The offset applied to readings from S-0251 is -8 and has not been revised.
Vegetation around Amber Strand is cut back twice a year under the standing arrangement.
Correspondence shows the tenancy at Amber Strand was renewed for a further 57 years.

### S-0252 -- Bronze Hollow

A spare sensor head is kept at Bronze Hollow against the failure that took out the district in the previous cycle.
Drainage work near Bronze Hollow was completed without interruption to the record.
The logbook kept at Bronze Hollow runs to 27 pages and the earlier volumes are held off site.
Status settled: revision 5 for S-0252, lodged 2034-09-14.
Load 498 at tier 3 is what that revision carries for Bronze Hollow.
Calibration gear for S-0252 travels with the district van and is shared with 27 other sites.
Bronze Hollow shares its power feed with the neighbouring pumping station and has its own cut-out.
Weather at Bronze Hollow closed the approach for 28 days during the period under review and no readings were lost.
Vegetation around Bronze Hollow is cut back twice a year under the standing arrangement.
The fence line at Bronze Hollow was rerun 35 metres to the east to clear the culvert.

### S-0253 -- Marram Cleave

Weather at Marram Cleave closed the approach for 22 days during the period under review and no readings were lost.
The access key for S-0253 is held at the district office and signed out per visit.
The district file for Marram Cleave shows revision 4 lodged on 2034-01-20.
For S-0253 the status is open, the tier is 2, and the load is 742.
The approach to Marram Cleave crosses 36 field boundaries and the wayleave is held by the county.
A spare sensor head is kept at Marram Cleave against the failure that took out the district in the previous cycle.
The survey party reached Marram Cleave on the thirteenth of the month and found the access track passable for light vehicles only.
The notes for S-0253 mention a disused well inside the compound, capped and recorded but not surveyed.
The logbook kept at Marram Cleave runs to 3 pages and the earlier volumes are held off site.
The site plan for Marram Cleave is the fifth revision and supersedes the sketch held in the district folder.

### S-0254 -- Indigo Combe

The instrument housing at Indigo Combe is the original pattern and its door seal is checked each visit.
On 2034-10-20 the district accepted revision 5 for Indigo Combe and marked it settled.
S-0254 carries tier 3 on that revision and a load of 447.
The notes for S-0254 mention a disused well inside the compound, capped and recorded but not surveyed.
A housekeeping note against S-0254 asks that the cable run be rewalked before the next dry season.
Maintenance visits to S-0254 are scheduled quarterly and the ninth of those was carried out as planned.

### S-0255 -- Mellow Dingle

The instrument housing at Mellow Dingle is the original pattern and its door seal is checked each visit.
The load recorded for S-0255 is 868, on a return at tier 1.
That return for Mellow Dingle is revision 6, lodged 2034-06-17, and its status is settled.
A visitor log is kept at Mellow Dingle and shows 79 entries for the period.
The logbook kept at Mellow Dingle runs to 89 pages and the earlier volumes are held off site.
Signal strength at Mellow Dingle has been marginal since the mast on the ridge was lowered.

### S-0256 -- Beacon Bight

The access key for S-0256 is held at the district office and signed out per visit.
The site plan for Beacon Bight is the third revision and supersedes the sketch held in the district folder.
Weather at Beacon Bight closed the approach for 36 days during the period under review and no readings were lost.
The reading shelter at Beacon Bight takes water in heavy weather and the floor was relaid.
Beacon Bight shares its power feed with the neighbouring pumping station and has its own cut-out.
Calibration gear for S-0256 travels with the district van and is shared with 29 other sites.
Correspondence about S-0256 is filed under the district rather than under the site, which has caused confusion before.
Revision 5 of the return for Beacon Bight was lodged on 2034-12-14 and stands returned.
That revision places S-0256 in tier 4 and gives its load as 367.
The logbook kept at Beacon Bight runs to 88 pages and the earlier volumes are held off site.

### S-0257 -- Dapple Fell

Signal strength at Dapple Fell has been marginal since the mast on the ridge was lowered.
Vegetation around Dapple Fell is cut back twice a year under the standing arrangement.
The survey party reached Dapple Fell on the twelfth of the month and found the access track passable for light vehicles only.
The site plan for Dapple Fell is the tenth revision and supersedes the sketch held in the district folder.
S-0257 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Correspondence shows the tenancy at Dapple Fell was renewed for a further 9 years.
S-0257 appears at revision 2 with a load of 766.
That revision of Dapple Fell was lodged 2034-09-28, is settled, and places the station in tier 3.
A spare sensor head is kept at Dapple Fell against the failure that took out the district in the previous cycle.
Calibration gear for S-0257 travels with the district van and is shared with 15 other sites.
An earlier clerk recorded Dapple Fell under a shortened spelling, and both forms still appear in the older indexes.
A housekeeping note against S-0257 asks that the cable run be rewalked before the next dry season.

### S-0258 -- Tamarisk Spur

Tamarisk Spur shares its power feed with the neighbouring pumping station and has its own cut-out.
The load recorded for S-0258 is 383, on a return at tier 1.
That return for Tamarisk Spur is revision 6, lodged 2034-03-13, and its status is settled.
Vegetation around Tamarisk Spur is cut back twice a year under the standing arrangement.
Calibration gear for S-0258 travels with the district van and is shared with 7 other sites.
Maintenance visits to S-0258 are scheduled quarterly and the twelfth of those was carried out as planned.

### S-0259 -- Yarrow Mere

A spare sensor head is kept at Yarrow Mere against the failure that took out the district in the previous cycle.
An earlier clerk recorded Yarrow Mere under a shortened spelling, and both forms still appear in the older indexes.
Calibration gear for S-0259 travels with the district van and is shared with 10 other sites.
S-0259 appears at revision 1 with a load of 960.
That revision of Yarrow Mere was lodged 2034-03-01, is open, and places the station in tier 2.
Correspondence shows the tenancy at Yarrow Mere was renewed for a further 68 years.

### S-0260 -- Flint Hallow

A visitor log is kept at Flint Hallow and shows 33 entries for the period.
A spare sensor head is kept at Flint Hallow against the failure that took out the district in the previous cycle.
Status withdrawn: revision 5 for S-0260, lodged 2034-03-11.
Load 930 at tier 1 is what that revision carries for Flint Hallow.
The offset applied to readings from S-0260 is 5 and has not been revised.
The survey party reached Flint Hallow on the ninth of the month and found the access track passable for light vehicles only.
Access to Flint Hallow is by the service road from the south; the gate code was reissued after the fourth inspection.
Telemetry from S-0260 arrives on the first relay and is batched nightly rather than streamed.

### S-0261 -- Lichen Down

A housekeeping note against S-0261 asks that the cable run be rewalked before the next dry season.
The survey party reached Lichen Down on the tenth of the month and found the access track passable for light vehicles only.
A visitor log is kept at Lichen Down and shows 14 entries for the period.
The approach to Lichen Down crosses 26 field boundaries and the wayleave is held by the county.
The site plan for Lichen Down is the eleventh revision and supersedes the sketch held in the district folder.
The enclosure at Lichen Down was rebuilt in timber after the old fencing was taken by the river.
The logbook kept at Lichen Down runs to 19 pages and the earlier volumes are held off site.
Revision 4 of the return for Lichen Down was lodged on 2034-12-02 and stands withdrawn.
That revision places S-0261 in tier 8 and gives its load as 557.
Calibration gear for S-0261 travels with the district van and is shared with 5 other sites.
Weather at Lichen Down closed the approach for 8 days during the period under review and no readings were lost.
Access to Lichen Down is by the service road from the south; the gate code was reissued after the fourteenth inspection.

### S-0262 -- Ember Beck

Calibration gear for S-0262 travels with the district van and is shared with 36 other sites.
Telemetry from S-0262 arrives on the fifth relay and is batched nightly rather than streamed.
The access key for S-0262 is held at the district office and signed out per visit.
Status settled: revision 1 for S-0262, lodged 2034-04-22.
Load 128 at tier 3 is what that revision carries for Ember Beck.
Signal strength at Ember Beck has been marginal since the mast on the ridge was lowered.
Ember Beck has been on the register since the first consolidation and its paperwork has never been reconstructed.
The site plan for Ember Beck is the fourteenth revision and supersedes the sketch held in the district folder.
The approach to Ember Beck crosses 28 field boundaries and the wayleave is held by the county.

### S-0263 -- Sedge Scarp

Maintenance visits to S-0263 are scheduled quarterly and the seventh of those was carried out as planned.
The site plan for Sedge Scarp is the eleventh revision and supersedes the sketch held in the district folder.
The district file for Sedge Scarp shows revision 6 lodged on 2034-07-09.
For S-0263 the status is settled, the tier is 2, and the load is 410.
The approach to Sedge Scarp crosses 29 field boundaries and the wayleave is held by the county.
The reading shelter at Sedge Scarp takes water in heavy weather and the floor was relaid.
The fence line at Sedge Scarp was rerun 11 metres to the east to clear the culvert.
Calibration gear for S-0263 travels with the district van and is shared with 7 other sites.

### S-0264 -- Midland Weir

The reading shelter at Midland Weir takes water in heavy weather and the floor was relaid.
Drainage work near Midland Weir was completed without interruption to the record.
Status provisional: revision 3 for S-0264, lodged 2034-03-12.
Load 826 at tier 1 is what that revision carries for Midland Weir.
A calibration offset of 8 is recorded for S-0264 against the district standard.
A spare sensor head is kept at Midland Weir against the failure that took out the district in the previous cycle.
The site plan for Midland Weir is the third revision and supersedes the sketch held in the district folder.
The notes for S-0264 mention a disused well inside the compound, capped and recorded but not surveyed.
The survey party reached Midland Weir on the fifth of the month and found the access track passable for light vehicles only.
An earlier clerk recorded Midland Weir under a shortened spelling, and both forms still appear in the older indexes.
A housekeeping note against S-0264 asks that the cable run be rewalked before the next dry season.
Vegetation around Midland Weir is cut back twice a year under the standing arrangement.

### S-0265 -- Hollow Bourne

Signal strength at Hollow Bourne has been marginal since the mast on the ridge was lowered.
The reading shelter at Hollow Bourne takes water in heavy weather and the floor was relaid.
On 2034-08-11 the district accepted revision 2 for Hollow Bourne and marked it withdrawn.
S-0265 carries tier 5 on that revision and a load of 355.
Telemetry from S-0265 arrives on the fourteenth relay and is batched nightly rather than streamed.
A visitor log is kept at Hollow Bourne and shows 83 entries for the period.
Hollow Bourne has been on the register since the first consolidation and its paperwork has never been reconstructed.
Calibration gear for S-0265 travels with the district van and is shared with 21 other sites.
A spare sensor head is kept at Hollow Bourne against the failure that took out the district in the previous cycle.

### S-0266 -- Quince Combe

The site plan for Quince Combe is the fifth revision and supersedes the sketch held in the district folder.
The load recorded for S-0266 is 397, on a return at tier 7.
That return for Quince Combe is revision 2, lodged 2034-07-06, and its status is returned.
Two of the anchors at Quince Combe were replaced after the frost and the work is recorded in the district ledger.
The instrument housing at Quince Combe is the original pattern and its door seal is checked each visit.
Calibration gear for S-0266 travels with the district van and is shared with 40 other sites.
Vegetation around Quince Combe is cut back twice a year under the standing arrangement.
A housekeeping note against S-0266 asks that the cable run be rewalked before the next dry season.
The access key for S-0266 is held at the district office and signed out per visit.
Maintenance visits to S-0266 are scheduled quarterly and the ninth of those was carried out as planned.

### S-0267 -- Quarry Warren

S-0267 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The instrument housing at Quarry Warren is the original pattern and its door seal is checked each visit.
A housekeeping note against S-0267 asks that the cable run be rewalked before the next dry season.
The fence line at Quarry Warren was rerun 13 metres to the east to clear the culvert.
The district file for Quarry Warren shows revision 5 lodged on 2034-04-23.
For S-0267 the status is settled, the tier is 1, and the load is 986.
Vegetation around Quarry Warren is cut back twice a year under the standing arrangement.
The logbook kept at Quarry Warren runs to 13 pages and the earlier volumes are held off site.
Correspondence about S-0267 is filed under the district rather than under the site, which has caused confusion before.

### S-0268 -- Crag Haven

Crag Haven has been on the register since the first consolidation and its paperwork has never been reconstructed.
S-0268 appears at revision 5 with a load of 331.
That revision of Crag Haven was lodged 2034-11-03, is settled, and places the station in tier 2.
An earlier clerk recorded Crag Haven under a shortened spelling, and both forms still appear in the older indexes.
Signal strength at Crag Haven has been marginal since the mast on the ridge was lowered.
The logbook kept at Crag Haven runs to 88 pages and the earlier volumes are held off site.

### S-0269 -- Hazel Bight

Signal strength at Hazel Bight has been marginal since the mast on the ridge was lowered.
Tier 6 is where Hazel Bight sits on revision 1, whose status is returned.
The load on that revision of S-0269, lodged 2034-01-09, is 841.
The enclosure at Hazel Bight was rebuilt in timber after the old fencing was taken by the river.
The fence line at Hazel Bight was rerun 27 metres to the east to clear the culvert.
The notes for S-0269 mention a disused well inside the compound, capped and recorded but not surveyed.
The instrument housing at Hazel Bight is the original pattern and its door seal is checked each visit.

### S-0270 -- Coral Pike

A visitor log is kept at Coral Pike and shows 71 entries for the period.
Weather at Coral Pike closed the approach for 35 days during the period under review and no readings were lost.
Correspondence about S-0270 is filed under the district rather than under the site, which has caused confusion before.
Access to Coral Pike is by the service road from the south; the gate code was reissued after the fourteenth inspection.
Coral Pike shares its power feed with the neighbouring pumping station and has its own cut-out.
The fence line at Coral Pike was rerun 5 metres to the east to clear the culvert.
S-0270 appears at revision 2 with a load of 578.
That revision of Coral Pike was lodged 2034-06-04, is returned, and places the station in tier 9.
Coral Pike carries a calibration offset of 39 on the current instrument head.
The instrument housing at Coral Pike is the original pattern and its door seal is checked each visit.

### S-0271 -- Ochre Holt

Calibration gear for S-0271 travels with the district van and is shared with 5 other sites.
Signal strength at Ochre Holt has been marginal since the mast on the ridge was lowered.
Vegetation around Ochre Holt is cut back twice a year under the standing arrangement.
The logbook kept at Ochre Holt runs to 31 pages and the earlier volumes are held off site.
Ochre Holt has been on the register since the first consolidation and its paperwork has never been reconstructed.
Revision 1 of the return for Ochre Holt was lodged on 2034-11-10 and stands withdrawn.
That revision places S-0271 in tier 4 and gives its load as 206.
The approach to Ochre Holt crosses 31 field boundaries and the wayleave is held by the county.

### S-0272 -- Hollow Channel

Telemetry from S-0272 arrives on the thirteenth relay and is batched nightly rather than streamed.
Signal strength at Hollow Channel has been marginal since the mast on the ridge was lowered.
Maintenance visits to S-0272 are scheduled quarterly and the fourth of those was carried out as planned.
Weather at Hollow Channel closed the approach for 20 days during the period under review and no readings were lost.
Hollow Channel has been on the register since the first consolidation and its paperwork has never been reconstructed.
The load recorded for S-0272 is 428, on a return at tier 1.
That return for Hollow Channel is revision 5, lodged 2034-06-07, and its status is settled.
A housekeeping note against S-0272 asks that the cable run be rewalked before the next dry season.

### S-0273 -- Lichen Thwaite

The site plan for Lichen Thwaite is the twelfth revision and supersedes the sketch held in the district folder.
Tier 6 is where Lichen Thwaite sits on revision 1, whose status is returned.
The load on that revision of S-0273, lodged 2034-03-27, is 527.
Vegetation around Lichen Thwaite is cut back twice a year under the standing arrangement.
The logbook kept at Lichen Thwaite runs to 4 pages and the earlier volumes are held off site.
Maintenance visits to S-0273 are scheduled quarterly and the third of those was carried out as planned.

### S-0274 -- Sable Culvert

The enclosure at Sable Culvert was rebuilt in timber after the old fencing was taken by the river.
Sable Culvert has been on the register since the first consolidation and its paperwork has never been reconstructed.
Status settled: revision 2 for S-0274, lodged 2034-01-26.
Load 974 at tier 4 is what that revision carries for Sable Culvert.
Correspondence shows the tenancy at Sable Culvert was renewed for a further 65 years.
Maintenance visits to S-0274 are scheduled quarterly and the first of those was carried out as planned.
Weather at Sable Culvert closed the approach for 9 days during the period under review and no readings were lost.
Access to Sable Culvert is by the service road from the south; the gate code was reissued after the seventh inspection.
The logbook kept at Sable Culvert runs to 87 pages and the earlier volumes are held off site.

### S-0275 -- Beacon Quay

A spare sensor head is kept at Beacon Quay against the failure that took out the district in the previous cycle.
Correspondence about S-0275 is filed under the district rather than under the site, which has caused confusion before.
Revision 6 of the return for Beacon Quay was lodged on 2034-12-16 and stands settled.
That revision places S-0275 in tier 4 and gives its load as 486.
The site plan for Beacon Quay is the ninth revision and supersedes the sketch held in the district folder.
Maintenance visits to S-0275 are scheduled quarterly and the first of those was carried out as planned.

### S-0276 -- Bronze Narrows

Bronze Narrows has been on the register since the first consolidation and its paperwork has never been reconstructed.
Drainage work near Bronze Narrows was completed without interruption to the record.
The site plan for Bronze Narrows is the sixth revision and supersedes the sketch held in the district folder.
Vegetation around Bronze Narrows is cut back twice a year under the standing arrangement.
The district file for Bronze Narrows shows revision 6 lodged on 2034-08-04.
For S-0276 the status is returned, the tier is 3, and the load is 604.
Bronze Narrows carries a calibration offset of -24 on the current instrument head.
Access to Bronze Narrows is by the service road from the south; the gate code was reissued after the thirteenth inspection.

### S-0277 -- Granite Yard

The site plan for Granite Yard is the ninth revision and supersedes the sketch held in the district folder.
The survey party reached Granite Yard on the tenth of the month and found the access track passable for light vehicles only.
Correspondence shows the tenancy at Granite Yard was renewed for a further 7 years.
The logbook kept at Granite Yard runs to 28 pages and the earlier volumes are held off site.
Granite Yard lodged revision 4 on 2034-12-03.
The return for S-0277 is settled, sits at tier 4, and records a load of 803.
Granite Yard has been on the register since the first consolidation and its paperwork has never been reconstructed.
Drainage work near Granite Yard was completed without interruption to the record.

### S-0278 -- Auburn Rill

Two of the anchors at Auburn Rill were replaced after the frost and the work is recorded in the district ledger.
S-0278 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Revision 3 of the return for Auburn Rill was lodged on 2034-04-12 and stands settled.
That revision places S-0278 in tier 2 and gives its load as 578.
Auburn Rill has been on the register since the first consolidation and its paperwork has never been reconstructed.
Auburn Rill shares its power feed with the neighbouring pumping station and has its own cut-out.
The site plan for Auburn Rill is the fourteenth revision and supersedes the sketch held in the district folder.
The enclosure at Auburn Rill was rebuilt in timber after the old fencing was taken by the river.
Maintenance visits to S-0278 are scheduled quarterly and the fourteenth of those was carried out as planned.
Calibration gear for S-0278 travels with the district van and is shared with 9 other sites.
The approach to Auburn Rill crosses 4 field boundaries and the wayleave is held by the county.

### S-0279 -- Basalt Cairn

The logbook kept at Basalt Cairn runs to 57 pages and the earlier volumes are held off site.
The district file for Basalt Cairn shows revision 3 lodged on 2034-06-20.
For S-0279 the status is returned, the tier is 6, and the load is 157.
S-0279 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Telemetry from S-0279 arrives on the fifth relay and is batched nightly rather than streamed.
The survey party reached Basalt Cairn on the seventh of the month and found the access track passable for light vehicles only.
Two of the anchors at Basalt Cairn were replaced after the frost and the work is recorded in the district ledger.
Vegetation around Basalt Cairn is cut back twice a year under the standing arrangement.
Basalt Cairn has been on the register since the first consolidation and its paperwork has never been reconstructed.

### S-0280 -- Mellow Warren

The reading shelter at Mellow Warren takes water in heavy weather and the floor was relaid.
The notes for S-0280 mention a disused well inside the compound, capped and recorded but not surveyed.
Access to Mellow Warren is by the service road from the south; the gate code was reissued after the fourteenth inspection.
Mellow Warren has been on the register since the first consolidation and its paperwork has never been reconstructed.
The fence line at Mellow Warren was rerun 23 metres to the east to clear the culvert.
On 2034-04-26 the district accepted revision 5 for Mellow Warren and marked it settled.
S-0280 carries tier 1 on that revision and a load of 865.
S-0280 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Maintenance visits to S-0280 are scheduled quarterly and the tenth of those was carried out as planned.

### S-0281 -- Tamarisk Knoll

Tamarisk Knoll has been on the register since the first consolidation and its paperwork has never been reconstructed.
The site plan for Tamarisk Knoll is the seventh revision and supersedes the sketch held in the district folder.
The logbook kept at Tamarisk Knoll runs to 27 pages and the earlier volumes are held off site.
The notes for S-0281 mention a disused well inside the compound, capped and recorded but not surveyed.
The instrument housing at Tamarisk Knoll is the original pattern and its door seal is checked each visit.
Tamarisk Knoll shares its power feed with the neighbouring pumping station and has its own cut-out.
Tier 6 is where Tamarisk Knoll sits on revision 4, whose status is returned.
The load on that revision of S-0281, lodged 2034-11-09, is 763.
Access to Tamarisk Knoll is by the service road from the south; the gate code was reissued after the second inspection.
An earlier clerk recorded Tamarisk Knoll under a shortened spelling, and both forms still appear in the older indexes.
Calibration gear for S-0281 travels with the district van and is shared with 22 other sites.

### S-0282 -- Russet Bluff

A housekeeping note against S-0282 asks that the cable run be rewalked before the next dry season.
Russet Bluff shares its power feed with the neighbouring pumping station and has its own cut-out.
Telemetry from S-0282 arrives on the thirteenth relay and is batched nightly rather than streamed.
The district file for Russet Bluff shows revision 6 lodged on 2034-09-09.
For S-0282 the status is settled, the tier is 2, and the load is 231.
Correspondence shows the tenancy at Russet Bluff was renewed for a further 74 years.
The instrument housing at Russet Bluff is the original pattern and its door seal is checked each visit.
The access key for S-0282 is held at the district office and signed out per visit.
The site plan for Russet Bluff is the first revision and supersedes the sketch held in the district folder.
Drainage work near Russet Bluff was completed without interruption to the record.
A visitor log is kept at Russet Bluff and shows 32 entries for the period.
Correspondence about S-0282 is filed under the district rather than under the site, which has caused confusion before.

### S-0283 -- Pebble Spur

Telemetry from S-0283 arrives on the third relay and is batched nightly rather than streamed.
The fence line at Pebble Spur was rerun 2 metres to the east to clear the culvert.
Signal strength at Pebble Spur has been marginal since the mast on the ridge was lowered.
Tier 9 is where Pebble Spur sits on revision 3, whose status is provisional.
The load on that revision of S-0283, lodged 2034-07-13, is 864.
A spare sensor head is kept at Pebble Spur against the failure that took out the district in the previous cycle.
Vegetation around Pebble Spur is cut back twice a year under the standing arrangement.
Weather at Pebble Spur closed the approach for 32 days during the period under review and no readings were lost.

### S-0284 -- Umber Shoal

The access key for S-0284 is held at the district office and signed out per visit.
Umber Shoal shares its power feed with the neighbouring pumping station and has its own cut-out.
The load recorded for S-0284 is 227, on a return at tier 5.
That return for Umber Shoal is revision 1, lodged 2034-09-08, and its status is provisional.
The approach to Umber Shoal crosses 3 field boundaries and the wayleave is held by the county.
An earlier clerk recorded Umber Shoal under a shortened spelling, and both forms still appear in the older indexes.
Umber Shoal has been on the register since the first consolidation and its paperwork has never been reconstructed.
Drainage work near Umber Shoal was completed without interruption to the record.
Two of the anchors at Umber Shoal were replaced after the frost and the work is recorded in the district ledger.

### S-0285 -- Fallow Slade

The notes for S-0285 mention a disused well inside the compound, capped and recorded but not surveyed.
A spare sensor head is kept at Fallow Slade against the failure that took out the district in the previous cycle.
Access to Fallow Slade is by the service road from the south; the gate code was reissued after the third inspection.
The load recorded for S-0285 is 882, on a return at tier 5.
That return for Fallow Slade is revision 2, lodged 2034-01-12, and its status is provisional.
Calibration gear for S-0285 travels with the district van and is shared with 26 other sites.
Two of the anchors at Fallow Slade were replaced after the frost and the work is recorded in the district ledger.

### S-0286 -- Beacon Gate

Drainage work near Beacon Gate was completed without interruption to the record.
A spare sensor head is kept at Beacon Gate against the failure that took out the district in the previous cycle.
Tier 7 is where Beacon Gate sits on revision 5, whose status is returned.
The load on that revision of S-0286, lodged 2034-11-24, is 806.
The access key for S-0286 is held at the district office and signed out per visit.
Access to Beacon Gate is by the service road from the south; the gate code was reissued after the eighth inspection.
Weather at Beacon Gate closed the approach for 7 days during the period under review and no readings were lost.
The instrument housing at Beacon Gate is the original pattern and its door seal is checked each visit.
The notes for S-0286 mention a disused well inside the compound, capped and recorded but not surveyed.

### S-0287 -- Bramble Landing

The logbook kept at Bramble Landing runs to 17 pages and the earlier volumes are held off site.
Access to Bramble Landing is by the service road from the south; the gate code was reissued after the third inspection.
The approach to Bramble Landing crosses 8 field boundaries and the wayleave is held by the county.
The enclosure at Bramble Landing was rebuilt in timber after the old fencing was taken by the river.
A housekeeping note against S-0287 asks that the cable run be rewalked before the next dry season.
Tier 8 is where Bramble Landing sits on revision 5, whose status is provisional.
The load on that revision of S-0287, lodged 2034-12-24, is 897.
The fence line at Bramble Landing was rerun 20 metres to the east to clear the culvert.
Vegetation around Bramble Landing is cut back twice a year under the standing arrangement.

### S-0288 -- Spindle Cove

The approach to Spindle Cove crosses 12 field boundaries and the wayleave is held by the county.
Access to Spindle Cove is by the service road from the south; the gate code was reissued after the fourth inspection.
The logbook kept at Spindle Cove runs to 58 pages and the earlier volumes are held off site.
The survey party reached Spindle Cove on the ninth of the month and found the access track passable for light vehicles only.
Telemetry from S-0288 arrives on the sixth relay and is batched nightly rather than streamed.
The site plan for Spindle Cove is the fifth revision and supersedes the sketch held in the district folder.
The instrument housing at Spindle Cove is the original pattern and its door seal is checked each visit.
Weather at Spindle Cove closed the approach for 18 days during the period under review and no readings were lost.
Status open: revision 5 for S-0288, lodged 2034-11-28.
Load 293 at tier 7 is what that revision carries for Spindle Cove.
The offset applied to readings from S-0288 is 21 and has not been revised.
The notes for S-0288 mention a disused well inside the compound, capped and recorded but not surveyed.
S-0288 was one of the sites brought forward in the consolidation and its numbering reflects that order.

### S-0289 -- Sable Spur

The approach to Sable Spur crosses 19 field boundaries and the wayleave is held by the county.
Signal strength at Sable Spur has been marginal since the mast on the ridge was lowered.
The enclosure at Sable Spur was rebuilt in timber after the old fencing was taken by the river.
S-0289 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Weather at Sable Spur closed the approach for 18 days during the period under review and no readings were lost.
A housekeeping note against S-0289 asks that the cable run be rewalked before the next dry season.
The district file for Sable Spur shows revision 4 lodged on 2034-07-01.
For S-0289 the status is settled, the tier is 3, and the load is 228.
Maintenance visits to S-0289 are scheduled quarterly and the ninth of those was carried out as planned.

### S-0290 -- Pebble Landing

Drainage work near Pebble Landing was completed without interruption to the record.
Maintenance visits to S-0290 are scheduled quarterly and the ninth of those was carried out as planned.
The approach to Pebble Landing crosses 13 field boundaries and the wayleave is held by the county.
The notes for S-0290 mention a disused well inside the compound, capped and recorded but not surveyed.
Correspondence about S-0290 is filed under the district rather than under the site, which has caused confusion before.
Calibration gear for S-0290 travels with the district van and is shared with 11 other sites.
Revision 2 of the return for Pebble Landing was lodged on 2034-07-20 and stands settled.
That revision places S-0290 in tier 4 and gives its load as 864.
Correspondence shows the tenancy at Pebble Landing was renewed for a further 13 years.
A housekeeping note against S-0290 asks that the cable run be rewalked before the next dry season.
The fence line at Pebble Landing was rerun 39 metres to the east to clear the culvert.

### S-0291 -- Garnet Bourne

The survey party reached Garnet Bourne on the third of the month and found the access track passable for light vehicles only.
Access to Garnet Bourne is by the service road from the south; the gate code was reissued after the eleventh inspection.
The reading shelter at Garnet Bourne takes water in heavy weather and the floor was relaid.
Correspondence about S-0291 is filed under the district rather than under the site, which has caused confusion before.
S-0291 appears at revision 4 with a load of 527.
That revision of Garnet Bourne was lodged 2034-10-04, is open, and places the station in tier 5.
Garnet Bourne carries a calibration offset of 21 on the current instrument head.
Signal strength at Garnet Bourne has been marginal since the mast on the ridge was lowered.
Telemetry from S-0291 arrives on the ninth relay and is batched nightly rather than streamed.

### S-0292 -- Cinder Copse

Weather at Cinder Copse closed the approach for 7 days during the period under review and no readings were lost.
S-0292 appears at revision 5 with a load of 774.
That revision of Cinder Copse was lodged 2034-07-07, is settled, and places the station in tier 3.
Cinder Copse has been on the register since the first consolidation and its paperwork has never been reconstructed.
Calibration gear for S-0292 travels with the district van and is shared with 13 other sites.
Correspondence shows the tenancy at Cinder Copse was renewed for a further 65 years.

### S-0293 -- Flint Glade

The instrument housing at Flint Glade is the original pattern and its door seal is checked each visit.
A visitor log is kept at Flint Glade and shows 24 entries for the period.
Weather at Flint Glade closed the approach for 11 days during the period under review and no readings were lost.
The load recorded for S-0293 is 807, on a return at tier 2.
That return for Flint Glade is revision 1, lodged 2034-01-14, and its status is settled.
A calibration offset of -3 is recorded for S-0293 against the district standard.
Calibration gear for S-0293 travels with the district van and is shared with 5 other sites.
The notes for S-0293 mention a disused well inside the compound, capped and recorded but not surveyed.
Correspondence about S-0293 is filed under the district rather than under the site, which has caused confusion before.
The approach to Flint Glade crosses 26 field boundaries and the wayleave is held by the county.
The site plan for Flint Glade is the eleventh revision and supersedes the sketch held in the district folder.
A housekeeping note against S-0293 asks that the cable run be rewalked before the next dry season.

### S-0294 -- Heather Gate

Maintenance visits to S-0294 are scheduled quarterly and the eighth of those was carried out as planned.
Heather Gate has been on the register since the first consolidation and its paperwork has never been reconstructed.
Heather Gate shares its power feed with the neighbouring pumping station and has its own cut-out.
Status withdrawn: revision 1 for S-0294, lodged 2034-05-03.
Load 497 at tier 2 is what that revision carries for Heather Gate.
An earlier clerk recorded Heather Gate under a shortened spelling, and both forms still appear in the older indexes.
A housekeeping note against S-0294 asks that the cable run be rewalked before the next dry season.
Correspondence about S-0294 is filed under the district rather than under the site, which has caused confusion before.
The enclosure at Heather Gate was rebuilt in timber after the old fencing was taken by the river.

### S-0295 -- Calder Glade

Correspondence about S-0295 is filed under the district rather than under the site, which has caused confusion before.
A visitor log is kept at Calder Glade and shows 41 entries for the period.
Telemetry from S-0295 arrives on the fourteenth relay and is batched nightly rather than streamed.
Signal strength at Calder Glade has been marginal since the mast on the ridge was lowered.
Vegetation around Calder Glade is cut back twice a year under the standing arrangement.
The access key for S-0295 is held at the district office and signed out per visit.
The district file for Calder Glade shows revision 3 lodged on 2034-06-06.
For S-0295 the status is settled, the tier is 2, and the load is 702.
Weather at Calder Glade closed the approach for 27 days during the period under review and no readings were lost.
The fence line at Calder Glade was rerun 27 metres to the east to clear the culvert.
Calder Glade has been on the register since the first consolidation and its paperwork has never been reconstructed.

### S-0296 -- Lichen Mere

The notes for S-0296 mention a disused well inside the compound, capped and recorded but not surveyed.
S-0296 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Correspondence shows the tenancy at Lichen Mere was renewed for a further 59 years.
An earlier clerk recorded Lichen Mere under a shortened spelling, and both forms still appear in the older indexes.
The survey party reached Lichen Mere on the tenth of the month and found the access track passable for light vehicles only.
The site plan for Lichen Mere is the third revision and supersedes the sketch held in the district folder.
The fence line at Lichen Mere was rerun 31 metres to the east to clear the culvert.
Two of the anchors at Lichen Mere were replaced after the frost and the work is recorded in the district ledger.
Telemetry from S-0296 arrives on the thirteenth relay and is batched nightly rather than streamed.
The district file for Lichen Mere shows revision 2 lodged on 2034-04-03.
For S-0296 the status is settled, the tier is 3, and the load is 916.
Vegetation around Lichen Mere is cut back twice a year under the standing arrangement.

### S-0297 -- Quince Landing

Telemetry from S-0297 arrives on the fifth relay and is batched nightly rather than streamed.
An earlier clerk recorded Quince Landing under a shortened spelling, and both forms still appear in the older indexes.
Quince Landing has been on the register since the first consolidation and its paperwork has never been reconstructed.
Maintenance visits to S-0297 are scheduled quarterly and the fifth of those was carried out as planned.
The load recorded for S-0297 is 830, on a return at tier 3.
That return for Quince Landing is revision 2, lodged 2034-08-13, and its status is settled.
Quince Landing carries a calibration offset of 6 on the current instrument head.
S-0297 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The site plan for Quince Landing is the tenth revision and supersedes the sketch held in the district folder.
The logbook kept at Quince Landing runs to 4 pages and the earlier volumes are held off site.
Two of the anchors at Quince Landing were replaced after the frost and the work is recorded in the district ledger.
Signal strength at Quince Landing has been marginal since the mast on the ridge was lowered.
Calibration gear for S-0297 travels with the district van and is shared with 11 other sites.

### S-0298 -- Harrow Narrows

Harrow Narrows has been on the register since the first consolidation and its paperwork has never been reconstructed.
Status settled: revision 3 for S-0298, lodged 2034-05-16.
Load 475 at tier 3 is what that revision carries for Harrow Narrows.
A calibration offset of -29 is recorded for S-0298 against the district standard.
An earlier clerk recorded Harrow Narrows under a shortened spelling, and both forms still appear in the older indexes.
Maintenance visits to S-0298 are scheduled quarterly and the thirteenth of those was carried out as planned.
The site plan for Harrow Narrows is the seventh revision and supersedes the sketch held in the district folder.
The logbook kept at Harrow Narrows runs to 80 pages and the earlier volumes are held off site.
The access key for S-0298 is held at the district office and signed out per visit.

### S-0299 -- Saffron Narrows

Signal strength at Saffron Narrows has been marginal since the mast on the ridge was lowered.
A housekeeping note against S-0299 asks that the cable run be rewalked before the next dry season.
The instrument housing at Saffron Narrows is the original pattern and its door seal is checked each visit.
The notes for S-0299 mention a disused well inside the compound, capped and recorded but not surveyed.
S-0299 appears at revision 2 with a load of 582.
That revision of Saffron Narrows was lodged 2034-06-02, is open, and places the station in tier 2.
A visitor log is kept at Saffron Narrows and shows 74 entries for the period.
S-0299 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Saffron Narrows shares its power feed with the neighbouring pumping station and has its own cut-out.
Saffron Narrows has been on the register since the first consolidation and its paperwork has never been reconstructed.
A spare sensor head is kept at Saffron Narrows against the failure that took out the district in the previous cycle.
An earlier clerk recorded Saffron Narrows under a shortened spelling, and both forms still appear in the older indexes.

### S-0300 -- Indigo Landing

Access to Indigo Landing is by the service road from the south; the gate code was reissued after the ninth inspection.
The approach to Indigo Landing crosses 29 field boundaries and the wayleave is held by the county.
A spare sensor head is kept at Indigo Landing against the failure that took out the district in the previous cycle.
Indigo Landing has been on the register since the first consolidation and its paperwork has never been reconstructed.
Telemetry from S-0300 arrives on the eighth relay and is batched nightly rather than streamed.
Revision 1 of the return for Indigo Landing was lodged on 2034-06-26 and stands returned.
That revision places S-0300 in tier 6 and gives its load as 219.
The offset applied to readings from S-0300 is 7 and has not been revised.
Correspondence about S-0300 is filed under the district rather than under the site, which has caused confusion before.
The reading shelter at Indigo Landing takes water in heavy weather and the floor was relaid.
The instrument housing at Indigo Landing is the original pattern and its door seal is checked each visit.
The fence line at Indigo Landing was rerun 5 metres to the east to clear the culvert.

### S-0301 -- Dusk Bank

Access to Dusk Bank is by the service road from the south; the gate code was reissued after the fifth inspection.
An earlier clerk recorded Dusk Bank under a shortened spelling, and both forms still appear in the older indexes.
The notes for S-0301 mention a disused well inside the compound, capped and recorded but not surveyed.
Revision 5 of the return for Dusk Bank was lodged on 2034-10-02 and stands returned.
That revision places S-0301 in tier 8 and gives its load as 693.
Telemetry from S-0301 arrives on the fourteenth relay and is batched nightly rather than streamed.
Maintenance visits to S-0301 are scheduled quarterly and the thirteenth of those was carried out as planned.

### S-0302 -- Sorrel Cairn

The approach to Sorrel Cairn crosses 15 field boundaries and the wayleave is held by the county.
S-0302 appears at revision 4 with a load of 527.
That revision of Sorrel Cairn was lodged 2034-11-04, is provisional, and places the station in tier 6.
Sorrel Cairn carries a calibration offset of -11 on the current instrument head.
The reading shelter at Sorrel Cairn takes water in heavy weather and the floor was relaid.
The notes for S-0302 mention a disused well inside the compound, capped and recorded but not surveyed.
Telemetry from S-0302 arrives on the fourth relay and is batched nightly rather than streamed.
Sorrel Cairn shares its power feed with the neighbouring pumping station and has its own cut-out.
Access to Sorrel Cairn is by the service road from the south; the gate code was reissued after the twelfth inspection.
A visitor log is kept at Sorrel Cairn and shows 79 entries for the period.

### S-0303 -- Willow Copse

The instrument housing at Willow Copse is the original pattern and its door seal is checked each visit.
The notes for S-0303 mention a disused well inside the compound, capped and recorded but not surveyed.
Correspondence about S-0303 is filed under the district rather than under the site, which has caused confusion before.
The access key for S-0303 is held at the district office and signed out per visit.
Willow Copse has been on the register since the first consolidation and its paperwork has never been reconstructed.
On 2034-07-18 the district accepted revision 5 for Willow Copse and marked it settled.
S-0303 carries tier 7 on that revision and a load of 302.
Willow Copse carries sequence mark 4 in this quarter's reconciliation.
Weather at Willow Copse closed the approach for 11 days during the period under review and no readings were lost.

### S-0304 -- Cinder Landing

Drainage work near Cinder Landing was completed without interruption to the record.
Status returned: revision 5 for S-0304, lodged 2034-09-21.
Load 295 at tier 6 is what that revision carries for Cinder Landing.
A calibration offset of -4 is recorded for S-0304 against the district standard.
An earlier clerk recorded Cinder Landing under a shortened spelling, and both forms still appear in the older indexes.
The approach to Cinder Landing crosses 16 field boundaries and the wayleave is held by the county.
Access to Cinder Landing is by the service road from the south; the gate code was reissued after the third inspection.
A spare sensor head is kept at Cinder Landing against the failure that took out the district in the previous cycle.
The access key for S-0304 is held at the district office and signed out per visit.
Signal strength at Cinder Landing has been marginal since the mast on the ridge was lowered.

### S-0305 -- Vellum Bight

S-0305 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The instrument housing at Vellum Bight is the original pattern and its door seal is checked each visit.
The enclosure at Vellum Bight was rebuilt in timber after the old fencing was taken by the river.
Vellum Bight shares its power feed with the neighbouring pumping station and has its own cut-out.
The site plan for Vellum Bight is the eleventh revision and supersedes the sketch held in the district folder.
Tier 1 is where Vellum Bight sits on revision 6, whose status is settled.
The load on that revision of S-0305, lodged 2034-01-13, is 838.
The survey party reached Vellum Bight on the thirteenth of the month and found the access track passable for light vehicles only.
The access key for S-0305 is held at the district office and signed out per visit.
Vegetation around Vellum Bight is cut back twice a year under the standing arrangement.

### S-0306 -- Spindle Pike

Weather at Spindle Pike closed the approach for 40 days during the period under review and no readings were lost.
Revision 5 of the return for Spindle Pike was lodged on 2034-12-16 and stands settled.
That revision places S-0306 in tier 3 and gives its load as 234.
Correspondence shows the tenancy at Spindle Pike was renewed for a further 71 years.
S-0306 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Signal strength at Spindle Pike has been marginal since the mast on the ridge was lowered.
The approach to Spindle Pike crosses 31 field boundaries and the wayleave is held by the county.
The notes for S-0306 mention a disused well inside the compound, capped and recorded but not surveyed.
A spare sensor head is kept at Spindle Pike against the failure that took out the district in the previous cycle.
Calibration gear for S-0306 travels with the district van and is shared with 18 other sites.

### S-0307 -- Tamarisk Shoal

Access to Tamarisk Shoal is by the service road from the south; the gate code was reissued after the fourth inspection.
Telemetry from S-0307 arrives on the first relay and is batched nightly rather than streamed.
Signal strength at Tamarisk Shoal has been marginal since the mast on the ridge was lowered.
The load recorded for S-0307 is 238, on a return at tier 3.
That return for Tamarisk Shoal is revision 2, lodged 2034-01-07, and its status is settled.
The fence line at Tamarisk Shoal was rerun 28 metres to the east to clear the culvert.
Tamarisk Shoal shares its power feed with the neighbouring pumping station and has its own cut-out.
The survey party reached Tamarisk Shoal on the eleventh of the month and found the access track passable for light vehicles only.
Two of the anchors at Tamarisk Shoal were replaced after the frost and the work is recorded in the district ledger.

### S-0308 -- Marram Moor

An earlier clerk recorded Marram Moor under a shortened spelling, and both forms still appear in the older indexes.
The site plan for Marram Moor is the eighth revision and supersedes the sketch held in the district folder.
Marram Moor lodged revision 5 on 2034-07-01.
The return for S-0308 is settled, sits at tier 9, and records a load of 460.
Two of the anchors at Marram Moor were replaced after the frost and the work is recorded in the district ledger.
A housekeeping note against S-0308 asks that the cable run be rewalked before the next dry season.
Correspondence about S-0308 is filed under the district rather than under the site, which has caused confusion before.

### S-0309 -- Marram Knap

Drainage work near Marram Knap was completed without interruption to the record.
Vegetation around Marram Knap is cut back twice a year under the standing arrangement.
An earlier clerk recorded Marram Knap under a shortened spelling, and both forms still appear in the older indexes.
S-0309 appears at revision 1 with a load of 105.
That revision of Marram Knap was lodged 2034-03-13, is settled, and places the station in tier 3.
The return for Marram Knap replaces an entry formerly held at S-0990, a code retired at the consolidation and never reissued.
The survey party reached Marram Knap on the third of the month and found the access track passable for light vehicles only.
The instrument housing at Marram Knap is the original pattern and its door seal is checked each visit.
Access to Marram Knap is by the service road from the south; the gate code was reissued after the tenth inspection.
The notes for S-0309 mention a disused well inside the compound, capped and recorded but not surveyed.

### S-0310 -- Saffron Shaw

Correspondence about S-0310 is filed under the district rather than under the site, which has caused confusion before.
A spare sensor head is kept at Saffron Shaw against the failure that took out the district in the previous cycle.
On 2034-04-24 the district accepted revision 1 for Saffron Shaw and marked it provisional.
S-0310 carries tier 4 on that revision and a load of 435.
The access key for S-0310 is held at the district office and signed out per visit.
The enclosure at Saffron Shaw was rebuilt in timber after the old fencing was taken by the river.
Two of the anchors at Saffron Shaw were replaced after the frost and the work is recorded in the district ledger.
Weather at Saffron Shaw closed the approach for 8 days during the period under review and no readings were lost.
Maintenance visits to S-0310 are scheduled quarterly and the first of those was carried out as planned.

### S-0311 -- Fallow Hallow

Fallow Hallow shares its power feed with the neighbouring pumping station and has its own cut-out.
S-0311 appears at revision 6 with a load of 290.
That revision of Fallow Hallow was lodged 2034-08-10, is settled, and places the station in tier 4.
Calibration gear for S-0311 travels with the district van and is shared with 35 other sites.
Weather at Fallow Hallow closed the approach for 17 days during the period under review and no readings were lost.
The enclosure at Fallow Hallow was rebuilt in timber after the old fencing was taken by the river.
Drainage work near Fallow Hallow was completed without interruption to the record.
The logbook kept at Fallow Hallow runs to 76 pages and the earlier volumes are held off site.
S-0311 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Telemetry from S-0311 arrives on the eighth relay and is batched nightly rather than streamed.
The fence line at Fallow Hallow was rerun 5 metres to the east to clear the culvert.

### S-0312 -- Tamarisk Staithe

Tamarisk Staithe has been on the register since the first consolidation and its paperwork has never been reconstructed.
Two of the anchors at Tamarisk Staithe were replaced after the frost and the work is recorded in the district ledger.
The access key for S-0312 is held at the district office and signed out per visit.
Revision 5 of the return for Tamarisk Staithe was lodged on 2034-12-13 and stands provisional.
That revision places S-0312 in tier 2 and gives its load as 366.
Correspondence about S-0312 is filed under the district rather than under the site, which has caused confusion before.
The survey party reached Tamarisk Staithe on the second of the month and found the access track passable for light vehicles only.
The logbook kept at Tamarisk Staithe runs to 86 pages and the earlier volumes are held off site.

### S-0313 -- Amber Cairn

The approach to Amber Cairn crosses 21 field boundaries and the wayleave is held by the county.
The fence line at Amber Cairn was rerun 33 metres to the east to clear the culvert.
A spare sensor head is kept at Amber Cairn against the failure that took out the district in the previous cycle.
S-0313 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The district file for Amber Cairn shows revision 4 lodged on 2034-05-10.
For S-0313 the status is settled, the tier is 5, and the load is 932.
Telemetry from S-0313 arrives on the first relay and is batched nightly rather than streamed.
Drainage work near Amber Cairn was completed without interruption to the record.

### S-0314 -- Osier Hollow

Two of the anchors at Osier Hollow were replaced after the frost and the work is recorded in the district ledger.
The logbook kept at Osier Hollow runs to 39 pages and the earlier volumes are held off site.
S-0314 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The access key for S-0314 is held at the district office and signed out per visit.
Status settled: revision 6 for S-0314, lodged 2034-04-16.
Load 143 at tier 2 is what that revision carries for Osier Hollow.
Weather at Osier Hollow closed the approach for 26 days during the period under review and no readings were lost.
A spare sensor head is kept at Osier Hollow against the failure that took out the district in the previous cycle.
A housekeeping note against S-0314 asks that the cable run be rewalked before the next dry season.

### S-0315 -- Jasper Pasture

Signal strength at Jasper Pasture has been marginal since the mast on the ridge was lowered.
Vegetation around Jasper Pasture is cut back twice a year under the standing arrangement.
The survey party reached Jasper Pasture on the sixth of the month and found the access track passable for light vehicles only.
Maintenance visits to S-0315 are scheduled quarterly and the eleventh of those was carried out as planned.
The district file for Jasper Pasture shows revision 3 lodged on 2034-06-22.
For S-0315 the status is withdrawn, the tier is 5, and the load is 376.
The access key for S-0315 is held at the district office and signed out per visit.
The fence line at Jasper Pasture was rerun 22 metres to the east to clear the culvert.

### S-0316 -- Brindle Ferry

Two of the anchors at Brindle Ferry were replaced after the frost and the work is recorded in the district ledger.
A housekeeping note against S-0316 asks that the cable run be rewalked before the next dry season.
Correspondence about S-0316 is filed under the district rather than under the site, which has caused confusion before.
A spare sensor head is kept at Brindle Ferry against the failure that took out the district in the previous cycle.
On 2034-03-10 the district accepted revision 4 for Brindle Ferry and marked it withdrawn.
S-0316 carries tier 6 on that revision and a load of 352.
The instrument housing at Brindle Ferry is the original pattern and its door seal is checked each visit.
The site plan for Brindle Ferry is the tenth revision and supersedes the sketch held in the district folder.
The approach to Brindle Ferry crosses 29 field boundaries and the wayleave is held by the county.

### S-0317 -- Tamarisk Brae

The enclosure at Tamarisk Brae was rebuilt in timber after the old fencing was taken by the river.
Weather at Tamarisk Brae closed the approach for 34 days during the period under review and no readings were lost.
The logbook kept at Tamarisk Brae runs to 48 pages and the earlier volumes are held off site.
The district file for Tamarisk Brae shows revision 4 lodged on 2034-06-03.
For S-0317 the status is provisional, the tier is 5, and the load is 781.
Tamarisk Brae carries a calibration offset of 27 on the current instrument head.
The fence line at Tamarisk Brae was rerun 12 metres to the east to clear the culvert.
An earlier clerk recorded Tamarisk Brae under a shortened spelling, and both forms still appear in the older indexes.
The survey party reached Tamarisk Brae on the sixth of the month and found the access track passable for light vehicles only.
Correspondence shows the tenancy at Tamarisk Brae was renewed for a further 77 years.

### S-0318 -- Midland Brae

The reading shelter at Midland Brae takes water in heavy weather and the floor was relaid.
Weather at Midland Brae closed the approach for 25 days during the period under review and no readings were lost.
The notes for S-0318 mention a disused well inside the compound, capped and recorded but not surveyed.
The enclosure at Midland Brae was rebuilt in timber after the old fencing was taken by the river.
The load recorded for S-0318 is 138, on a return at tier 4.
That return for Midland Brae is revision 5, lodged 2034-10-11, and its status is settled.
A housekeeping note against S-0318 asks that the cable run be rewalked before the next dry season.
Midland Brae shares its power feed with the neighbouring pumping station and has its own cut-out.
A spare sensor head is kept at Midland Brae against the failure that took out the district in the previous cycle.

### S-0319 -- Hollow Furlong

Correspondence about S-0319 is filed under the district rather than under the site, which has caused confusion before.
A visitor log is kept at Hollow Furlong and shows 9 entries for the period.
On 2034-09-16 the district accepted revision 1 for Hollow Furlong and marked it settled.
S-0319 carries tier 2 on that revision and a load of 627.
The survey party reached Hollow Furlong on the first of the month and found the access track passable for light vehicles only.
Calibration gear for S-0319 travels with the district van and is shared with 28 other sites.
Maintenance visits to S-0319 are scheduled quarterly and the first of those was carried out as planned.

### S-0320 -- Dapple Ledge

A spare sensor head is kept at Dapple Ledge against the failure that took out the district in the previous cycle.
The district file for Dapple Ledge shows revision 6 lodged on 2034-08-13.
For S-0320 the status is open, the tier is 9, and the load is 318.
A housekeeping note against S-0320 asks that the cable run be rewalked before the next dry season.
An earlier clerk recorded Dapple Ledge under a shortened spelling, and both forms still appear in the older indexes.
Maintenance visits to S-0320 are scheduled quarterly and the tenth of those was carried out as planned.
Vegetation around Dapple Ledge is cut back twice a year under the standing arrangement.
The access key for S-0320 is held at the district office and signed out per visit.
S-0320 was one of the sites brought forward in the consolidation and its numbering reflects that order.

### S-0321 -- Calder Crossing

The instrument housing at Calder Crossing is the original pattern and its door seal is checked each visit.
A spare sensor head is kept at Calder Crossing against the failure that took out the district in the previous cycle.
Drainage work near Calder Crossing was completed without interruption to the record.
The enclosure at Calder Crossing was rebuilt in timber after the old fencing was taken by the river.
Calder Crossing lodged revision 3 on 2034-05-15.
The return for S-0321 is settled, sits at tier 1, and records a load of 780.
Correspondence shows the tenancy at Calder Crossing was renewed for a further 41 years.
The access key for S-0321 is held at the district office and signed out per visit.
The logbook kept at Calder Crossing runs to 30 pages and the earlier volumes are held off site.
Calder Crossing shares its power feed with the neighbouring pumping station and has its own cut-out.
Maintenance visits to S-0321 are scheduled quarterly and the sixth of those was carried out as planned.

### S-0322 -- Fallow Withy

The instrument housing at Fallow Withy is the original pattern and its door seal is checked each visit.
Access to Fallow Withy is by the service road from the south; the gate code was reissued after the sixth inspection.
The survey party reached Fallow Withy on the eighth of the month and found the access track passable for light vehicles only.
Tier 4 is where Fallow Withy sits on revision 6, whose status is settled.
The load on that revision of S-0322, lodged 2034-05-08, is 739.
A visitor log is kept at Fallow Withy and shows 68 entries for the period.
Fallow Withy shares its power feed with the neighbouring pumping station and has its own cut-out.
The logbook kept at Fallow Withy runs to 26 pages and the earlier volumes are held off site.
The fence line at Fallow Withy was rerun 19 metres to the east to clear the culvert.
A housekeeping note against S-0322 asks that the cable run be rewalked before the next dry season.
The access key for S-0322 is held at the district office and signed out per visit.

### S-0323 -- Willow Cairn

The instrument housing at Willow Cairn is the original pattern and its door seal is checked each visit.
The approach to Willow Cairn crosses 2 field boundaries and the wayleave is held by the county.
A visitor log is kept at Willow Cairn and shows 24 entries for the period.
The survey party reached Willow Cairn on the eleventh of the month and found the access track passable for light vehicles only.
S-0323 appears at revision 4 with a load of 239.
That revision of Willow Cairn was lodged 2034-08-26, is open, and places the station in tier 7.
Weather at Willow Cairn closed the approach for 4 days during the period under review and no readings were lost.
Drainage work near Willow Cairn was completed without interruption to the record.
A spare sensor head is kept at Willow Cairn against the failure that took out the district in the previous cycle.
The enclosure at Willow Cairn was rebuilt in timber after the old fencing was taken by the river.

### S-0324 -- Verdigris Staithe

The site plan for Verdigris Staithe is the eleventh revision and supersedes the sketch held in the district folder.
The instrument housing at Verdigris Staithe is the original pattern and its door seal is checked each visit.
Telemetry from S-0324 arrives on the fifth relay and is batched nightly rather than streamed.
Tier 4 is where Verdigris Staithe sits on revision 1, whose status is settled.
The load on that revision of S-0324, lodged 2034-11-28, is 555.
An earlier clerk recorded Verdigris Staithe under a shortened spelling, and both forms still appear in the older indexes.
The access key for S-0324 is held at the district office and signed out per visit.
A housekeeping note against S-0324 asks that the cable run be rewalked before the next dry season.
Calibration gear for S-0324 travels with the district van and is shared with 8 other sites.
Verdigris Staithe has been on the register since the first consolidation and its paperwork has never been reconstructed.
Two of the anchors at Verdigris Staithe were replaced after the frost and the work is recorded in the district ledger.

### S-0325 -- Amber Staithe

Maintenance visits to S-0325 are scheduled quarterly and the fourth of those was carried out as planned.
Two of the anchors at Amber Staithe were replaced after the frost and the work is recorded in the district ledger.
Tier 1 is where Amber Staithe sits on revision 5, whose status is settled.
The load on that revision of S-0325, lodged 2034-04-12, is 266.
A calibration offset of -7 is recorded for S-0325 against the district standard.
The access key for S-0325 is held at the district office and signed out per visit.
Weather at Amber Staithe closed the approach for 28 days during the period under review and no readings were lost.
The fence line at Amber Staithe was rerun 39 metres to the east to clear the culvert.
The reading shelter at Amber Staithe takes water in heavy weather and the floor was relaid.
Correspondence shows the tenancy at Amber Staithe was renewed for a further 56 years.
The approach to Amber Staithe crosses 24 field boundaries and the wayleave is held by the county.

### S-0326 -- Sorrel Bight

The notes for S-0326 mention a disused well inside the compound, capped and recorded but not surveyed.
Drainage work near Sorrel Bight was completed without interruption to the record.
Vegetation around Sorrel Bight is cut back twice a year under the standing arrangement.
An earlier clerk recorded Sorrel Bight under a shortened spelling, and both forms still appear in the older indexes.
The reading shelter at Sorrel Bight takes water in heavy weather and the floor was relaid.
Correspondence about S-0326 is filed under the district rather than under the site, which has caused confusion before.
Two of the anchors at Sorrel Bight were replaced after the frost and the work is recorded in the district ledger.
The load recorded for S-0326 is 531, on a return at tier 8.
That return for Sorrel Bight is revision 1, lodged 2034-06-19, and its status is open.
Sorrel Bight has been on the register since the first consolidation and its paperwork has never been reconstructed.

### S-0327 -- Umber Terrace

Correspondence shows the tenancy at Umber Terrace was renewed for a further 13 years.
Status settled: revision 1 for S-0327, lodged 2034-01-19.
Load 402 at tier 4 is what that revision carries for Umber Terrace.
An earlier clerk recorded Umber Terrace under a shortened spelling, and both forms still appear in the older indexes.
Correspondence about S-0327 is filed under the district rather than under the site, which has caused confusion before.
Two of the anchors at Umber Terrace were replaced after the frost and the work is recorded in the district ledger.

### S-0328 -- Umber Quay

A housekeeping note against S-0328 asks that the cable run be rewalked before the next dry season.
Umber Quay has been on the register since the first consolidation and its paperwork has never been reconstructed.
A spare sensor head is kept at Umber Quay against the failure that took out the district in the previous cycle.
Drainage work near Umber Quay was completed without interruption to the record.
Signal strength at Umber Quay has been marginal since the mast on the ridge was lowered.
The fence line at Umber Quay was rerun 28 metres to the east to clear the culvert.
The access key for S-0328 is held at the district office and signed out per visit.
Revision 6 of the return for Umber Quay was lodged on 2034-06-14 and stands returned.
That revision places S-0328 in tier 9 and gives its load as 697.
Umber Quay shares its power feed with the neighbouring pumping station and has its own cut-out.
Access to Umber Quay is by the service road from the south; the gate code was reissued after the fourteenth inspection.
Calibration gear for S-0328 travels with the district van and is shared with 27 other sites.

### S-0329 -- Birch Terrace

The enclosure at Birch Terrace was rebuilt in timber after the old fencing was taken by the river.
A spare sensor head is kept at Birch Terrace against the failure that took out the district in the previous cycle.
Access to Birch Terrace is by the service road from the south; the gate code was reissued after the fourth inspection.
The district file for Birch Terrace shows revision 2 lodged on 2034-11-25.
For S-0329 the status is settled, the tier is 4, and the load is 847.
Birch Terrace has been on the register since the first consolidation and its paperwork has never been reconstructed.
Two of the anchors at Birch Terrace were replaced after the frost and the work is recorded in the district ledger.
The approach to Birch Terrace crosses 35 field boundaries and the wayleave is held by the county.
A visitor log is kept at Birch Terrace and shows 71 entries for the period.
The access key for S-0329 is held at the district office and signed out per visit.

### S-0330 -- Harrow Glade

Drainage work near Harrow Glade was completed without interruption to the record.
Correspondence about S-0330 is filed under the district rather than under the site, which has caused confusion before.
Tier 2 is where Harrow Glade sits on revision 3, whose status is returned.
The load on that revision of S-0330, lodged 2034-07-01, is 826.
Calibration gear for S-0330 travels with the district van and is shared with 19 other sites.
The notes for S-0330 mention a disused well inside the compound, capped and recorded but not surveyed.
The access key for S-0330 is held at the district office and signed out per visit.
A housekeeping note against S-0330 asks that the cable run be rewalked before the next dry season.
The approach to Harrow Glade crosses 20 field boundaries and the wayleave is held by the county.
S-0330 was one of the sites brought forward in the consolidation and its numbering reflects that order.

### S-0331 -- Basalt Butte

The reading shelter at Basalt Butte takes water in heavy weather and the floor was relaid.
An earlier clerk recorded Basalt Butte under a shortened spelling, and both forms still appear in the older indexes.
The fence line at Basalt Butte was rerun 33 metres to the east to clear the culvert.
The district file for Basalt Butte shows revision 4 lodged on 2034-02-21.
For S-0331 the status is returned, the tier is 9, and the load is 996.
The access key for S-0331 is held at the district office and signed out per visit.
The notes for S-0331 mention a disused well inside the compound, capped and recorded but not surveyed.
Drainage work near Basalt Butte was completed without interruption to the record.

### S-0332 -- Heather Tarn

The reading shelter at Heather Tarn takes water in heavy weather and the floor was relaid.
The fence line at Heather Tarn was rerun 25 metres to the east to clear the culvert.
A spare sensor head is kept at Heather Tarn against the failure that took out the district in the previous cycle.
Calibration gear for S-0332 travels with the district van and is shared with 16 other sites.
Status settled: revision 3 for S-0332, lodged 2034-02-07.
Load 334 at tier 2 is what that revision carries for Heather Tarn.
Heather Tarn shares its power feed with the neighbouring pumping station and has its own cut-out.
A housekeeping note against S-0332 asks that the cable run be rewalked before the next dry season.
The notes for S-0332 mention a disused well inside the compound, capped and recorded but not surveyed.
A visitor log is kept at Heather Tarn and shows 73 entries for the period.
The instrument housing at Heather Tarn is the original pattern and its door seal is checked each visit.
The logbook kept at Heather Tarn runs to 67 pages and the earlier volumes are held off site.

### S-0333 -- Vellum Coomb

Two of the anchors at Vellum Coomb were replaced after the frost and the work is recorded in the district ledger.
The fence line at Vellum Coomb was rerun 22 metres to the east to clear the culvert.
Vellum Coomb has been on the register since the first consolidation and its paperwork has never been reconstructed.
Telemetry from S-0333 arrives on the tenth relay and is batched nightly rather than streamed.
On 2034-10-21 the district accepted revision 1 for Vellum Coomb and marked it returned.
S-0333 carries tier 3 on that revision and a load of 151.
Drainage work near Vellum Coomb was completed without interruption to the record.
A spare sensor head is kept at Vellum Coomb against the failure that took out the district in the previous cycle.
The logbook kept at Vellum Coomb runs to 43 pages and the earlier volumes are held off site.

### S-0334 -- Beacon Glade

The access key for S-0334 is held at the district office and signed out per visit.
Maintenance visits to S-0334 are scheduled quarterly and the second of those was carried out as planned.
Beacon Glade lodged revision 1 on 2034-09-21.
The return for S-0334 is settled, sits at tier 3, and records a load of 543.
The instrument housing at Beacon Glade is the original pattern and its door seal is checked each visit.
The survey party reached Beacon Glade on the first of the month and found the access track passable for light vehicles only.

### S-0335 -- Harrow Sand

The access key for S-0335 is held at the district office and signed out per visit.
A visitor log is kept at Harrow Sand and shows 43 entries for the period.
Harrow Sand has been on the register since the first consolidation and its paperwork has never been reconstructed.
Calibration gear for S-0335 travels with the district van and is shared with 34 other sites.
On 2034-06-23 the district accepted revision 6 for Harrow Sand and marked it open.
S-0335 carries tier 2 on that revision and a load of 341.
The enclosure at Harrow Sand was rebuilt in timber after the old fencing was taken by the river.
Vegetation around Harrow Sand is cut back twice a year under the standing arrangement.
The reading shelter at Harrow Sand takes water in heavy weather and the floor was relaid.
A housekeeping note against S-0335 asks that the cable run be rewalked before the next dry season.
An earlier clerk recorded Harrow Sand under a shortened spelling, and both forms still appear in the older indexes.
The logbook kept at Harrow Sand runs to 69 pages and the earlier volumes are held off site.

### S-0336 -- Nettle Ripple

Access to Nettle Ripple is by the service road from the south; the gate code was reissued after the eleventh inspection.
Vegetation around Nettle Ripple is cut back twice a year under the standing arrangement.
Drainage work near Nettle Ripple was completed without interruption to the record.
S-0336 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Correspondence about S-0336 is filed under the district rather than under the site, which has caused confusion before.
Nettle Ripple lodged revision 5 on 2034-11-19.
The return for S-0336 is open, sits at tier 4, and records a load of 135.
The enclosure at Nettle Ripple was rebuilt in timber after the old fencing was taken by the river.
An earlier clerk recorded Nettle Ripple under a shortened spelling, and both forms still appear in the older indexes.
A spare sensor head is kept at Nettle Ripple against the failure that took out the district in the previous cycle.
The reading shelter at Nettle Ripple takes water in heavy weather and the floor was relaid.

### S-0337 -- Sable Ripple

Access to Sable Ripple is by the service road from the south; the gate code was reissued after the eleventh inspection.
The notes for S-0337 mention a disused well inside the compound, capped and recorded but not surveyed.
Signal strength at Sable Ripple has been marginal since the mast on the ridge was lowered.
The load recorded for S-0337 is 582, on a return at tier 1.
That return for Sable Ripple is revision 4, lodged 2034-04-23, and its status is settled.
The fence line at Sable Ripple was rerun 17 metres to the east to clear the culvert.
Correspondence shows the tenancy at Sable Ripple was renewed for a further 65 years.
Sable Ripple shares its power feed with the neighbouring pumping station and has its own cut-out.
An earlier clerk recorded Sable Ripple under a shortened spelling, and both forms still appear in the older indexes.
The survey party reached Sable Ripple on the fourteenth of the month and found the access track passable for light vehicles only.

### S-0338 -- Rowan Beck

Maintenance visits to S-0338 are scheduled quarterly and the sixth of those was carried out as planned.
The load recorded for S-0338 is 874, on a return at tier 3.
That return for Rowan Beck is revision 3, lodged 2034-04-12, and its status is settled.
The survey party reached Rowan Beck on the seventh of the month and found the access track passable for light vehicles only.
Correspondence about S-0338 is filed under the district rather than under the site, which has caused confusion before.
Weather at Rowan Beck closed the approach for 10 days during the period under review and no readings were lost.
The enclosure at Rowan Beck was rebuilt in timber after the old fencing was taken by the river.
Correspondence shows the tenancy at Rowan Beck was renewed for a further 7 years.
Rowan Beck has been on the register since the first consolidation and its paperwork has never been reconstructed.
S-0338 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Rowan Beck shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0339 -- Meadow Yard

A housekeeping note against S-0339 asks that the cable run be rewalked before the next dry season.
The approach to Meadow Yard crosses 2 field boundaries and the wayleave is held by the county.
Maintenance visits to S-0339 are scheduled quarterly and the seventh of those was carried out as planned.
The load recorded for S-0339 is 699, on a return at tier 3.
That return for Meadow Yard is revision 4, lodged 2034-11-16, and its status is settled.
The logbook kept at Meadow Yard runs to 13 pages and the earlier volumes are held off site.
Drainage work near Meadow Yard was completed without interruption to the record.
Telemetry from S-0339 arrives on the tenth relay and is batched nightly rather than streamed.
Vegetation around Meadow Yard is cut back twice a year under the standing arrangement.
The notes for S-0339 mention a disused well inside the compound, capped and recorded but not surveyed.
Meadow Yard shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0340 -- Hazel Quay

Maintenance visits to S-0340 are scheduled quarterly and the first of those was carried out as planned.
Weather at Hazel Quay closed the approach for 7 days during the period under review and no readings were lost.
The approach to Hazel Quay crosses 18 field boundaries and the wayleave is held by the county.
On 2034-11-13 the district accepted revision 3 for Hazel Quay and marked it settled.
S-0340 carries tier 3 on that revision and a load of 996.
A visitor log is kept at Hazel Quay and shows 9 entries for the period.
Access to Hazel Quay is by the service road from the south; the gate code was reissued after the twelfth inspection.
A spare sensor head is kept at Hazel Quay against the failure that took out the district in the previous cycle.
The site plan for Hazel Quay is the second revision and supersedes the sketch held in the district folder.

### S-0341 -- Tamarisk Brook

Calibration gear for S-0341 travels with the district van and is shared with 37 other sites.
The district file for Tamarisk Brook shows revision 4 lodged on 2034-12-28.
For S-0341 the status is settled, the tier is 3, and the load is 432.
The reading shelter at Tamarisk Brook takes water in heavy weather and the floor was relaid.
Maintenance visits to S-0341 are scheduled quarterly and the thirteenth of those was carried out as planned.
Telemetry from S-0341 arrives on the eleventh relay and is batched nightly rather than streamed.
The access key for S-0341 is held at the district office and signed out per visit.
Vegetation around Tamarisk Brook is cut back twice a year under the standing arrangement.
The site plan for Tamarisk Brook is the sixth revision and supersedes the sketch held in the district folder.

### S-0342 -- Bramble Terrace

Correspondence shows the tenancy at Bramble Terrace was renewed for a further 60 years.
Bramble Terrace has been on the register since the first consolidation and its paperwork has never been reconstructed.
The enclosure at Bramble Terrace was rebuilt in timber after the old fencing was taken by the river.
Correspondence about S-0342 is filed under the district rather than under the site, which has caused confusion before.
Tier 9 is where Bramble Terrace sits on revision 1, whose status is open.
The load on that revision of S-0342, lodged 2034-04-22, is 986.
A calibration offset of -38 is recorded for S-0342 against the district standard.
The notes for S-0342 mention a disused well inside the compound, capped and recorded but not surveyed.
The reading shelter at Bramble Terrace takes water in heavy weather and the floor was relaid.

### S-0343 -- Marram Copse

The access key for S-0343 is held at the district office and signed out per visit.
Maintenance visits to S-0343 are scheduled quarterly and the eleventh of those was carried out as planned.
Tier 6 is where Marram Copse sits on revision 2, whose status is returned.
The load on that revision of S-0343, lodged 2034-10-16, is 531.
Marram Copse carries a calibration offset of 16 on the current instrument head.
Weather at Marram Copse closed the approach for 35 days during the period under review and no readings were lost.
The fence line at Marram Copse was rerun 6 metres to the east to clear the culvert.
S-0343 was one of the sites brought forward in the consolidation and its numbering reflects that order.

### S-0344 -- Crag Furlong

Telemetry from S-0344 arrives on the tenth relay and is batched nightly rather than streamed.
Crag Furlong has been on the register since the first consolidation and its paperwork has never been reconstructed.
The load recorded for S-0344 is 681, on a return at tier 7.
That return for Crag Furlong is revision 6, lodged 2034-01-07, and its status is returned.
A calibration offset of -3 is recorded for S-0344 against the district standard.
The site plan for Crag Furlong is the tenth revision and supersedes the sketch held in the district folder.
A housekeeping note against S-0344 asks that the cable run be rewalked before the next dry season.
Crag Furlong shares its power feed with the neighbouring pumping station and has its own cut-out.
The survey party reached Crag Furlong on the eleventh of the month and found the access track passable for light vehicles only.

### S-0345 -- Midland Coomb

Drainage work near Midland Coomb was completed without interruption to the record.
Correspondence shows the tenancy at Midland Coomb was renewed for a further 42 years.
The site plan for Midland Coomb is the eleventh revision and supersedes the sketch held in the district folder.
S-0345 appears at revision 4 with a load of 878.
That revision of Midland Coomb was lodged 2034-05-11, is settled, and places the station in tier 2.
A spare sensor head is kept at Midland Coomb against the failure that took out the district in the previous cycle.
Access to Midland Coomb is by the service road from the south; the gate code was reissued after the fourteenth inspection.
The reading shelter at Midland Coomb takes water in heavy weather and the floor was relaid.
The survey party reached Midland Coomb on the sixth of the month and found the access track passable for light vehicles only.
Two of the anchors at Midland Coomb were replaced after the frost and the work is recorded in the district ledger.

### S-0346 -- Pebble Ledge

Pebble Ledge shares its power feed with the neighbouring pumping station and has its own cut-out.
Pebble Ledge has been on the register since the first consolidation and its paperwork has never been reconstructed.
Maintenance visits to S-0346 are scheduled quarterly and the fifth of those was carried out as planned.
The site plan for Pebble Ledge is the sixth revision and supersedes the sketch held in the district folder.
Correspondence about S-0346 is filed under the district rather than under the site, which has caused confusion before.
A visitor log is kept at Pebble Ledge and shows 87 entries for the period.
The district file for Pebble Ledge shows revision 6 lodged on 2034-09-14.
For S-0346 the status is settled, the tier is 3, and the load is 171.
Correspondence shows the tenancy at Pebble Ledge was renewed for a further 20 years.
Calibration gear for S-0346 travels with the district van and is shared with 35 other sites.
A housekeeping note against S-0346 asks that the cable run be rewalked before the next dry season.
The approach to Pebble Ledge crosses 28 field boundaries and the wayleave is held by the county.

### S-0347 -- Cedar Gully

Vegetation around Cedar Gully is cut back twice a year under the standing arrangement.
Drainage work near Cedar Gully was completed without interruption to the record.
A housekeeping note against S-0347 asks that the cable run be rewalked before the next dry season.
A visitor log is kept at Cedar Gully and shows 26 entries for the period.
Cedar Gully lodged revision 2 on 2034-07-08.
The return for S-0347 is open, sits at tier 9, and records a load of 257.
The approach to Cedar Gully crosses 34 field boundaries and the wayleave is held by the county.
The instrument housing at Cedar Gully is the original pattern and its door seal is checked each visit.
The survey party reached Cedar Gully on the thirteenth of the month and found the access track passable for light vehicles only.
S-0347 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Weather at Cedar Gully closed the approach for 38 days during the period under review and no readings were lost.

### S-0348 -- Copper Cove

Vegetation around Copper Cove is cut back twice a year under the standing arrangement.
The survey party reached Copper Cove on the seventh of the month and found the access track passable for light vehicles only.
The district file for Copper Cove shows revision 1 lodged on 2034-01-06.
For S-0348 the status is returned, the tier is 2, and the load is 637.
The offset applied to readings from S-0348 is 26 and has not been revised.
Calibration gear for S-0348 travels with the district van and is shared with 28 other sites.
The instrument housing at Copper Cove is the original pattern and its door seal is checked each visit.
Copper Cove shares its power feed with the neighbouring pumping station and has its own cut-out.
The site plan for Copper Cove is the sixth revision and supersedes the sketch held in the district folder.
The access key for S-0348 is held at the district office and signed out per visit.
The logbook kept at Copper Cove runs to 19 pages and the earlier volumes are held off site.
Maintenance visits to S-0348 are scheduled quarterly and the first of those was carried out as planned.
Telemetry from S-0348 arrives on the eighth relay and is batched nightly rather than streamed.

### S-0349 -- Pewter Mere

Weather at Pewter Mere closed the approach for 14 days during the period under review and no readings were lost.
A housekeeping note against S-0349 asks that the cable run be rewalked before the next dry season.
Correspondence about S-0349 is filed under the district rather than under the site, which has caused confusion before.
Revision 2 of the return for Pewter Mere was lodged on 2034-09-03 and stands settled.
That revision places S-0349 in tier 3 and gives its load as 351.
The notes for S-0349 mention a disused well inside the compound, capped and recorded but not surveyed.
Two of the anchors at Pewter Mere were replaced after the frost and the work is recorded in the district ledger.

### S-0350 -- Russet Culvert

Two of the anchors at Russet Culvert were replaced after the frost and the work is recorded in the district ledger.
S-0350 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Revision 6 of the return for Russet Culvert was lodged on 2034-02-19 and stands withdrawn.
That revision places S-0350 in tier 3 and gives its load as 476.
Russet Culvert has been on the register since the first consolidation and its paperwork has never been reconstructed.
A housekeeping note against S-0350 asks that the cable run be rewalked before the next dry season.
The approach to Russet Culvert crosses 15 field boundaries and the wayleave is held by the county.
The enclosure at Russet Culvert was rebuilt in timber after the old fencing was taken by the river.

### S-0351 -- Verdigris Brook

The reading shelter at Verdigris Brook takes water in heavy weather and the floor was relaid.
Revision 6 of the return for Verdigris Brook was lodged on 2034-03-26 and stands settled.
That revision places S-0351 in tier 4 and gives its load as 654.
A housekeeping note against S-0351 asks that the cable run be rewalked before the next dry season.
An earlier clerk recorded Verdigris Brook under a shortened spelling, and both forms still appear in the older indexes.
A spare sensor head is kept at Verdigris Brook against the failure that took out the district in the previous cycle.
Two of the anchors at Verdigris Brook were replaced after the frost and the work is recorded in the district ledger.
S-0351 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Drainage work near Verdigris Brook was completed without interruption to the record.

### S-0352 -- Shale Ferry

Correspondence about S-0352 is filed under the district rather than under the site, which has caused confusion before.
Calibration gear for S-0352 travels with the district van and is shared with 12 other sites.
The reading shelter at Shale Ferry takes water in heavy weather and the floor was relaid.
S-0352 was one of the sites brought forward in the consolidation and its numbering reflects that order.
An earlier clerk recorded Shale Ferry under a shortened spelling, and both forms still appear in the older indexes.
Shale Ferry has been on the register since the first consolidation and its paperwork has never been reconstructed.
On 2034-02-12 the district accepted revision 2 for Shale Ferry and marked it provisional.
S-0352 carries tier 2 on that revision and a load of 512.
The site plan for Shale Ferry is the fourth revision and supersedes the sketch held in the district folder.

### S-0353 -- Dapple Mill

Vegetation around Dapple Mill is cut back twice a year under the standing arrangement.
The district file for Dapple Mill shows revision 2 lodged on 2034-09-21.
For S-0353 the status is settled, the tier is 4, and the load is 269.
A calibration offset of -28 is recorded for S-0353 against the district standard.
Maintenance visits to S-0353 are scheduled quarterly and the thirteenth of those was carried out as planned.
An earlier clerk recorded Dapple Mill under a shortened spelling, and both forms still appear in the older indexes.
Signal strength at Dapple Mill has been marginal since the mast on the ridge was lowered.

### S-0354 -- Meadow Barrow

Weather at Meadow Barrow closed the approach for 36 days during the period under review and no readings were lost.
Access to Meadow Barrow is by the service road from the south; the gate code was reissued after the eighth inspection.
Signal strength at Meadow Barrow has been marginal since the mast on the ridge was lowered.
Vegetation around Meadow Barrow is cut back twice a year under the standing arrangement.
The approach to Meadow Barrow crosses 4 field boundaries and the wayleave is held by the county.
Meadow Barrow shares its power feed with the neighbouring pumping station and has its own cut-out.
Meadow Barrow lodged revision 2 on 2034-07-18.
The return for S-0354 is settled, sits at tier 2, and records a load of 269.
The survey party reached Meadow Barrow on the sixth of the month and found the access track passable for light vehicles only.
The enclosure at Meadow Barrow was rebuilt in timber after the old fencing was taken by the river.

### S-0355 -- Kestrel Furlong

Two of the anchors at Kestrel Furlong were replaced after the frost and the work is recorded in the district ledger.
An earlier clerk recorded Kestrel Furlong under a shortened spelling, and both forms still appear in the older indexes.
Maintenance visits to S-0355 are scheduled quarterly and the thirteenth of those was carried out as planned.
Kestrel Furlong lodged revision 5 on 2034-07-21.
The return for S-0355 is settled, sits at tier 2, and records a load of 686.
The offset applied to readings from S-0355 is -24 and has not been revised.
S-0355 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Signal strength at Kestrel Furlong has been marginal since the mast on the ridge was lowered.
The approach to Kestrel Furlong crosses 13 field boundaries and the wayleave is held by the county.
A visitor log is kept at Kestrel Furlong and shows 74 entries for the period.

### S-0356 -- Hazel Terrace

Hazel Terrace shares its power feed with the neighbouring pumping station and has its own cut-out.
Telemetry from S-0356 arrives on the twelfth relay and is batched nightly rather than streamed.
A spare sensor head is kept at Hazel Terrace against the failure that took out the district in the previous cycle.
Access to Hazel Terrace is by the service road from the south; the gate code was reissued after the second inspection.
The instrument housing at Hazel Terrace is the original pattern and its door seal is checked each visit.
Revision 2 of the return for Hazel Terrace was lodged on 2034-06-09 and stands settled.
That revision places S-0356 in tier 2 and gives its load as 540.
Weather at Hazel Terrace closed the approach for 9 days during the period under review and no readings were lost.
Drainage work near Hazel Terrace was completed without interruption to the record.
Vegetation around Hazel Terrace is cut back twice a year under the standing arrangement.

### S-0357 -- Indigo Fell

The notes for S-0357 mention a disused well inside the compound, capped and recorded but not surveyed.
Correspondence about S-0357 is filed under the district rather than under the site, which has caused confusion before.
S-0357 appears at revision 3 with a load of 179.
That revision of Indigo Fell was lodged 2034-12-07, is settled, and places the station in tier 4.
A spare sensor head is kept at Indigo Fell against the failure that took out the district in the previous cycle.
The survey party reached Indigo Fell on the fourth of the month and found the access track passable for light vehicles only.
Correspondence shows the tenancy at Indigo Fell was renewed for a further 51 years.
Indigo Fell shares its power feed with the neighbouring pumping station and has its own cut-out.
Signal strength at Indigo Fell has been marginal since the mast on the ridge was lowered.

### S-0358 -- Clover Mere

A spare sensor head is kept at Clover Mere against the failure that took out the district in the previous cycle.
Weather at Clover Mere closed the approach for 15 days during the period under review and no readings were lost.
S-0358 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The notes for S-0358 mention a disused well inside the compound, capped and recorded but not surveyed.
A housekeeping note against S-0358 asks that the cable run be rewalked before the next dry season.
Revision 1 of the return for Clover Mere was lodged on 2034-11-21 and stands settled.
That revision places S-0358 in tier 2 and gives its load as 778.
The reading shelter at Clover Mere takes water in heavy weather and the floor was relaid.
The site plan for Clover Mere is the fourth revision and supersedes the sketch held in the district folder.
Signal strength at Clover Mere has been marginal since the mast on the ridge was lowered.
Correspondence shows the tenancy at Clover Mere was renewed for a further 77 years.
The logbook kept at Clover Mere runs to 53 pages and the earlier volumes are held off site.

### S-0359 -- Pewter Beck

The enclosure at Pewter Beck was rebuilt in timber after the old fencing was taken by the river.
Pewter Beck lodged revision 6 on 2034-02-17.
The return for S-0359 is provisional, sits at tier 4, and records a load of 109.
Drainage work near Pewter Beck was completed without interruption to the record.
An earlier clerk recorded Pewter Beck under a shortened spelling, and both forms still appear in the older indexes.
The access key for S-0359 is held at the district office and signed out per visit.
S-0359 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Correspondence shows the tenancy at Pewter Beck was renewed for a further 39 years.
The survey party reached Pewter Beck on the twelfth of the month and found the access track passable for light vehicles only.

### S-0360 -- Yarrow Gate

The fence line at Yarrow Gate was rerun 18 metres to the east to clear the culvert.
The load recorded for S-0360 is 606, on a return at tier 7.
That return for Yarrow Gate is revision 5, lodged 2034-02-17, and its status is withdrawn.
Calibration gear for S-0360 travels with the district van and is shared with 6 other sites.
Signal strength at Yarrow Gate has been marginal since the mast on the ridge was lowered.
Vegetation around Yarrow Gate is cut back twice a year under the standing arrangement.
Maintenance visits to S-0360 are scheduled quarterly and the eleventh of those was carried out as planned.
Yarrow Gate shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0361 -- Vellum Dingle

Correspondence shows the tenancy at Vellum Dingle was renewed for a further 28 years.
The district file for Vellum Dingle shows revision 2 lodged on 2034-06-19.
For S-0361 the status is settled, the tier is 3, and the load is 564.
Access to Vellum Dingle is by the service road from the south; the gate code was reissued after the twelfth inspection.
Correspondence about S-0361 is filed under the district rather than under the site, which has caused confusion before.
Drainage work near Vellum Dingle was completed without interruption to the record.
A housekeeping note against S-0361 asks that the cable run be rewalked before the next dry season.
Vellum Dingle has been on the register since the first consolidation and its paperwork has never been reconstructed.
The reading shelter at Vellum Dingle takes water in heavy weather and the floor was relaid.
The instrument housing at Vellum Dingle is the original pattern and its door seal is checked each visit.

### S-0362 -- Mellow Vale

Vegetation around Mellow Vale is cut back twice a year under the standing arrangement.
Maintenance visits to S-0362 are scheduled quarterly and the third of those was carried out as planned.
Weather at Mellow Vale closed the approach for 20 days during the period under review and no readings were lost.
Mellow Vale shares its power feed with the neighbouring pumping station and has its own cut-out.
Correspondence shows the tenancy at Mellow Vale was renewed for a further 57 years.
The fence line at Mellow Vale was rerun 21 metres to the east to clear the culvert.
An earlier clerk recorded Mellow Vale under a shortened spelling, and both forms still appear in the older indexes.
The load recorded for S-0362 is 319, on a return at tier 3.
That return for Mellow Vale is revision 6, lodged 2034-06-23, and its status is provisional.
Two of the anchors at Mellow Vale were replaced after the frost and the work is recorded in the district ledger.

### S-0363 -- Birch Gully

The reading shelter at Birch Gully takes water in heavy weather and the floor was relaid.
An earlier clerk recorded Birch Gully under a shortened spelling, and both forms still appear in the older indexes.
The district file for Birch Gully shows revision 2 lodged on 2034-03-06.
For S-0363 the status is settled, the tier is 4, and the load is 930.
Access to Birch Gully is by the service road from the south; the gate code was reissued after the twelfth inspection.
The access key for S-0363 is held at the district office and signed out per visit.
Birch Gully shares its power feed with the neighbouring pumping station and has its own cut-out.
Signal strength at Birch Gully has been marginal since the mast on the ridge was lowered.

### S-0364 -- Sorrel Glade

The survey party reached Sorrel Glade on the sixth of the month and found the access track passable for light vehicles only.
Sorrel Glade shares its power feed with the neighbouring pumping station and has its own cut-out.
The site plan for Sorrel Glade is the second revision and supersedes the sketch held in the district folder.
The reading shelter at Sorrel Glade takes water in heavy weather and the floor was relaid.
Tier 2 is where Sorrel Glade sits on revision 6, whose status is settled.
The load on that revision of S-0364, lodged 2034-04-22, is 568.
The offset applied to readings from S-0364 is 39 and has not been revised.
The access key for S-0364 is held at the district office and signed out per visit.

### S-0365 -- Crag Scarp

Two of the anchors at Crag Scarp were replaced after the frost and the work is recorded in the district ledger.
A housekeeping note against S-0365 asks that the cable run be rewalked before the next dry season.
Vegetation around Crag Scarp is cut back twice a year under the standing arrangement.
The site plan for Crag Scarp is the fourth revision and supersedes the sketch held in the district folder.
Maintenance visits to S-0365 are scheduled quarterly and the third of those was carried out as planned.
Status settled: revision 2 for S-0365, lodged 2034-06-10.
Load 502 at tier 1 is what that revision carries for Crag Scarp.
Crag Scarp carries a calibration offset of -27 on the current instrument head.
Correspondence about S-0365 is filed under the district rather than under the site, which has caused confusion before.

### S-0366 -- Kestrel Staithe

Drainage work near Kestrel Staithe was completed without interruption to the record.
The approach to Kestrel Staithe crosses 15 field boundaries and the wayleave is held by the county.
Status open: revision 1 for S-0366, lodged 2034-08-08.
Load 807 at tier 2 is what that revision carries for Kestrel Staithe.
Access to Kestrel Staithe is by the service road from the south; the gate code was reissued after the second inspection.
A visitor log is kept at Kestrel Staithe and shows 81 entries for the period.

### S-0367 -- Vellum Cove

Weather at Vellum Cove closed the approach for 21 days during the period under review and no readings were lost.
A housekeeping note against S-0367 asks that the cable run be rewalked before the next dry season.
Two of the anchors at Vellum Cove were replaced after the frost and the work is recorded in the district ledger.
The load recorded for S-0367 is 159, on a return at tier 3.
That return for Vellum Cove is revision 2, lodged 2034-03-11, and its status is returned.
Vellum Cove has been on the register since the first consolidation and its paperwork has never been reconstructed.
Vellum Cove shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0368 -- Basalt Ferry

Maintenance visits to S-0368 are scheduled quarterly and the fourteenth of those was carried out as planned.
Revision 4 of the return for Basalt Ferry was lodged on 2034-09-02 and stands settled.
That revision places S-0368 in tier 1 and gives its load as 915.
The instrument housing at Basalt Ferry is the original pattern and its door seal is checked each visit.
Calibration gear for S-0368 travels with the district van and is shared with 28 other sites.
Access to Basalt Ferry is by the service road from the south; the gate code was reissued after the tenth inspection.

### S-0369 -- Gorse Basin

Calibration gear for S-0369 travels with the district van and is shared with 9 other sites.
S-0369 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Correspondence shows the tenancy at Gorse Basin was renewed for a further 66 years.
Tier 9 is where Gorse Basin sits on revision 6, whose status is returned.
The load on that revision of S-0369, lodged 2034-07-11, is 353.
Two of the anchors at Gorse Basin were replaced after the frost and the work is recorded in the district ledger.
The reading shelter at Gorse Basin takes water in heavy weather and the floor was relaid.
Weather at Gorse Basin closed the approach for 38 days during the period under review and no readings were lost.
The survey party reached Gorse Basin on the eleventh of the month and found the access track passable for light vehicles only.
Gorse Basin has been on the register since the first consolidation and its paperwork has never been reconstructed.

### S-0370 -- Saffron Shoal

An earlier clerk recorded Saffron Shoal under a shortened spelling, and both forms still appear in the older indexes.
Signal strength at Saffron Shoal has been marginal since the mast on the ridge was lowered.
Access to Saffron Shoal is by the service road from the south; the gate code was reissued after the twelfth inspection.
The fence line at Saffron Shoal was rerun 22 metres to the east to clear the culvert.
A housekeeping note against S-0370 asks that the cable run be rewalked before the next dry season.
The enclosure at Saffron Shoal was rebuilt in timber after the old fencing was taken by the river.
Tier 9 is where Saffron Shoal sits on revision 6, whose status is provisional.
The load on that revision of S-0370, lodged 2034-03-15, is 705.
Weather at Saffron Shoal closed the approach for 40 days during the period under review and no readings were lost.
The survey party reached Saffron Shoal on the fifth of the month and found the access track passable for light vehicles only.

### S-0371 -- Osier Shaw

The fence line at Osier Shaw was rerun 3 metres to the east to clear the culvert.
Telemetry from S-0371 arrives on the second relay and is batched nightly rather than streamed.
The instrument housing at Osier Shaw is the original pattern and its door seal is checked each visit.
Weather at Osier Shaw closed the approach for 30 days during the period under review and no readings were lost.
Vegetation around Osier Shaw is cut back twice a year under the standing arrangement.
A spare sensor head is kept at Osier Shaw against the failure that took out the district in the previous cycle.
The district file for Osier Shaw shows revision 5 lodged on 2034-01-14.
For S-0371 the status is settled, the tier is 2, and the load is 986.
Osier Shaw carries a calibration offset of 38 on the current instrument head.
A visitor log is kept at Osier Shaw and shows 59 entries for the period.
The survey party reached Osier Shaw on the thirteenth of the month and found the access track passable for light vehicles only.

### S-0372 -- Quince Anchorage

The fence line at Quince Anchorage was rerun 26 metres to the east to clear the culvert.
Revision 5 of the return for Quince Anchorage was lodged on 2034-03-14 and stands returned.
That revision places S-0372 in tier 8 and gives its load as 967.
Drainage work near Quince Anchorage was completed without interruption to the record.
A visitor log is kept at Quince Anchorage and shows 85 entries for the period.
Calibration gear for S-0372 travels with the district van and is shared with 29 other sites.
Correspondence about S-0372 is filed under the district rather than under the site, which has caused confusion before.
The logbook kept at Quince Anchorage runs to 40 pages and the earlier volumes are held off site.
The survey party reached Quince Anchorage on the thirteenth of the month and found the access track passable for light vehicles only.

### S-0373 -- Dapple Thwaite

Two of the anchors at Dapple Thwaite were replaced after the frost and the work is recorded in the district ledger.
The site plan for Dapple Thwaite is the sixth revision and supersedes the sketch held in the district folder.
Revision 6 of the return for Dapple Thwaite was lodged on 2034-09-05 and stands settled.
That revision places S-0373 in tier 1 and gives its load as 560.
The notes for S-0373 mention a disused well inside the compound, capped and recorded but not surveyed.
The approach to Dapple Thwaite crosses 25 field boundaries and the wayleave is held by the county.
Telemetry from S-0373 arrives on the fourteenth relay and is batched nightly rather than streamed.
The fence line at Dapple Thwaite was rerun 14 metres to the east to clear the culvert.
Dapple Thwaite shares its power feed with the neighbouring pumping station and has its own cut-out.
Correspondence shows the tenancy at Dapple Thwaite was renewed for a further 23 years.
The access key for S-0373 is held at the district office and signed out per visit.

### S-0374 -- Birch Basin

Weather at Birch Basin closed the approach for 33 days during the period under review and no readings were lost.
The instrument housing at Birch Basin is the original pattern and its door seal is checked each visit.
Maintenance visits to S-0374 are scheduled quarterly and the fifth of those was carried out as planned.
A housekeeping note against S-0374 asks that the cable run be rewalked before the next dry season.
Birch Basin shares its power feed with the neighbouring pumping station and has its own cut-out.
The notes for S-0374 mention a disused well inside the compound, capped and recorded but not surveyed.
A visitor log is kept at Birch Basin and shows 80 entries for the period.
Birch Basin has been on the register since the first consolidation and its paperwork has never been reconstructed.
The load recorded for S-0374 is 387, on a return at tier 1.
That return for Birch Basin is revision 4, lodged 2034-02-22, and its status is provisional.
A spare sensor head is kept at Birch Basin against the failure that took out the district in the previous cycle.
Drainage work near Birch Basin was completed without interruption to the record.

### S-0375 -- Birch Landing

Calibration gear for S-0375 travels with the district van and is shared with 5 other sites.
S-0375 was one of the sites brought forward in the consolidation and its numbering reflects that order.
A visitor log is kept at Birch Landing and shows 9 entries for the period.
Vegetation around Birch Landing is cut back twice a year under the standing arrangement.
Birch Landing shares its power feed with the neighbouring pumping station and has its own cut-out.
The notes for S-0375 mention a disused well inside the compound, capped and recorded but not surveyed.
The approach to Birch Landing crosses 7 field boundaries and the wayleave is held by the county.
Drainage work near Birch Landing was completed without interruption to the record.
The load recorded for S-0375 is 453, on a return at tier 4.
That return for Birch Landing is revision 4, lodged 2034-04-23, and its status is returned.
The fence line at Birch Landing was rerun 36 metres to the east to clear the culvert.

### S-0376 -- Meadow Bight

An earlier clerk recorded Meadow Bight under a shortened spelling, and both forms still appear in the older indexes.
Vegetation around Meadow Bight is cut back twice a year under the standing arrangement.
Meadow Bight shares its power feed with the neighbouring pumping station and has its own cut-out.
Weather at Meadow Bight closed the approach for 20 days during the period under review and no readings were lost.
The load recorded for S-0376 is 892, on a return at tier 9.
That return for Meadow Bight is revision 4, lodged 2034-07-05, and its status is provisional.
A housekeeping note against S-0376 asks that the cable run be rewalked before the next dry season.

### S-0377 -- Hollow Mere

A spare sensor head is kept at Hollow Mere against the failure that took out the district in the previous cycle.
Two of the anchors at Hollow Mere were replaced after the frost and the work is recorded in the district ledger.
Hollow Mere lodged revision 2 on 2034-07-25.
The return for S-0377 is open, sits at tier 1, and records a load of 994.
A calibration offset of -16 is recorded for S-0377 against the district standard.
Maintenance visits to S-0377 are scheduled quarterly and the eleventh of those was carried out as planned.
The enclosure at Hollow Mere was rebuilt in timber after the old fencing was taken by the river.
The access key for S-0377 is held at the district office and signed out per visit.
The approach to Hollow Mere crosses 40 field boundaries and the wayleave is held by the county.
Telemetry from S-0377 arrives on the third relay and is batched nightly rather than streamed.

### S-0378 -- Amber Coomb

Amber Coomb has been on the register since the first consolidation and its paperwork has never been reconstructed.
The instrument housing at Amber Coomb is the original pattern and its door seal is checked each visit.
The logbook kept at Amber Coomb runs to 59 pages and the earlier volumes are held off site.
The survey party reached Amber Coomb on the eighth of the month and found the access track passable for light vehicles only.
Two of the anchors at Amber Coomb were replaced after the frost and the work is recorded in the district ledger.
Amber Coomb shares its power feed with the neighbouring pumping station and has its own cut-out.
The district file for Amber Coomb shows revision 3 lodged on 2034-08-17.
For S-0378 the status is settled, the tier is 3, and the load is 260.
Access to Amber Coomb is by the service road from the south; the gate code was reissued after the eleventh inspection.

### S-0379 -- Yarrow Ledge

The enclosure at Yarrow Ledge was rebuilt in timber after the old fencing was taken by the river.
S-0379 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The logbook kept at Yarrow Ledge runs to 69 pages and the earlier volumes are held off site.
The approach to Yarrow Ledge crosses 24 field boundaries and the wayleave is held by the county.
An earlier clerk recorded Yarrow Ledge under a shortened spelling, and both forms still appear in the older indexes.
Revision 6 of the return for Yarrow Ledge was lodged on 2034-05-10 and stands withdrawn.
That revision places S-0379 in tier 2 and gives its load as 405.
Maintenance visits to S-0379 are scheduled quarterly and the eighth of those was carried out as planned.
Access to Yarrow Ledge is by the service road from the south; the gate code was reissued after the eighth inspection.
The site plan for Yarrow Ledge is the sixth revision and supersedes the sketch held in the district folder.
Two of the anchors at Yarrow Ledge were replaced after the frost and the work is recorded in the district ledger.
Calibration gear for S-0379 travels with the district van and is shared with 5 other sites.

### S-0380 -- Saffron Ferry

An earlier clerk recorded Saffron Ferry under a shortened spelling, and both forms still appear in the older indexes.
S-0380 appears at revision 4 with a load of 680.
That revision of Saffron Ferry was lodged 2034-04-17, is withdrawn, and places the station in tier 4.
Vegetation around Saffron Ferry is cut back twice a year under the standing arrangement.
Telemetry from S-0380 arrives on the first relay and is batched nightly rather than streamed.
Maintenance visits to S-0380 are scheduled quarterly and the second of those was carried out as planned.
The logbook kept at Saffron Ferry runs to 69 pages and the earlier volumes are held off site.
Two of the anchors at Saffron Ferry were replaced after the frost and the work is recorded in the district ledger.
The survey party reached Saffron Ferry on the seventh of the month and found the access track passable for light vehicles only.
The fence line at Saffron Ferry was rerun 37 metres to the east to clear the culvert.
A housekeeping note against S-0380 asks that the cable run be rewalked before the next dry season.

### S-0381 -- Cedar Down

A housekeeping note against S-0381 asks that the cable run be rewalked before the next dry season.
Cedar Down has been on the register since the first consolidation and its paperwork has never been reconstructed.
Calibration gear for S-0381 travels with the district van and is shared with 7 other sites.
S-0381 appears at revision 3 with a load of 231.
That revision of Cedar Down was lodged 2034-06-15, is open, and places the station in tier 9.
The survey party reached Cedar Down on the fourteenth of the month and found the access track passable for light vehicles only.
An earlier clerk recorded Cedar Down under a shortened spelling, and both forms still appear in the older indexes.

### S-0303 -- Midland Causeway

The enclosure at Midland Causeway was rebuilt in timber after the old fencing was taken by the river.
Correspondence about S-0303 is filed under the district rather than under the site, which has caused confusion before.
The survey party reached Midland Causeway on the thirteenth of the month and found the access track passable for light vehicles only.
The district file for Midland Causeway shows revision 4 lodged on 2034-04-18.
For S-0303 the status is settled, the tier is 6, and the load is 414.
Midland Causeway carries sequence mark 4 in this quarter's reconciliation.
Weather at Midland Causeway closed the approach for 5 days during the period under review and no readings were lost.

### S-0383 -- Pebble Dingle

The fence line at Pebble Dingle was rerun 21 metres to the east to clear the culvert.
The instrument housing at Pebble Dingle is the original pattern and its door seal is checked each visit.
The reading shelter at Pebble Dingle takes water in heavy weather and the floor was relaid.
Pebble Dingle has been on the register since the first consolidation and its paperwork has never been reconstructed.
The approach to Pebble Dingle crosses 40 field boundaries and the wayleave is held by the county.
Drainage work near Pebble Dingle was completed without interruption to the record.
S-0383 appears at revision 4 with a load of 280.
That revision of Pebble Dingle was lodged 2034-09-15, is settled, and places the station in tier 9.
Pebble Dingle carries sequence mark 1 in this quarter's reconciliation.
Access to Pebble Dingle is by the service road from the south; the gate code was reissued after the ninth inspection.
Vegetation around Pebble Dingle is cut back twice a year under the standing arrangement.
Weather at Pebble Dingle closed the approach for 18 days during the period under review and no readings were lost.

### S-0222 -- Birch Reach

The enclosure at Birch Reach was rebuilt in timber after the old fencing was taken by the river.
Correspondence shows the tenancy at Birch Reach was renewed for a further 87 years.
Vegetation around Birch Reach is cut back twice a year under the standing arrangement.
Maintenance visits to S-0222 are scheduled quarterly and the fourteenth of those was carried out as planned.
The reading shelter at Birch Reach takes water in heavy weather and the floor was relaid.
On 2034-08-17 the district accepted revision 5 for Birch Reach and marked it settled.
S-0222 carries tier 5 on that revision and a load of 531.
Drainage work near Birch Reach was completed without interruption to the record.
The survey party reached Birch Reach on the sixth of the month and found the access track passable for light vehicles only.
Two of the anchors at Birch Reach were replaced after the frost and the work is recorded in the district ledger.
The approach to Birch Reach crosses 2 field boundaries and the wayleave is held by the county.
The notes for S-0222 mention a disused well inside the compound, capped and recorded but not surveyed.

### S-0385 -- Flint Tarn

Signal strength at Flint Tarn has been marginal since the mast on the ridge was lowered.
The survey party reached Flint Tarn on the thirteenth of the month and found the access track passable for light vehicles only.
Correspondence shows the tenancy at Flint Tarn was renewed for a further 43 years.
An earlier clerk recorded Flint Tarn under a shortened spelling, and both forms still appear in the older indexes.
Flint Tarn lodged revision 4 on 2034-01-01.
The return for S-0385 is settled, sits at tier 2, and records a load of 996.
Flint Tarn carries a calibration offset of -36 on the current instrument head.
Access to Flint Tarn is by the service road from the south; the gate code was reissued after the fourteenth inspection.
A visitor log is kept at Flint Tarn and shows 86 entries for the period.

### S-0386 -- Nettle Hallow

S-0386 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The reading shelter at Nettle Hallow takes water in heavy weather and the floor was relaid.
An earlier clerk recorded Nettle Hallow under a shortened spelling, and both forms still appear in the older indexes.
The notes for S-0386 mention a disused well inside the compound, capped and recorded but not surveyed.
Correspondence about S-0386 is filed under the district rather than under the site, which has caused confusion before.
The approach to Nettle Hallow crosses 3 field boundaries and the wayleave is held by the county.
The survey party reached Nettle Hallow on the fifth of the month and found the access track passable for light vehicles only.
Revision 4 of the return for Nettle Hallow was lodged on 2034-02-12 and stands returned.
That revision places S-0386 in tier 7 and gives its load as 117.
The fence line at Nettle Hallow was rerun 7 metres to the east to clear the culvert.
The access key for S-0386 is held at the district office and signed out per visit.
Vegetation around Nettle Hallow is cut back twice a year under the standing arrangement.

### S-0387 -- Hollow Barrow

The site plan for Hollow Barrow is the ninth revision and supersedes the sketch held in the district folder.
Correspondence about S-0387 is filed under the district rather than under the site, which has caused confusion before.
The reading shelter at Hollow Barrow takes water in heavy weather and the floor was relaid.
Vegetation around Hollow Barrow is cut back twice a year under the standing arrangement.
S-0387 appears at revision 5 with a load of 490.
That revision of Hollow Barrow was lodged 2034-09-03, is settled, and places the station in tier 5.
Hollow Barrow carries sequence mark 6 in this quarter's reconciliation.
A spare sensor head is kept at Hollow Barrow against the failure that took out the district in the previous cycle.
A visitor log is kept at Hollow Barrow and shows 32 entries for the period.
The notes for S-0387 mention a disused well inside the compound, capped and recorded but not surveyed.
A housekeeping note against S-0387 asks that the cable run be rewalked before the next dry season.
The approach to Hollow Barrow crosses 24 field boundaries and the wayleave is held by the county.

### S-0388 -- Ochre Ford

The enclosure at Ochre Ford was rebuilt in timber after the old fencing was taken by the river.
A housekeeping note against S-0388 asks that the cable run be rewalked before the next dry season.
The survey party reached Ochre Ford on the tenth of the month and found the access track passable for light vehicles only.
Ochre Ford lodged revision 4 on 2034-06-25.
The return for S-0388 is settled, sits at tier 3, and records a load of 819.
Signal strength at Ochre Ford has been marginal since the mast on the ridge was lowered.

### S-0389 -- Gorse Shoal

Vegetation around Gorse Shoal is cut back twice a year under the standing arrangement.
The approach to Gorse Shoal crosses 35 field boundaries and the wayleave is held by the county.
Two of the anchors at Gorse Shoal were replaced after the frost and the work is recorded in the district ledger.
Access to Gorse Shoal is by the service road from the south; the gate code was reissued after the first inspection.
The load recorded for S-0389 is 989, on a return at tier 3.
That return for Gorse Shoal is revision 1, lodged 2034-02-24, and its status is provisional.
A spare sensor head is kept at Gorse Shoal against the failure that took out the district in the previous cycle.
Correspondence about S-0389 is filed under the district rather than under the site, which has caused confusion before.
A housekeeping note against S-0389 asks that the cable run be rewalked before the next dry season.

### S-0390 -- Rowan Tarn

The access key for S-0390 is held at the district office and signed out per visit.
Tier 8 is where Rowan Tarn sits on revision 1, whose status is provisional.
The load on that revision of S-0390, lodged 2034-06-14, is 724.
Signal strength at Rowan Tarn has been marginal since the mast on the ridge was lowered.
The notes for S-0390 mention a disused well inside the compound, capped and recorded but not surveyed.
A visitor log is kept at Rowan Tarn and shows 68 entries for the period.
Two of the anchors at Rowan Tarn were replaced after the frost and the work is recorded in the district ledger.
Correspondence about S-0390 is filed under the district rather than under the site, which has caused confusion before.

### S-0391 -- Pebble Cairn

The logbook kept at Pebble Cairn runs to 30 pages and the earlier volumes are held off site.
Correspondence shows the tenancy at Pebble Cairn was renewed for a further 24 years.
The survey party reached Pebble Cairn on the fourteenth of the month and found the access track passable for light vehicles only.
A spare sensor head is kept at Pebble Cairn against the failure that took out the district in the previous cycle.
Calibration gear for S-0391 travels with the district van and is shared with 6 other sites.
Two of the anchors at Pebble Cairn were replaced after the frost and the work is recorded in the district ledger.
On 2034-10-25 the district accepted revision 1 for Pebble Cairn and marked it open.
S-0391 carries tier 8 on that revision and a load of 809.
Pebble Cairn has been on the register since the first consolidation and its paperwork has never been reconstructed.
Vegetation around Pebble Cairn is cut back twice a year under the standing arrangement.

### S-0392 -- Harrow Vale

Harrow Vale has been on the register since the first consolidation and its paperwork has never been reconstructed.
S-0392 was one of the sites brought forward in the consolidation and its numbering reflects that order.
A spare sensor head is kept at Harrow Vale against the failure that took out the district in the previous cycle.
Maintenance visits to S-0392 are scheduled quarterly and the thirteenth of those was carried out as planned.
Revision 4 of the return for Harrow Vale was lodged on 2034-01-02 and stands settled.
That revision places S-0392 in tier 5 and gives its load as 346.
An earlier clerk recorded Harrow Vale under a shortened spelling, and both forms still appear in the older indexes.
Calibration gear for S-0392 travels with the district van and is shared with 31 other sites.

### S-0393 -- Lichen Gully

Maintenance visits to S-0393 are scheduled quarterly and the twelfth of those was carried out as planned.
The instrument housing at Lichen Gully is the original pattern and its door seal is checked each visit.
The notes for S-0393 mention a disused well inside the compound, capped and recorded but not surveyed.
Signal strength at Lichen Gully has been marginal since the mast on the ridge was lowered.
Lichen Gully lodged revision 3 on 2034-11-02.
The return for S-0393 is withdrawn, sits at tier 6, and records a load of 707.
The offset applied to readings from S-0393 is -15 and has not been revised.
Correspondence about S-0393 is filed under the district rather than under the site, which has caused confusion before.
Correspondence shows the tenancy at Lichen Gully was renewed for a further 68 years.
The access key for S-0393 is held at the district office and signed out per visit.
The logbook kept at Lichen Gully runs to 74 pages and the earlier volumes are held off site.
The approach to Lichen Gully crosses 27 field boundaries and the wayleave is held by the county.
Weather at Lichen Gully closed the approach for 21 days during the period under review and no readings were lost.

### S-0394 -- Thistle Cleave

Weather at Thistle Cleave closed the approach for 34 days during the period under review and no readings were lost.
Correspondence shows the tenancy at Thistle Cleave was renewed for a further 17 years.
The district file for Thistle Cleave shows revision 5 lodged on 2034-04-18.
For S-0394 the status is settled, the tier is 2, and the load is 563.
A visitor log is kept at Thistle Cleave and shows 82 entries for the period.
Signal strength at Thistle Cleave has been marginal since the mast on the ridge was lowered.
The site plan for Thistle Cleave is the fifth revision and supersedes the sketch held in the district folder.

### S-0395 -- Auburn Pasture

Maintenance visits to S-0395 are scheduled quarterly and the eleventh of those was carried out as planned.
The access key for S-0395 is held at the district office and signed out per visit.
The approach to Auburn Pasture crosses 10 field boundaries and the wayleave is held by the county.
The survey party reached Auburn Pasture on the eleventh of the month and found the access track passable for light vehicles only.
Correspondence shows the tenancy at Auburn Pasture was renewed for a further 25 years.
The load recorded for S-0395 is 870, on a return at tier 6.
That return for Auburn Pasture is revision 2, lodged 2034-01-22, and its status is provisional.
A visitor log is kept at Auburn Pasture and shows 29 entries for the period.
Weather at Auburn Pasture closed the approach for 7 days during the period under review and no readings were lost.

### S-0396 -- Birch Bluff

The access key for S-0396 is held at the district office and signed out per visit.
Drainage work near Birch Bluff was completed without interruption to the record.
Correspondence shows the tenancy at Birch Bluff was renewed for a further 85 years.
S-0396 appears at revision 3 with a load of 183.
That revision of Birch Bluff was lodged 2034-09-02, is settled, and places the station in tier 1.
Signal strength at Birch Bluff has been marginal since the mast on the ridge was lowered.

### S-0397 -- Bronze Dingle

Correspondence shows the tenancy at Bronze Dingle was renewed for a further 56 years.
Drainage work near Bronze Dingle was completed without interruption to the record.
Bronze Dingle lodged revision 5 on 2034-12-04.
The return for S-0397 is settled, sits at tier 3, and records a load of 307.
Two of the anchors at Bronze Dingle were replaced after the frost and the work is recorded in the district ledger.
Signal strength at Bronze Dingle has been marginal since the mast on the ridge was lowered.
A spare sensor head is kept at Bronze Dingle against the failure that took out the district in the previous cycle.
A visitor log is kept at Bronze Dingle and shows 88 entries for the period.
Maintenance visits to S-0397 are scheduled quarterly and the fourth of those was carried out as planned.
S-0397 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The enclosure at Bronze Dingle was rebuilt in timber after the old fencing was taken by the river.
A housekeeping note against S-0397 asks that the cable run be rewalked before the next dry season.

### S-0398 -- Calder Brook

S-0398 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Tier 1 is where Calder Brook sits on revision 6, whose status is withdrawn.
The load on that revision of S-0398, lodged 2034-09-07, is 773.
The site plan for Calder Brook is the ninth revision and supersedes the sketch held in the district folder.
A spare sensor head is kept at Calder Brook against the failure that took out the district in the previous cycle.
Drainage work near Calder Brook was completed without interruption to the record.
The access key for S-0398 is held at the district office and signed out per visit.

### S-0399 -- Midland Headland

S-0399 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The site plan for Midland Headland is the third revision and supersedes the sketch held in the district folder.
Telemetry from S-0399 arrives on the eleventh relay and is batched nightly rather than streamed.
Access to Midland Headland is by the service road from the south; the gate code was reissued after the seventh inspection.
Vegetation around Midland Headland is cut back twice a year under the standing arrangement.
Midland Headland has been on the register since the first consolidation and its paperwork has never been reconstructed.
Signal strength at Midland Headland has been marginal since the mast on the ridge was lowered.
Calibration gear for S-0399 travels with the district van and is shared with 12 other sites.
On 2034-11-03 the district accepted revision 2 for Midland Headland and marked it settled.
S-0399 carries tier 2 on that revision and a load of 547.
Weather at Midland Headland closed the approach for 18 days during the period under review and no readings were lost.
The survey party reached Midland Headland on the ninth of the month and found the access track passable for light vehicles only.

### S-0400 -- Pebble Tarn

Maintenance visits to S-0400 are scheduled quarterly and the thirteenth of those was carried out as planned.
A housekeeping note against S-0400 asks that the cable run be rewalked before the next dry season.
Weather at Pebble Tarn closed the approach for 2 days during the period under review and no readings were lost.
A spare sensor head is kept at Pebble Tarn against the failure that took out the district in the previous cycle.
The site plan for Pebble Tarn is the eleventh revision and supersedes the sketch held in the district folder.
Signal strength at Pebble Tarn has been marginal since the mast on the ridge was lowered.
An earlier clerk recorded Pebble Tarn under a shortened spelling, and both forms still appear in the older indexes.
On 2034-04-04 the district accepted revision 5 for Pebble Tarn and marked it settled.
S-0400 carries tier 1 on that revision and a load of 231.
A calibration offset of -9 is recorded for S-0400 against the district standard.
The logbook kept at Pebble Tarn runs to 35 pages and the earlier volumes are held off site.

### S-0401 -- Yarrow Ripple

A housekeeping note against S-0401 asks that the cable run be rewalked before the next dry season.
Signal strength at Yarrow Ripple has been marginal since the mast on the ridge was lowered.
Drainage work near Yarrow Ripple was completed without interruption to the record.
The load recorded for S-0401 is 711, on a return at tier 4.
That return for Yarrow Ripple is revision 1, lodged 2034-09-13, and its status is settled.
Maintenance visits to S-0401 are scheduled quarterly and the eighth of those was carried out as planned.
The fence line at Yarrow Ripple was rerun 10 metres to the east to clear the culvert.
Telemetry from S-0401 arrives on the eighth relay and is batched nightly rather than streamed.
Correspondence about S-0401 is filed under the district rather than under the site, which has caused confusion before.

### S-0402 -- Fallow Wharf

Fallow Wharf shares its power feed with the neighbouring pumping station and has its own cut-out.
Drainage work near Fallow Wharf was completed without interruption to the record.
The load recorded for S-0402 is 261, on a return at tier 2.
That return for Fallow Wharf is revision 1, lodged 2034-01-09, and its status is settled.
The notes for S-0402 mention a disused well inside the compound, capped and recorded but not surveyed.
Vegetation around Fallow Wharf is cut back twice a year under the standing arrangement.
The fence line at Fallow Wharf was rerun 35 metres to the east to clear the culvert.
Signal strength at Fallow Wharf has been marginal since the mast on the ridge was lowered.
A visitor log is kept at Fallow Wharf and shows 71 entries for the period.

### S-0403 -- Indigo Pike

Drainage work near Indigo Pike was completed without interruption to the record.
Correspondence shows the tenancy at Indigo Pike was renewed for a further 12 years.
Indigo Pike shares its power feed with the neighbouring pumping station and has its own cut-out.
Status returned: revision 3 for S-0403, lodged 2034-02-02.
Load 342 at tier 7 is what that revision carries for Indigo Pike.
Indigo Pike has been on the register since the first consolidation and its paperwork has never been reconstructed.
The approach to Indigo Pike crosses 37 field boundaries and the wayleave is held by the county.
The enclosure at Indigo Pike was rebuilt in timber after the old fencing was taken by the river.

### S-0404 -- Brindle Brae

Maintenance visits to S-0404 are scheduled quarterly and the eighth of those was carried out as planned.
The logbook kept at Brindle Brae runs to 45 pages and the earlier volumes are held off site.
Calibration gear for S-0404 travels with the district van and is shared with 24 other sites.
Tier 3 is where Brindle Brae sits on revision 3, whose status is settled.
The load on that revision of S-0404, lodged 2034-08-08, is 724.
A calibration offset of -8 is recorded for S-0404 against the district standard.
The instrument housing at Brindle Brae is the original pattern and its door seal is checked each visit.

### S-0405 -- Gorse Wharf

Calibration gear for S-0405 travels with the district van and is shared with 36 other sites.
Telemetry from S-0405 arrives on the first relay and is batched nightly rather than streamed.
A housekeeping note against S-0405 asks that the cable run be rewalked before the next dry season.
Gorse Wharf lodged revision 3 on 2034-10-15.
The return for S-0405 is settled, sits at tier 4, and records a load of 866.
Correspondence about S-0405 is filed under the district rather than under the site, which has caused confusion before.

### S-0406 -- Mellow Culvert

Telemetry from S-0406 arrives on the tenth relay and is batched nightly rather than streamed.
The site plan for Mellow Culvert is the ninth revision and supersedes the sketch held in the district folder.
Mellow Culvert lodged revision 4 on 2034-10-13.
The return for S-0406 is settled, sits at tier 1, and records a load of 541.
A calibration offset of 16 is recorded for S-0406 against the district standard.
Weather at Mellow Culvert closed the approach for 7 days during the period under review and no readings were lost.
A visitor log is kept at Mellow Culvert and shows 76 entries for the period.

### S-0407 -- Russet Mere

Drainage work near Russet Mere was completed without interruption to the record.
Telemetry from S-0407 arrives on the eleventh relay and is batched nightly rather than streamed.
Revision 5 of the return for Russet Mere was lodged on 2034-04-01 and stands settled.
That revision places S-0407 in tier 2 and gives its load as 443.
The offset applied to readings from S-0407 is -11 and has not been revised.
Signal strength at Russet Mere has been marginal since the mast on the ridge was lowered.
Weather at Russet Mere closed the approach for 28 days during the period under review and no readings were lost.
Maintenance visits to S-0407 are scheduled quarterly and the twelfth of those was carried out as planned.

### S-0408 -- Hazel Copse

The site plan for Hazel Copse is the ninth revision and supersedes the sketch held in the district folder.
The enclosure at Hazel Copse was rebuilt in timber after the old fencing was taken by the river.
On 2034-12-14 the district accepted revision 6 for Hazel Copse and marked it settled.
S-0408 carries tier 1 on that revision and a load of 388.
A visitor log is kept at Hazel Copse and shows 27 entries for the period.
Vegetation around Hazel Copse is cut back twice a year under the standing arrangement.
Signal strength at Hazel Copse has been marginal since the mast on the ridge was lowered.
Hazel Copse has been on the register since the first consolidation and its paperwork has never been reconstructed.
Correspondence about S-0408 is filed under the district rather than under the site, which has caused confusion before.
A spare sensor head is kept at Hazel Copse against the failure that took out the district in the previous cycle.

### S-0409 -- Umber Haven

The reading shelter at Umber Haven takes water in heavy weather and the floor was relaid.
The site plan for Umber Haven is the thirteenth revision and supersedes the sketch held in the district folder.
The district file for Umber Haven shows revision 5 lodged on 2034-03-18.
For S-0409 the status is settled, the tier is 3, and the load is 345.
The logbook kept at Umber Haven runs to 9 pages and the earlier volumes are held off site.
The access key for S-0409 is held at the district office and signed out per visit.

### S-0410 -- Saffron Culvert

Access to Saffron Culvert is by the service road from the south; the gate code was reissued after the sixth inspection.
The approach to Saffron Culvert crosses 14 field boundaries and the wayleave is held by the county.
The reading shelter at Saffron Culvert takes water in heavy weather and the floor was relaid.
Correspondence about S-0410 is filed under the district rather than under the site, which has caused confusion before.
Telemetry from S-0410 arrives on the eighth relay and is batched nightly rather than streamed.
On 2034-09-18 the district accepted revision 1 for Saffron Culvert and marked it provisional.
S-0410 carries tier 6 on that revision and a load of 338.
The logbook kept at Saffron Culvert runs to 48 pages and the earlier volumes are held off site.

### S-0411 -- Dusk Dale

Weather at Dusk Dale closed the approach for 8 days during the period under review and no readings were lost.
Correspondence shows the tenancy at Dusk Dale was renewed for a further 45 years.
Calibration gear for S-0411 travels with the district van and is shared with 16 other sites.
Maintenance visits to S-0411 are scheduled quarterly and the fourth of those was carried out as planned.
Tier 4 is where Dusk Dale sits on revision 6, whose status is settled.
The load on that revision of S-0411, lodged 2034-09-15, is 797.
S-0411 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Dusk Dale shares its power feed with the neighbouring pumping station and has its own cut-out.
Access to Dusk Dale is by the service road from the south; the gate code was reissued after the sixth inspection.
The instrument housing at Dusk Dale is the original pattern and its door seal is checked each visit.

### S-0412 -- Bramble Fell

The notes for S-0412 mention a disused well inside the compound, capped and recorded but not surveyed.
Signal strength at Bramble Fell has been marginal since the mast on the ridge was lowered.
The load recorded for S-0412 is 140, on a return at tier 1.
That return for Bramble Fell is revision 4, lodged 2034-07-25, and its status is withdrawn.
Weather at Bramble Fell closed the approach for 10 days during the period under review and no readings were lost.
The fence line at Bramble Fell was rerun 34 metres to the east to clear the culvert.
Bramble Fell has been on the register since the first consolidation and its paperwork has never been reconstructed.
Correspondence shows the tenancy at Bramble Fell was renewed for a further 54 years.
Access to Bramble Fell is by the service road from the south; the gate code was reissued after the thirteenth inspection.
Correspondence about S-0412 is filed under the district rather than under the site, which has caused confusion before.
A visitor log is kept at Bramble Fell and shows 74 entries for the period.
Two of the anchors at Bramble Fell were replaced after the frost and the work is recorded in the district ledger.

### S-0413 -- Yarrow Delve

The logbook kept at Yarrow Delve runs to 25 pages and the earlier volumes are held off site.
Yarrow Delve has been on the register since the first consolidation and its paperwork has never been reconstructed.
Maintenance visits to S-0413 are scheduled quarterly and the third of those was carried out as planned.
Two of the anchors at Yarrow Delve were replaced after the frost and the work is recorded in the district ledger.
Tier 6 is where Yarrow Delve sits on revision 2, whose status is open.
The load on that revision of S-0413, lodged 2034-04-12, is 259.
An earlier clerk recorded Yarrow Delve under a shortened spelling, and both forms still appear in the older indexes.
Signal strength at Yarrow Delve has been marginal since the mast on the ridge was lowered.

### S-0414 -- Meadow Copse

Meadow Copse has been on the register since the first consolidation and its paperwork has never been reconstructed.
Meadow Copse lodged revision 2 on 2034-02-20.
The return for S-0414 is settled, sits at tier 4, and records a load of 539.
Weather at Meadow Copse closed the approach for 33 days during the period under review and no readings were lost.
The notes for S-0414 mention a disused well inside the compound, capped and recorded but not surveyed.
Two of the anchors at Meadow Copse were replaced after the frost and the work is recorded in the district ledger.

### S-0415 -- Verdigris Cleave

The reading shelter at Verdigris Cleave takes water in heavy weather and the floor was relaid.
The notes for S-0415 mention a disused well inside the compound, capped and recorded but not surveyed.
Revision 5 of the return for Verdigris Cleave was lodged on 2034-07-14 and stands settled.
That revision places S-0415 in tier 1 and gives its load as 181.
Vegetation around Verdigris Cleave is cut back twice a year under the standing arrangement.
S-0415 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Correspondence about S-0415 is filed under the district rather than under the site, which has caused confusion before.
The approach to Verdigris Cleave crosses 12 field boundaries and the wayleave is held by the county.

### S-0416 -- Quince Ledge

S-0416 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The survey party reached Quince Ledge on the sixth of the month and found the access track passable for light vehicles only.
A spare sensor head is kept at Quince Ledge against the failure that took out the district in the previous cycle.
Two of the anchors at Quince Ledge were replaced after the frost and the work is recorded in the district ledger.
The logbook kept at Quince Ledge runs to 40 pages and the earlier volumes are held off site.
Drainage work near Quince Ledge was completed without interruption to the record.
Telemetry from S-0416 arrives on the first relay and is batched nightly rather than streamed.
The load recorded for S-0416 is 672, on a return at tier 1.
That return for Quince Ledge is revision 5, lodged 2034-06-07, and its status is settled.
A calibration offset of -31 is recorded for S-0416 against the district standard.
Weather at Quince Ledge closed the approach for 24 days during the period under review and no readings were lost.
Access to Quince Ledge is by the service road from the south; the gate code was reissued after the twelfth inspection.
The instrument housing at Quince Ledge is the original pattern and its door seal is checked each visit.

### S-0417 -- Teasel Shoal

Access to Teasel Shoal is by the service road from the south; the gate code was reissued after the seventh inspection.
Correspondence about S-0417 is filed under the district rather than under the site, which has caused confusion before.
Correspondence shows the tenancy at Teasel Shoal was renewed for a further 45 years.
Teasel Shoal has been on the register since the first consolidation and its paperwork has never been reconstructed.
The fence line at Teasel Shoal was rerun 11 metres to the east to clear the culvert.
On 2034-01-24 the district accepted revision 3 for Teasel Shoal and marked it returned.
S-0417 carries tier 8 on that revision and a load of 938.
The enclosure at Teasel Shoal was rebuilt in timber after the old fencing was taken by the river.

### S-0418 -- Pebble Ripple

The notes for S-0418 mention a disused well inside the compound, capped and recorded but not surveyed.
Calibration gear for S-0418 travels with the district van and is shared with 4 other sites.
The fence line at Pebble Ripple was rerun 26 metres to the east to clear the culvert.
S-0418 was one of the sites brought forward in the consolidation and its numbering reflects that order.
A visitor log is kept at Pebble Ripple and shows 13 entries for the period.
Correspondence shows the tenancy at Pebble Ripple was renewed for a further 66 years.
The reading shelter at Pebble Ripple takes water in heavy weather and the floor was relaid.
S-0418 appears at revision 3 with a load of 746.
That revision of Pebble Ripple was lodged 2034-11-28, is settled, and places the station in tier 2.
Two of the anchors at Pebble Ripple were replaced after the frost and the work is recorded in the district ledger.

### S-0419 -- Indigo Bluff

The survey party reached Indigo Bluff on the eighth of the month and found the access track passable for light vehicles only.
The enclosure at Indigo Bluff was rebuilt in timber after the old fencing was taken by the river.
The fence line at Indigo Bluff was rerun 2 metres to the east to clear the culvert.
Weather at Indigo Bluff closed the approach for 17 days during the period under review and no readings were lost.
The instrument housing at Indigo Bluff is the original pattern and its door seal is checked each visit.
S-0419 appears at revision 5 with a load of 438.
That revision of Indigo Bluff was lodged 2034-09-13, is settled, and places the station in tier 1.
Maintenance visits to S-0419 are scheduled quarterly and the first of those was carried out as planned.
A visitor log is kept at Indigo Bluff and shows 76 entries for the period.
Indigo Bluff has been on the register since the first consolidation and its paperwork has never been reconstructed.

### S-0420 -- Vellum Crossing

The site plan for Vellum Crossing is the tenth revision and supersedes the sketch held in the district folder.
The approach to Vellum Crossing crosses 34 field boundaries and the wayleave is held by the county.
The instrument housing at Vellum Crossing is the original pattern and its door seal is checked each visit.
Tier 9 is where Vellum Crossing sits on revision 2, whose status is returned.
The load on that revision of S-0420, lodged 2034-11-12, is 630.
Vegetation around Vellum Crossing is cut back twice a year under the standing arrangement.
Signal strength at Vellum Crossing has been marginal since the mast on the ridge was lowered.

### S-0421 -- Rowan Mere

The instrument housing at Rowan Mere is the original pattern and its door seal is checked each visit.
On 2034-06-18 the district accepted revision 2 for Rowan Mere and marked it withdrawn.
S-0421 carries tier 9 on that revision and a load of 680.
Correspondence about S-0421 is filed under the district rather than under the site, which has caused confusion before.
The enclosure at Rowan Mere was rebuilt in timber after the old fencing was taken by the river.
Rowan Mere has been on the register since the first consolidation and its paperwork has never been reconstructed.

### S-0422 -- Tamarisk Narrows

Correspondence shows the tenancy at Tamarisk Narrows was renewed for a further 30 years.
Tier 2 is where Tamarisk Narrows sits on revision 1, whose status is provisional.
The load on that revision of S-0422, lodged 2034-03-19, is 699.
A housekeeping note against S-0422 asks that the cable run be rewalked before the next dry season.
The notes for S-0422 mention a disused well inside the compound, capped and recorded but not surveyed.
An earlier clerk recorded Tamarisk Narrows under a shortened spelling, and both forms still appear in the older indexes.
Correspondence about S-0422 is filed under the district rather than under the site, which has caused confusion before.
Weather at Tamarisk Narrows closed the approach for 13 days during the period under review and no readings were lost.
Signal strength at Tamarisk Narrows has been marginal since the mast on the ridge was lowered.
The access key for S-0422 is held at the district office and signed out per visit.
Tamarisk Narrows shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0423 -- Flint Knoll

The enclosure at Flint Knoll was rebuilt in timber after the old fencing was taken by the river.
Correspondence about S-0423 is filed under the district rather than under the site, which has caused confusion before.
On 2034-03-13 the district accepted revision 1 for Flint Knoll and marked it settled.
S-0423 carries tier 2 on that revision and a load of 716.
Two of the anchors at Flint Knoll were replaced after the frost and the work is recorded in the district ledger.
Telemetry from S-0423 arrives on the ninth relay and is batched nightly rather than streamed.
The notes for S-0423 mention a disused well inside the compound, capped and recorded but not surveyed.
A visitor log is kept at Flint Knoll and shows 79 entries for the period.
A housekeeping note against S-0423 asks that the cable run be rewalked before the next dry season.

### S-0424 -- Granite Narrows

A visitor log is kept at Granite Narrows and shows 17 entries for the period.
Two of the anchors at Granite Narrows were replaced after the frost and the work is recorded in the district ledger.
The site plan for Granite Narrows is the sixth revision and supersedes the sketch held in the district folder.
A spare sensor head is kept at Granite Narrows against the failure that took out the district in the previous cycle.
Tier 3 is where Granite Narrows sits on revision 2, whose status is settled.
The load on that revision of S-0424, lodged 2034-09-13, is 435.
Telemetry from S-0424 arrives on the fourteenth relay and is batched nightly rather than streamed.
S-0424 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Access to Granite Narrows is by the service road from the south; the gate code was reissued after the fourth inspection.

### S-0425 -- Shale Spur

Weather at Shale Spur closed the approach for 27 days during the period under review and no readings were lost.
On 2034-07-22 the district accepted revision 1 for Shale Spur and marked it open.
S-0425 carries tier 8 on that revision and a load of 422.
The offset applied to readings from S-0425 is 16 and has not been revised.
Correspondence shows the tenancy at Shale Spur was renewed for a further 43 years.
Correspondence about S-0425 is filed under the district rather than under the site, which has caused confusion before.
Signal strength at Shale Spur has been marginal since the mast on the ridge was lowered.
The reading shelter at Shale Spur takes water in heavy weather and the floor was relaid.
An earlier clerk recorded Shale Spur under a shortened spelling, and both forms still appear in the older indexes.
Vegetation around Shale Spur is cut back twice a year under the standing arrangement.

### S-0426 -- Lichen Staithe

An earlier clerk recorded Lichen Staithe under a shortened spelling, and both forms still appear in the older indexes.
Weather at Lichen Staithe closed the approach for 4 days during the period under review and no readings were lost.
Drainage work near Lichen Staithe was completed without interruption to the record.
Correspondence shows the tenancy at Lichen Staithe was renewed for a further 36 years.
The instrument housing at Lichen Staithe is the original pattern and its door seal is checked each visit.
The enclosure at Lichen Staithe was rebuilt in timber after the old fencing was taken by the river.
Tier 1 is where Lichen Staithe sits on revision 6, whose status is returned.
The load on that revision of S-0426, lodged 2034-08-07, is 787.
The site plan for Lichen Staithe is the seventh revision and supersedes the sketch held in the district folder.

### S-0427 -- Bronze Furlong

The access key for S-0427 is held at the district office and signed out per visit.
Status open: revision 2 for S-0427, lodged 2034-12-06.
Load 736 at tier 9 is what that revision carries for Bronze Furlong.
The reading shelter at Bronze Furlong takes water in heavy weather and the floor was relaid.
The enclosure at Bronze Furlong was rebuilt in timber after the old fencing was taken by the river.
The approach to Bronze Furlong crosses 36 field boundaries and the wayleave is held by the county.
S-0427 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Telemetry from S-0427 arrives on the fifth relay and is batched nightly rather than streamed.
Drainage work near Bronze Furlong was completed without interruption to the record.
The survey party reached Bronze Furlong on the third of the month and found the access track passable for light vehicles only.
Bronze Furlong shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0428 -- Ochre Bluff

Drainage work near Ochre Bluff was completed without interruption to the record.
Signal strength at Ochre Bluff has been marginal since the mast on the ridge was lowered.
Tier 4 is where Ochre Bluff sits on revision 4, whose status is settled.
The load on that revision of S-0428, lodged 2034-09-28, is 928.
The enclosure at Ochre Bluff was rebuilt in timber after the old fencing was taken by the river.
An earlier clerk recorded Ochre Bluff under a shortened spelling, and both forms still appear in the older indexes.

### S-0429 -- Umber Thwaite

The instrument housing at Umber Thwaite is the original pattern and its door seal is checked each visit.
The approach to Umber Thwaite crosses 21 field boundaries and the wayleave is held by the county.
Status settled: revision 3 for S-0429, lodged 2034-12-17.
Load 945 at tier 3 is what that revision carries for Umber Thwaite.
Umber Thwaite carries a calibration offset of -23 on the current instrument head.
Correspondence shows the tenancy at Umber Thwaite was renewed for a further 17 years.
Drainage work near Umber Thwaite was completed without interruption to the record.
Calibration gear for S-0429 travels with the district van and is shared with 7 other sites.
Signal strength at Umber Thwaite has been marginal since the mast on the ridge was lowered.

### S-0430 -- Nettle Ferry

Drainage work near Nettle Ferry was completed without interruption to the record.
The survey party reached Nettle Ferry on the ninth of the month and found the access track passable for light vehicles only.
Signal strength at Nettle Ferry has been marginal since the mast on the ridge was lowered.
Tier 2 is where Nettle Ferry sits on revision 6, whose status is settled.
The load on that revision of S-0430, lodged 2034-08-08, is 547.
The enclosure at Nettle Ferry was rebuilt in timber after the old fencing was taken by the river.

### S-0431 -- Nettle Basin

The instrument housing at Nettle Basin is the original pattern and its door seal is checked each visit.
The approach to Nettle Basin crosses 21 field boundaries and the wayleave is held by the county.
Nettle Basin has been on the register since the first consolidation and its paperwork has never been reconstructed.
The reading shelter at Nettle Basin takes water in heavy weather and the floor was relaid.
A visitor log is kept at Nettle Basin and shows 31 entries for the period.
Access to Nettle Basin is by the service road from the south; the gate code was reissued after the fourteenth inspection.
The load recorded for S-0431 is 991, on a return at tier 6.
That return for Nettle Basin is revision 4, lodged 2034-08-18, and its status is withdrawn.
The access key for S-0431 is held at the district office and signed out per visit.

### S-0432 -- Kestrel Copse

The survey party reached Kestrel Copse on the thirteenth of the month and found the access track passable for light vehicles only.
S-0432 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Kestrel Copse has been on the register since the first consolidation and its paperwork has never been reconstructed.
S-0432 appears at revision 2 with a load of 167.
That revision of Kestrel Copse was lodged 2034-06-19, is settled, and places the station in tier 3.
An earlier clerk recorded Kestrel Copse under a shortened spelling, and both forms still appear in the older indexes.
The site plan for Kestrel Copse is the fourteenth revision and supersedes the sketch held in the district folder.
Correspondence shows the tenancy at Kestrel Copse was renewed for a further 70 years.
The approach to Kestrel Copse crosses 40 field boundaries and the wayleave is held by the county.

### S-0433 -- Verdigris Yard

A visitor log is kept at Verdigris Yard and shows 53 entries for the period.
The enclosure at Verdigris Yard was rebuilt in timber after the old fencing was taken by the river.
Verdigris Yard has been on the register since the first consolidation and its paperwork has never been reconstructed.
Correspondence shows the tenancy at Verdigris Yard was renewed for a further 5 years.
The district file for Verdigris Yard shows revision 1 lodged on 2034-07-18.
For S-0433 the status is settled, the tier is 4, and the load is 803.
The offset applied to readings from S-0433 is 6 and has not been revised.
Calibration gear for S-0433 travels with the district van and is shared with 11 other sites.

### S-0434 -- Quarry Ripple

Signal strength at Quarry Ripple has been marginal since the mast on the ridge was lowered.
Calibration gear for S-0434 travels with the district van and is shared with 29 other sites.
On 2034-05-18 the district accepted revision 6 for Quarry Ripple and marked it settled.
S-0434 carries tier 4 on that revision and a load of 590.
Correspondence about S-0434 is filed under the district rather than under the site, which has caused confusion before.
A visitor log is kept at Quarry Ripple and shows 7 entries for the period.
The approach to Quarry Ripple crosses 36 field boundaries and the wayleave is held by the county.

### S-0435 -- Gorse Tarn

Correspondence shows the tenancy at Gorse Tarn was renewed for a further 87 years.
Signal strength at Gorse Tarn has been marginal since the mast on the ridge was lowered.
A spare sensor head is kept at Gorse Tarn against the failure that took out the district in the previous cycle.
The district file for Gorse Tarn shows revision 1 lodged on 2034-08-17.
For S-0435 the status is settled, the tier is 4, and the load is 783.
Access to Gorse Tarn is by the service road from the south; the gate code was reissued after the eleventh inspection.
Telemetry from S-0435 arrives on the fourth relay and is batched nightly rather than streamed.

### S-0436 -- Crag Ferry

Correspondence about S-0436 is filed under the district rather than under the site, which has caused confusion before.
The access key for S-0436 is held at the district office and signed out per visit.
The fence line at Crag Ferry was rerun 7 metres to the east to clear the culvert.
A housekeeping note against S-0436 asks that the cable run be rewalked before the next dry season.
A spare sensor head is kept at Crag Ferry against the failure that took out the district in the previous cycle.
The logbook kept at Crag Ferry runs to 86 pages and the earlier volumes are held off site.
S-0436 appears at revision 3 with a load of 223.
That revision of Crag Ferry was lodged 2034-08-25, is settled, and places the station in tier 1.
Crag Ferry has been on the register since the first consolidation and its paperwork has never been reconstructed.

### S-0437 -- Basalt Beck

Calibration gear for S-0437 travels with the district van and is shared with 33 other sites.
Weather at Basalt Beck closed the approach for 16 days during the period under review and no readings were lost.
Two of the anchors at Basalt Beck were replaced after the frost and the work is recorded in the district ledger.
The enclosure at Basalt Beck was rebuilt in timber after the old fencing was taken by the river.
Revision 1 of the return for Basalt Beck was lodged on 2034-11-22 and stands returned.
That revision places S-0437 in tier 9 and gives its load as 621.
The offset applied to readings from S-0437 is -12 and has not been revised.
Correspondence about S-0437 is filed under the district rather than under the site, which has caused confusion before.

### S-0438 -- Pewter Delve

Two of the anchors at Pewter Delve were replaced after the frost and the work is recorded in the district ledger.
The instrument housing at Pewter Delve is the original pattern and its door seal is checked each visit.
A spare sensor head is kept at Pewter Delve against the failure that took out the district in the previous cycle.
The site plan for Pewter Delve is the eighth revision and supersedes the sketch held in the district folder.
S-0438 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The load recorded for S-0438 is 796, on a return at tier 1.
That return for Pewter Delve is revision 6, lodged 2034-06-16, and its status is returned.
The reading shelter at Pewter Delve takes water in heavy weather and the floor was relaid.
Calibration gear for S-0438 travels with the district van and is shared with 13 other sites.

### S-0439 -- Nettle Quay

Correspondence shows the tenancy at Nettle Quay was renewed for a further 14 years.
The access key for S-0439 is held at the district office and signed out per visit.
The reading shelter at Nettle Quay takes water in heavy weather and the floor was relaid.
Nettle Quay lodged revision 6 on 2034-08-12.
The return for S-0439 is withdrawn, sits at tier 8, and records a load of 148.
Signal strength at Nettle Quay has been marginal since the mast on the ridge was lowered.
Access to Nettle Quay is by the service road from the south; the gate code was reissued after the eighth inspection.
The fence line at Nettle Quay was rerun 3 metres to the east to clear the culvert.
The logbook kept at Nettle Quay runs to 29 pages and the earlier volumes are held off site.
Calibration gear for S-0439 travels with the district van and is shared with 34 other sites.
A spare sensor head is kept at Nettle Quay against the failure that took out the district in the previous cycle.

### S-0440 -- Marram Sand

The site plan for Marram Sand is the fifth revision and supersedes the sketch held in the district folder.
The reading shelter at Marram Sand takes water in heavy weather and the floor was relaid.
Access to Marram Sand is by the service road from the south; the gate code was reissued after the first inspection.
Two of the anchors at Marram Sand were replaced after the frost and the work is recorded in the district ledger.
The load recorded for S-0440 is 203, on a return at tier 2.
That return for Marram Sand is revision 3, lodged 2034-08-14, and its status is settled.
Correspondence about S-0440 is filed under the district rather than under the site, which has caused confusion before.
Correspondence shows the tenancy at Marram Sand was renewed for a further 80 years.
The survey party reached Marram Sand on the second of the month and found the access track passable for light vehicles only.
A housekeeping note against S-0440 asks that the cable run be rewalked before the next dry season.
A spare sensor head is kept at Marram Sand against the failure that took out the district in the previous cycle.
Telemetry from S-0440 arrives on the seventh relay and is batched nightly rather than streamed.

### S-0441 -- Flint Shaw

Weather at Flint Shaw closed the approach for 15 days during the period under review and no readings were lost.
The instrument housing at Flint Shaw is the original pattern and its door seal is checked each visit.
Status returned: revision 6 for S-0441, lodged 2034-01-12.
Load 261 at tier 9 is what that revision carries for Flint Shaw.
Drainage work near Flint Shaw was completed without interruption to the record.
The reading shelter at Flint Shaw takes water in heavy weather and the floor was relaid.
An earlier clerk recorded Flint Shaw under a shortened spelling, and both forms still appear in the older indexes.

### S-0442 -- Pebble Down

The enclosure at Pebble Down was rebuilt in timber after the old fencing was taken by the river.
The load recorded for S-0442 is 112, on a return at tier 1.
That return for Pebble Down is revision 4, lodged 2034-11-08, and its status is settled.
The offset applied to readings from S-0442 is -14 and has not been revised.
S-0442 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Signal strength at Pebble Down has been marginal since the mast on the ridge was lowered.
A visitor log is kept at Pebble Down and shows 49 entries for the period.
Pebble Down has been on the register since the first consolidation and its paperwork has never been reconstructed.
The survey party reached Pebble Down on the second of the month and found the access track passable for light vehicles only.
The access key for S-0442 is held at the district office and signed out per visit.
A housekeeping note against S-0442 asks that the cable run be rewalked before the next dry season.

### S-0443 -- Vellum Sand

The survey party reached Vellum Sand on the second of the month and found the access track passable for light vehicles only.
Correspondence shows the tenancy at Vellum Sand was renewed for a further 39 years.
The fence line at Vellum Sand was rerun 39 metres to the east to clear the culvert.
Tier 6 is where Vellum Sand sits on revision 3, whose status is returned.
The load on that revision of S-0443, lodged 2034-06-22, is 437.
A housekeeping note against S-0443 asks that the cable run be rewalked before the next dry season.

### S-0444 -- Fallow Tarn

Fallow Tarn shares its power feed with the neighbouring pumping station and has its own cut-out.
The access key for S-0444 is held at the district office and signed out per visit.
Correspondence about S-0444 is filed under the district rather than under the site, which has caused confusion before.
Telemetry from S-0444 arrives on the thirteenth relay and is batched nightly rather than streamed.
Weather at Fallow Tarn closed the approach for 27 days during the period under review and no readings were lost.
The load recorded for S-0444 is 368, on a return at tier 4.
That return for Fallow Tarn is revision 1, lodged 2034-02-01, and its status is settled.
The logbook kept at Fallow Tarn runs to 8 pages and the earlier volumes are held off site.
Fallow Tarn has been on the register since the first consolidation and its paperwork has never been reconstructed.

### S-0445 -- Russet Combe

Weather at Russet Combe closed the approach for 34 days during the period under review and no readings were lost.
An earlier clerk recorded Russet Combe under a shortened spelling, and both forms still appear in the older indexes.
The site plan for Russet Combe is the second revision and supersedes the sketch held in the district folder.
Correspondence shows the tenancy at Russet Combe was renewed for a further 63 years.
The district file for Russet Combe shows revision 6 lodged on 2034-12-13.
For S-0445 the status is provisional, the tier is 7, and the load is 312.
Two of the anchors at Russet Combe were replaced after the frost and the work is recorded in the district ledger.
Russet Combe has been on the register since the first consolidation and its paperwork has never been reconstructed.
Calibration gear for S-0445 travels with the district van and is shared with 24 other sites.
The approach to Russet Combe crosses 34 field boundaries and the wayleave is held by the county.
The survey party reached Russet Combe on the sixth of the month and found the access track passable for light vehicles only.

### S-0446 -- Dapple Shaw

Dapple Shaw has been on the register since the first consolidation and its paperwork has never been reconstructed.
An earlier clerk recorded Dapple Shaw under a shortened spelling, and both forms still appear in the older indexes.
S-0446 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Correspondence about S-0446 is filed under the district rather than under the site, which has caused confusion before.
On 2034-09-02 the district accepted revision 4 for Dapple Shaw and marked it provisional.
S-0446 carries tier 4 on that revision and a load of 364.
Vegetation around Dapple Shaw is cut back twice a year under the standing arrangement.
The fence line at Dapple Shaw was rerun 5 metres to the east to clear the culvert.

### S-0447 -- Osier Anchorage

Correspondence about S-0447 is filed under the district rather than under the site, which has caused confusion before.
Correspondence shows the tenancy at Osier Anchorage was renewed for a further 80 years.
An earlier clerk recorded Osier Anchorage under a shortened spelling, and both forms still appear in the older indexes.
Vegetation around Osier Anchorage is cut back twice a year under the standing arrangement.
S-0447 appears at revision 1 with a load of 706.
That revision of Osier Anchorage was lodged 2034-10-11, is settled, and places the station in tier 2.
A housekeeping note against S-0447 asks that the cable run be rewalked before the next dry season.
The logbook kept at Osier Anchorage runs to 33 pages and the earlier volumes are held off site.
The enclosure at Osier Anchorage was rebuilt in timber after the old fencing was taken by the river.
The instrument housing at Osier Anchorage is the original pattern and its door seal is checked each visit.

### S-0448 -- Bronze Mere

Bronze Mere shares its power feed with the neighbouring pumping station and has its own cut-out.
Revision 4 of the return for Bronze Mere was lodged on 2034-12-06 and stands settled.
That revision places S-0448 in tier 3 and gives its load as 734.
The enclosure at Bronze Mere was rebuilt in timber after the old fencing was taken by the river.
A housekeeping note against S-0448 asks that the cable run be rewalked before the next dry season.
Bronze Mere has been on the register since the first consolidation and its paperwork has never been reconstructed.
The notes for S-0448 mention a disused well inside the compound, capped and recorded but not surveyed.
Telemetry from S-0448 arrives on the fourteenth relay and is batched nightly rather than streamed.
Correspondence shows the tenancy at Bronze Mere was renewed for a further 47 years.
The logbook kept at Bronze Mere runs to 20 pages and the earlier volumes are held off site.

### S-0449 -- Chalk Bluff

S-0449 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Tier 3 is where Chalk Bluff sits on revision 2, whose status is settled.
The load on that revision of S-0449, lodged 2034-03-25, is 128.
An earlier clerk recorded Chalk Bluff under a shortened spelling, and both forms still appear in the older indexes.
A spare sensor head is kept at Chalk Bluff against the failure that took out the district in the previous cycle.
The instrument housing at Chalk Bluff is the original pattern and its door seal is checked each visit.
Chalk Bluff shares its power feed with the neighbouring pumping station and has its own cut-out.
Signal strength at Chalk Bluff has been marginal since the mast on the ridge was lowered.

### S-0450 -- Rowan Hallow

Two of the anchors at Rowan Hallow were replaced after the frost and the work is recorded in the district ledger.
Drainage work near Rowan Hallow was completed without interruption to the record.
Calibration gear for S-0450 travels with the district van and is shared with 27 other sites.
The fence line at Rowan Hallow was rerun 39 metres to the east to clear the culvert.
Tier 2 is where Rowan Hallow sits on revision 3, whose status is returned.
The load on that revision of S-0450, lodged 2034-01-18, is 288.
S-0450 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Maintenance visits to S-0450 are scheduled quarterly and the thirteenth of those was carried out as planned.

### S-0451 -- Copper Bank

Weather at Copper Bank closed the approach for 20 days during the period under review and no readings were lost.
The logbook kept at Copper Bank runs to 78 pages and the earlier volumes are held off site.
Tier 7 is where Copper Bank sits on revision 4, whose status is open.
The load on that revision of S-0451, lodged 2034-05-22, is 433.
A calibration offset of 10 is recorded for S-0451 against the district standard.
Copper Bank has been on the register since the first consolidation and its paperwork has never been reconstructed.
The notes for S-0451 mention a disused well inside the compound, capped and recorded but not surveyed.
A housekeeping note against S-0451 asks that the cable run be rewalked before the next dry season.
Two of the anchors at Copper Bank were replaced after the frost and the work is recorded in the district ledger.
Telemetry from S-0451 arrives on the fourth relay and is batched nightly rather than streamed.
Correspondence shows the tenancy at Copper Bank was renewed for a further 60 years.
The survey party reached Copper Bank on the second of the month and found the access track passable for light vehicles only.

### S-0452 -- Cedar Shoal

The site plan for Cedar Shoal is the fourth revision and supersedes the sketch held in the district folder.
Calibration gear for S-0452 travels with the district van and is shared with 19 other sites.
The enclosure at Cedar Shoal was rebuilt in timber after the old fencing was taken by the river.
The reading shelter at Cedar Shoal takes water in heavy weather and the floor was relaid.
S-0452 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Two of the anchors at Cedar Shoal were replaced after the frost and the work is recorded in the district ledger.
On 2034-04-24 the district accepted revision 1 for Cedar Shoal and marked it settled.
S-0452 carries tier 2 on that revision and a load of 651.
The approach to Cedar Shoal crosses 37 field boundaries and the wayleave is held by the county.
The survey party reached Cedar Shoal on the fourteenth of the month and found the access track passable for light vehicles only.

### S-0453 -- Lichen Beck

The reading shelter at Lichen Beck takes water in heavy weather and the floor was relaid.
The enclosure at Lichen Beck was rebuilt in timber after the old fencing was taken by the river.
A spare sensor head is kept at Lichen Beck against the failure that took out the district in the previous cycle.
S-0453 appears at revision 2 with a load of 374.
That revision of Lichen Beck was lodged 2034-03-06, is settled, and places the station in tier 2.
Two of the anchors at Lichen Beck were replaced after the frost and the work is recorded in the district ledger.
Lichen Beck shares its power feed with the neighbouring pumping station and has its own cut-out.
Access to Lichen Beck is by the service road from the south; the gate code was reissued after the fourth inspection.

### S-0454 -- Beacon Copse

Beacon Copse shares its power feed with the neighbouring pumping station and has its own cut-out.
The instrument housing at Beacon Copse is the original pattern and its door seal is checked each visit.
Vegetation around Beacon Copse is cut back twice a year under the standing arrangement.
Access to Beacon Copse is by the service road from the south; the gate code was reissued after the thirteenth inspection.
S-0454 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The logbook kept at Beacon Copse runs to 11 pages and the earlier volumes are held off site.
Revision 2 of the return for Beacon Copse was lodged on 2034-10-28 and stands withdrawn.
That revision places S-0454 in tier 5 and gives its load as 327.
The offset applied to readings from S-0454 is 2 and has not been revised.
Signal strength at Beacon Copse has been marginal since the mast on the ridge was lowered.
The enclosure at Beacon Copse was rebuilt in timber after the old fencing was taken by the river.
A visitor log is kept at Beacon Copse and shows 38 entries for the period.

### S-0455 -- Ochre Ledge

The instrument housing at Ochre Ledge is the original pattern and its door seal is checked each visit.
Status settled: revision 2 for S-0455, lodged 2034-06-19.
Load 935 at tier 4 is what that revision carries for Ochre Ledge.
Correspondence about S-0455 is filed under the district rather than under the site, which has caused confusion before.
A housekeeping note against S-0455 asks that the cable run be rewalked before the next dry season.
Correspondence shows the tenancy at Ochre Ledge was renewed for a further 88 years.
The approach to Ochre Ledge crosses 6 field boundaries and the wayleave is held by the county.
An earlier clerk recorded Ochre Ledge under a shortened spelling, and both forms still appear in the older indexes.

### S-0456 -- Gorse Bank

The instrument housing at Gorse Bank is the original pattern and its door seal is checked each visit.
S-0456 appears at revision 5 with a load of 755.
That revision of Gorse Bank was lodged 2034-08-09, is provisional, and places the station in tier 9.
Correspondence shows the tenancy at Gorse Bank was renewed for a further 89 years.
The approach to Gorse Bank crosses 7 field boundaries and the wayleave is held by the county.
The notes for S-0456 mention a disused well inside the compound, capped and recorded but not surveyed.

### S-0457 -- Pewter Pike

Drainage work near Pewter Pike was completed without interruption to the record.
The access key for S-0457 is held at the district office and signed out per visit.
Maintenance visits to S-0457 are scheduled quarterly and the third of those was carried out as planned.
On 2034-12-09 the district accepted revision 3 for Pewter Pike and marked it settled.
S-0457 carries tier 4 on that revision and a load of 695.
The notes for S-0457 mention a disused well inside the compound, capped and recorded but not surveyed.
Weather at Pewter Pike closed the approach for 22 days during the period under review and no readings were lost.

### S-0458 -- Nettle Narrows

An earlier clerk recorded Nettle Narrows under a shortened spelling, and both forms still appear in the older indexes.
The logbook kept at Nettle Narrows runs to 12 pages and the earlier volumes are held off site.
S-0458 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Vegetation around Nettle Narrows is cut back twice a year under the standing arrangement.
Telemetry from S-0458 arrives on the twelfth relay and is batched nightly rather than streamed.
Calibration gear for S-0458 travels with the district van and is shared with 33 other sites.
Tier 4 is where Nettle Narrows sits on revision 5, whose status is settled.
The load on that revision of S-0458, lodged 2034-07-26, is 851.
Two of the anchors at Nettle Narrows were replaced after the frost and the work is recorded in the district ledger.

### S-0459 -- Flint Pike

Telemetry from S-0459 arrives on the ninth relay and is batched nightly rather than streamed.
The reading shelter at Flint Pike takes water in heavy weather and the floor was relaid.
Correspondence about S-0459 is filed under the district rather than under the site, which has caused confusion before.
The approach to Flint Pike crosses 16 field boundaries and the wayleave is held by the county.
Flint Pike shares its power feed with the neighbouring pumping station and has its own cut-out.
The notes for S-0459 mention a disused well inside the compound, capped and recorded but not surveyed.
A visitor log is kept at Flint Pike and shows 22 entries for the period.
S-0459 appears at revision 1 with a load of 663.
That revision of Flint Pike was lodged 2034-01-21, is settled, and places the station in tier 3.
Flint Pike carries a calibration offset of -3 on the current instrument head.
The logbook kept at Flint Pike runs to 6 pages and the earlier volumes are held off site.
Flint Pike has been on the register since the first consolidation and its paperwork has never been reconstructed.

### S-0460 -- Nettle Mill

Nettle Mill shares its power feed with the neighbouring pumping station and has its own cut-out.
An earlier clerk recorded Nettle Mill under a shortened spelling, and both forms still appear in the older indexes.
Weather at Nettle Mill closed the approach for 25 days during the period under review and no readings were lost.
Correspondence shows the tenancy at Nettle Mill was renewed for a further 26 years.
Tier 2 is where Nettle Mill sits on revision 2, whose status is settled.
The load on that revision of S-0460, lodged 2034-12-01, is 725.
The site plan for Nettle Mill is the third revision and supersedes the sketch held in the district folder.

### S-0461 -- Sorrel Delve

Weather at Sorrel Delve closed the approach for 30 days during the period under review and no readings were lost.
An earlier clerk recorded Sorrel Delve under a shortened spelling, and both forms still appear in the older indexes.
A spare sensor head is kept at Sorrel Delve against the failure that took out the district in the previous cycle.
Sorrel Delve has been on the register since the first consolidation and its paperwork has never been reconstructed.
Revision 1 of the return for Sorrel Delve was lodged on 2034-09-20 and stands withdrawn.
That revision places S-0461 in tier 1 and gives its load as 368.
The approach to Sorrel Delve crosses 23 field boundaries and the wayleave is held by the county.
The enclosure at Sorrel Delve was rebuilt in timber after the old fencing was taken by the river.
Vegetation around Sorrel Delve is cut back twice a year under the standing arrangement.

### S-0462 -- Tamarisk Furlong

Correspondence about S-0462 is filed under the district rather than under the site, which has caused confusion before.
The notes for S-0462 mention a disused well inside the compound, capped and recorded but not surveyed.
Weather at Tamarisk Furlong closed the approach for 25 days during the period under review and no readings were lost.
An earlier clerk recorded Tamarisk Furlong under a shortened spelling, and both forms still appear in the older indexes.
Tier 2 is where Tamarisk Furlong sits on revision 5, whose status is settled.
The load on that revision of S-0462, lodged 2034-09-19, is 931.
The offset applied to readings from S-0462 is -7 and has not been revised.
Two of the anchors at Tamarisk Furlong were replaced after the frost and the work is recorded in the district ledger.
The approach to Tamarisk Furlong crosses 8 field boundaries and the wayleave is held by the county.
The reading shelter at Tamarisk Furlong takes water in heavy weather and the floor was relaid.
The access key for S-0462 is held at the district office and signed out per visit.
Signal strength at Tamarisk Furlong has been marginal since the mast on the ridge was lowered.

### S-0463 -- Jasper Dingle

The enclosure at Jasper Dingle was rebuilt in timber after the old fencing was taken by the river.
Jasper Dingle lodged revision 2 on 2034-07-13.
The return for S-0463 is returned, sits at tier 3, and records a load of 772.
Jasper Dingle shares its power feed with the neighbouring pumping station and has its own cut-out.
Drainage work near Jasper Dingle was completed without interruption to the record.
Weather at Jasper Dingle closed the approach for 4 days during the period under review and no readings were lost.
Jasper Dingle has been on the register since the first consolidation and its paperwork has never been reconstructed.
An earlier clerk recorded Jasper Dingle under a shortened spelling, and both forms still appear in the older indexes.

### S-0464 -- Bronze Headland

Vegetation around Bronze Headland is cut back twice a year under the standing arrangement.
Revision 4 of the return for Bronze Headland was lodged on 2034-12-28 and stands settled.
That revision places S-0464 in tier 1 and gives its load as 189.
The access key for S-0464 is held at the district office and signed out per visit.
Weather at Bronze Headland closed the approach for 40 days during the period under review and no readings were lost.
Correspondence about S-0464 is filed under the district rather than under the site, which has caused confusion before.
S-0464 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Correspondence shows the tenancy at Bronze Headland was renewed for a further 17 years.
Signal strength at Bronze Headland has been marginal since the mast on the ridge was lowered.
The logbook kept at Bronze Headland runs to 73 pages and the earlier volumes are held off site.

### S-0465 -- Russet Fell

A housekeeping note against S-0465 asks that the cable run be rewalked before the next dry season.
The instrument housing at Russet Fell is the original pattern and its door seal is checked each visit.
Russet Fell has been on the register since the first consolidation and its paperwork has never been reconstructed.
The notes for S-0465 mention a disused well inside the compound, capped and recorded but not surveyed.
Correspondence about S-0465 is filed under the district rather than under the site, which has caused confusion before.
A visitor log is kept at Russet Fell and shows 35 entries for the period.
The district file for Russet Fell shows revision 1 lodged on 2034-04-28.
For S-0465 the status is settled, the tier is 2, and the load is 701.
Russet Fell carries a calibration offset of -22 on the current instrument head.
Russet Fell shares its power feed with the neighbouring pumping station and has its own cut-out.
Weather at Russet Fell closed the approach for 7 days during the period under review and no readings were lost.

### S-0466 -- Willow Combe

Correspondence shows the tenancy at Willow Combe was renewed for a further 3 years.
An earlier clerk recorded Willow Combe under a shortened spelling, and both forms still appear in the older indexes.
Willow Combe has been on the register since the first consolidation and its paperwork has never been reconstructed.
Signal strength at Willow Combe has been marginal since the mast on the ridge was lowered.
Tier 2 is where Willow Combe sits on revision 5, whose status is settled.
The load on that revision of S-0466, lodged 2034-06-05, is 468.
A calibration offset of -19 is recorded for S-0466 against the district standard.
The enclosure at Willow Combe was rebuilt in timber after the old fencing was taken by the river.

### S-0467 -- Meadow Fell

The survey party reached Meadow Fell on the thirteenth of the month and found the access track passable for light vehicles only.
A housekeeping note against S-0467 asks that the cable run be rewalked before the next dry season.
Two of the anchors at Meadow Fell were replaced after the frost and the work is recorded in the district ledger.
Weather at Meadow Fell closed the approach for 7 days during the period under review and no readings were lost.
Telemetry from S-0467 arrives on the second relay and is batched nightly rather than streamed.
A spare sensor head is kept at Meadow Fell against the failure that took out the district in the previous cycle.
S-0467 appears at revision 4 with a load of 347.
That revision of Meadow Fell was lodged 2034-12-05, is settled, and places the station in tier 9.
Meadow Fell carries sequence mark 3 in this quarter's reconciliation.
The reading shelter at Meadow Fell takes water in heavy weather and the floor was relaid.

### S-0221 -- Lichen Ripple

A visitor log is kept at Lichen Ripple and shows 67 entries for the period.
Revision 2 of the return for Lichen Ripple was lodged on 2034-03-13 and stands settled.
That revision places S-0221 in tier 7 and gives its load as 941.
The reconciliation sequence mark carried by this revision of S-0221 is 5.
The reading shelter at Lichen Ripple takes water in heavy weather and the floor was relaid.
Calibration gear for S-0221 travels with the district van and is shared with 3 other sites.
S-0221 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The access key for S-0221 is held at the district office and signed out per visit.
Access to Lichen Ripple is by the service road from the south; the gate code was reissued after the first inspection.
Drainage work near Lichen Ripple was completed without interruption to the record.
Lichen Ripple shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0469 -- Fennel Delve

Correspondence shows the tenancy at Fennel Delve was renewed for a further 21 years.
Fennel Delve shares its power feed with the neighbouring pumping station and has its own cut-out.
Fennel Delve lodged revision 6 on 2034-08-09.
The return for S-0469 is settled, sits at tier 2, and records a load of 978.
The logbook kept at Fennel Delve runs to 87 pages and the earlier volumes are held off site.
The fence line at Fennel Delve was rerun 27 metres to the east to clear the culvert.
Fennel Delve has been on the register since the first consolidation and its paperwork has never been reconstructed.

### S-0470 -- Marram Pike

The survey party reached Marram Pike on the eighth of the month and found the access track passable for light vehicles only.
Marram Pike shares its power feed with the neighbouring pumping station and has its own cut-out.
Telemetry from S-0470 arrives on the thirteenth relay and is batched nightly rather than streamed.
S-0470 appears at revision 2 with a load of 571.
That revision of Marram Pike was lodged 2034-10-01, is settled, and places the station in tier 4.
The offset applied to readings from S-0470 is -30 and has not been revised.
A visitor log is kept at Marram Pike and shows 33 entries for the period.
Access to Marram Pike is by the service road from the south; the gate code was reissued after the fifth inspection.
Maintenance visits to S-0470 are scheduled quarterly and the fourteenth of those was carried out as planned.

### S-0471 -- Midland Knoll

The enclosure at Midland Knoll was rebuilt in timber after the old fencing was taken by the river.
Tier 6 is where Midland Knoll sits on revision 3, whose status is withdrawn.
The load on that revision of S-0471, lodged 2034-03-06, is 892.
A housekeeping note against S-0471 asks that the cable run be rewalked before the next dry season.
Midland Knoll has been on the register since the first consolidation and its paperwork has never been reconstructed.
The site plan for Midland Knoll is the ninth revision and supersedes the sketch held in the district folder.
A visitor log is kept at Midland Knoll and shows 87 entries for the period.
Two of the anchors at Midland Knoll were replaced after the frost and the work is recorded in the district ledger.
The instrument housing at Midland Knoll is the original pattern and its door seal is checked each visit.
Maintenance visits to S-0471 are scheduled quarterly and the fourth of those was carried out as planned.
The reading shelter at Midland Knoll takes water in heavy weather and the floor was relaid.

### S-0472 -- Kestrel Bluff

Kestrel Bluff shares its power feed with the neighbouring pumping station and has its own cut-out.
Signal strength at Kestrel Bluff has been marginal since the mast on the ridge was lowered.
Weather at Kestrel Bluff closed the approach for 34 days during the period under review and no readings were lost.
Access to Kestrel Bluff is by the service road from the south; the gate code was reissued after the sixth inspection.
The district file for Kestrel Bluff shows revision 3 lodged on 2034-12-12.
For S-0472 the status is settled, the tier is 5, and the load is 849.
S-0472 was one of the sites brought forward in the consolidation and its numbering reflects that order.

### S-0473 -- Ridge Basin

S-0473 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Calibration gear for S-0473 travels with the district van and is shared with 3 other sites.
Vegetation around Ridge Basin is cut back twice a year under the standing arrangement.
Ridge Basin shares its power feed with the neighbouring pumping station and has its own cut-out.
Tier 1 is where Ridge Basin sits on revision 4, whose status is settled.
The load on that revision of S-0473, lodged 2034-09-14, is 565.
The site plan for Ridge Basin is the fifth revision and supersedes the sketch held in the district folder.
The fence line at Ridge Basin was rerun 10 metres to the east to clear the culvert.
The reading shelter at Ridge Basin takes water in heavy weather and the floor was relaid.

### S-0474 -- Granite Dale

Granite Dale shares its power feed with the neighbouring pumping station and has its own cut-out.
A spare sensor head is kept at Granite Dale against the failure that took out the district in the previous cycle.
S-0474 was one of the sites brought forward in the consolidation and its numbering reflects that order.
An earlier clerk recorded Granite Dale under a shortened spelling, and both forms still appear in the older indexes.
Telemetry from S-0474 arrives on the seventh relay and is batched nightly rather than streamed.
Granite Dale has been on the register since the first consolidation and its paperwork has never been reconstructed.
Granite Dale lodged revision 5 on 2034-07-09.
The return for S-0474 is returned, sits at tier 2, and records a load of 719.
The access key for S-0474 is held at the district office and signed out per visit.
A housekeeping note against S-0474 asks that the cable run be rewalked before the next dry season.

### S-0475 -- Shale Bourne

Access to Shale Bourne is by the service road from the south; the gate code was reissued after the seventh inspection.
The enclosure at Shale Bourne was rebuilt in timber after the old fencing was taken by the river.
The instrument housing at Shale Bourne is the original pattern and its door seal is checked each visit.
S-0475 appears at revision 2 with a load of 517.
That revision of Shale Bourne was lodged 2034-05-23, is settled, and places the station in tier 3.
A calibration offset of 35 is recorded for S-0475 against the district standard.
The reading shelter at Shale Bourne takes water in heavy weather and the floor was relaid.

### S-0476 -- Cedar Drift

Weather at Cedar Drift closed the approach for 10 days during the period under review and no readings were lost.
Two of the anchors at Cedar Drift were replaced after the frost and the work is recorded in the district ledger.
Drainage work near Cedar Drift was completed without interruption to the record.
Maintenance visits to S-0476 are scheduled quarterly and the twelfth of those was carried out as planned.
On 2034-11-28 the district accepted revision 3 for Cedar Drift and marked it settled.
S-0476 carries tier 4 on that revision and a load of 805.
The enclosure at Cedar Drift was rebuilt in timber after the old fencing was taken by the river.

### S-0477 -- Verdigris Brae

A housekeeping note against S-0477 asks that the cable run be rewalked before the next dry season.
On 2034-08-02 the district accepted revision 2 for Verdigris Brae and marked it returned.
S-0477 carries tier 4 on that revision and a load of 473.
The logbook kept at Verdigris Brae runs to 32 pages and the earlier volumes are held off site.
Drainage work near Verdigris Brae was completed without interruption to the record.
The fence line at Verdigris Brae was rerun 13 metres to the east to clear the culvert.

### S-0478 -- Tamarisk Causeway

The site plan for Tamarisk Causeway is the twelfth revision and supersedes the sketch held in the district folder.
Telemetry from S-0478 arrives on the tenth relay and is batched nightly rather than streamed.
A spare sensor head is kept at Tamarisk Causeway against the failure that took out the district in the previous cycle.
The notes for S-0478 mention a disused well inside the compound, capped and recorded but not surveyed.
A housekeeping note against S-0478 asks that the cable run be rewalked before the next dry season.
S-0478 appears at revision 5 with a load of 293.
That revision of Tamarisk Causeway was lodged 2034-01-02, is settled, and places the station in tier 5.
Correspondence about S-0478 is filed under the district rather than under the site, which has caused confusion before.
The approach to Tamarisk Causeway crosses 27 field boundaries and the wayleave is held by the county.
Correspondence shows the tenancy at Tamarisk Causeway was renewed for a further 86 years.
A visitor log is kept at Tamarisk Causeway and shows 12 entries for the period.

### S-0479 -- Midland Bank

The fence line at Midland Bank was rerun 39 metres to the east to clear the culvert.
Vegetation around Midland Bank is cut back twice a year under the standing arrangement.
Signal strength at Midland Bank has been marginal since the mast on the ridge was lowered.
Maintenance visits to S-0479 are scheduled quarterly and the first of those was carried out as planned.
Calibration gear for S-0479 travels with the district van and is shared with 14 other sites.
Midland Bank lodged revision 1 on 2034-02-14.
The return for S-0479 is provisional, sits at tier 2, and records a load of 181.
The site plan for Midland Bank is the twelfth revision and supersedes the sketch held in the district folder.
Midland Bank has been on the register since the first consolidation and its paperwork has never been reconstructed.
The logbook kept at Midland Bank runs to 27 pages and the earlier volumes are held off site.
The access key for S-0479 is held at the district office and signed out per visit.
A housekeeping note against S-0479 asks that the cable run be rewalked before the next dry season.

### S-0480 -- Hollow Bight

The notes for S-0480 mention a disused well inside the compound, capped and recorded but not surveyed.
Maintenance visits to S-0480 are scheduled quarterly and the twelfth of those was carried out as planned.
Telemetry from S-0480 arrives on the seventh relay and is batched nightly rather than streamed.
S-0480 appears at revision 2 with a load of 665.
That revision of Hollow Bight was lodged 2034-04-19, is settled, and places the station in tier 2.
Vegetation around Hollow Bight is cut back twice a year under the standing arrangement.
Hollow Bight has been on the register since the first consolidation and its paperwork has never been reconstructed.
The fence line at Hollow Bight was rerun 23 metres to the east to clear the culvert.

### S-0481 -- Pewter Moor

Two of the anchors at Pewter Moor were replaced after the frost and the work is recorded in the district ledger.
A housekeeping note against S-0481 asks that the cable run be rewalked before the next dry season.
The logbook kept at Pewter Moor runs to 36 pages and the earlier volumes are held off site.
The instrument housing at Pewter Moor is the original pattern and its door seal is checked each visit.
The district file for Pewter Moor shows revision 6 lodged on 2034-05-25.
For S-0481 the status is returned, the tier is 7, and the load is 235.
Pewter Moor has been on the register since the first consolidation and its paperwork has never been reconstructed.

### S-0482 -- Harrow Ghyll

S-0482 was one of the sites brought forward in the consolidation and its numbering reflects that order.
The site plan for Harrow Ghyll is the thirteenth revision and supersedes the sketch held in the district folder.
Maintenance visits to S-0482 are scheduled quarterly and the eleventh of those was carried out as planned.
Telemetry from S-0482 arrives on the ninth relay and is batched nightly rather than streamed.
Harrow Ghyll shares its power feed with the neighbouring pumping station and has its own cut-out.
The logbook kept at Harrow Ghyll runs to 67 pages and the earlier volumes are held off site.
The instrument housing at Harrow Ghyll is the original pattern and its door seal is checked each visit.
Tier 5 is where Harrow Ghyll sits on revision 4, whose status is returned.
The load on that revision of S-0482, lodged 2034-04-16, is 982.
Weather at Harrow Ghyll closed the approach for 11 days during the period under review and no readings were lost.

### S-0483 -- Meadow Glade

Access to Meadow Glade is by the service road from the south; the gate code was reissued after the fourth inspection.
Revision 6 of the return for Meadow Glade was lodged on 2034-12-05 and stands settled.
That revision places S-0483 in tier 1 and gives its load as 390.
The reading shelter at Meadow Glade takes water in heavy weather and the floor was relaid.
Meadow Glade shares its power feed with the neighbouring pumping station and has its own cut-out.
Correspondence shows the tenancy at Meadow Glade was renewed for a further 39 years.

### S-0484 -- Sable Ghyll

Calibration gear for S-0484 travels with the district van and is shared with 14 other sites.
Access to Sable Ghyll is by the service road from the south; the gate code was reissued after the fourteenth inspection.
Correspondence shows the tenancy at Sable Ghyll was renewed for a further 68 years.
The enclosure at Sable Ghyll was rebuilt in timber after the old fencing was taken by the river.
Telemetry from S-0484 arrives on the ninth relay and is batched nightly rather than streamed.
Tier 3 is where Sable Ghyll sits on revision 4, whose status is settled.
The load on that revision of S-0484, lodged 2034-02-26, is 695.
The offset applied to readings from S-0484 is 17 and has not been revised.
Sable Ghyll has been on the register since the first consolidation and its paperwork has never been reconstructed.

### S-0485 -- Russet Butte

Correspondence shows the tenancy at Russet Butte was renewed for a further 33 years.
A housekeeping note against S-0485 asks that the cable run be rewalked before the next dry season.
Access to Russet Butte is by the service road from the south; the gate code was reissued after the fourteenth inspection.
On 2034-07-15 the district accepted revision 3 for Russet Butte and marked it settled.
S-0485 carries tier 2 on that revision and a load of 324.
Russet Butte carries a calibration offset of 29 on the current instrument head.
Weather at Russet Butte closed the approach for 15 days during the period under review and no readings were lost.
The access key for S-0485 is held at the district office and signed out per visit.
The logbook kept at Russet Butte runs to 53 pages and the earlier volumes are held off site.
An earlier clerk recorded Russet Butte under a shortened spelling, and both forms still appear in the older indexes.

### S-0486 -- Flint Yard

Two of the anchors at Flint Yard were replaced after the frost and the work is recorded in the district ledger.
The enclosure at Flint Yard was rebuilt in timber after the old fencing was taken by the river.
Calibration gear for S-0486 travels with the district van and is shared with 16 other sites.
Flint Yard shares its power feed with the neighbouring pumping station and has its own cut-out.
The instrument housing at Flint Yard is the original pattern and its door seal is checked each visit.
The survey party reached Flint Yard on the second of the month and found the access track passable for light vehicles only.
The load recorded for S-0486 is 709, on a return at tier 8.
That return for Flint Yard is revision 1, lodged 2034-02-03, and its status is withdrawn.
Access to Flint Yard is by the service road from the south; the gate code was reissued after the fourteenth inspection.
A spare sensor head is kept at Flint Yard against the failure that took out the district in the previous cycle.
The reading shelter at Flint Yard takes water in heavy weather and the floor was relaid.
Signal strength at Flint Yard has been marginal since the mast on the ridge was lowered.

### S-0487 -- Garnet Headland

The logbook kept at Garnet Headland runs to 71 pages and the earlier volumes are held off site.
The notes for S-0487 mention a disused well inside the compound, capped and recorded but not surveyed.
Drainage work near Garnet Headland was completed without interruption to the record.
The district file for Garnet Headland shows revision 6 lodged on 2034-08-13.
For S-0487 the status is settled, the tier is 4, and the load is 306.
A housekeeping note against S-0487 asks that the cable run be rewalked before the next dry season.
The survey party reached Garnet Headland on the fourth of the month and found the access track passable for light vehicles only.

### S-0488 -- Jasper Gully

Telemetry from S-0488 arrives on the eighth relay and is batched nightly rather than streamed.
The instrument housing at Jasper Gully is the original pattern and its door seal is checked each visit.
The notes for S-0488 mention a disused well inside the compound, capped and recorded but not surveyed.
The site plan for Jasper Gully is the thirteenth revision and supersedes the sketch held in the district folder.
On 2034-03-20 the district accepted revision 1 for Jasper Gully and marked it provisional.
S-0488 carries tier 7 on that revision and a load of 471.
A calibration offset of 21 is recorded for S-0488 against the district standard.
An earlier clerk recorded Jasper Gully under a shortened spelling, and both forms still appear in the older indexes.
Drainage work near Jasper Gully was completed without interruption to the record.

### S-0489 -- Thistle Strand

Thistle Strand has been on the register since the first consolidation and its paperwork has never been reconstructed.
Weather at Thistle Strand closed the approach for 7 days during the period under review and no readings were lost.
The approach to Thistle Strand crosses 9 field boundaries and the wayleave is held by the county.
The instrument housing at Thistle Strand is the original pattern and its door seal is checked each visit.
Tier 2 is where Thistle Strand sits on revision 6, whose status is settled.
The load on that revision of S-0489, lodged 2034-01-24, is 372.
The notes for S-0489 mention a disused well inside the compound, capped and recorded but not surveyed.
The site plan for Thistle Strand is the fourth revision and supersedes the sketch held in the district folder.
The logbook kept at Thistle Strand runs to 82 pages and the earlier volumes are held off site.
Vegetation around Thistle Strand is cut back twice a year under the standing arrangement.
Correspondence shows the tenancy at Thistle Strand was renewed for a further 71 years.
An earlier clerk recorded Thistle Strand under a shortened spelling, and both forms still appear in the older indexes.

### S-0490 -- Willow Dale

The approach to Willow Dale crosses 15 field boundaries and the wayleave is held by the county.
The site plan for Willow Dale is the twelfth revision and supersedes the sketch held in the district folder.
An earlier clerk recorded Willow Dale under a shortened spelling, and both forms still appear in the older indexes.
Willow Dale has been on the register since the first consolidation and its paperwork has never been reconstructed.
Vegetation around Willow Dale is cut back twice a year under the standing arrangement.
The load recorded for S-0490 is 885, on a return at tier 4.
That return for Willow Dale is revision 3, lodged 2034-11-03, and its status is settled.
A calibration offset of 34 is recorded for S-0490 against the district standard.
The access key for S-0490 is held at the district office and signed out per visit.

### S-0491 -- Marram Thwaite

Drainage work near Marram Thwaite was completed without interruption to the record.
S-0491 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Marram Thwaite shares its power feed with the neighbouring pumping station and has its own cut-out.
An earlier clerk recorded Marram Thwaite under a shortened spelling, and both forms still appear in the older indexes.
Vegetation around Marram Thwaite is cut back twice a year under the standing arrangement.
Weather at Marram Thwaite closed the approach for 30 days during the period under review and no readings were lost.
Signal strength at Marram Thwaite has been marginal since the mast on the ridge was lowered.
Revision 6 of the return for Marram Thwaite was lodged on 2034-11-05 and stands settled.
That revision places S-0491 in tier 4 and gives its load as 305.
Two of the anchors at Marram Thwaite were replaced after the frost and the work is recorded in the district ledger.

### S-0492 -- Coral Culvert

S-0492 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Coral Culvert shares its power feed with the neighbouring pumping station and has its own cut-out.
The reading shelter at Coral Culvert takes water in heavy weather and the floor was relaid.
Coral Culvert has been on the register since the first consolidation and its paperwork has never been reconstructed.
Weather at Coral Culvert closed the approach for 10 days during the period under review and no readings were lost.
Two of the anchors at Coral Culvert were replaced after the frost and the work is recorded in the district ledger.
Calibration gear for S-0492 travels with the district van and is shared with 32 other sites.
The approach to Coral Culvert crosses 6 field boundaries and the wayleave is held by the county.
Status withdrawn: revision 5 for S-0492, lodged 2034-10-07.
Load 551 at tier 9 is what that revision carries for Coral Culvert.
A spare sensor head is kept at Coral Culvert against the failure that took out the district in the previous cycle.
An earlier clerk recorded Coral Culvert under a shortened spelling, and both forms still appear in the older indexes.

### S-0493 -- Ridge Shaw

Drainage work near Ridge Shaw was completed without interruption to the record.
The fence line at Ridge Shaw was rerun 22 metres to the east to clear the culvert.
S-0493 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Two of the anchors at Ridge Shaw were replaced after the frost and the work is recorded in the district ledger.
The load recorded for S-0493 is 698, on a return at tier 4.
That return for Ridge Shaw is revision 2, lodged 2034-02-27, and its status is provisional.
Ridge Shaw carries a calibration offset of -17 on the current instrument head.
Access to Ridge Shaw is by the service road from the south; the gate code was reissued after the sixth inspection.
The approach to Ridge Shaw crosses 6 field boundaries and the wayleave is held by the county.
The reading shelter at Ridge Shaw takes water in heavy weather and the floor was relaid.

### S-0494 -- Pewter Knoll

The site plan for Pewter Knoll is the eighth revision and supersedes the sketch held in the district folder.
The load recorded for S-0494 is 164, on a return at tier 6.
That return for Pewter Knoll is revision 3, lodged 2034-12-20, and its status is provisional.
The access key for S-0494 is held at the district office and signed out per visit.
The logbook kept at Pewter Knoll runs to 64 pages and the earlier volumes are held off site.
Correspondence about S-0494 is filed under the district rather than under the site, which has caused confusion before.
The approach to Pewter Knoll crosses 18 field boundaries and the wayleave is held by the county.
A spare sensor head is kept at Pewter Knoll against the failure that took out the district in the previous cycle.

### S-0495 -- Dusk Cairn

The survey party reached Dusk Cairn on the eighth of the month and found the access track passable for light vehicles only.
Tier 5 is where Dusk Cairn sits on revision 6, whose status is provisional.
The load on that revision of S-0495, lodged 2034-11-07, is 611.
Calibration gear for S-0495 travels with the district van and is shared with 5 other sites.
Dusk Cairn has been on the register since the first consolidation and its paperwork has never been reconstructed.
The access key for S-0495 is held at the district office and signed out per visit.

### S-0496 -- Vellum Barrow

Vegetation around Vellum Barrow is cut back twice a year under the standing arrangement.
The site plan for Vellum Barrow is the eleventh revision and supersedes the sketch held in the district folder.
The logbook kept at Vellum Barrow runs to 72 pages and the earlier volumes are held off site.
Status settled: revision 5 for S-0496, lodged 2034-01-15.
Load 283 at tier 4 is what that revision carries for Vellum Barrow.
Vellum Barrow shares its power feed with the neighbouring pumping station and has its own cut-out.
The notes for S-0496 mention a disused well inside the compound, capped and recorded but not surveyed.

### S-0497 -- Flint Gully

An earlier clerk recorded Flint Gully under a shortened spelling, and both forms still appear in the older indexes.
Vegetation around Flint Gully is cut back twice a year under the standing arrangement.
The instrument housing at Flint Gully is the original pattern and its door seal is checked each visit.
Tier 4 is where Flint Gully sits on revision 3, whose status is settled.
The load on that revision of S-0497, lodged 2034-11-04, is 753.
The offset applied to readings from S-0497 is 29 and has not been revised.
The fence line at Flint Gully was rerun 30 metres to the east to clear the culvert.
A visitor log is kept at Flint Gully and shows 49 entries for the period.

### S-0498 -- Birch Weir

An earlier clerk recorded Birch Weir under a shortened spelling, and both forms still appear in the older indexes.
Correspondence shows the tenancy at Birch Weir was renewed for a further 24 years.
Vegetation around Birch Weir is cut back twice a year under the standing arrangement.
The enclosure at Birch Weir was rebuilt in timber after the old fencing was taken by the river.
Birch Weir shares its power feed with the neighbouring pumping station and has its own cut-out.
Status withdrawn: revision 2 for S-0498, lodged 2034-04-18.
Load 595 at tier 6 is what that revision carries for Birch Weir.
The offset applied to readings from S-0498 is -29 and has not been revised.
The approach to Birch Weir crosses 12 field boundaries and the wayleave is held by the county.

### S-0499 -- Bronze Mill

Two of the anchors at Bronze Mill were replaced after the frost and the work is recorded in the district ledger.
Bronze Mill has been on the register since the first consolidation and its paperwork has never been reconstructed.
A housekeeping note against S-0499 asks that the cable run be rewalked before the next dry season.
Tier 3 is where Bronze Mill sits on revision 3, whose status is settled.
The load on that revision of S-0499, lodged 2034-12-06, is 247.
The fence line at Bronze Mill was rerun 33 metres to the east to clear the culvert.
Calibration gear for S-0499 travels with the district van and is shared with 13 other sites.
Bronze Mill shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0500 -- Dusk Terrace

The enclosure at Dusk Terrace was rebuilt in timber after the old fencing was taken by the river.
Correspondence shows the tenancy at Dusk Terrace was renewed for a further 78 years.
A housekeeping note against S-0500 asks that the cable run be rewalked before the next dry season.
Tier 4 is where Dusk Terrace sits on revision 5, whose status is settled.
The load on that revision of S-0500, lodged 2034-03-02, is 155.
Two of the anchors at Dusk Terrace were replaced after the frost and the work is recorded in the district ledger.
Drainage work near Dusk Terrace was completed without interruption to the record.
S-0500 was one of the sites brought forward in the consolidation and its numbering reflects that order.

### S-0501 -- Granite Ferry

An earlier clerk recorded Granite Ferry under a shortened spelling, and both forms still appear in the older indexes.
Drainage work near Granite Ferry was completed without interruption to the record.
Access to Granite Ferry is by the service road from the south; the gate code was reissued after the eleventh inspection.
Tier 1 is where Granite Ferry sits on revision 3, whose status is settled.
The load on that revision of S-0501, lodged 2034-09-03, is 503.
Weather at Granite Ferry closed the approach for 29 days during the period under review and no readings were lost.
Signal strength at Granite Ferry has been marginal since the mast on the ridge was lowered.

### S-0502 -- Lichen Ford

The reading shelter at Lichen Ford takes water in heavy weather and the floor was relaid.
Weather at Lichen Ford closed the approach for 5 days during the period under review and no readings were lost.
Revision 6 of the return for Lichen Ford was lodged on 2034-02-23 and stands settled.
That revision places S-0502 in tier 1 and gives its load as 815.
Correspondence shows the tenancy at Lichen Ford was renewed for a further 52 years.
Two of the anchors at Lichen Ford were replaced after the frost and the work is recorded in the district ledger.
The fence line at Lichen Ford was rerun 16 metres to the east to clear the culvert.
Signal strength at Lichen Ford has been marginal since the mast on the ridge was lowered.
Lichen Ford shares its power feed with the neighbouring pumping station and has its own cut-out.

### S-0503 -- Pebble Knap

An earlier clerk recorded Pebble Knap under a shortened spelling, and both forms still appear in the older indexes.
The site plan for Pebble Knap is the third revision and supersedes the sketch held in the district folder.
Revision 6 of the return for Pebble Knap was lodged on 2034-06-04 and stands returned.
That revision places S-0503 in tier 2 and gives its load as 529.
The enclosure at Pebble Knap was rebuilt in timber after the old fencing was taken by the river.
S-0503 was one of the sites brought forward in the consolidation and its numbering reflects that order.
Correspondence about S-0503 is filed under the district rather than under the site, which has caused confusion before.

### S-0504 -- Nettle Shoal

The approach to Nettle Shoal crosses 36 field boundaries and the wayleave is held by the county.
The load recorded for S-0504 is 735, on a return at tier 9.
That return for Nettle Shoal is revision 1, lodged 2034-08-27, and its status is open.
Drainage work near Nettle Shoal was completed without interruption to the record.
The logbook kept at Nettle Shoal runs to 78 pages and the earlier volumes are held off site.
An earlier clerk recorded Nettle Shoal under a shortened spelling, and both forms still appear in the older indexes.
A spare sensor head is kept at Nettle Shoal against the failure that took out the district in the previous cycle.
Telemetry from S-0504 arrives on the first relay and is batched nightly rather than streamed.
Nettle Shoal shares its power feed with the neighbouring pumping station and has its own cut-out.
A housekeeping note against S-0504 asks that the cable run be rewalked before the next dry season.

### S-0505 -- Shale Hallow

Maintenance visits to S-0505 are scheduled quarterly and the ninth of those was carried out as planned.
Signal strength at Shale Hallow has been marginal since the mast on the ridge was lowered.
The approach to Shale Hallow crosses 26 field boundaries and the wayleave is held by the county.
Shale Hallow has been on the register since the first consolidation and its paperwork has never been reconstructed.
The load recorded for S-0505 is 133, on a return at tier 3.
That return for Shale Hallow is revision 1, lodged 2034-04-11, and its status is settled.
A calibration offset of -18 is recorded for S-0505 against the district standard.
Shale Hallow shares its power feed with the neighbouring pumping station and has its own cut-out.
The enclosure at Shale Hallow was rebuilt in timber after the old fencing was taken by the river.

### S-0506 -- Umber Vale

Drainage work near Umber Vale was completed without interruption to the record.
The logbook kept at Umber Vale runs to 17 pages and the earlier volumes are held off site.
A visitor log is kept at Umber Vale and shows 11 entries for the period.
The site plan for Umber Vale is the ninth revision and supersedes the sketch held in the district folder.
The approach to Umber Vale crosses 7 field boundaries and the wayleave is held by the county.
Vegetation around Umber Vale is cut back twice a year under the standing arrangement.
S-0506 appears at revision 1 with a load of 582.
That revision of Umber Vale was lodged 2034-04-01, is settled, and places the station in tier 2.
Weather at Umber Vale closed the approach for 19 days during the period under review and no readings were lost.
Calibration gear for S-0506 travels with the district van and is shared with 5 other sites.
Correspondence about S-0506 is filed under the district rather than under the site, which has caused confusion before.

### S-0507 -- Ochre Mill

The notes for S-0507 mention a disused well inside the compound, capped and recorded but not surveyed.
The fence line at Ochre Mill was rerun 5 metres to the east to clear the culvert.
The reading shelter at Ochre Mill takes water in heavy weather and the floor was relaid.
Maintenance visits to S-0507 are scheduled quarterly and the fourth of those was carried out as planned.
Vegetation around Ochre Mill is cut back twice a year under the standing arrangement.
A spare sensor head is kept at Ochre Mill against the failure that took out the district in the previous cycle.
Weather at Ochre Mill closed the approach for 6 days during the period under review and no readings were lost.
On 2034-10-19 the district accepted revision 4 for Ochre Mill and marked it returned.
S-0507 carries tier 5 on that revision and a load of 190.
S-0507 was one of the sites brought forward in the consolidation and its numbering reflects that order.

### S-0508 -- Brindle Sand

Correspondence shows the tenancy at Brindle Sand was renewed for a further 11 years.
The approach to Brindle Sand crosses 38 field boundaries and the wayleave is held by the county.
Calibration gear for S-0508 travels with the district van and is shared with 30 other sites.
The fence line at Brindle Sand was rerun 15 metres to the east to clear the culvert.
Revision 1 of the return for Brindle Sand was lodged on 2034-11-28 and stands settled.
That revision places S-0508 in tier 4 and gives its load as 641.
Brindle Sand carries a calibration offset of 23 on the current instrument head.
Access to Brindle Sand is by the service road from the south; the gate code was reissued after the thirteenth inspection.
Brindle Sand has been on the register since the first consolidation and its paperwork has never been reconstructed.
The logbook kept at Brindle Sand runs to 36 pages and the earlier volumes are held off site.

### S-0509 -- Copper Reach

Correspondence shows the tenancy at Copper Reach was renewed for a further 37 years.
The enclosure at Copper Reach was rebuilt in timber after the old fencing was taken by the river.
Vegetation around Copper Reach is cut back twice a year under the standing arrangement.
Revision 5 of the return for Copper Reach was lodged on 2034-07-01 and stands withdrawn.
That revision places S-0509 in tier 9 and gives its load as 446.
A spare sensor head is kept at Copper Reach against the failure that took out the district in the previous cycle.
Signal strength at Copper Reach has been marginal since the mast on the ridge was lowered.
Two of the anchors at Copper Reach were replaced after the frost and the work is recorded in the district ledger.
Telemetry from S-0509 arrives on the fourteenth relay and is batched nightly rather than streamed.
An earlier clerk recorded Copper Reach under a shortened spelling, and both forms still appear in the older indexes.

### S-0510 -- Marram Spur

The enclosure at Marram Spur was rebuilt in timber after the old fencing was taken by the river.
Correspondence about S-0510 is filed under the district rather than under the site, which has caused confusion before.
A housekeeping note against S-0510 asks that the cable run be rewalked before the next dry season.
S-0510 appears at revision 4 with a load of 177.
That revision of Marram Spur was lodged 2034-10-19, is returned, and places the station in tier 4.
Drainage work near Marram Spur was completed without interruption to the record.
The survey party reached Marram Spur on the eleventh of the month and found the access track passable for light vehicles only.

### S-0511 -- Bramble Causeway

The survey party reached Bramble Causeway on the fifth of the month and found the access track passable for light vehicles only.
The site plan for Bramble Causeway is the fifth revision and supersedes the sketch held in the district folder.
Bramble Causeway has been on the register since the first consolidation and its paperwork has never been reconstructed.
Two of the anchors at Bramble Causeway were replaced after the frost and the work is recorded in the district ledger.
The approach to Bramble Causeway crosses 24 field boundaries and the wayleave is held by the county.
The notes for S-0511 mention a disused well inside the compound, capped and recorded but not surveyed.
A visitor log is kept at Bramble Causeway and shows 85 entries for the period.
The district file for Bramble Causeway shows revision 2 lodged on 2034-02-04.
For S-0511 the status is withdrawn, the tier is 8, and the load is 340.
The offset applied to readings from S-0511 is -10 and has not been revised.
An earlier clerk recorded Bramble Causeway under a shortened spelling, and both forms still appear in the older indexes.
Weather at Bramble Causeway closed the approach for 22 days during the period under review and no readings were lost.

### S-0512 -- Tamarisk Bluff

The logbook kept at Tamarisk Bluff runs to 75 pages and the earlier volumes are held off site.
The approach to Tamarisk Bluff crosses 16 field boundaries and the wayleave is held by the county.
Maintenance visits to S-0512 are scheduled quarterly and the twelfth of those was carried out as planned.
Calibration gear for S-0512 travels with the district van and is shared with 38 other sites.
Drainage work near Tamarisk Bluff was completed without interruption to the record.
The fence line at Tamarisk Bluff was rerun 19 metres to the east to clear the culvert.
Weather at Tamarisk Bluff closed the approach for 39 days during the period under review and no readings were lost.
On 2034-04-02 the district accepted revision 3 for Tamarisk Bluff and marked it settled.
S-0512 carries tier 3 on that revision and a load of 670.
Correspondence shows the tenancy at Tamarisk Bluff was renewed for a further 11 years.

### S-0513 -- Jasper Bight

Correspondence shows the tenancy at Jasper Bight was renewed for a further 21 years.
Signal strength at Jasper Bight has been marginal since the mast on the ridge was lowered.
Jasper Bight shares its power feed with the neighbouring pumping station and has its own cut-out.
The instrument housing at Jasper Bight is the original pattern and its door seal is checked each visit.
The access key for S-0513 is held at the district office and signed out per visit.
The district file for Jasper Bight shows revision 6 lodged on 2034-01-09.
For S-0513 the status is returned, the tier is 9, and the load is 295.
The logbook kept at Jasper Bight runs to 5 pages and the earlier volumes are held off site.
The enclosure at Jasper Bight was rebuilt in timber after the old fencing was taken by the river.

### S-0514 -- Vellum Down

Weather at Vellum Down closed the approach for 12 days during the period under review and no readings were lost.
The site plan for Vellum Down is the eighth revision and supersedes the sketch held in the district folder.
The load recorded for S-0514 is 879, on a return at tier 1.
That return for Vellum Down is revision 1, lodged 2034-10-28, and its status is settled.
Signal strength at Vellum Down has been marginal since the mast on the ridge was lowered.
A spare sensor head is kept at Vellum Down against the failure that took out the district in the previous cycle.
The enclosure at Vellum Down was rebuilt in timber after the old fencing was taken by the river.
Access to Vellum Down is by the service road from the south; the gate code was reissued after the second inspection.


## 7. Before you stop

`answer.json` in your working directory, one JSON object, the nine keys above. Do not
modify or delete `NOTICE.txt`. Work until the answer is complete, then stop.
