# Allocation keys

## Purpose

The parcel pipeline has several names for the same operational stage.  Component documents
use a human-readable stage label because those pages are read during deployment review.  The
allocation archive uses an opaque four-digit key because keys remain stable when prose labels
are revised.  These are two views of one stage, not two independent rosters.

## Inputs

Every stage document records a `deployment_ordinal` in its configuration table.  Every stage
module records a `REGION_OFFSET` constant.  An ordinal is local to this deployment plan; the
offset is local to the region adapter.  Neither input is an allocation decision, and neither
is copied into the manifest or the operations summary.

## Canonical join rule

The canonical join formula is: deployment_ordinal * region_offset.

The product is written as a four-digit decimal key.  To follow a stage from its human label
to the archive, read both inputs for that stage, perform the multiplication, preserve all
digits of the product, and search for the allocation record whose filename contains that key.
Do not pair records by directory order, by the order of modules, or by the order in which a
reviewer happened to open files.  A record without a computed key is not evidence about any
stage.

## Reading a decision

The allocation record is authoritative for the disposition of the key it names.  `reroute`
means that the stage needs the alternate parcel route; `retain` means that it stays on its
current route.  This page defines the join, not the disposition of any particular stage.

## Maintenance note

When a label changes, update the component page and its normal cross-references.  Do not add a
label-to-key table: the absence of such a table is intentional, since a table copied from one
deployment plan becomes stale when ordinals or region adapters change.  A later reviewer can
reproduce the join from the two inputs and the record name.
