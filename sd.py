import json,re,sys,collections,datetime
year,dkf,woof,out=sys.argv[1:5]
DAYS=[f"{year}-11-{d:02d}" for d in (9,10,11,12)]
CH=["heildsala","vefur","bud","verkstaedi"]
R={c:{"kr":[0]*4,"n":[0]*4,"h":[[0]*24 for _ in DAYS]} for c in CH}
top=collections.defaultdict(lambda:[ "",0,0]); last={c:"" for c in CH}
for r in json.load(open(dkf)):
    day=r["InvoiceDate"][:10]
    if day not in DAYS or str(r.get("CNumber","")).startswith("6704170850"): continue
    i=DAYS.index(day); o=r.get("Origin"); pos=str(r.get("PosInvoice") or "")[:3]
    for l in r.get("Lines",[]):
        if l.get("ItemCode","").lower() in ("shipping","") : continue
        t=top[l["ItemCode"].lower()]; t[0]=l.get("Text","")[:60]; t[1]+=l.get("Quantity",0); t[2]+=l.get("TotalAmountWithTax",0)
    if o==6: continue                      # vefur er talinn úr WooCommerce
    c="heildsala" if o!=5 else ("verkstaedi" if pos in ("130","140") else "bud")
    a=r.get("TotalAmountWithTax",0); R[c]["kr"][i]+=a; R[c]["n"][i]+=1 if a>0 else 0
    cr=r.get("Created","")
    hh=int(cr[11:13]) if cr[:10]==day else (23 if cr[:10]>day else 0)
    R[c]["h"][i][hh]+=a; last[c]=max(last[c],cr[:16])
BAD={"cancelled","failed","refunded","pending","trash","checkout-draft","draft","auto-draft"}
seen=set()
for m in re.finditer(r'"id":\s*(\d+),\s*"status":\s*"([^"]+)",\s*"date_created":\s*"([^"]+)",\s*"total":\s*"([-\d.]+)",\s*"total_tax":\s*"([-\d.]+)"',open(woof).read()):
    oid,st,dc,tot,tax=m.groups()
    if oid in seen or dc[:10] not in DAYS or st in BAD: continue
    seen.add(oid); i=DAYS.index(dc[:10]); a=float(tot)
    R["vefur"]["kr"][i]+=a; R["vefur"]["n"][i]+=1; R["vefur"]["h"][i][int(dc[11:13])]+=a; last["vefur"]=max(last["vefur"],dc[:16])
for c in CH:
    R[c]["kr"]=[round(x) for x in R[c]["kr"]]; R[c]["h"]=[[round(x) for x in h] for h in R[c]["h"]]; R[c]["last"]=last[c]
T=sorted(([v[0],round(v[1]),round(v[2])] for v in top.values() if v[2]>0),key=lambda x:-x[2])[:12]
D={"year":int(year),"updated":datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),"ch":R,"top":T}
json.dump(D,open(out,"w"),ensure_ascii=False,separators=(",",":"))
print(out,{c:R[c]["kr"] for c in CH},{c:R[c]["n"] for c in CH},last)
