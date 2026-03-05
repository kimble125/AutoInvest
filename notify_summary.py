"""ntfy.sh 알림용 브리핑 요약 추출 스크립트.

GitHub Actions 워크플로우의 Send notification 스텝에서
브리핑 .md 파일에서 주요 지표를 추출해 stdout으로 출력합니다.
"""
import glob
import sys

KEYWORDS = ['KOSPI', 'S&P', 'NASDAQ', 'USD/KRW', 'Bitcoin', 'VIX']

files = sorted(glob.glob('vault/50_Archive/Daily/Economy/**/*.md', recursive=True))
if not files:
    print('브리핑 생성 완료')
    sys.exit(0)

with open(files[-1], encoding='utf-8') as f:
    lines = f.readlines()

out = []
for line in lines:
    line = line.strip()
    if '|' in line and any(k in line for k in KEYWORDS):
        cells = [c.strip() for c in line.split('|') if c.strip()]
        if len(cells) >= 3:
            out.append(f'{cells[0]}: {cells[1]} ({cells[2]})')
    if len(out) >= 6:
        break

print('\n'.join(out) if out else '브리핑 생성 완료')
