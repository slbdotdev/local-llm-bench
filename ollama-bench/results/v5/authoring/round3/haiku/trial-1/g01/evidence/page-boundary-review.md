# Page-boundary review

The importer receives a sequence of pages but the public adapter receives the
records in their arrival order. A page boundary has no effect on source
identity, key identity, arithmetic, labels, or order. This review compares
three page partitions of the same logical sequence.

Partition A puts every record in one page. Partition B puts each record in its
own page. Partition C alternates page lengths one, three, two, one, and four.
After flattening, all three are the same ordered records and must produce equal
values. A caller that reduces each page independently can get a different order
or lose a source-only page when it merges page results.

The logical sequence begins with an empty `svc` page, then an accepted error
change, then an empty service page, then a `core` rejected-only page, then an
accepted platform build, then a service duplicate. The correct outer order is
service then platform even though service's first accepted entry follows the
platform source-only page. Service's error entry remains first when the later
duplicate arrives.

Page metadata is not part of the record schema and must not appear in output.
The adapter sees only record order. It must not read a page number, infer a
reset at an empty list, or sort records by source to make pages mergeable.

The same ownership rule applies across pages: output labels are new lists and
input pages remain unchanged. A streaming caller can retain and resend a page
after a transformation without observing mutations.
