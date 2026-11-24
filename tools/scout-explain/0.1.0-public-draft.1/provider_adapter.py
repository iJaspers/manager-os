"""Provider-neutral ingestion: host supplies JSON results; this module makes no network calls."""
import json
from pathlib import Path
from scout import Evidence, rank, explain, save_checkpoint
MAX_RESULTS=100
MAX_FIELD=4000

def ingest(payload):
    if not isinstance(payload,dict) or not isinstance(payload.get('results'),list): raise ValueError('expected results array')
    if len(payload['results'])>MAX_RESULTS: raise ValueError('too many results')
    records=[]
    for row in payload['results']:
        if not isinstance(row,dict): raise ValueError('invalid result')
        fields=[row.get(k,'') for k in ('title','url','excerpt')]
        if not all(isinstance(v,str) and len(v)<=MAX_FIELD for v in fields): raise ValueError('invalid field')
        records.append(Evidence(*fields,fetched=False,official=False))
    return records

def report(payload,goal,level='practical',checkpoint=None):
    if not isinstance(goal,str) or not goal.strip() or len(goal)>500: raise ValueError('invalid goal')
    ranked=rank(ingest(payload),goal)
    if checkpoint is not None: save_checkpoint(checkpoint,ranked)
    return '\n\n'.join(explain(item,level) for item in ranked)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('input',type=Path)
    p.add_argument('--goal',required=True)
    p.add_argument('--level',choices=['simple','practical','technical'],default='practical')
    p.add_argument('--checkpoint',type=Path)
    args=p.parse_args()
    print(report(json.loads(args.input.read_text(encoding='utf-8')),args.goal,args.level,args.checkpoint))
