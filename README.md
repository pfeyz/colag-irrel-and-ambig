# Irrelevance and Ambiguity

How can (oracle) knowledge of the trigger status of an input sentence effect
learning?

The learner is inspecting a sentence S. Given this oracle knowledge, they know
that this sentence either

- contains a global trigger for Pi=0 or 1.
- is known to be ambiguous evidence wrt Pi. Some languages with Pi=0 license it,
  as do some with Pi=1.
- is irrelevant as evidence wrt Pi.

They use this knowledge to inform how they incorporate S into their
hypothesis-updating procedure.

## A note on parameter numbering

(because I keep mixing this up.)

The parameters are listed and numbered from left to right. SP, HIP, HCP etc are
parameter numbers 1, 2, 3 etc. In the integer grammar id representation of a
grammar, these are the would be the three most significant bits.

Subject position (SP) is parameter #1, which corresponds to the 13th bit in the
integer grammar id and binary bitstring.

- 0000000000000 has SP=0 (no question inversion)
- 1000000000000 (grammar id 4096) has parameter 1, SP, set to 1 (obligatory
question inversion).

Q-inversion (QInv) is parameter #13, which corresponds to the 1st bit in the
grammar bitstring.

- 0000000000000 has QInv off (subject initial)
- 0000000000001 (grammar id 1) has Qinv, parameter 13, set to 1 (subject final).
