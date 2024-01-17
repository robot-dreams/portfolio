import os
import shutil
import subprocess

TMPFILE = 'out.png'

files = os.listdir()
for file in files:
    if file.startswith('old_') or not file.endswith('.png'):
        continue
    shutil.copyfile(file, 'old_' + file)
    result = subprocess.run(['convert', file, '-print', '%w', '/dev/null'], capture_output=True)
    if result.returncode != 0:
        raise Exception(result.stderr)

    size = int(result.stdout)
    result = subprocess.run(['convert', file, '-extent', f'{size}x{size}', '(', '+clone', '-alpha', 'transparent', '-draw', f'circle {size/2},{size/2} {size/2},0', ')', '-compose', 'copyopacity', '-composite', TMPFILE])
    if result.returncode != 0:
        raise Exception(result.stderr)

    os.rename(TMPFILE, file)
