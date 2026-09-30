'use strict';
const searchURL = new URL('search.json', document.currentScript.src);
const search = document.querySelector('#chapter-search');
let searchIndex = null;
if (search) fetch(searchURL).then(r => r.json()).then(index => { searchIndex = index; if (search.value) search.dispatchEvent(new Event('input')); }).catch(() => {});
if (search) search.addEventListener('input', () => {
  const needle = search.value.trim().toLowerCase();
  document.querySelectorAll('[data-chapter]').forEach(row => { row.hidden = !(searchIndex?.[row.dataset.slug] || row.dataset.chapter).includes(needle); });
});
const resultsTable = document.querySelector('#result-rows');
if (resultsTable) {
  fetch('data/results.json').then(r => { if (!r.ok) throw Error('Result file unavailable'); return r.json(); }).then(data => {
    const p = document.querySelector('#provider');
    const s = document.querySelector('#state');
    const q = document.querySelector('#result-search');
    function render() {
      const needle = q.value.toLowerCase();
      const rows = data.results.filter(r => (!p.value || r.provider === p.value) && (!s.value || r.status === s.value) && (r.asset_id + ' ' + r.control_id + ' ' + r.title).toLowerCase().includes(needle));
      resultsTable.replaceChildren();
      for (const r of rows) {
        const tr = document.createElement('tr');
        for (const value of [r.asset_id, r.control_id + ' · ' + r.title, r.status, r.accepted_risk ? 'Accepted risk · still FAIL' : '—', r.reasons.join(' | ')]) {
          const td = document.createElement('td');
          if (value === r.status) { const span = document.createElement('span'); span.className = 'badge ' + r.status; span.textContent = value; td.append(span); }
          else td.textContent = value;
          tr.append(td);
        }
        tr.lastChild.className = 'result-reason';
        resultsTable.append(tr);
      }
      document.querySelector('#visible-count').textContent = rows.length + ' of ' + data.results.length + ' pairs shown. Headline metrics use the full declared population.';
    }
    for (const el of [p, s, q]) el.addEventListener('input', render);
    render();
  }).catch(err => { document.querySelector('#visible-count').textContent = err.message + '. Serve the site over HTTP to load the result data.'; });
}
const maturity = {
  aws: ['Reviewed account/region inventory, scoped API exports, private S3 baseline and manual evidence review.', 'AWS Config rules, Macie where appropriate, EventBridge collection, S3 evidence and tracked remediation.', 'Organization-wide scope reconciliation, governed policies, regional custody, signed releases and validated process evidence.'],
  azure: ['Reviewed subscriptions, Resource Graph exports, Bicep storage baseline and documented access reviews.', 'Azure Policy initiatives, Purview supported scans, Entra process evidence and monitored diagnostics.', 'Governed landing zones, tested exemptions, regional evidence stores and sustained control-quality SLOs.'],
  gcp: ['Reviewed projects, Cloud Asset Inventory, explicit storage prevention and owner-reviewed classification.', 'Scheduled/event collection, supported discovery, SCC findings and BigQuery result history.', 'Organization-level reconciliation, governed data policies, regional custody and reviewed compliance-tool integration.']
};
let cloud = 'aws', tier = 0;
function showMaturity() {
  const body = document.querySelector('#maturity-body');
  if (!body) return;
  body.textContent = maturity[cloud][tier];
  document.querySelectorAll('[data-cloud]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.cloud === cloud)));
  document.querySelectorAll('[data-tier]').forEach(b => b.setAttribute('aria-pressed', String(Number(b.dataset.tier) === tier)));
}
document.querySelectorAll('[data-cloud]').forEach(b => b.addEventListener('click', () => { cloud = b.dataset.cloud; showMaturity(); }));
document.querySelectorAll('[data-tier]').forEach(b => b.addEventListener('click', () => { tier = Number(b.dataset.tier); showMaturity(); }));
showMaturity();
const slides = Array.from(document.querySelectorAll('.slide'));
if (slides.length) {
  let index = Math.max(0, Math.min(slides.length - 1, (parseInt(location.hash.slice(1), 10) || 1) - 1));
  function show() { slides.forEach((s,i) => { s.hidden = i !== index; }); document.querySelector('#slide-count').textContent = (index + 1) + ' / ' + slides.length; history.replaceState(null, '', '#' + (index+1)); }
  function move(delta) { index = Math.max(0, Math.min(slides.length - 1, index + delta)); show(); }
  document.querySelector('#previous-slide').addEventListener('click', () => move(-1));
  document.querySelector('#next-slide').addEventListener('click', () => move(1));
  document.querySelector('#print-slides').addEventListener('click', () => window.print());
  document.addEventListener('keydown', e => { if (e.key === 'ArrowRight' || e.key === 'PageDown') { e.preventDefault(); move(1); } if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); move(-1); } });
  show();
}
