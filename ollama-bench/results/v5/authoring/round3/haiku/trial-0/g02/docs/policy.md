# Policy precedence

Rules are scoped to a package, a platform, and a half-open release window. A wildcard platform matches every platform. With several active rules, the greatest revision wins. If revisions tie, an exact platform rule beats a wildcard. If nothing matches, the default is allow. A rule that is outside its window has no effect.

The policy archive contains old decisions, but the current JSON snapshot is the source consumed by the command. The history documents explain why a revision exists; they do not change the precedence rule. A deny anywhere in the transitive closure makes the complete plan empty because a partial release is not deployable.

Examples: an exact `windows` allow at revision 6 beats a wildcard deny at revision 3. A wildcard allow at revision 8 beats an exact Linux deny at revision 7. The end date is not included.
