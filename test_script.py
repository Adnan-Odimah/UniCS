import subprocess
import json
parameters = ["CONCURRENT_PER_PROXY", "base_delay"]
# currently 5 | 1.5 | base * (2 ** attempt)
"""
    "attempt2": {
        "CONCURRENT_PER_PROXY": 10,
        "base_delay": 1.5,
    },
"""

values = {
    "attempt1": {
        "CONCURRENT_PER_PROXY": 5,
        "base_delay": 1.5,
    },
    "attempt2": {
        "CONCURRENT_PER_PROXY": 10,
        "base_delay": 1.5,
    },
    "attempt3": {
        "CONCURRENT_PER_PROXY": 10,
        "base_delay": 1,
    },
    "attempt4": {
        "CONCURRENT_PER_PROXY": 25,
        "base_delay": 1,
    },
}

results = []
for i, attempt in enumerate(values):
    # run with parameters, and save the output
    result = subprocess.run(["python3", "webscraper/url_gen.py", str(values[attempt]["CONCURRENT_PER_PROXY"]), str(values[attempt]["base_delay"])])
    results.append({"attempt": i, "result": result.stdout})


with open("results.json", "w") as f:
    json.dump(results, f)
