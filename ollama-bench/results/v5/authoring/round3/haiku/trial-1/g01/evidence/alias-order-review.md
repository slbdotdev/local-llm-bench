# Alias and order review

Alias expansion happens at the moment a record or change is encountered. It is
not a preprocessing pass that sorts or rewrites the input. The first raw record
`batch` establishes worker, even if its only change is void. A later `core`
record establishes platform. A later `jobs` record finds worker. The output
order is worker then platform.

Within worker, the first accepted key can be `task`, which becomes jobs. A later
accepted `lat` becomes latency. A still later `job` updates jobs. The output
order is jobs then latency. The alias spelling on the update does not create a
second entry and cannot move jobs after latency.

Within platform, a first accepted `compile` becomes build. A later accepted
`ERR` becomes error. The output order is build then error. A rejected `cfg`
between them does not reserve config's position. If a later accepted cfg
appears, it is appended after error.

The same canonical key in worker and platform is independent state. Position
maps must be per canonical source, not global. The same canonical source under
two raw aliases shares state. These are two different dimensions of identity.

The canonical source used to select a local key table is the emitted source
value, not the raw record spelling. Thus `core` and `platform` both use the
platform table and `batch` and `worker` both use worker. A raw source's case or
tab can prevent the source alias, which in turn prevents the local alias.
