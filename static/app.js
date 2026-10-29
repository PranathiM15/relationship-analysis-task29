const datasetSelect = document.getElementById('datasetSelect');
const xSelect = document.getElementById('xSelect');
const ySelect = document.getElementById('ySelect');
const fileInput = document.getElementById('csvFile');
const uploadName = document.getElementById('uploadName');
const plotBtn = document.getElementById('plotBtn');
const statusEl = document.getElementById('status');
let uploadId = null;
let currentDataset = datasetSelect.value;
let datasetLabel = datasetSelect.options[datasetSelect.selectedIndex].text;

function status(message, error=false) {
  statusEl.textContent = message;
  statusEl.classList.toggle('error', error);
}
function fillColumnOptions(columns) {
  xSelect.innerHTML = '';
  ySelect.innerHTML = '';
  columns.forEach((column, i) => {
    for (const select of [xSelect, ySelect]) {
      const option = document.createElement('option');
      option.value = column;
      option.textContent = column.replaceAll('_', ' ');
      select.appendChild(option);
    }
    if (i === 1) ySelect.value = column;
  });
  if (columns.length > 1) ySelect.value = columns[1];
}
async function readDataset(name) {
  uploadId = null;
  fileInput.value = '';
  uploadName.textContent = 'Drop a CSV file here';
  currentDataset = name;
  datasetLabel = datasetSelect.options[datasetSelect.selectedIndex].text;
  status('Reading dataset…');
  try {
    const res = await fetch(`/api/dataset?name=${encodeURIComponent(name)}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Could not load dataset.');
    fillColumnOptions(data.columns);
    status(`${data.rows.toLocaleString()} rows · ${data.column_count} columns · ${data.columns.length} numeric variables`);
    await generatePlot();
  } catch (err) { status(err.message, true); }
}
async function uploadDataset(file) {
  if (!file) return;
  status('Reading your CSV…');
  const body = new FormData(); body.append('file', file);
  try {
    const res = await fetch('/api/upload', {method:'POST', body});
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Upload failed.');
    uploadId = data.upload_id;
    currentDataset = null;
    datasetLabel = data.name;
    fillColumnOptions(data.columns);
    uploadName.textContent = data.name;
    status(`${data.rows.toLocaleString()} rows · ${data.column_count} columns · uploaded locally`);
    await generatePlot();
  } catch (err) { status(err.message, true); }
}
async function generatePlot() {
  plotBtn.disabled = true;
  plotBtn.innerHTML = 'Analyzing your data <span>…</span>';
  status('Calculating correlation and drawing your plot…');
  try {
    const res = await fetch('/api/analyze', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({dataset:currentDataset, upload_id:uploadId, x:xSelect.value, y:ySelect.value})
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Could not analyze this selection.');
    const chart = document.getElementById('chart');
    chart.innerHTML = '';
    const image = document.createElement('img');
    image.src = data.image; image.alt = `Scatter plot comparing ${data.x} and ${data.y}`;
    chart.appendChild(image);
    document.getElementById('correlation').textContent = `${data.correlation >= 0 ? '+' : ''}${data.correlation.toFixed(3)}`;
    document.getElementById('patternLabel').textContent = data.pattern;
    document.getElementById('chartCount').textContent = `${data.rows_used.toLocaleString()} POINTS`;
    document.getElementById('summary').innerHTML = `<b>${data.pattern} relationship.</b> ${escapeHtml(data.interpretation)}<span class="caveat">Pearson's r is a measure of linear association. Correlation does not prove causation.</span>`;
    const list = document.getElementById('observations'); list.innerHTML = '';
    data.observations.forEach(text => { const li=document.createElement('li'); li.textContent=text; list.appendChild(li); });
    status(`Analysis complete · ${data.rows_used.toLocaleString()} valid rows · ${datasetLabel}`);
  } catch (err) { status(err.message, true); }
  finally { plotBtn.disabled = false; plotBtn.innerHTML = 'Generate scatter plot <span>↗</span>'; }
}
function escapeHtml(value) { return String(value).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[ch])); }
datasetSelect.addEventListener('change', () => readDataset(datasetSelect.value));
fileInput.addEventListener('change', () => uploadDataset(fileInput.files[0]));
plotBtn.addEventListener('click', generatePlot);
readDataset(datasetSelect.value);
