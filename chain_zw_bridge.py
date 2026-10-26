#!/usr/bin/env python3
"""Standalone EngAIn ZW brace-packet bridge for chain_mr_sketch.py.

Experimental ZW transport adapter, NOT an AP rule executor or runtime integration.
Accepts documented brace-style ZW records, resolves through the unchanged chain
sketch, and emits ZW records. No JSON serialization is used for the wire packet.
"""
from __future__ import annotations
import argparse
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Any
from chain_mr_sketch import Target, Chain, step_chain

ELEMENTS = frozenset(('earth','water','fire','lightning','ice','moon','shadow','spirit'))
TOKEN = re.compile(r'"(?:\\.|[^"\\])*"|[{}\[\]]|[^\s{}\[\]]+')


def tokenize(s: str) -> list[str]:
    tokens = TOKEN.findall(s)
    # Reject invalid tokens rather than silently accepting extra characters.
    if re.sub(TOKEN, '', s).strip():
        raise ValueError('unrecognized ZW characters')
    return tokens


def atom(t: str) -> Any:
    if t.startswith('"'):
        # ZW quoted string support. The demo deliberately uses only bare words.
        import json
        return json.loads(t)
    if t in ('true','false'):
        return t == 'true'
    if t in ('null','none'):
        return None
    try:
        if re.fullmatch(r'[+-]?\d+',t):
            return int(t)
        if re.fullmatch(r'[+-]?(?:\d+\.\d*|\.\d+)(?:[eE][+-]?\d+)?',t):
            return float(t)
    except ValueError:
        pass
    return t


def parse_zw(text: str) -> dict:
    tokens = tokenize(text)
    i = 0
    def read():
        nonlocal i
        if i >= len(tokens): raise ValueError('truncated ZW packet')
        t = tokens[i]; i += 1
        if t == '[':
            seq=[]
            while True:
                if i >= len(tokens): raise ValueError('unclosed [')
                if tokens[i] == ']':
                    i += 1; return seq
                seq.append(read())
        if t == '{':
            if i >= len(tokens): raise ValueError('unclosed {')
            key=tokens[i]; i+=1
            if key in '{}[]': raise ValueError('missing ZW record tag')
            fields={'_tag':key}
            values=[]
            while True:
                if i >= len(tokens): raise ValueError('unclosed {')
                if tokens[i] == '}':
                    i+=1
                    if values:
                        if len(values)!=1 or len(fields)!=1:
                            raise ValueError('not a simple tag/value field')
                        return (key,values[0])
                    return fields
                v=read()
                if isinstance(v,tuple):
                    k,val=v
                    if k in fields: raise ValueError('duplicate field '+k)
                    fields[k]=val
                elif isinstance(v,dict):
                    k=v['_tag']
                    if k in fields: raise ValueError('duplicate field '+k)
                    fields[k]=v
                else:
                    values.append(v)
        if t in ('}',']'): raise ValueError('unexpected ZW closer')
        return atom(t)
    data=read()
    if i!=len(tokens): raise ValueError('trailing ZW payload')
    if not isinstance(data,dict): raise ValueError('expected ZW record')
    return data


def validate_input(packet: dict) -> tuple[dict[str,Target],list[dict]]:
    if packet.get('_tag')!='combat_chain_request' or packet.get('version')!=1:
        raise ValueError('expected combat_chain_request version 1')
    ts=packet.get('targets'); hits=packet.get('hits')
    if not isinstance(ts,list) or not isinstance(hits,list):
        raise ValueError('targets and hits must be ZW arrays')
    targets={}
    for item in ts:
        if not isinstance(item,dict) or item.get('_tag')!='target':
            raise ValueError('bad target record')
        tid=item.get('id'); hp=item.get('hp')
        if not isinstance(tid,str) or not isinstance(hp,(float,int)) or isinstance(hp,bool):
            raise ValueError('bad target ID or HP')
        if tid in targets: raise ValueError('duplicate target '+tid)
        resist={}
        for k,v in item.items():
            if k.startswith('resist_'):
                el=k.removeprefix('resist_')
                if el not in ELEMENTS or not isinstance(v,(int,float)) or not (0<=v<=1):
                    raise ValueError('bad resistance '+k)
                resist[el]=float(v)
        targets[tid]=Target(float(hp),resist)
    resolved=[]
    for item in hits:
        if not isinstance(item,dict) or item.get('_tag')!='hit':
            raise ValueError('bad hit record')
        if not isinstance(item.get('id'),str) or not isinstance(item.get('target'),str) or type(item.get('primary')) is not bool:
            raise ValueError('missing hit ID, target or primary')
        affinity=item.get('affinity')
        if affinity is not None and affinity not in ELEMENTS:
            raise ValueError('invalid affinity')
        damage={}
        for k,v in item.items():
            if k.startswith('damage_'):
                el=k.removeprefix('damage_')
                if el not in ELEMENTS or not isinstance(v,(int,float)) or isinstance(v,bool) or not (v>=0):
                    raise ValueError('bad element damage '+k)
                damage[el]=float(v)
        if not damage: raise ValueError('hit has no elemental damage')
        hit={'id':item['id'],'target':item['target'],'primary':item['primary'],'damage':damage,'affinity':affinity}
        for k in ('ongoing','standard','strength'):
            v=item.get(k)
            if v is None: continue
            if not isinstance(v,(int,float)) or isinstance(v,bool) or not (v>=0):
                raise ValueError('bad '+k)
            hit[k]=float(v)
        resolved.append(hit)
    return targets,resolved


def zw_atom(v: Any) -> str:
    if v is None: return 'null'
    if v is True: return 'true'
    if v is False: return 'false'
    if isinstance(v,(int,float)): return str(v)
    if isinstance(v,str) and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_\-]*',v): return v
    import json
    return json.dumps(str(v))


def encode_result(targets: dict[str,Target],accepted: list[str], alerts: list[str]) -> str:
    lines=['{combat_chain_response','  {version 1}','  {accepted ['+' '.join(map(zw_atom,accepted))+']}','  {targets [']
    for tid,t in targets.items():
        els=' '.join(map(zw_atom,t.chain.elements))
        lines.append('    {target {id '+zw_atom(tid)+'} {hp '+zw_atom(t.hp)+'} {elements ['+els+']} {state '+zw_atom(t.chain.state)+'} {closed '+zw_atom(t.chain.closed)+'} {ongoing '+zw_atom(t.chain.ongoing)+'}}')
    lines+=['  ]}','  {alerts ['+' '.join(map(zw_atom,alerts))+']}','}']
    return '\n'.join(lines)+'\n'


def run_zw(source: str) -> str:
    ts, hits=validate_input(parse_zw(source))
    after, accepted, alerts=step_chain(ts,hits)
    return encode_result(after,accepted,alerts)


def main():
    p=argparse.ArgumentParser(description='Run a ZW combat chain request using the Python reference sketch')
    p.add_argument('packet',type=Path)
    p.add_argument('--out',type=Path,help='ZW result file (default stdout)')
    args=p.parse_args()
    result=run_zw(args.packet.read_text())
    # Also validates the *serialized response*, not just the input parser.
    parsed=parse_zw(result)
    assert parsed['_tag']=='combat_chain_response'
    if args.out:
        args.out.write_text(result)
        print('WROTE',args.out)
    else:
        print(result,end='')

if __name__=='__main__': main()
