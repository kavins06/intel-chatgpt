#!/usr/bin/env python3
"""Check an intel evidence record's structure, not its substantive truth."""
import argparse
import datetime
import json
import math
import sys

KINDS = {'fact','attributed_claim','inference','assumption','estimate','forecast','scenario','recommendation'}


def nonempty(value):
    return isinstance(value,str) and bool(value.strip())


def check(data):
    errors, warnings, scores = [], [], []
    if not isinstance(data,dict):
        return {'valid_structure':False,'errors':['Root must be a JSON object.'],'warnings':[], 'scope':'Structure only; no source entailment or factual verification.'}
    if not nonempty(data.get('question')):
        errors.append('Missing question.')
    try:
        datetime.date.fromisoformat(data.get('as_of',''))
    except (TypeError, ValueError):
        errors.append('as_of must be a valid YYYY-MM-DD date.')
    collections = {}
    for name in ['sources','claims','forecasts']:
        value = data.get(name,[])
        if not isinstance(value,list) or any(not isinstance(x,dict) for x in value):
            errors.append(f'{name} must be an array of objects.')
            value=[]
        collections[name]=value
    sources,claims,forecasts = [collections[n] for n in ['sources','claims','forecasts']]
    ids = {}
    for name, items in collections.items():
        seen=set()
        for item in items:
            identifier=item.get('id')
            if not nonempty(identifier):
                errors.append(f'{name}: missing string ID.')
            elif identifier in seen:
                errors.append(f'{name}: duplicate ID {identifier}.')
            else:
                seen.add(identifier)
        ids[name]=seen
    source_map={s['id']:s for s in sources if nonempty(s.get('id'))}
    for source in sources:
        label=source.get('id','source')
        for field in ['title','locator','family']:
            if not nonempty(source.get(field)):
                errors.append(f'{label}: missing source {field}.')
    graph={}
    for claim in claims:
        label=claim.get('id','claim')
        if not nonempty(claim.get('text')):
            errors.append(f'{label}: missing claim text.')
        kind=claim.get('kind')
        if not isinstance(kind,str) or kind not in KINDS:
            errors.append(f'{label}: invalid claim kind.')
        evidence=claim.get('evidence',[])
        if not isinstance(evidence,list) or any(not isinstance(x,dict) for x in evidence):
            errors.append(f'{label}: evidence must be an array of objects.')
            evidence=[]
        families=set()
        for ev in evidence:
            sid=ev.get('source_id')
            if not isinstance(sid,str) or sid not in ids['sources']:
                errors.append(f'{label}: unknown or invalid evidence source ID.')
            else:
                family=source_map[sid].get('family')
                if nonempty(family): families.add(family)
            if not nonempty(ev.get('locator')):
                errors.append(f'{label}: missing precise evidence locator.')
        premises=claim.get('premises',[])
        if not isinstance(premises,list) or any(not isinstance(x,str) for x in premises):
            errors.append(f'{label}: premises must be an array of claim IDs.')
            premises=[]
        for premise in premises:
            if premise not in ids['claims']:
                errors.append(f'{label}: unknown premise {premise}.')
        if nonempty(label): graph[label]=premises
        if kind in ('fact','attributed_claim') and not evidence:
            errors.append(f'{label}: factual or attributed claim has no evidence.')
        if kind in ('inference','recommendation'):
            if not evidence and not premises:
                errors.append(f'{label}: {kind} has no evidence or linked premises.')
            if not nonempty(claim.get('rationale')):
                errors.append(f'{label}: {kind} needs a concise rationale.')
        if kind=='estimate' and not nonempty(claim.get('method')):
            errors.append(f'{label}: estimate needs its method.')
        if kind=='assumption' and not nonempty(claim.get('test')):
            warnings.append(f'{label}: add a way to test or stress this assumption.')
        confidence=claim.get('confidence')
        if kind in ('fact','attributed_claim','inference') and confidence is None:
            warnings.append(f'{label}: add justified confidence.')
        if confidence is not None:
            if confidence not in ('low','moderate','high'):
                errors.append(f'{label}: confidence must be low, moderate, or high.')
            if not nonempty(claim.get('confidence_reason')):
                errors.append(f'{label}: confidence lacks a reason.')
        if len(evidence)>1 and len(families)<2:
            warnings.append(f'{label}: multiple citations do not establish independent evidence families.')
    visiting,done=set(),set()
    def visit(node):
        if node in visiting:
            errors.append(f'Circular premise dependency involving {node}.')
            return
        if node in done: return
        visiting.add(node)
        for nxt in graph.get(node,[]): visit(nxt)
        visiting.remove(node);done.add(node)
    for node in graph: visit(node)
    for forecast in forecasts:
        label=forecast.get('id','forecast')
        for field in ['question','resolution_rule','basis']:
            if not nonempty(forecast.get(field)):
                errors.append(f'{label}: missing forecast {field}.')
        try:
            datetime.date.fromisoformat(forecast.get('deadline',''))
        except (TypeError,ValueError):
            errors.append(f'{label}: invalid deadline.')
        p=forecast.get('probability')
        valid_p=type(p) in (int,float) and math.isfinite(p) and 0<=p<=1
        if not valid_p: errors.append(f'{label}: probability must be a finite number in [0,1].')
        if 'outcome' in forecast:
            y=forecast['outcome']
            if type(y) not in (int,float) or y not in (0,1):
                errors.append(f'{label}: outcome must be 0 or 1; omit for unresolved events.')
            elif valid_p: scores.append((p-y)**2)
    if not claims:
        warnings.append('No claims to audit.')
    return {'valid_structure':not errors,'errors':errors,'warnings':warnings,
            'counts':{n:len(x) for n,x in collections.items()},
            'resolved_binary_forecasts':len(scores),'mean_brier_score':sum(scores)/len(scores) if scores else None,
            'scope':'Structure only; this does not verify source contents, citation entailment, truth, or analytical quality.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('record')
    args=parser.parse_args()
    try:
        with open(args.record) as f:
            data=json.load(f,parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Non-finite JSON number: '+x)))
        result=check(data)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0 if result['valid_structure'] else 1
    except (ValueError,OSError) as exc:
        print(json.dumps({'valid_structure':False,'errors':[str(exc)]}),file=sys.stderr)
        return 2


if __name__=='__main__':
    sys.exit(main())
