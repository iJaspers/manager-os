#!/usr/bin/env python3
"""BOB-089: Offline read-only source-linked handoff review.

Validates proposals and evidence, does not modify tasks, ownership or records.
"""
import sys,json,re,os,stat
from datetime import datetime
VALID_STATES={'UNKNOWN','HOLD','DRAFT','REVIEW','DONE','CONSUMED','DEFERRED','ABANDONED'}

def evaluate(d):
    issues=[]
    if not isinstance(d,dict):return {'bob_id':'BOB-089','status':'HOLD','issues':['NOT_AN_OBJECT']}
    allowed={'owner','source_task','source_observed_at','proposal','evidence_refs','source_state','new_evidence_changes_answer','claim_resolved','owner_approval_evidence','performed_write','automated_send'}
    if set(d)-allowed:issues.append('UNKNOWN_FIELD')
    for field in ('new_evidence_changes_answer','claim_resolved','owner_approval_evidence','performed_write','automated_send'):
        if field in d and type(d[field]) is not bool:issues.append('INVALID_'+field.upper())
    for field in ('owner','source_task','source_observed_at','proposal'):
        if not isinstance(d.get(field),str) or not d[field].strip() or len(d[field])>4096 or any(ord(c)<32 and c not in '\n\t' for c in d[field]):issues.append('MISSING_OR_INVALID_'+field.upper())
    try:
        observed=datetime.fromisoformat(d.get('source_observed_at','').replace('Z','+00:00'))
        if observed.tzinfo is None:raise ValueError()
    except (AttributeError,TypeError,ValueError):issues.append('INVALID_OBSERVATION_TIME')
    if isinstance(d.get('source_task'),str) and d['source_task'].startswith('http') and not re.match(r'^https://',d['source_task']):
        issues.append('INSECURE_SOURCE_LINK')
    evidence=d.get('evidence_refs')
    if not isinstance(evidence,list) or not evidence or len(evidence)>50 or any(not isinstance(x,str) or not x.strip() or len(x)>2048 or any(ord(c)<32 for c in x) for x in evidence):
        issues.append('MISSING_VERIFIABLE_EVIDENCE_REF')
    elif len(set(evidence))<len(evidence):issues.append('DUPLICATE_EVIDENCE_REF')
    state=d.get('source_state')
    if not isinstance(state, str) or state not in VALID_STATES:issues.append('UNKNOWN_SOURCE_STATE')
    if state in ('DONE','CONSUMED','DEFERRED','ABANDONED') and d.get('new_evidence_changes_answer') is not True:
        issues.append('REOPENING_STOPPED_SOURCE_WITHOUT_NEW_EVIDENCE')
    if d.get('claim_resolved') is True and d.get('owner_approval_evidence') is not True:
        issues.append('UNSUPPORTED_RESOLUTION_CLAIM')
    if d.get('performed_write') is True:issues.append('SOURCE_OR_EXTERNAL_WRITE_NOT_ALLOWED')
    if d.get('automated_send') is True:issues.append('AUTOMATED_EXTERNAL_ACTION_NOT_ALLOWED')
    if isinstance(d.get('owner'),str) and d['owner'].strip().upper()=='BOB':issues.append('BOB_CANNOT_BE_SOURCE_OWNER')
    if d.get('source_state')=='UNKNOWN' and d.get('claim_resolved') is True:
        issues.append('UNKNOWN_NOT_RESOLVED')
    return {'bob_id':'BOB-089','status':'HOLD' if issues else 'REVIEWABLE_HANDOFF_PROPOSAL',
            'issues':sorted(set(issues)),'owner':d.get('owner') if isinstance(d.get('owner'),str) and len(d['owner'])<=4096 else None, 'source_task':d.get('source_task') if isinstance(d.get('source_task'),str) and len(d['source_task'])<=4096 else None,
            'limitations':['Syntactic/evidence-link gate; does not verify linked source contents','Handoff is not source-owner approval or resolution']}

def main():
    if len(sys.argv)!=2:raise SystemExit('usage: python handoff.py input.json')
    try:
        fd=os.open(sys.argv[1],os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
        with os.fdopen(fd,'rb') as f:
            info=os.fstat(f.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size>65536:raise ValueError()
            data=f.read(65537)
        if len(data)>65536:raise ValueError()
        def unique(pairs):
            result={}
            for key,value in pairs:
                if key in result:raise ValueError()
                result[key]=value
            return result
        d=json.loads(data.decode('utf-8'),object_pairs_hook=unique)
        r=evaluate(d)
    except (OSError,ValueError,TypeError,RecursionError):r={'bob_id':'BOB-089','status':'HOLD','issues':['INVALID_INPUT']}
    print(json.dumps(r,indent=2,sort_keys=True))
    return 2 if r['status']=='HOLD' else 0
if __name__=='__main__':sys.exit(main())
