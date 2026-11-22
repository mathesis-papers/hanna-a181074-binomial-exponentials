# Hanna's OEIS A181074, Comments (2 October 2010): integrality and bivariate extensions

The note proves Hanna's conjecture in [OEIS A181074, Comments](https://oeis.org/A181074), dated 2 October 2010: the displayed formal exponential has integer coefficients in every degree. It also proves the corresponding conjectures for A181070, A181076, A181078, A181080, A181082 and A181084, establishes the stated integrality of A166894, and gives a theorem for arbitrary `U(t)` in `1 + t Z[[t]]` and three affine exponent families. A reflected-polynomial corollary treats `[t^k]P(t)^n` with exponent `r(dn-k)+s` for `deg(P)<=d` and `r,s>=1`. An entropy argument proves the A166895 limit formula recorded by V. Kotesovec on 20 November 2024.

Authors, in order: Haobo Ma (ChronoAI Pte Ltd, Singapore); Wenlin Zhang (National University of Singapore; ChronoAI Pte Ltd, Singapore). The note and accompanying original material are licensed under CC BY 4.0.

The coefficient congruences extend Moree's integral Witt transform (2003; inspected version 2005, Theorem 4(2)) and Gossow's Gauss-congruence framework (2024, Theorem 3.3 and Example 3.4). The one-variable exponential/Euler-product equivalence is credited to Du, Huang and Li (2005, Theorem 2), with the later Dold formulation of Byszewski, Graff and Ward (2021). The note reproves these antecedents and applies them to index-dependent powers; it makes no priority claim.

A bivariate corollary gives integer triangles A209424, A228899, A209196 and A228904, row sums A167007 and A184730, and column and central subsequences. The logarithmic arrays A209427 and A219207 satisfy Gauss congruences, and an entropy argument proves Kotesovec's stated maximizing-position limit for A219207. The lowered-power variants in the Comments of A228899 and A184730 have coefficients `31/2` at `x^4 y^2` and `85/2` at `x^4` after setting `y=1`, confirming their asserted nonintegrality.

## Files

- `note.tex`: self-contained LaTeX source with complete proofs and bibliography.
- `metadata.json`: scientific description, authors, license and statement coverage.
- `coverage.json`: exact posing locator and written, Lean-declaration and finite-check coverage.
- `verify.py`: standard-library Python 3 exact-arithmetic checker.
- `reference-data.json`: mathematical coefficients with OEIS and G. C. Greubel attribution.
- `checks.json`: deterministic expected checker output and exact finite ranges.
- `SHA256SUMS`: hashes of the other source-archive members.

## Build

Use Tectonic 0.17.0:

```sh
tectonic note.tex
```

Alternatively use a normal TeX installation:

```sh
pdflatex -interaction=nonstopmode -halt-on-error note.tex
pdflatex -interaction=nonstopmode -halt-on-error note.tex
```

The bibliography is included in the main source; BibTeX is not required. The source uses standard LaTeX packages `geometry`, `amsmath`, `amssymb`, `amsthm`, `booktabs`, `array`, `longtable`, `microtype` and `hyperref`. Tectonic may download its standard TeX resource bundle on first use.

## Reproduce the finite checks

No Python dependencies or network access are needed:

```sh
python3 verify.py --output reproduced-checks.json
cmp checks.json reproduced-checks.json
sha256sum -c SHA256SUMS
```

The checker compares exact rational exponential coefficients with an independently expanded integer Euler product. It matches A181074 against all 76 values of [Greubel's published table](https://oeis.org/A181074/b181074.txt), checks the other seven exponentials through degree 40, and compares the displayed companion logarithmic coefficients. It also tests coefficient lifts and powered congruences for rows 1–24 and columns 0–24, at primes 2, 3, 5, 7, 11 and 13, and two additional integer-series examples through degree 30. Nine reflected-polynomial cases are checked through degree 24, including negative coefficients and an enlarged degree bound. Another 495 exact rational checks test the elementary binomial probability bounds used in the limit proof. Complete ranges and counts appear in `checks.json`.

For each of the four bivariate triangles, a rational polynomial recurrence and an independently expanded monomial Euler product agree through row 12. The checker matches the saved OEIS prefixes, two row-sum sequences, a column and a central subsequence; antidiagonal sums also agree with the corresponding one-variable series. These are finite checks of the stated identities, distinct from the all-index written proofs.

## Mathematical coverage

The all-index integrality statements and the general theorem for `U` have written proofs in the note. The `result` declarations in the pinned [A181074](https://github.com/the-omega-institute/trureturing/blob/abb48f723fe221da235c625800ba0d2ca1755296/D5/S1/Recurrence/Algebraic/HannaA181074Integrality.lean), [A181070](https://github.com/the-omega-institute/trureturing/blob/abb48f723fe221da235c625800ba0d2ca1755296/D5/S1/Recurrence/Algebraic/HannaA181070Integrality.lean) and [A181080](https://github.com/the-omega-institute/trureturing/blob/abb48f723fe221da235c625800ba0d2ca1755296/D5/S1/Recurrence/Algebraic/HannaA181080Integrality.lean) Lean sources have the corresponding coefficient-integrality statements, each for its own sequence and all nonnegative coefficient indices. The reflected-polynomial extension, remaining specializations, logarithmic identities and A166895 limit are written proofs rather than conclusions of those three declarations. The Python program supplies finite exact checks, not an inference from a finite prefix to all coefficients or a computation of the limit.

The lowered-exponent series in the Comments of A181074, A181070 and A181080 have respective degree-six coefficients `1481/2`, `45/2` and `327/2`. These confirm the sources' nonintegrality assertions: integrality of those variants is not asserted in the sources. The linked A181072 random-walk formulas and A181073 digit-permutation statements are outside the note's coverage. The note also distinguishes the defining formulas from the cross-reference or display discrepancies in A181075, A181079 and A181081.

The bivariate Euler product, all four triangle statements, the row/column/subsequence identities and the A219207 maximizing-position limit have written proofs; none is the conclusion of the three linked `result` declarations.

Primary posing source: [OEIS A181074, Name and Comments](https://oeis.org/A181074), Paul D. Hanna, 2 October 2010, entry revision 9 dated 3 August 2024. The note's bibliography gives the companion entries and the standard Dold/Euler-product criterion. Third-party mathematical data retain their indicated source attribution and applicable source terms.
