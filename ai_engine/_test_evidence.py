# -*- coding: utf-8 -*-
import asyncio
from code_evidence import build_code_evidence, invalidate_cache

invalidate_cache()
r = asyncio.run(build_code_evidence('https://github.com/W1413580489/chatbot-wrapper-test'))
print('ok:', r.get('ok'))
if r.get('ok'):
    print('repo:', r.get('repo'))
    print('file_count:', r.get('file_count'))
    print('key_files:', len(r.get('key_files', [])))
    for kf in r.get('key_files', [])[:3]:
        print(f'  [{kf["path"]}] content_len={len(kf["content"])}')
    print('evidence_text_len:', len(r.get('evidence_text', '')))
    print('--- first 800 chars ---')
    print(r.get('evidence_text', '')[:800])
else:
    print('error:', r.get('error'))
