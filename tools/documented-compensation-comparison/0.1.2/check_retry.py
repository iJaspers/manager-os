# SPDX-License-Identifier: MIT
# Copyright (c) 2026 iJaspers. See LICENSE.
#!/usr/bin/env python3
import hashlib,json,pathlib,subprocess,sys,tempfile
tool=pathlib.Path(__file__).with_name('tool.py').resolve()
example=json.loads((tool.parent/'example.json').read_text())
with tempfile.TemporaryDirectory() as directory:
    root=pathlib.Path(directory);p=root/'input.json';data=json.dumps(example).encode();p.write_bytes(data);digest=hashlib.sha256(data).hexdigest()
    def run():return subprocess.run([sys.executable,str(tool),'--input',str(p)],capture_output=True,timeout=12,check=True).stdout
    first=run();assert json.loads(first)['status']=='COMPLETE_SCENARIOS_NOT_OFFER_VERIFICATION'
    for _ in range(5):assert run()==first
    assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
    p.write_text('{"offers":[');bad=run();assert json.loads(bad)['status']=='INVALID_INPUT';assert run()==bad
    p.write_bytes(data);assert run()==first;assert list(root.iterdir())==[p]
print(json.dumps({'passed':5,'failed':0,'checks':['5 repeated CLI runs byte-identical','input bytes unchanged','malformed input produces repeatable structured rejection','corrected input restores identical output','no extra files created in input directory'],'scope':'existing stateless CLI, no durable job queue/retry service implied'}))
