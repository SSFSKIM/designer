"""Aggregation must match the sealed best rule, not select failed or missing starts."""
import copy
import unittest
import inactive_complete as complete


def starts():
    rows = []
    for i in range(16):
        ls = dict(converged=True, weightedSquaredError=16-i, maximumCodes=20+i,
                  zeroFloorBracketCodes=None)
        mm = dict(converged=True, weightedSquaredError=20+i, maximumCodes=16-i,
                  zeroFloorBracketCodes=None)
        rows.append(dict(startIndex=i, leastSquares=ls, minimax=mm))
    return rows


class MergeTests(unittest.TestCase):
    def test_original_index_tie_break_and_forward_feasibility(self):
        rows = starts()
        rows[15]['leastSquares']['converged'] = False
        rows[15]['minimax']['converged'] = False
        rows[13]['leastSquares']['weightedSquaredError'] = 2
        merged = complete.merge(list(reversed(rows)), 'M0', 'device')
        self.assertEqual(merged['leastSquares']['startIndex'], 13)
        self.assertEqual(merged['minimax']['startIndex'], 14)
        self.assertEqual([r['startIndex'] for r in merged['starts']], list(range(16)))

    def test_no_completed_converged_result_means_no_selected_candidate(self):
        rows = starts()
        for row in rows:
            row['leastSquares']['converged'] = False
            row['minimax']['converged'] = False
        result = complete.merge(rows, 'M0', 'device')
        self.assertIsNone(result['leastSquares'])
        self.assertIsNone(result['minimax'])
        rows[0]['minimax']['maximumCodes'] = 1e-10
        rows[0]['minimax']['zeroFloorBracketCodes'] = [0, 1e-10]
        result = complete.merge(rows, 'M0', 'device')
        self.assertEqual(result['minimax']['startIndex'], 0)
        self.assertFalse(result['minimax']['converged'])

    def test_missing_or_duplicated_original_start_refused(self):
        for rows in (starts()[:-1], starts()+[starts()[0]], starts()[:-1]+[starts()[0]]):
            with self.assertRaises(ValueError):
                complete.merge(rows, 'M0', 'device')


if __name__ == '__main__':
    unittest.main()
