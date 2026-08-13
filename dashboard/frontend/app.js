const charts = {};
const $ = id => document.getElementById(id);
const filterIds = ['author','district','assembly','category','subcategory','event','party','leader','sector','scheme'];
let currentPreset = 'last7';

function esc(v) {
  return String(v ?? '').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
}

function setOptions(id, values, label) {
  const el = $(id);
  const current = el.value;
  el.innerHTML = `<option value="">${esc(label)}</option>`;
  (values || []).forEach(v => {
    const o = document.createElement('option'); o.value = v; o.textContent = v; el.appendChild(o);
  });
  if ([...el.options].some(o => o.value === current)) el.value = current;
}

async function loadFilters() {
  const data = await fetch('/api/filters').then(r => r.json());
  setOptions('author', data.authors, 'All authors');
  setOptions('district', data.districts, 'All districts');
  setOptions('assembly', data.assemblies, 'All assemblies');
  setOptions('category', data.categories, 'All categories');
  setOptions('subcategory', data.subcategories, 'All sub-categories');
  setOptions('event', data.events, 'All events');
  setOptions('party', data.parties, 'All parties');
  setOptions('leader', data.leaders, 'All leaders');
  setOptions('sector', data.sectors, 'All sectors');
  setOptions('scheme', data.schemes, 'All schemes');
}

function params() {
  const p = new URLSearchParams();
  p.set('preset', currentPreset);
  const exact = $('exactDate').value;
  const from = $('fromDate').value;
  const to = $('toDate').value;
  if (exact) p.set('date', exact); else { if (from) p.set('from_date', from); if (to) p.set('to_date', to); }
  filterIds.forEach(id => { if ($(id).value) p.set(id, $(id).value); });
  return p.toString();
}

function draw(id, type, labels, values, options={}) {
  if (charts[id]) charts[id].destroy();
  charts[id] = new Chart($(id), {
    type,
    data: { labels, datasets: [{ label: options.label || 'Posts', data: values, borderWidth: 1 }] },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: type === 'doughnut' } }, scales: type === 'doughnut' ? {} : { y: { beginAtZero: true, ticks: { precision: 0 } } } }
  });
}

function renderPosts(posts) {
  $('postCount').textContent = `${posts.length} shown`;
  $('postsBody').innerHTML = posts.length ? posts.map(p => `
    <tr>
      <td><strong>${esc(p.post_date)}</strong></td>
      <td>${esc(p.author)}</td>
      <td>${esc(p.category || 'Not Classified')}${p.subcategory ? `<small>${esc(p.subcategory)}</small>` : ''}</td>
      <td>${esc(p.event)}</td>
      <td>${esc(p.party)}</td>
      <td>${esc(p.leader)}</td>
      <td>${esc(p.sector)}${p.scheme ? `<small>${esc(p.scheme)}</small>` : ''}</td>
      <td class="summary">${esc(p.summary)}</td>
      <td>${p.url ? `<a href="${esc(p.url)}" target="_blank" rel="noopener">Open</a>` : ''}</td>
    </tr>`).join('') : '<tr><td colspan="9" class="empty">No posts found for this selection.</td></tr>';
}

function setPeriodLabel(period) {
  if (period.exact) $('periodLabel').textContent = period.exact;
  else if (period.from || period.to) $('periodLabel').textContent = `${period.from || 'Start'} → ${period.to || 'Today'}`;
  else $('periodLabel').textContent = period.preset === 'last30' ? 'Last 30 Days' : period.preset === 'today' ? 'Today' : period.preset === 'thisweek' ? 'This Week' : period.preset === 'thismonth' ? 'This Month' : 'Last 7 Days';
}

async function loadDashboard() {
  $('dataStatus').textContent = 'Updating…';
  const data = await fetch('/api/summary?' + params()).then(r => r.json());
  setPeriodLabel(data.period);
  $('total').textContent = data.total_posts;
  $('political').textContent = data.political_posts;
  $('development').textContent = data.development_posts;
  $('lawOrder').textContent = data.law_order_posts;
  $('welfare').textContent = data.welfare_posts;
  $('opposition').textContent = data.opposition_mentions;
  draw('dailyChart', 'line', data.daily.map(x => x.date), data.daily.map(x => x.value));
  draw('categoryChart', 'doughnut', data.categories.map(x => x.label), data.categories.map(x => x.value));
  draw('sectorChart', 'bar', data.sectors.map(x => x.label), data.sectors.map(x => x.value));
  draw('partyChart', 'bar', data.parties.map(x => x.label), data.parties.map(x => x.value));
  draw('eventChart', 'bar', data.events.map(x => x.label), data.events.map(x => x.value));
  draw('leaderChart', 'bar', data.leaders.map(x => x.label), data.leaders.map(x => x.value));
  renderPosts(data.posts);
  $('dataStatus').textContent = `Showing ${data.total_posts} valid posts`;
}

function selectPreset(preset) {
  currentPreset = preset;
  document.querySelectorAll('.quick').forEach(b => b.classList.toggle('active', b.dataset.preset === preset));
  $('exactDate').value = ''; $('fromDate').value = ''; $('toDate').value = '';
  loadDashboard();
}

async function refreshData() {
  $('dataStatus').textContent = 'Refreshing sheet data…';
  await fetch('/api/refresh', { method: 'POST' });
  await loadFilters();
  await loadDashboard();
}

document.addEventListener('DOMContentLoaded', async () => {
  document.querySelectorAll('.quick').forEach(b => b.addEventListener('click', () => selectPreset(b.dataset.preset)));
  filterIds.forEach(id => $(id).addEventListener('change', loadDashboard));
  $('exactDate').addEventListener('change', () => { currentPreset = 'custom'; document.querySelectorAll('.quick').forEach(b => b.classList.remove('active')); loadDashboard(); });
  $('customBtn').addEventListener('click', () => { currentPreset = 'custom'; document.querySelectorAll('.quick').forEach(b => b.classList.remove('active')); loadDashboard(); });
  $('resetDates').addEventListener('click', () => selectPreset('last7'));
  $('resetFilters').addEventListener('click', () => { filterIds.forEach(id => $(id).value = ''); loadDashboard(); });
  $('refreshBtn').addEventListener('click', refreshData);
  try { await loadFilters(); await loadDashboard(); } catch (e) { $('dataStatus').textContent = 'Could not load dashboard data'; console.error(e); }
});
