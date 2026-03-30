import re
with open('test_api.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

match = re.search(r'<pre class="exception_value">(.*?)</pre>', text, re.DOTALL)
if match:
    print(f"EXCEPTION: {match.group(1).strip()}")

traceback_match = re.search(r'<div class="traceback">(.*?)</div>', text, re.DOTALL)
if traceback_match:
    print(f"TRACEBACK TEASER: {traceback_match.group(1)[:500]}")
