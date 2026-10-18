# Leads: loose ends and unused clues

Exact values. Link a backlog item or ledger id when you work on one.

## 8x32 base-60 grid (p40-53) — E0014, E0023, E0026, B05, B11

Two-character tokens, digits `0-9A-Za-x`, value = 60*first + second, giving 256 bytes spanning 0..255
(entropy 7.17 bits/byte). First bytes `cbe7a7ba61ed7eb7`. Not an RSA modulus: big-endian it is divisible
by 2, 5, 43 and 53. Get the bytes with `lp.keysources.Grid60Bytes()`.

## Page-56 hash — E0013, E0022

```
36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a8425893dc7500b464fda
f1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4
```
(one 128-hex-digit value; algorithm unconfirmed, usually assumed SHA-512 or BLAKE2b)

## Page-15 square — B10

```
3258 3222 3152 3038
3278 3299 3298 2838
3288 3294 3296 2472
4516 1206  708 1820
```
Exact rule (mortlach, 2016, reproduces every cell): take the primes at 0-based index
0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987 (the Fibonacci numbers; the (F+1)-th
prime, 1-based), B = 2, 3, 5, 7, 13, 23, 43, 79, 149, 263, 463, 829, 1481, 2593, 4507, 7817; then
C = |3301 - B| = 3299, 3298, 3296, 3294, 3288, 3278, 3258, 3222, 3152, 3038, 2838, 2472, 1820, 708,
1206, 4516, laid out in a spiral. Note the absolute value: 4516 and 1206 come from 7817 and 4507.
(Verified 2026-10-18; the earlier wording "3301 +- primes with Fibonacci prime indices" was imprecise.)

## Numbers printed in the unsolved pages — B11

- Numbered list 1-5 in section p33-39 (like the list in The Loss of Divinity).
- A lone numeral 7 in p8-14.
- Cuneiform numerals 1033 and 3301 in the p33-39 artwork.

## 2012 P.S. number (131 digits) — E0022

```
99554414790940424414351515490472769096534141749790794321708050837
x 104593961812606247801193807142122161186583731774511103180935025763
```
Both factors prime. The product is
`10412790658919985359827898739594318956404425106955675643739226952372682423852959081739834390370374474764863415203423499357108713631`.

## 2013 cookies — E0021, E0022

- 167 = `6941f707ff39d259ff71657a79cb6b54c184d2f0455810109c1a960860bde0e6`
- 761 = `7bc1e7805ccfa518920f0d94fc4e8f7dbd83287a03b337b89109cd2287befae5`

## Other

- Telnet prime list missing the primes 73..1223.
- Prime-length runs of spaces in the 2012, 2014 and 2015 signed messages.
- "9133" at the end of the 2014 onion-4 string.
- The never-visited 2012 Britannica onion.
- Other numbers used as keys so far (E0019, E0022): 3301, 1033, 761, 167, 1231507051321, 845145127,
  1595277641 (parable number), PGP key ids 7A35090F / 181F01E57A35090F.
