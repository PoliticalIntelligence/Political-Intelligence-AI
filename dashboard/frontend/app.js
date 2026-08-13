const DATA_URL="./data/dashboard-data.json";
const state={allRows:[],filteredRows:[],startDate:null,endDate:null,page:1,pageSize:25,charts:{}};
const FILTERS=[["author","Author"],["district","District"],["assembly","Assembly"],["main-category","AI Main Category"],["sub-category","AI Sub Category"],["event-type","AI Event Type"],["party","AI Party Mentioned"],["leader","AI Leader Mentioned"],["sector","AI Development Sector"],["scheme","AI Government Scheme"]];
const byId=id=>document.getElementById(id);
const clean=v=>v==null?"":String(v).trim();

function parseDateValue(v){
  if(!v)return null;
  const s=clean(v);
  if(/^\d{4}-\d{2}-\d{2}/.test(s)){const d=new Date(s.slice(0,10)+"T00:00:00");return isNaN(d)?null:d}
  const d=new Date(s); return isNaN(d)?null:new Date(d.getFullYear(),d.getMonth(),d.getDate());
}
function isoDate(d){return [d.getFullYear(),String(d.getMonth()+1).padStart(2,"0"),String(d.getDate()).padStart(2,"0")].join("-")}
function setDateRange(start,end,label){
  state.startDate=isoDate(start);state.endDate=isoDate(end);
  byId("periodTitle").textContent=`${state.startDate} → ${state.endDate}`;
  document.querySelectorAll(".preset").forEach(b=>b.classList.remove("active"));
  if(label)document.querySelector(`[data-preset="${label}"]`)?.classList.add("active");
  byId("specificDate").value="";byId("fromDate").value=state.startDate;byId("toDate").value=state.endDate;
  state.page=1;applyAll();
}
function startOfWeek(d){const x=new Date(d),day=x.getDay(),diff=day===0?-6:1-day;x.setDate(x.getDate()+diff);x.setHours(0,0,0,0);return x}
function endOfWeek(d){const x=startOfWeek(d);x.setDate(x.getDate()+6);return x}
function startOfMonth(d){return new Date(d.getFullYear(),d.getMonth(),1)}
function endOfMonth(d){return new Date(d.getFullYear(),d.getMonth()+1,0)}
function initialiseDateState(){const t=new Date(),s=new Date(t);s.setDate(s.getDate()-6);setDateRange(s,t,"7d")}
function populateFilters(){
  for(const [id,field] of FILTERS){
    const select=byId(`f-${id}`),values=new Set(["All"]);
    for(const row of state.allRows){const v=clean(row[field]);if(v)values.add(v)}
    const sorted=Array.from(values);sorted.splice(1,sorted.length-1,...sorted.slice(1).sort((a,b)=>a.localeCompare(b)));
    select.innerHTML=sorted.map(v=>`<option value="${esc(v)}">${esc(v)}</option>`).join("");
    select.addEventListener("change",()=>{state.page=1;applyAll()});
  }
}
function currentFilters(){const o={};for(const [id,field] of FILTERS)o[field]=clean(byId(`f-${id}`).value);return o}
function matches(row,field,want){return !want||want==="All"||clean(row[field])===want}
function inDateRange(row){
  const d=parseDateValue(row["Post Date"]||row["Timestamp"]);if(!d||!state.startDate||!state.endDate)return false;
  return d>=new Date(state.startDate+"T00:00:00")&&d<=new Date(state.endDate+"T23:59:59");
}
function applyAll(){const f=currentFilters();state.filteredRows=state.allRows.filter(r=>inDateRange(r)&&FILTERS.every(([,field])=>matches(r,field,f[field])));render()}
function countField(rows,field,value){return rows.filter(r=>clean(r[field]).toLowerCase()===value.toLowerCase()).length}
function makeCounts(rows,field,n=12){const c={};for(const r of rows){const v=clean(r[field])||"Not Classified";c[v]=(c[v]||0)+1}return Object.entries(c).sort((a,b)=>b[1]-a[1]).slice(0,n)}
function render(){
  const rows=state.filteredRows;
  byId("validCount").textContent=`Showing ${rows.length.toLocaleString("en-IN")} valid posts`;
  byId("kpi-total").textContent=rows.length.toLocaleString("en-IN");
  byId("kpi-political").textContent=countField(rows,"AI Main Category","Political").toLocaleString("en-IN");
  byId("kpi-development").textContent=countField(rows,"AI Main Category","Development").toLocaleString("en-IN");
  byId("kpi-law").textContent=countField(rows,"AI Main Category","Law & Order").toLocaleString("en-IN");
  byId("kpi-welfare").textContent=countField(rows,"AI Main Category","Welfare").toLocaleString("en-IN");
  byId("kpi-opposition").textContent=rows.filter(r=>{const v=clean(r["AI Opposition Mention"]).toLowerCase();return v&&!["no","none","false","0","not mentioned"].includes(v)}).length.toLocaleString("en-IN");
  renderCharts();renderTable();
}
function renderCharts(){
  [["categoryChart","AI Main Category","doughnut",12],["sectorChart","AI Development Sector","bar",12],["partyChart","AI Party Mentioned","bar",12],["leaderChart","AI Leader Mentioned","bar",10]].forEach(([id,field,type,n])=>{
    const data=makeCounts(state.filteredRows,field,n),canvas=byId(id);
    if(state.charts[id])state.charts[id].destroy();
    state.charts[id]=new Chart(canvas,{type,data:{labels:data.map(x=>x[0]),datasets:[{data:data.map(x=>x[1]),borderWidth:1}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:type==="doughnut",position:"right"}},scales:type==="bar"?{y:{beginAtZero:true}}:undefined}});
  });
}
function renderTable(){
  const start=(state.page-1)*state.pageSize,rows=state.filteredRows.slice(start,start+state.pageSize);
  byId("postTableBody").innerHTML=rows.map(r=>{
    const url=clean(r["Post URL"]),date=clean(r["Post Date"]||r["Timestamp"]),summary=clean(r["AI Summary"])||clean(r["Post Text"]).slice(0,240);
    return `<tr><td>${esc(formatDate(date))}</td><td>${esc(r["Author"])}</td><td>${esc(r["AI Main Category"])}</td><td>${esc(r["AI Sub Category"])}</td><td>${esc(r["AI Event Type"])}</td><td>${esc(r["AI Party Mentioned"])}</td><td>${esc(r["AI Development Sector"])}</td><td>${esc(r["AI Place of Visit"])}</td><td class="summary">${esc(summary)}</td><td>${url?`<a href="${escAttr(url)}" target="_blank" rel="noopener">Open</a>`:"—"}</td></tr>`
  }).join("");
  const totalPages=Math.max(1,Math.ceil(state.filteredRows.length/state.pageSize));
  byId("pageInfo").textContent=`Page ${state.page} of ${totalPages}`;byId("prevPage").disabled=state.page<=1;byId("nextPage").disabled=state.page>=totalPages;
  byId("tableNote").textContent=`${state.filteredRows.length.toLocaleString("en-IN")} posts match the current date range and filters.`;
}
function formatDate(v){const d=parseDateValue(v);return d?d.toLocaleDateString("en-IN",{day:"2-digit",month:"short",year:"numeric"}):v||"—"}
function esc(v){return String(v??"").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;")}
function escAttr(v){return esc(v).replaceAll("`","&#096;")}
function resetFilters(){for(const [id] of FILTERS)byId(`f-${id}`).value="All";state.page=1;applyAll()}
function csvCell(v){return `"${String(v??"").replaceAll('"','""')}"`}
function downloadCsv(){
  const cols=["Post Date","Author","District","Assembly","AI Main Category","AI Sub Category","AI Event Type","AI Party Mentioned","AI Leader Mentioned","AI Development Sector","AI Government Scheme","AI Place of Visit","AI Opposition Mention","AI Opposition Target","AI Summary","Post URL"];
  const out=[cols.map(csvCell).join(",")];for(const r of state.filteredRows)out.push(cols.map(c=>csvCell(r[c])).join(","));
  const blob=new Blob([out.join("\n")],{type:"text/csv;charset=utf-8;"}),u=URL.createObjectURL(blob),a=document.createElement("a");a.href=u;a.download=`political-intelligence-${state.startDate}-to-${state.endDate}.csv`;a.click();URL.revokeObjectURL(u);
}
async function loadData(){
  try{
    const res=await fetch(DATA_URL,{cache:"no-store"});if(!res.ok)throw new Error(`HTTP ${res.status}`);
    const payload=await res.json();state.allRows=Array.isArray(payload.rows)?payload.rows.filter(r=>clean(r["Author"])):[];
    const upd=payload.generated_at?new Date(payload.generated_at):null;
    byId("dataStatus").textContent=`${state.allRows.length.toLocaleString("en-IN")} posts loaded`;
    byId("updatedAt").textContent=`Data updated: ${upd&&!isNaN(upd) ? upd.toLocaleString("en-IN"):"—"}`;
    populateFilters();initialiseDateState();
  }catch(e){console.error(e);byId("dataStatus").textContent="Data unavailable";byId("periodTitle").textContent="Unable to load dashboard data"}
}
function bindEvents(){
  document.querySelectorAll(".preset").forEach(b=>b.addEventListener("click",()=>{
    const t=new Date(),p=b.dataset.preset,s=new Date(t);
    if(p==="7d"){s.setDate(s.getDate()-6);setDateRange(s,t,p)}
    else if(p==="30d"){s.setDate(s.getDate()-29);setDateRange(s,t,p)}
    else if(p==="today")setDateRange(t,t,p);
    else if(p==="week")setDateRange(startOfWeek(t),endOfWeek(t),p);
    else if(p==="month")setDateRange(startOfMonth(t),endOfMonth(t),p);
  }));
  byId("applyCustom").addEventListener("click",()=>{
    const specific=byId("specificDate").value,from=byId("fromDate").value,to=byId("toDate").value;
    if(specific){const d=new Date(specific+"T00:00:00");setDateRange(d,d,null);return}
    if(!from||!to||from>to){alert("Please select a valid From and To date.");return}
    state.startDate=from;state.endDate=to;byId("periodTitle").textContent=`${from} → ${to}`;document.querySelectorAll(".preset").forEach(b=>b.classList.remove("active"));state.page=1;applyAll();
  });
  byId("resetDates").addEventListener("click",initialiseDateState);byId("resetFilters").addEventListener("click",resetFilters);byId("downloadCsv").addEventListener("click",downloadCsv);
  byId("prevPage").addEventListener("click",()=>{if(state.page>1){state.page--;renderTable()}});byId("nextPage").addEventListener("click",()=>{const n=Math.max(1,Math.ceil(state.filteredRows.length/state.pageSize));if(state.page<n){state.page++;renderTable()}});
}
bindEvents();loadData();