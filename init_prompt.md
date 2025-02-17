This is a shift scheduling problem, where nurses must be assigned to shifts while satisfying various constraints. Hard constraints must be satisfied, while soft constraints must be minimised for the best quality solution.

Each nurse has one specific contract, which sets limits on distribution and number of assignments in the scheduling period.
Each contract is shown in the format

Each nurse has one or more skills


# Constraints
## Hard Constraints
1. A nurse can work only one shift per day
2. Each shift must have the minimum required nurses per skill
3. These shift transitions are forbidden {insert here}
4. A shift requiring a specific skill must be assigned to a nurse with that skill


## Soft Constraints
1. Not meeting optimal coverage for shifts: (weight: 30)
2. violations of minimum/maximum consecutive assignments: (weight: 15/30)
3. Not respecting minimum/maximum rest periods: (weight: 30)
4. Scheduling a nurse for a undesired shift: (weight: 10)
5. If a nurse works a weekend shift, they must work both Saturday and Sunday: (weight: 30)
6. A must work within the contracted limits within the entire planning period: (weight: 20)
7. The total weekend shifts a nurse works should not exceed the contract limit: (weight: 30)