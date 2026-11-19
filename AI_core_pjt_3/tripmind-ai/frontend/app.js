const $ = (id) => document.getElementById(id);
let sessionId = sessionStorage.getItem("tripmind-session");
let requestPending = false;
let planSelection = 0;
let logSelection = 0;

function node(tag, text, className) {
  const item = document.createElement(tag);
  if (text) item.textContent = text;
  if (className) item.className = className;
  return item;
}

function button(label, action, className = "secondary") {
  const item = node("button", label, className);
  item.type = "button";
  item.addEventListener("click", action);
  return item;
}

async function api(path, method = "GET", body) {
  let response;
  try {
    response = await fetch("/api" + path, {
      method, headers: body ? { "Content-Type": "application/json" } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new Error("서버에 연결하지 못했습니다.");
  }
  if (response.status === 204) return null;
  const result = await response.json().catch(() => null);
  if (!response.ok || !result) throw new Error(result?.error?.message || "요청을 처리하지 못했습니다.");
  return result;
}

function appendMessage(text, className) {
  const box = $("messages");
  box.append(node("p", text, "message " + className));
  box.scrollTop = box.scrollHeight;
}

const stages = {
  analyze: "요청 분석", plan: "작업 계획", execute: "Tool 실행", integrate: "결과 통합",
  decide: "제약 판단", replan: "재계획", respond: "최종 응답",
};

function showEvents(list, events) {
  list.replaceChildren();
  for (const event of events) {
    const p = event.payload;
    const stage = stages[event.node] || event.node;
    const labels = {
      node_enter: () => stage + " 시작",
      node_exit: () => stage + (p.ok ? " 완료" : " 실패") + " · " + p.duration_ms + "ms",
      tool_requested: () => p.tool + " 호출",
      tool_completed: () => p.tool + " · " + (p.ok ? "성공" : p.error_code) + " · " + p.duration_ms + "ms",
      tool_reused: () => p.tool + " 결과 재사용",
      llm_decision: () => "요청 분류 · " + p.intent,
      conditions_extracted: () => p.needs_input ? "추가 입력 필요" : "여행 조건 확인",
      plan_created: () => p.tools.join(" → "),
      constraints_checked: () => "적합 후보 " + p.matched + " / 목표 " + p.target,
      replanned: () => "재계획 " + p.count + "회 · " + p.reason,
      run_finished: () => "응답 완료 · " + p.duration_ms + "ms",
    };
    list.append(node("li", labels[event.type]?.() || event.type, event.type === "replanned" ? "replan" : ""));
  }
}

function conflictText(result, verb) {
  return result.conflicts.length
    ? verb + "했습니다. 시간이 겹치는 계획 · " + result.conflicts.map((p) => p.title).join(", ")
    : verb + "했습니다.";
}

function showDraft(plan) {
  const container = $("draft");
  container.replaceChildren();
  container.hidden = !plan;
  if (!plan) return;
  const save = button("이 일정 저장", async () => {
    save.disabled = true;
    try {
      const result = await api("/plans", "POST", plan);
      $("chat-status").textContent = conflictText(result, "저장");
    } catch (error) {
      $("chat-status").textContent = error.message;
      save.disabled = false;
    }
  }, "");
  container.append(save);
}

function showEvidence(evidence) {
  if (!evidence.length) return;
  const sources = node("div", "", "message assistant");
  sources.append(node("strong", "출처"));
  const links = node("ul");
  for (const item of evidence) {
    const row = node("li");
    const link = node("a", item.source + " · " + item.fact);
    link.href = item.reference_url;
    link.target = "_blank";
    link.rel = "noopener";
    row.append(link);
    links.append(row);
  }
  sources.append(links);
  $("messages").append(sources);
  $("messages").scrollTop = $("messages").scrollHeight;
}

$("chat-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = $("message").value.trim();
  if (requestPending || !message) return;
  requestPending = true;
  $("send").disabled = true;
  $("new-chat").disabled = true;
  $("message").value = "";
  $("suggestions").hidden = true;
  $("chat-status").textContent = "여행 조건을 확인하고 있습니다…";
  $("events").replaceChildren();
  $("event-empty").hidden = false;
  showDraft(null);
  appendMessage(message, "user");
  try {
    const result = await api("/chat", "POST", { message, session_id: sessionId });
    sessionId = result.session_id;
    sessionStorage.setItem("tripmind-session", sessionId);
    appendMessage(result.reply, "assistant");
    showEvidence(result.evidence);
    const warnings = [...new Set(result.warnings.map((w) => [w.tool, w.message, w.code].filter(Boolean).join(" · ")))];
    for (const warning of warnings) appendMessage(warning, "assistant notice");
    $("event-empty").hidden = Boolean(result.events.length);
    showEvents($("events"), result.events);
    showDraft(result.draft_plan);
    $("chat-status").textContent = "";
  } catch (error) {
    $("chat-status").textContent = error.message;
    $("message").value = message;
  } finally {
    requestPending = false;
    $("send").disabled = false;
    $("new-chat").disabled = false;
  }
});

for (const chip of document.querySelectorAll(".chip")) {
  chip.addEventListener("click", () => {
    const kstDate = new Intl.DateTimeFormat("sv-SE", { timeZone: "Asia/Seoul" })
      .format(new Date(Date.now() + 2 * 86400000));
    $("message").value = chip.dataset.example === "plan"
      ? kstDate + " " + chip.dataset.region + ", 오전 10시부터 오후 6시까지 관광지 3곳 추천해 줘."
      : kstDate + " " + chip.dataset.region + "에 비가 오면 실내 관광지로 바꿔 줘.";
    $("message").focus();
  });
}

$("new-chat").addEventListener("click", () => {
  sessionId = null;
  sessionStorage.removeItem("tripmind-session");
  $("messages").replaceChildren();
  appendMessage("새 여행 조건을 알려 주세요.", "assistant");
  $("events").replaceChildren();
  $("event-empty").hidden = false;
  $("chat-status").textContent = "";
  $("message").value = "";
  $("suggestions").hidden = false;
  showDraft(null);
});

async function loadPlans(offset = 0) {
  const list = $("plan-list");
  if (!offset) list.replaceChildren(node("p", "불러오는 중…", "muted"));
  try {
    const result = await api("/plans?offset=" + offset);
    if (!offset) list.replaceChildren();
    if (!result.total) list.append(node("p", "저장한 계획이 없습니다.", "muted"));
    for (const plan of result.items) {
      list.append(button(plan.title + " · " + plan.visit_date + " · " + plan.start_time + "–" + plan.end_time,
        () => openPlan(plan.id)));
    }
    if (offset + result.items.length < result.total) {
      const more = button("계획 더 보기", () => {
        more.remove();
        loadPlans(offset + result.items.length);
      });
      list.append(more);
    }
  } catch (error) {
    if (!offset) list.replaceChildren();
    $("plan-status").textContent = error.message;
  }
}

function field(form, label, name, type, value) {
  const wrapper = node("label", label);
  const input = node(type === "textarea" ? "textarea" : "input");
  if (type !== "textarea") input.type = type;
  input.name = name;
  input.value = value || "";
  input.required = !["notes", "items"].includes(name);
  wrapper.append(input);
  form.append(wrapper);
  return input;
}

async function openPlan(id) {
  const selection = ++planSelection;
  const panel = $("plan-detail");
  panel.hidden = false;
  panel.replaceChildren(node("p", "불러오는 중…", "muted"));
  try {
    const plan = await api("/plans/" + id);
    if (selection !== planSelection) return;
    const form = node("form");
    field(form, "제목", "title", "text", plan.title);
    field(form, "지역", "region", "text", plan.region);
    field(form, "날짜", "visit_date", "date", plan.visit_date);
    field(form, "시작 시간", "start_time", "time", plan.start_time);
    field(form, "종료 시간", "end_time", "time", plan.end_time);
    field(form, "메모", "notes", "textarea", plan.notes);
    const stops = plan.items.map((item) => item.title).join("\n");
    field(form, "방문 장소 · 한 줄에 한 곳", "items", "textarea", stops);
    const items = node("ol");
    for (const item of plan.items) {
      items.append(node("li", item.title + (item.address ? " · " + item.address : "")));
    }
    const actions = node("div", "", "actions");
    const submit = node("button", "변경 저장");
    submit.type = "submit";
    const remove = button("삭제", async () => {
      if (!confirm("이 여행 계획을 삭제할까요?")) return;
      submit.disabled = remove.disabled = true;
      try {
        await api("/plans/" + id, "DELETE");
        if (selection === planSelection) panel.hidden = true;
        $("plan-status").textContent = "계획을 삭제했습니다.";
        await loadPlans();
      } catch (error) {
        $("plan-status").textContent = error.message;
        submit.disabled = remove.disabled = false;
      }
    }, "danger");
    actions.append(submit, remove);
    form.append(actions);
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const values = Object.fromEntries(new FormData(form));
      const titles = values.items;
      delete values.items;
      values.notes ||= null;
      if (titles !== stops) {
        const existing = new Map(plan.items.map((item) => [item.title, item]));
        values.items = titles.split("\n").map((title) => title.trim()).filter(Boolean)
          .map((title) => existing.get(title) || { title });
      }
      submit.disabled = remove.disabled = true;
      try {
        const result = await api("/plans/" + id, "PATCH", values);
        $("plan-status").textContent = conflictText(result, "수정");
        await loadPlans();
        if (selection === planSelection) await openPlan(id);
      } catch (error) {
        $("plan-status").textContent = error.message;
      } finally {
        submit.disabled = remove.disabled = false;
      }
    });
    panel.replaceChildren(node("h2", "계획 상세"), items, form);
  } catch (error) {
    if (selection !== planSelection) return;
    panel.hidden = true;
    $("plan-status").textContent = error.message;
  }
}

async function loadLogs(offset = 0) {
  const list = $("log-list");
  if (!offset) list.replaceChildren(node("p", "불러오는 중…", "muted"));
  try {
    const result = await api("/logs?offset=" + offset);
    if (!offset) list.replaceChildren();
    if (!result.total) list.append(node("p", "저장된 실행 로그가 없습니다.", "muted"));
    for (const log of result.items) {
      const time = new Date(log.last_event_at).toLocaleString("ko-KR", { timeZone: "Asia/Seoul" });
      list.append(button(time + " · 실행 " + log.run_count + "건 · 이벤트 " + log.event_count + "건",
        () => openLog(log.session_id)));
    }
    if (offset + result.items.length < result.total) {
      const more = button("로그 더 보기", () => {
        more.remove();
        loadLogs(offset + result.items.length);
      });
      list.append(more);
    }
  } catch (error) {
    if (!offset) list.replaceChildren();
    $("log-status").textContent = error.message;
  }
}

async function openLog(id) {
  const selection = ++logSelection;
  const panel = $("log-detail");
  panel.hidden = false;
  panel.replaceChildren(node("p", "불러오는 중…", "muted"));
  try {
    const result = await api("/logs/" + id);
    if (selection !== logSelection) return;
    const events = node("ol", "", "event-list");
    showEvents(events, result.events);
    const remove = button("이 세션의 로그 삭제", async () => {
      if (!confirm("이 세션의 실행 로그를 삭제할까요?")) return;
      remove.disabled = true;
      try {
        await api("/logs/" + id, "DELETE");
        if (selection === logSelection) panel.hidden = true;
        $("log-status").textContent = "실행 로그를 삭제했습니다.";
        await loadLogs();
      } catch (error) {
        $("log-status").textContent = error.message;
        remove.disabled = false;
      }
    }, "danger");
    panel.replaceChildren(node("h2", "실행 이력"), events, node("div", "", "actions"));
    panel.lastElementChild.append(remove);
  } catch (error) {
    if (selection !== logSelection) return;
    panel.hidden = true;
    $("log-status").textContent = error.message;
  }
}

for (const tab of document.querySelectorAll(".tab")) {
  tab.addEventListener("click", () => {
    for (const other of document.querySelectorAll(".tab")) other.removeAttribute("aria-current");
    tab.setAttribute("aria-current", "page");
    for (const view of document.querySelectorAll(".view")) view.hidden = view.id !== tab.dataset.view;
    if (tab.dataset.view === "plans") loadPlans();
    if (tab.dataset.view === "logs") loadLogs();
  });
}
$("refresh-plans").addEventListener("click", () => loadPlans());
$("refresh-logs").addEventListener("click", () => loadLogs());
