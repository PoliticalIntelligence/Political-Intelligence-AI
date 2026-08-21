const DATA_URL = "./data/dashboard-data.json";

const state = {
  allRows: [],
  filteredRows: [],

  startDate: null,
  endDate: null,

  page: 1,
  pageSize: 25,

  charts: {}
};


/* ============================================================
   BASIC HELPERS
   ============================================================ */

const byId = id => document.getElementById(id);

const clean = value =>
  value == null ? "" : String(value).trim();


/* ============================================================
   DATE HELPERS
   ============================================================ */

function parseDateValue(value) {

  if (!value) {
    return null;
  }

  const s = clean(value);

  /*
   * YYYY-MM-DD
   */
  if (/^\d{4}-\d{2}-\d{2}/.test(s)) {

    const d = new Date(
      s.slice(0, 10) + "T00:00:00"
    );

    return isNaN(d) ? null : d;
  }


  /*
   * DD-MM-YYYY
   */
  if (/^\d{2}-\d{2}-\d{4}$/.test(s)) {

    const parts = s.split("-");

    const d = new Date(
      Number(parts[2]),
      Number(parts[1]) - 1,
      Number(parts[0])
    );

    return isNaN(d) ? null : d;
  }


  /*
   * Generic date
   */
  const d = new Date(s);

  if (isNaN(d)) {
    return null;
  }

  return new Date(
    d.getFullYear(),
    d.getMonth(),
    d.getDate()
  );
}


function isoDate(date) {

  return [
    date.getFullYear(),

    String(
      date.getMonth() + 1
    ).padStart(2, "0"),

    String(
      date.getDate()
    ).padStart(2, "0")

  ].join("-");
}


function formatDate(value) {

  const date = parseDateValue(value);

  if (!date) {
    return value || "—";
  }

  return date.toLocaleDateString(
    "en-IN",
    {
      day: "2-digit",
      month: "short",
      year: "numeric"
    }
  );
}


/* ============================================================
   DATE RANGE
   ============================================================ */

function setDateRange(start, end, label) {

  state.startDate = isoDate(start);
  state.endDate = isoDate(end);

  byId("periodTitle").textContent =
    `${state.startDate} → ${state.endDate}`;


  document
    .querySelectorAll(".preset")
    .forEach(button =>
      button.classList.remove("active")
    );


  if (label) {

    document
      .querySelector(
        `[data-preset="${label}"]`
      )
      ?.classList.add("active");
  }


  byId("specificDate").value = "";
  byId("fromDate").value = state.startDate;
  byId("toDate").value = state.endDate;


  state.page = 1;

  applyAll();
}


function startOfWeek(date) {

  const d = new Date(date);

  const day = d.getDay();

  const diff =
    day === 0
      ? -6
      : 1 - day;

  d.setDate(
    d.getDate() + diff
  );

  d.setHours(
    0,
    0,
    0,
    0
  );

  return d;
}


function endOfWeek(date) {

  const d =
    startOfWeek(date);

  d.setDate(
    d.getDate() + 6
  );

  return d;
}


function startOfMonth(date) {

  return new Date(
    date.getFullYear(),
    date.getMonth(),
    1
  );
}


function endOfMonth(date) {

  return new Date(
    date.getFullYear(),
    date.getMonth() + 1,
    0
  );
}


function initialiseDateState() {

  const today =
    new Date();

  const start =
    new Date(today);

  start.setDate(
    start.getDate() - 6
  );

  setDateRange(
    start,
    today,
    "7d"
  );
}


/* ============================================================
   FILTERS
   ============================================================ */

function populateSelect(
  id,
  field,
  includeAll = true
) {

  const select =
    byId(id);

  if (!select) {
    return;
  }


  const values =
    new Set();


  if (includeAll) {
    values.add("All");
  }


  for (const row of state.allRows) {

    const value =
      clean(row[field]);

    if (value) {
      values.add(value);
    }
  }


  const sorted =
    Array.from(values);


  if (includeAll) {

    sorted.splice(
      1,
      sorted.length - 1,

      ...sorted
        .slice(1)
        .sort(
          (a, b) =>
            a.localeCompare(
              b,
              "en",
              {
                sensitivity: "base"
              }
            )
        )
    );

  } else {

    sorted.sort(
      (a, b) =>
        a.localeCompare(
          b,
          "en",
          {
            sensitivity: "base"
          }
        )
    );
  }


  select.innerHTML =
    sorted
      .map(
        value =>
          `<option value="${esc(value)}">${esc(value)}</option>`
      )
      .join("");
}


function populateFilters() {

  populateSelect(
    "f-author",
    "Author",
    true
  );

  populateSelect(
    "f-main-category",
    "AI Main Category",
    true
  );


  byId("f-author")
    .addEventListener(
      "change",
      () => {

        state.page = 1;

        applyAll();
      }
    );


  byId("f-main-category")
    .addEventListener(
      "change",
      () => {

        state.page = 1;

        applyAll();
      }
    );
}


function getAuthorFilter() {

  return clean(
    byId("f-author")?.value
  );
}


function getCategoryFilter() {

  return clean(
    byId("f-main-category")?.value
  );
}


/* ============================================================
   FILTER MATCHING
   ============================================================ */

function matches(
  row,
  field,
  wanted
) {

  return (
    !wanted ||
    wanted === "All" ||
    clean(row[field]) === wanted
  );
}


function inDateRange(row) {

  /*
   * IMPORTANT:
   * Dashboard uses Post Date first.
   * Timestamp is only the fallback.
   */

  const postDate =
    parseDateValue(
      row["Post Date"]
    );


  const timestamp =
    parseDateValue(
      row["Timestamp"]
    );


  const date =
    postDate || timestamp;


  if (
    !date ||
    !state.startDate ||
    !state.endDate
  ) {

    return false;
  }


  const start =
    new Date(
      state.startDate +
      "T00:00:00"
    );


  const end =
    new Date(
      state.endDate +
      "T23:59:59"
    );


  return (
    date >= start &&
    date <= end
  );
}


function applyAll() {

  const author =
    getAuthorFilter();

  const category =
    getCategoryFilter();


  state.filteredRows =
    state.allRows.filter(
      row => {

        if (!inDateRange(row)) {
          return false;
        }


        if (
          !matches(
            row,
            "Author",
            author
          )
        ) {
          return false;
        }


        if (
          !matches(
            row,
            "AI Main Category",
            category
          )
        ) {
          return false;
        }


        return true;
      }
    );


  render();
}


/* ============================================================
   COUNT HELPERS
   ============================================================ */

function countField(
  rows,
  field,
  value
) {

  return rows.filter(
    row =>
      clean(row[field])
        .toLowerCase() ===
      value.toLowerCase()
  ).length;
}


function makeCounts(
  rows,
  field,
  limit = 12
) {

  const counts = {};


  for (const row of rows) {

    const value =
      clean(row[field]) ||
      "Not Classified";


    counts[value] =
      (counts[value] || 0) + 1;
  }


  return Object
    .entries(counts)
    .sort(
      (a, b) =>
        b[1] - a[1]
    )
    .slice(
      0,
      limit
    );
}


/* ============================================================
   KPI HELPERS
   ============================================================ */

function getActiveMLACount(rows) {

  return new Set(
    rows
      .map(
        row =>
          clean(row["Author"])
      )
      .filter(Boolean)
  ).size;
}


function getAveragePostsPerMLA(rows) {

  const active =
    getActiveMLACount(rows);

  if (!active) {
    return 0;
  }

  return rows.length / active;
}


function getAIAnalysedCount(rows) {

  return rows.filter(
    row =>
      Boolean(
        clean(
          row["AI Processed At"]
        )
      )
  ).length;
}


function getSelectedMLAPostCount(rows) {

  const author =
    getAuthorFilter();


  if (
    !author ||
    author === "All"
  ) {

    return null;
  }


  return rows.length;
}


function getOppositionMentionCount(rows) {

  return rows.filter(
    row => {

      const value =
        clean(
          row["AI Opposition Mention"]
        ).toLowerCase();


      return (
        value &&
        ![
          "no",
          "none",
          "false",
          "0",
          "not mentioned"
        ].includes(value)
      );
    }
  ).length;
}


/* ============================================================
   RENDER
   ============================================================ */

function render() {

  const rows =
    state.filteredRows;


  byId("validCount").textContent =
    `Showing ${rows.length.toLocaleString("en-IN")} valid posts`;


  /*
   * KPI 1
   */
  byId("kpi-total").textContent =
    rows.length.toLocaleString("en-IN");


  /*
   * KPI 2
   */
  byId("kpi-political").textContent =
    getActiveMLACount(rows)
      .toLocaleString("en-IN");


  /*
   * KPI 3
   */
  byId("kpi-development").textContent =
    getAIAnalysedCount(rows)
      .toLocaleString("en-IN");


  /*
   * KPI 4
   */
  byId("kpi-law").textContent =
    getAveragePostsPerMLA(rows)
      .toFixed(1);


  /*
   * KPI 5
   */
  const selectedMLAPosts =
    getSelectedMLAPostCount(rows);


  byId("kpi-welfare").textContent =
    selectedMLAPosts === null
      ? "—"
      : selectedMLAPosts.toLocaleString(
          "en-IN"
        );


  /*
   * KPI 6
   */
  byId("kpi-opposition").textContent =
    getOppositionMentionCount(rows)
      .toLocaleString("en-IN");


  renderCategoryChart();

  renderActivityChart(
    "activityChart"
  );

  renderActivityChart(
    "activityChartLarge"
  );

  renderTable();
}


/* ============================================================
   CHART HELPERS
   ============================================================ */

function destroyChart(id) {

  if (
    state.charts[id]
  ) {

    state.charts[id].destroy();

    state.charts[id] = null;
  }
}


function commonOptions() {

  return {

    responsive: true,

    maintainAspectRatio: false,

    animation: {
      duration: 250
    },

    plugins: {

      legend: {
        display: false
      }
    }
  };
}


/* ============================================================
   MAIN CATEGORY CHART
   ============================================================ */

function renderCategoryChart() {

  const canvas =
    byId("categoryChart");


  if (!canvas) {
    return;
  }


  destroyChart(
    "categoryChart"
  );


  const data =
    makeCounts(
      state.filteredRows,
      "AI Main Category",
      12
    );


  state.charts.categoryChart =
    new Chart(
      canvas,
      {

        type: "doughnut",

        data: {

          labels:
            data.map(
              item => item[0]
            ),

          datasets: [
            {
              data:
                data.map(
                  item => item[1]
                ),

              borderWidth: 1
            }
          ]
        },


        options: {

          responsive: true,

          maintainAspectRatio: false,

          plugins: {

            legend: {

              display: true,

              position: "right"
            }

          }
        }
      }
    );
}


/* ============================================================
   ACTIVITY DATE HELPERS
   ============================================================ */

function getPostDate(row) {

  /*
   * Again: Post Date is authoritative.
   * Timestamp is fallback only.
   */

  return (
    parseDateValue(
      row["Post Date"]
    ) ||
    parseDateValue(
      row["Timestamp"]
    )
  );
}


function getDateCounts(rows) {

  const counts = {};


  for (const row of rows) {

    const date =
      getPostDate(row);


    if (!date) {
      continue;
    }


    const key =
      isoDate(date);


    counts[key] =
      (counts[key] || 0) + 1;
  }


  return counts;
}


function generateDateList(
  start,
  end
) {

  const dates = [];

  const current =
    new Date(start);

  const last =
    new Date(end);


  while (
    current <= last
  ) {

    dates.push(
      isoDate(current)
    );


    current.setDate(
      current.getDate() + 1
    );
  }


  return dates;
}


/* ============================================================
   SOCIAL MEDIA ACTIVITY LINE CHART
   ============================================================ */

function createActivityChart(
  canvasId,
  compact = false
) {

  const canvas =
    byId(canvasId);


  if (!canvas) {
    return;
  }


  destroyChart(
    canvasId
  );


  if (
    !state.startDate ||
    !state.endDate
  ) {

    return;
  }


  const start =
    new Date(
      state.startDate +
      "T00:00:00"
    );


  const end =
    new Date(
      state.endDate +
      "T00:00:00"
    );


  const dates =
    generateDateList(
      start,
      end
    );


  const dateCounts =
    getDateCounts(
      state.filteredRows
    );


  const selected =
    getAuthorFilter();


  const label =
    selected &&
    selected !== "All"
      ? `${selected} — Posts`
      : "All MLAs — Posts";


  state.charts[canvasId] =
    new Chart(
      canvas,
      {

        type: "line",

        data: {

          labels:
            dates.map(
              date =>
                compact
                  ? new Date(
                      date +
                      "T00:00:00"
                    ).toLocaleDateString(
                      "en-IN",
                      {
                        day: "2-digit",
                        month: "short"
                      }
                    )
                  : formatDate(date)
            ),

          datasets: [

            {

              label,

              data:
                dates.map(
                  date =>
                    dateCounts[date] ||
                    0
                ),

              borderWidth: compact
                ? 2
                : 3,

              pointRadius:
                compact ? 2 : 3,

              pointHoverRadius: 5,

              tension: 0.25,

              fill: true
            }

          ]

        },


        options: {

          responsive: true,

          maintainAspectRatio: false,

          interaction: {

            intersect: false,

            mode: "index"

          },


          plugins: {

            legend: {

              display: true,

              position:
                compact
                  ? "top"
                  : "top"

            },


            tooltip: {

              callbacks: {

                label: context =>
                  ` Posts: ${context.parsed.y}`

              }

            }

          },


          scales: {

            y: {

              beginAtZero: true,

              ticks: {
                precision: 0
              },

              title: {

                display: !compact,

                text: "Number of Posts"

              }

            },


            x: {

              title: {

                display: !compact,

                text: "Date"

              }

            }

          }

        }

      }
    );
}


function renderActivityChart(
  canvasId
) {

  createActivityChart(
    canvasId,
    canvasId === "activityChart"
  );
}


/* ============================================================
   TABLE
   ============================================================ */

function renderTable() {

  const start =
    (state.page - 1) *
    state.pageSize;


  const rows =
    state.filteredRows.slice(
      start,
      start + state.pageSize
    );


  byId("postTableBody").innerHTML =
    rows
      .map(
        row => {

          const url =
            clean(
              row["Post URL"]
            );


          const date =
            clean(
              row["Post Date"] ||
              row["Timestamp"]
            );


          const summary =
            clean(
              row["AI Summary"]
            ) ||
            clean(
              row["Post Text"]
            ).slice(
              0,
              240
            );


          return `

            <tr>

              <td>
                ${esc(
                  formatDate(date)
                )}
              </td>

              <td>
                ${esc(
                  row["Author"]
                )}
              </td>

              <td>
                ${esc(
                  row["AI Main Category"]
                )}
              </td>

              <td>
                ${esc(
                  row["AI Sub Category"]
                )}
              </td>

              <td>
                ${esc(
                  row["AI Event Type"]
                )}
              </td>

              <td>
                ${esc(
                  row["AI Party Mentioned"]
                )}
              </td>

              <td>
                ${esc(
                  row["AI Development Sector"]
                )}
              </td>

              <td>
                ${esc(
                  row["AI Place of Visit"]
                )}
              </td>

              <td class="summary">
                ${esc(summary)}
              </td>

              <td>

                ${
                  url
                    ? `
                      <a
                        href="${escAttr(url)}"
                        target="_blank"
                        rel="noopener"
                      >
                        Open
                      </a>
                    `
                    : "—"
                }

              </td>

            </tr>

          `;

        }
      )
      .join("");


  const totalPages =
    Math.max(
      1,

      Math.ceil(
        state.filteredRows.length /
        state.pageSize
      )
    );


  /*
   * Safety:
   * Keep current page inside bounds.
   */

  if (
    state.page > totalPages
  ) {

    state.page =
      totalPages;
  }


  byId("pageInfo").textContent =
    `Page ${state.page} of ${totalPages}`;


  byId("prevPage").disabled =
    state.page <= 1;


  byId("nextPage").disabled =
    state.page >= totalPages;


  byId("tableNote").textContent =
    `${state.filteredRows.length.toLocaleString(
      "en-IN"
    )} posts match the current date range and filters.`;
}


/* ============================================================
   ESCAPE HELPERS
   ============================================================ */

function esc(value) {

  return String(
    value ?? ""
  )

    .replaceAll(
      "&",
      "&amp;"
    )

    .replaceAll(
      "<",
      "&lt;"
    )

    .replaceAll(
      ">",
      "&gt;"
    )

    .replaceAll(
      '"',
      "&quot;"
    )

    .replaceAll(
      "'",
      "&#039;"
    );
}


function escAttr(value) {

  return esc(value)
    .replaceAll(
      "`",
      "&#096;"
    );
}


/* ============================================================
   RESET FILTERS
   ============================================================ */

function resetFilters() {

  byId("f-author").value =
    "All";

  byId("f-main-category").value =
    "All";

  state.page = 1;

  applyAll();
}


/* ============================================================
   CSV
   ============================================================ */

function csvCell(value) {

  return `"${String(
    value ?? ""
  ).replaceAll(
    '"',
    '""'
  )}"`;
}


function downloadCsv() {

  const columns = [

    "Post Date",
    "Author",
    "AI Main Category",
    "AI Sub Category",
    "AI Event Type",
    "AI Party Mentioned",
    "AI Development Sector",
    "AI Government Scheme",
    "AI Place of Visit",
    "AI Opposition Mention",
    "AI Opposition Target",
    "AI Summary",
    "Post URL"

  ];


  const output = [

    columns
      .map(csvCell)
      .join(",")

  ];


  for (
    const row
    of state.filteredRows
  ) {

    output.push(

      columns
        .map(
          column =>
            csvCell(
              row[column]
            )
        )
        .join(",")

    );
  }


  const blob =
    new Blob(
      [
        output.join("\n")
      ],
      {
        type:
          "text/csv;charset=utf-8;"
      }
    );


  const url =
    URL.createObjectURL(
      blob
    );


  const link =
    document.createElement(
      "a"
    );


  link.href =
    url;


  link.download =
    `up-mla-social-media-${state.startDate}-to-${state.endDate}.csv`;


  document.body.appendChild(
    link
  );


  link.click();

  link.remove();

  URL.revokeObjectURL(
    url
  );
}


/* ============================================================
   LOAD DATA
   ============================================================ */

async function loadData() {

  try {

    const response =
      await fetch(
        DATA_URL,
        {
          cache:
            "no-store"
        }
      );


    if (!response.ok) {

      throw new Error(
        `HTTP ${response.status}`
      );
    }


    const payload =
      await response.json();


    state.allRows =
      Array.isArray(
        payload.rows
      )

        ? payload.rows.filter(
            row =>
              clean(
                row["Author"]
              )
          )

        : [];


    const updated =
      payload.generated_at
        ? new Date(
            payload.generated_at
          )
        : null;


    byId("dataStatus").textContent =
      `${state.allRows.length.toLocaleString(
        "en-IN"
      )} posts loaded`;


    byId("updatedAt").textContent =
      `Data updated: ${
        updated &&
        !isNaN(updated)
          ? updated.toLocaleString(
              "en-IN"
            )
          : "—"
      }`;


    populateFilters();

    initialiseDateState();

  }

  catch (error) {

    console.error(
      "Dashboard data load failed:",
      error
    );


    byId("dataStatus").textContent =
      "Data unavailable";


    byId("periodTitle").textContent =
      "Unable to load dashboard data";
  }
}


/* ============================================================
   EVENTS
   ============================================================ */

function bindEvents() {


  /*
   * DATE PRESETS
   */

  document
    .querySelectorAll(".preset")
    .forEach(
      button => {

        button.addEventListener(
          "click",
          () => {

            const today =
              new Date();


            const preset =
              button.dataset.preset;


            const start =
              new Date(today);


            if (
              preset === "7d"
            ) {

              start.setDate(
                start.getDate() - 6
              );

              setDateRange(
                start,
                today,
                preset
              );

              return;
            }


            if (
              preset === "30d"
            ) {

              start.setDate(
                start.getDate() - 29
              );

              setDateRange(
                start,
                today,
                preset
              );

              return;
            }


            if (
              preset === "today"
            ) {

              setDateRange(
                today,
                today,
                preset
              );

              return;
            }


            if (
              preset === "week"
            ) {

              setDateRange(
                startOfWeek(today),
                endOfWeek(today),
                preset
              );

              return;
            }


            if (
              preset === "month"
            ) {

              setDateRange(
                startOfMonth(today),
                endOfMonth(today),
                preset
              );
            }

          }
        );

      }
    );


  /*
   * CUSTOM DATE RANGE
   */

  byId("applyCustom")
    .addEventListener(
      "click",
      () => {

        const specific =
          byId(
            "specificDate"
          ).value;


        const from =
          byId(
            "fromDate"
          ).value;


        const to =
          byId(
            "toDate"
          ).value;


        if (specific) {

          const date =
            new Date(
              specific +
              "T00:00:00"
            );


          setDateRange(
            date,
            date,
            null
          );

          return;
        }


        if (
          !from ||
          !to ||
          from > to
        ) {

          alert(
            "Please select a valid From and To date."
          );

          return;
        }


        state.startDate =
          from;

        state.endDate =
          to;


        byId(
          "periodTitle"
        ).textContent =
          `${from} → ${to}`;


        document
          .querySelectorAll(".preset")
          .forEach(
            button =>
              button.classList.remove(
                "active"
              )
          );


        state.page = 1;

        applyAll();
      }
    );


  /*
   * RESET DATES
   */

  byId("resetDates")
    .addEventListener(
      "click",
      initialiseDateState
    );


  /*
   * RESET FILTERS
   */

  byId("resetFilters")
    .addEventListener(
      "click",
      resetFilters
    );


  /*
   * CSV
   */

  byId("downloadCsv")
    .addEventListener(
      "click",
      downloadCsv
    );


  /*
   * PAGINATION
   */

  byId("prevPage")
    .addEventListener(
      "click",
      () => {

        if (
          state.page > 1
        ) {

          state.page--;

          renderTable();
        }
      }
    );


  byId("nextPage")
    .addEventListener(
      "click",
      () => {

        const totalPages =
          Math.max(
            1,

            Math.ceil(
              state.filteredRows.length /
              state.pageSize
            )
          );


        if (
          state.page <
          totalPages
        ) {

          state.page++;

          renderTable();
        }
      }
    );
}


/* ============================================================
   START DASHBOARD
   ============================================================ */

bindEvents();

loadData();