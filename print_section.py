with open(r'C:\Users\Telan\.gemini\antigravity\brain\89334601-5c7c-475f-97ea-ca7ad8eb231a\.system_generated\steps\2178\content.md', 'r', encoding='utf-8') as f:
    text = f.read()

import re
sub = text[125000:152000]
clean = re.sub(r'<[^>]+>', ' ', sub)
clean = re.sub(r'\\u2019', "'", clean)
clean = re.sub(r'\\u2014', "—", clean)
clean = re.sub(r'\s+', ' ', clean)
print(clean)
