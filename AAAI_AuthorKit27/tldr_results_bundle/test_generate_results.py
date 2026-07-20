import json
import tempfile
import unittest
from pathlib import Path

try:
    from . import generate_results
except ImportError:  # Support direct execution from this directory.
    import generate_results


class ResultsGenerationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data_path = Path(__file__).with_name("tldr_results.json")
        cls.data = json.loads(data_path.read_text(encoding="utf-8"))

    def test_summary_matches_key_claims(self):
        summary = generate_results.build_summary(self.data)

        self.assertEqual(len(summary["retrieval"]), 8)
        self.assertEqual(sum(row["gain"] > 0 for row in summary["retrieval"]), 7)
        self.assertAlmostEqual(summary["macro_gain"]["ZH+EN"], 2.825)
        self.assertAlmostEqual(summary["macro_gain"]["ZH-only"], 8.95)

        gains = {(row["regime"], row["dataset"]): row["gain"]
                 for row in summary["retrieval"]}
        self.assertAlmostEqual(gains[("ZH-only", "ContextASR-ZH")], 12.0)
        self.assertAlmostEqual(gains[("ZH-only", "ContextASR-EN")], 7.4)
        self.assertAlmostEqual(gains[("ZH-only", "AISpeechMeeting")], 16.5)
        self.assertAlmostEqual(gains[("ZH-only", "AISHELL1-NE")], -0.1)

    def test_tldr_has_lowest_retrieval_based_wer(self):
        summary = generate_results.build_summary(self.data)

        for row in summary["decoding"]:
            self.assertLess(row["tldr_wer"], row["prior_wer"])
            self.assertGreaterEqual(row["vs_prior_reduction"], 1.4)
            self.assertLessEqual(row["vs_prior_reduction"], 10.4)

    def test_invalid_duplicate_is_rejected(self):
        invalid = json.loads(json.dumps(self.data))
        invalid["retrieval"].append(dict(invalid["retrieval"][0]))

        with self.assertRaisesRegex(ValueError, "duplicate"):
            generate_results.build_summary(invalid)

    def test_all_outputs_are_generated(self):
        with tempfile.TemporaryDirectory() as directory:
            outputs = generate_results.generate_all(
                Path(__file__).with_name("tldr_results.json"), Path(directory)
            )

            self.assertEqual({path.suffix for path in outputs}, {".tex", ".pdf"})
            self.assertTrue(all(path.stat().st_size > 0 for path in outputs))


if __name__ == "__main__":
    unittest.main()
