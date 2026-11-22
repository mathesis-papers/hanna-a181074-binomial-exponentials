import argparse
from fractions import Fraction
import json
from math import comb, gcd, isqrt
from pathlib import Path


def prime_numbers(bound):
    return [candidate for candidate in range(2, bound + 1)
            if all(candidate % divisor for divisor in range(2, isqrt(candidate) + 1))]


def valuation(number, prime):
    exponent = 0
    while number % prime == 0:
        number //= prime
        exponent += 1
    return exponent


def mobius(number):
    result = 1
    divisor = 2
    while divisor * divisor <= number:
        if number % divisor == 0:
            number //= divisor
            result = -result
            if number % divisor == 0:
                return 0
        divisor += 1
    return -result if number > 1 else result


def base_coefficient(base, row, column):
    if base == 'weak':
        return comb(row + column - 1, column)
    return comb(row, column) if column <= row else 0


def power_exponent(kind, row, column):
    return {'k+1': column + 1, 'n': row, 'n+k-1': row + column - 1,
            'n+k': row + column, 'n+k+1': row + column + 1, 'n-k+1': row - column + 1,
            'k': column, 'n-k': row - column}[kind]


def ghost_coefficients(base, kind, degree):
    ghosts = [Fraction(0)] * (degree + 1)
    for total in range(1, degree + 1):
        for row in range(1, total + 1):
            column = total - row
            if base == 'ordinary' and column > row:
                continue
            value = base_coefficient(base, row, column) ** power_exponent(kind, row, column)
            ghosts[total] += Fraction(total * value, row)
    return ghosts


def exponential_coefficients(ghosts):
    coefficients = [Fraction(1)]
    for total in range(1, len(ghosts)):
        coefficients.append(sum((ghosts[index] * coefficients[total - index]
                                 for index in range(1, total + 1)), Fraction(0)) / total)
    return coefficients


def euler_product_coefficients(ghosts):
    degree = len(ghosts) - 1
    exponents = [0] * (degree + 1)
    coefficients = [1] + [0] * degree
    for total in range(1, degree + 1):
        numerator = sum(mobius(divisor) * ghosts[total // divisor]
                        for divisor in range(1, total + 1) if total % divisor == 0)
        exponent = numerator / total
        assert exponent.denominator == 1, ('Euler exponent', total, exponent)
        exponents[total] = int(exponent)
        factors = [1]
        for index in range(1, degree // total + 1):
            numerator = factors[-1] * (int(exponent) + index - 1)
            assert numerator % index == 0
            factors.append(numerator // index)
        updated = [0] * (degree + 1)
        for index, coefficient in enumerate(coefficients):
            for multiple, factor in enumerate(factors):
                target = index + multiple * total
                if target > degree:
                    break
                updated[target] += coefficient * factor
        coefficients = updated
    return coefficients, exponents


def check_dold(ghosts):
    count = 0
    degree = len(ghosts) - 1
    for prime in prime_numbers(degree):
        for index in range(1, degree // prime + 1):
            difference = ghosts[prime * index] - ghosts[index]
            assert difference.denominator == 1
            assert int(difference) % prime ** (valuation(index, prime) + 1) == 0
            count += 1
    return count


def check_local_congruences():
    lifts = 0
    power_checks = 0
    divisibility_checks = 0
    for base in ['weak', 'ordinary']:
        kinds = ['k+1', 'n', 'n+k-1', 'n+k', 'n+k+1']
        if base == 'ordinary':
            kinds.append('n-k+1')
        for row in range(1, 25):
            for column in range(25):
                if base == 'ordinary' and column > row:
                    continue
                value = base_coefficient(base, row, column)
                assert column * value % row == 0
                divisibility_checks += 1
                for prime in prime_numbers(13):
                    modulus = prime ** (valuation(row, prime) + 1)
                    lifted = base_coefficient(base, prime * row, prime * column)
                    assert (lifted - value) % modulus == 0
                    lifts += 1
                    for kind in kinds:
                        exponent = power_exponent(kind, row, column)
                        lifted_exponent = power_exponent(kind, prime * row, prime * column)
                        assert (pow(lifted, lifted_exponent, modulus)
                                - pow(value, exponent, modulus)) % modulus == 0
                        power_checks += 1
    return {'row_range': [1, 24], 'column_range': [0, 24], 'primes': prime_numbers(13),
            'base_divisibility_checks': divisibility_checks,
            'coefficient_lifts': lifts, 'powered_congruences': power_checks}


def check_general_series():
    results = []
    degree = 30
    for polynomial in [[1, 1, 1], [1, -2, 0, 1]]:
        powers = [[1] + [0] * degree]
        for row in range(1, degree + 1):
            powers.append([sum(polynomial[index] * powers[-1][column - index]
                               for index in range(min(column, len(polynomial) - 1) + 1))
                           for column in range(degree + 1)])
        for kind in ['k+1', 'n', 'n+k-1', 'n+k', 'n+k+1']:
            ghosts = [Fraction(0)] * (degree + 1)
            for total in range(1, degree + 1):
                ghosts[total] = sum((Fraction(total * powers[row][total - row]
                                              ** power_exponent(kind, row, total - row), row)
                                    for row in range(1, total + 1)), Fraction(0))
            coefficients = exponential_coefficients(ghosts)
            assert all(value.denominator == 1 for value in ghosts + coefficients)
            product, exponents = euler_product_coefficients(ghosts)
            assert product == coefficients
            results.append({'U_coefficients': polynomial, 'exponent': kind,
                            'degree': degree, 'dold_checks': check_dold(ghosts)})
    return results


def check_reflected_polynomials():
    degree = 24
    results = []
    for polynomial, degree_bound in [([1, 1, 1], 2), ([1, -2, 0, 1], 3), ([1, 2], 3)]:
        powers = [[1] + [0] * degree]
        for row in range(1, degree + 1):
            powers.append([sum(polynomial[index] * powers[-1][column - index]
                               for index in range(min(column, len(polynomial) - 1) + 1))
                           for column in range(degree + 1)])
        for slope, constant in [(1, 1), (2, 1), (1, 2)]:
            ghosts = [Fraction(0)] * (degree + 1)
            for total in range(1, degree + 1):
                for row in range(1, total + 1):
                    column = total - row
                    if column <= degree_bound * row:
                        exponent = slope * (degree_bound * row - column) + constant
                        ghosts[total] += Fraction(total * powers[row][column] ** exponent, row)
            coefficients = exponential_coefficients(ghosts)
            assert all(value.denominator == 1 for value in ghosts + coefficients)
            product, exponents = euler_product_coefficients(ghosts)
            assert product == coefficients
            results.append({'P_coefficients': polynomial, 'degree_bound': degree_bound,
                            'slope': slope, 'constant': constant, 'degree': degree,
                            'integer_euler_exponents': degree, 'dold_checks': check_dold(ghosts)})
    return results


def check_entropy_bounds():
    count = 0
    for size in range(1, 31):
        for chosen in range(size + 1):
            probability = Fraction(comb(size, chosen) * chosen ** chosen
                                   * (size - chosen) ** (size - chosen), size ** size)
            assert Fraction(1, size + 1) <= probability <= 1
            count += 1
    return {'binomial_size_range': [1, 30], 'exact_probability_bounds': count,
            'coverage': 'finite checks of the binomial inequalities used in the written limit proof'}


def triangle_array(kind, row, column):
    if kind == 'power-n':
        return comb(row, column) ** row
    if kind == 'power-k+1':
        return comb(row, column) ** (column + 1)
    if kind == 'square':
        return comb(row * row, row * column)
    if kind == 'mixed':
        return comb(row * column, column * column)
    if kind == 'lowered':
        return comb(row, column) ** column
    raise ValueError(kind)


def triangle_exponential(kind, degree):
    rows = [[Fraction(1)]]
    for row in range(1, degree + 1):
        values = [Fraction(0)] * (row + 1)
        for size in range(1, row + 1):
            for column in range(size + 1):
                value = triangle_array(kind, size, column)
                for tail, coefficient in enumerate(rows[row - size]):
                    values[column + tail] += value * coefficient
        rows.append([value / row for value in values])
    return rows


def triangle_product(kind, degree):
    coefficients = {(0, 0): 1}
    count = 0
    for row in range(1, degree + 1):
        for column in range(row + 1):
            numerator = sum(mobius(divisor) * triangle_array(kind, row // divisor, column // divisor)
                            for divisor in range(1, gcd(row, column) + 1)
                            if row % divisor == 0 and column % divisor == 0)
            assert numerator % row == 0
            exponent = numerator // row
            count += 1
            factors = [1]
            for multiple in range(1, degree // row + 1):
                numerator = factors[-1] * (exponent + multiple - 1)
                assert numerator % multiple == 0
                factors.append(numerator // multiple)
            updated = {}
            for (total, chosen), coefficient in coefficients.items():
                for multiple, factor in enumerate(factors):
                    target = (total + multiple * row, chosen + multiple * column)
                    if target[0] > degree:
                        break
                    updated[target] = updated.get(target, 0) + coefficient * factor
            coefficients = updated
    return [[coefficients.get((row, column), 0) for column in range(row + 1)]
            for row in range(degree + 1)], count


def check_bivariate(references):
    degree = 12
    kinds = {'A209424': 'power-n', 'A228899': 'power-k+1',
             'A209196': 'square', 'A228904': 'mixed'}
    results = []
    triangles = {}
    congruences = 0
    divisibility = 0
    for sequence, kind in kinds.items():
        rows = triangle_exponential(kind, degree)
        product, count = triangle_product(kind, degree)
        assert rows == product
        assert all(value.denominator == 1 for row in rows for value in row)
        flattened = [value for row in rows for value in row]
        expected = references['bivariate_sequences'][sequence]['values']
        assert flattened[:len(expected)] == [int(value) for value in expected]
        results.append({'sequence': sequence, 'row_range': [0, degree],
                        'integer_euler_exponents': count, 'published_prefix_matches': len(expected)})
        triangles[sequence] = rows
        for row in range(1, degree + 1):
            for column in range(row + 1):
                value = triangle_array(kind, row, column)
                assert column * value % row == 0
                divisibility += 1
                for prime in [2, 3, 5, 7]:
                    modulus = prime ** (valuation(row, prime) + 1)
                    assert (triangle_array(kind, prime * row, prime * column) - value) % modulus == 0
                    congruences += 1
    specialized = {}
    values = {'A167007': [sum(row) for row in triangles['A209424']],
              'A184730': [sum(row) for row in triangles['A228899']],
              'A209425': [row[2] for row in triangles['A209424'][2:]],
              'A209426': [triangles['A209424'][2 * index][index]
                           for index in range(degree // 2 + 1)]}
    for sequence, actual in values.items():
        expected = references['bivariate_sequences'][sequence]['values']
        count = min(len(actual), len(expected))
        assert actual[:count] == [int(value) for value in expected[:count]]
        specialized[sequence] = count
    for triangle, sequence, kind in [('A209424', 'A166894', 'n'),
                                     ('A228899', 'A181070', 'k+1')]:
        coefficients = exponential_coefficients(ghost_coefficients('ordinary', kind, degree))
        diagonal = [sum(triangles[triangle][row][total - row]
                        for row in range(total + 1) if 0 <= total - row <= row)
                    for total in range(degree + 1)]
        assert diagonal == coefficients
    lowered = triangle_exponential('lowered', 6)
    assert lowered[4][2] == Fraction(31, 2)
    assert sum(lowered[4]) == Fraction(85, 2)
    assert all(value.denominator == 1 for row in lowered[:4] for value in row)
    return {'arithmetic': 'independent exact rational recurrence and integer monomial Euler product',
            'triangles': results, 'specialization_prefix_matches': specialized,
            'array_divisibility_checks': divisibility, 'array_prime_power_congruences': congruences,
            'array_primes': [2, 3, 5, 7],
            'antidiagonal_matches_each': degree + 1,
            'lowered_power_coefficient_x4y2': str(lowered[4][2]),
            'lowered_power_row_sum_x4': str(sum(lowered[4]))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    arguments = parser.parse_args()
    reference_path = Path(__file__).with_name('reference-data.json')
    references = json.loads(reference_path.read_text())
    definitions = {'A181074': ('weak', 'k+1'), 'A181070': ('ordinary', 'k+1'),
                   'A181076': ('weak', 'n'), 'A181078': ('weak', 'n+k-1'),
                   'A181080': ('ordinary', 'n-k+1'), 'A181082': ('ordinary', 'n+k'),
                   'A166894': ('ordinary', 'n'), 'A181084': ('ordinary', 'n+k+1')}
    logs = {'A181074': 'A181075', 'A181070': 'A181071', 'A181076': 'A181077',
            'A181078': 'A181079', 'A181080': 'A181081', 'A181082': 'A181083',
            'A166894': 'A166895', 'A181084': 'A181085'}
    results = []
    main_coefficients = None
    for sequence, (base, kind) in definitions.items():
        degree = 75 if sequence == 'A181074' else 40
        ghosts = ghost_coefficients(base, kind, degree)
        coefficients = exponential_coefficients(ghosts)
        assert all(value.denominator == 1 for value in ghosts + coefficients)
        product, exponents = euler_product_coefficients(ghosts)
        assert product == coefficients
        reference = references['sequences'][sequence]
        count = min(len(reference['values']), degree + 1)
        assert coefficients[:count] == [int(value) for value in reference['values'][:count]]
        log_count = 0
        if sequence in logs:
            log_reference = references['sequences'][logs[sequence]]
            log_count = min(len(log_reference['values']), degree)
            assert ghosts[1:log_count + 1] == [int(value) for value in log_reference['values'][:log_count]]
        results.append({'sequence': sequence, 'degree': degree, 'coefficient_match_count': count,
                        'logarithmic_match_count': log_count, 'integer_euler_exponents': degree,
                        'dold_congruences': check_dold(ghosts)})
        if sequence == 'A181074':
            main_coefficients = [int(value) for value in coefficients[:11]]
    counterexamples = []
    for base, kind in [('weak', 'k'), ('ordinary', 'k'), ('ordinary', 'n-k')]:
        coefficients = exponential_coefficients(ghost_coefficients(base, kind, 8))
        first = next(index for index, value in enumerate(coefficients) if value.denominator != 1)
        counterexamples.append({'base': base, 'exponent': kind, 'first_noninteger_degree': first,
                                'coefficient': str(coefficients[first]),
                                'prefix': [str(value) for value in coefficients[:first + 1]]})
    report = {'status': 'pass', 'arithmetic': 'exact integers and rational numbers',
              'coverage': 'finite coefficient, Euler-product and congruence checks',
              'A181074_initial_coefficients': main_coefficients, 'sequences': results,
              'local_congruences': check_local_congruences(),
              'general_series_examples': check_general_series(),
              'reflected_polynomial_examples': check_reflected_polynomials(),
              'entropy_bounds': check_entropy_bounds(), 'counterexamples': counterexamples,
              'bivariate': check_bivariate(references)}
    content = json.dumps(report, indent=2) + '\n'
    if arguments.output:
        arguments.output.write_text(content)
    print(content, end='')


if __name__ == '__main__':
    main()
