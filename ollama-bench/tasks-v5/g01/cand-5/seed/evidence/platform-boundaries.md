# Platform boundary cases

Platform records arrive under `core`, `platform`, or ordinary-space variants.
They converge only after exact source alias lookup. `CORE` and `platform\t`
remain distinct. This is why source normalization cannot use casefold or broad
strip as a convenience.

The platform local table maps compile and compilation to build. Both aliases
are applied after a global key lookup. A raw key ` ERR ` becomes error through
the global table; it is not considered a platform-specific name. A raw key
`compile` is unchanged by global lookup and then becomes build. An unknown key
is retained after key edge-space removal and casefold.

The source can report a zero-valued add for build, a negative adjust for build,
and a negative remove for latency. All three are accepted and counted. A remove
of -7 contributes +7. An ignore of `cfg` with a label is not a zero-valued
accepted event: it is rejected, so it has no key, occurrence, amount, or label
effect.

Platform labels are merged per canonical key. A build label seen on a compile
change is the same label state as a label seen on a later build change. A
platform latency label is separate even if the raw label string matches. The
source and key scopes must not be collapsed into one global accumulator.

When a later platform alias record contains a new key, that key is appended
after keys accepted in the first platform record. It is not inserted according
to canonical spelling or contribution size. An empty alias record preserves
the bucket and leaves existing state untouched.
