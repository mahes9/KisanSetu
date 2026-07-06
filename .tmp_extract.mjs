import fs from 'fs';
const sym = process.argv[2];
const data = JSON.parse(fs.readFileSync(`.tmp_${sym}.json`, 'utf8'));
const tfs = ['W', 'D', '240', '60'];
const tfName = {W:'W1', D:'D1', '240':'H4', '60':'H1'};
const out = { symbol: sym };
for (const tf of tfs) {
  const d = data[tf];
  if (!d) { out[tfName[tf]] = 'NO DATA'; continue; }
  const labels = (d.labels?.[0]?.labels) || [];
  const boxes = (d.boxes?.[0]?.zones) || [];
  const price = d.quote?.last;
  // Pick first occurrence of each unique label text (most recent on chart)
  const labelMap = {};
  for (const l of labels) {
    if (!(l.text in labelMap)) labelMap[l.text] = l.price;
  }
  // Sort boxes by distance to price, take nearest 6
  const sorted = boxes.map(b => ({...b, mid: (b.high+b.low)/2, dist: Math.abs(((b.high+b.low)/2) - price)}))
    .sort((a,b)=>a.dist-b.dist).slice(0, 8);
  out[tfName[tf]] = {
    price,
    labels: labelMap,
    structureSeq: labels.slice(-8).map(l => `${l.text}@${l.price}`),
    nearestBoxes: sorted.map(b => `${b.type} ${b.low}-${b.high}`)
  };
}
console.log(JSON.stringify(out, null, 2));
