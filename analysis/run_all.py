"""Run every offline analysis in dependency order (no GPU, no raw data needed)."""
import runpy, pathlib
here = pathlib.Path(__file__).parent
for s in ['policy_comparison.py', 'external_security.py', 'make_table_numbers.py', 'statistics.py', 'tables_6_7_8.py', 'make_figures.py']:
    print(f'\n=== {s} ==='); runpy.run_path(str(here / s), run_name='__main__')
