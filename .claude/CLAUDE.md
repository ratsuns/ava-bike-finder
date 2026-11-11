# E-bike Rebate Finder — working notes

## Tests come first (Chris's rule for this project)
Use the `test-driven-development` skill (.claude/skills/test-driven-development) for every feature, fix or behavior
change: write the test, watch it fail for the right reason, then write the code. A bug gets a failing test that
reproduces it before the fix. Code written without a failing test first is rewritten test-first.

## The tests (all must pass; GitHub runs them on every push and Vercel publishes only after they pass)
    cd src && python -m bikespecs.test_rules && python -m videos.test_rules    # spec and video rules
    node src/tests/files_test.js .                                             # search-engine addresses, old-link forwarding
    node src/tests/serve.js "$PWD" 8765 &                                      # then, in a real browser:
    node src/tests/site_test.js   http://localhost:8765/                       #   every bike's window, real taps, no errors
    node src/tests/events_test.js http://localhost:8765/                       #   analytics events

Build after changing anything in src/: `cd src && SITE_DIR=.. python3 build2.py` (the tests check the built files).
