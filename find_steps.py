with open(r'C:\Users\Telan\.gemini\antigravity\brain\89334601-5c7c-475f-97ea-ca7ad8eb231a\.system_generated\steps\2178\content.md', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'Step \d', text)]
print('Matches:', len(matches))
for pos in matches:
    print('--- MATCH AT', pos, '---')
    print(text[pos:pos+1200])
