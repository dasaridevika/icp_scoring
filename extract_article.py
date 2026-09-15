import re

with open(r'C:\Users\Telan\.gemini\antigravity\brain\89334601-5c7c-475f-97ea-ca7ad8eb231a\.system_generated\steps\2178\content.md', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('"body_html":"')
if idx != -1:
    end_idx = text.find('","truncated_body_text"', idx)
    if end_idx == -1:
        end_idx = text.find('","', idx + 13)
    raw = text[idx+13:end_idx]
    # replace escapes
    raw = raw.replace(r'\"', '"').replace(r'\n', '\n').replace(r'\t', '\t').replace(r'\/', '/')
    clean = re.sub(r'<[^>]+>', ' ', raw)
    clean = re.sub(r'[ \t]+', ' ', clean)
    with open('gtm_article_clean.txt', 'w', encoding='utf-8') as out:
        out.write(clean)
    print('Length of extracted text:', len(clean))
    print('Preview:\n', clean[:2500])
else:
    print('Not found')
