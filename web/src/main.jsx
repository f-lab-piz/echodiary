import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";

const API_BASE = "http://localhost:8000";
const TOKEN_KEY = "echodiary_token";
const USER_KEY = "echodiary_user";

const style = `
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

:root {
  --bg: #f6efe6;
  --bg-soft: #f2e3cf;
  --ink: #1f1a15;
  --ink-soft: #64584d;
  --line: #d9c6ab;
  --card: #fffaf3;
  --accent: #d5553f;
  --accent-strong: #b53d2a;
  --ok: #235f34;
  --warn: #8b5a00;
  --error: #9a2c27;
}

* { box-sizing: border-box; }
body {
  margin: 0;
  background:
    radial-gradient(circle at 10% 0%, #f8e2c8 0%, transparent 34%),
    radial-gradient(circle at 90% 100%, #f0d6bd 0%, transparent 34%),
    var(--bg);
  color: var(--ink);
  font-family: "IBM Plex Sans", "Noto Sans KR", sans-serif;
}

a { color: inherit; }

.app-shell {
  max-width: 1080px;
  margin: 0 auto;
  padding: 20px 16px 48px;
}

.nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 20px;
}

.brand {
  font-family: "Fraunces", serif;
  font-size: 28px;
  margin: 0;
}

.nav-right {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.link-btn,
.btn {
  border: 1px solid var(--line);
  background: var(--card);
  color: var(--ink);
  border-radius: 12px;
  padding: 10px 14px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
}

.btn-primary {
  background: var(--accent);
  color: #fff8ee;
  border-color: var(--accent);
}

.btn-primary:hover { background: var(--accent-strong); }

.card {
  border: 1px solid var(--line);
  background: var(--card);
  border-radius: 18px;
  padding: 18px;
  box-shadow: 0 12px 30px rgba(72, 43, 10, 0.08);
}

.hero-title {
  font-family: "Fraunces", serif;
  font-size: clamp(34px, 7vw, 58px);
  line-height: 1.03;
  margin: 0;
}

.hero-sub {
  margin-top: 12px;
  color: var(--ink-soft);
  max-width: 680px;
}

label {
  display: block;
  font-size: 14px;
  margin-bottom: 8px;
  color: var(--ink-soft);
}

input,
textarea {
  width: 100%;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: #fffcf7;
  font-size: 15px;
  padding: 12px;
  font-family: inherit;
}

textarea { min-height: 130px; resize: vertical; }

.stack { display: grid; gap: 14px; }

.grid-main {
  display: grid;
  gap: 16px;
  grid-template-columns: 1.2fr 0.8fr;
  margin-top: 16px;
}

.badge {
  display: inline-flex;
  gap: 8px;
  align-items: center;
  border: 1px solid var(--line);
  background: var(--bg-soft);
  border-radius: 999px;
  font-size: 13px;
  color: var(--ink-soft);
  padding: 6px 12px;
}

.status {
  font-size: 14px;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid;
}
.status.ok { color: var(--ok); border-color: #7db68a; background: #edf8ef; }
.status.warn { color: var(--warn); border-color: #cda35b; background: #fff8ea; }
.status.error { color: var(--error); border-color: #d79b97; background: #fff0ef; }

.entry-card { margin-top: 12px; }
.entry-date { font-size: 13px; color: var(--ink-soft); }
.entry-text { white-space: pre-wrap; margin-top: 8px; line-height: 1.55; }

.auth-wrap {
  max-width: 420px;
  margin: 7vh auto 0;
}

@media (max-width: 900px) {
  .grid-main { grid-template-columns: 1fr; }
}
`;

function nowDateLabel() {
  return new Date().toISOString().slice(0, 10);
}

function parsePath() {
  const p = window.location.pathname;
  if (["/", "/login", "/signup", "/diaries"].includes(p)) return p;
  return "/";
}

function routeTo(path) {
  if (window.location.pathname === path) return;
  window.history.pushState({}, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
}

function App() {
  const [path, setPath] = useState(parsePath());
  const [token, setToken] = useState(localStorage.getItem(TOKEN_KEY) || "");
  const [user, setUser] = useState(localStorage.getItem(USER_KEY) || "");
  const [role, setRole] = useState("");

  useEffect(() => {
    const onPop = () => setPath(parsePath());
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  useEffect(() => {
    if (!token && path !== "/login" && path !== "/signup") routeTo("/login");
  }, [token, path]);

  const authHeaders = useMemo(() => (token ? { Authorization: `Bearer ${token}` } : {}), [token]);

  const onLoginSuccess = (payload) => {
    localStorage.setItem(TOKEN_KEY, payload.access_token);
    localStorage.setItem(USER_KEY, payload.username);
    setToken(payload.access_token);
    setUser(payload.username);
    setRole(payload.role);
    routeTo("/");
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setToken("");
    setUser("");
    setRole("");
    routeTo("/login");
  };

  if (path === "/login") return <LoginPage onLoginSuccess={onLoginSuccess} />;
  if (path === "/signup") return <SignupPage />;
  if (!token) return null;

  return (
    <div className="app-shell">
      <style>{style}</style>
      <header className="nav">
        <h1 className="brand">EchoDiary</h1>
        <div className="nav-right">
          <button className="link-btn" onClick={() => routeTo("/")}>메인</button>
          <button className="link-btn" onClick={() => routeTo("/diaries")}>일기 보관</button>
          <button className="btn" onClick={logout}>로그아웃</button>
        </div>
      </header>
      {path === "/" ? (
        <MainPage authHeaders={authHeaders} username={user} role={role} />
      ) : (
        <DiaryArchivePage authHeaders={authHeaders} username={user} />
      )}
    </div>
  );
}

function LoginPage({ onLoginSuccess }) {
  const [username, setUsername] = useState("demo-user");
  const [password, setPassword] = useState("demo-pass");
  const [message, setMessage] = useState("");

  const login = async () => {
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) {
      setMessage(data.detail || "로그인 실패");
      return;
    }
    onLoginSuccess(data);
  };

  return (
    <div className="app-shell auth-wrap">
      <style>{style}</style>
      <div className="card stack">
        <h1 className="brand" style={{ margin: 0 }}>EchoDiary</h1>
        <p className="hero-sub" style={{ marginTop: 0 }}>당신의 하루를 가장 따뜻한 문장으로 남깁니다.</p>
        <div>
          <label>아이디</label>
          <input value={username} onChange={(e) => setUsername(e.target.value)} />
        </div>
        <div>
          <label>비밀번호</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        {message && <div className="status error">{message}</div>}
        <button className="btn btn-primary" onClick={login}>로그인</button>
        <button className="btn" onClick={() => routeTo("/signup")}>회원가입으로 이동</button>
      </div>
    </div>
  );
}

function SignupPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [ok, setOk] = useState(false);

  const signup = async () => {
    const res = await fetch(`${API_BASE}/api/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) {
      setOk(false);
      setMessage(data.detail || "회원가입 실패");
      return;
    }
    setOk(true);
    setMessage(`회원가입 완료: ${data.username}`);
  };

  return (
    <div className="app-shell auth-wrap">
      <style>{style}</style>
      <div className="card stack">
        <h1 className="brand" style={{ margin: 0 }}>회원가입</h1>
        <div>
          <label>아이디</label>
          <input value={username} onChange={(e) => setUsername(e.target.value)} />
        </div>
        <div>
          <label>비밀번호</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        {message && <div className={`status ${ok ? "ok" : "error"}`}>{message}</div>}
        <button className="btn btn-primary" onClick={signup}>회원가입</button>
        <button className="btn" onClick={() => routeTo("/login")}>로그인으로 이동</button>
      </div>
    </div>
  );
}

function MainPage({ authHeaders, username, role }) {
  const [accountId] = useState(username || "demo-account");
  const [diaryId, setDiaryId] = useState("");
  const [personaId, setPersonaId] = useState("");
  const [inputText, setInputText] = useState("");
  const [draft, setDraft] = useState("");
  const [entryId, setEntryId] = useState("");
  const [status, setStatus] = useState({ type: "warn", text: "입력 후 제출하면 오늘 날짜로 초안을 생성합니다." });

  useEffect(() => {
    const boot = async () => {
      const personaListRes = await fetch(`${API_BASE}/api/personas?account_id=${accountId}`, { headers: authHeaders });
      const personas = personaListRes.ok ? await personaListRes.json() : [];

      let currentPersona = personas[0];
      if (!currentPersona) {
        const personaRes = await fetch(`${API_BASE}/api/personas`, {
          method: "POST",
          headers: { "Content-Type": "application/json", ...authHeaders },
          body: JSON.stringify({
            account_id: accountId,
            name: "기록 도우미",
            tone: "따뜻한",
            description: "오늘 감정을 다독이는 문장",
          }),
        });
        if (!personaRes.ok) {
          setStatus({ type: "error", text: "초기 Persona 생성에 실패했습니다." });
          return;
        }
        currentPersona = await personaRes.json();
      }

      const diaryListRes = await fetch(`${API_BASE}/api/diaries?account_id=${accountId}`, { headers: authHeaders });
      const diaries = diaryListRes.ok ? await diaryListRes.json() : [];

      let currentDiary = diaries[0];
      if (!currentDiary) {
        const diaryRes = await fetch(`${API_BASE}/api/diaries`, {
          method: "POST",
          headers: { "Content-Type": "application/json", ...authHeaders },
          body: JSON.stringify({ account_id: accountId, title: "오늘의 EchoDiary" }),
        });
        if (!diaryRes.ok) {
          setStatus({ type: "error", text: "기본 일기장 생성에 실패했습니다." });
          return;
        }
        currentDiary = await diaryRes.json();
      }

      await fetch(`${API_BASE}/api/diaries/${currentDiary.id}/personas/${currentPersona.id}`, {
        method: "POST",
        headers: authHeaders,
      });

      setDiaryId(currentDiary.id);
      setPersonaId(currentPersona.id);
    };
    boot();
  }, [accountId, authHeaders]);

  const generateDraft = async () => {
    if (!inputText.trim()) {
      setStatus({ type: "warn", text: "오늘 하루를 한 줄 이상 입력해주세요." });
      return;
    }
    setStatus({ type: "warn", text: "초안을 생성 중입니다..." });

    const res = await fetch(`${API_BASE}/api/entries/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders },
      body: JSON.stringify({ diary_id: diaryId, persona_id: personaId, input_text: `[${nowDateLabel()}] ${inputText}` }),
    });
    const data = await res.json();
    if (!res.ok) {
      setStatus({ type: "error", text: data.detail || "초안 생성 실패" });
      return;
    }
    setEntryId(data.id);
    setDraft(data.draft || "");
    setStatus({ type: "ok", text: "초안 생성이 완료됐습니다. 문장을 다듬고 저장하세요." });
  };

  const saveDraft = async () => {
    if (!entryId || !draft.trim()) {
      setStatus({ type: "warn", text: "저장할 초안이 없습니다." });
      return;
    }
    const res = await fetch(`${API_BASE}/api/entries/${entryId}/save`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders },
      body: JSON.stringify({ draft }),
    });
    const data = await res.json();
    if (!res.ok) {
      setStatus({ type: "error", text: data.detail || "저장 실패" });
      return;
    }
    setStatus({ type: "ok", text: "저장이 완료됐습니다. '일기 보관'에서 확인하세요." });
  };

  return (
    <>
      <section className="card">
        <h2 className="hero-title">오늘 하루는 어떠신가요</h2>
        <p className="hero-sub">하루를 자유롭게 적어주세요. EchoDiary가 오늘 날짜의 일기 초안으로 정리해드립니다.</p>
        <div className="badge">{nowDateLabel()} · {role || "user"}</div>
      </section>

      <section className="grid-main">
        <div className="card stack">
          <div>
            <label>오늘의 기록</label>
            <textarea value={inputText} onChange={(e) => setInputText(e.target.value)} placeholder="오늘 느꼈던 감정, 사건, 생각을 편하게 적어주세요." />
          </div>
          <button className="btn btn-primary" onClick={generateDraft}>제출하고 초안 만들기</button>
          <div className={`status ${status.type}`}>{status.text}</div>
        </div>

        <div className="card stack">
          <div>
            <label>생성된 일기 초안</label>
            <textarea value={draft} onChange={(e) => setDraft(e.target.value)} placeholder="생성된 문장이 여기에 표시됩니다." />
          </div>
          <button className="btn" onClick={saveDraft}>오늘 일기 저장</button>
        </div>
      </section>
    </>
  );
}

function DiaryArchivePage({ authHeaders, username }) {
  const [entries, setEntries] = useState([]);
  const [status, setStatus] = useState("불러오는 중...");

  useEffect(() => {
    const load = async () => {
      const diariesRes = await fetch(`${API_BASE}/api/diaries?account_id=${username}`, { headers: authHeaders });
      if (!diariesRes.ok) {
        setStatus("일기장을 불러오지 못했습니다.");
        return;
      }
      const diaries = await diariesRes.json();
      if (!diaries.length) {
        setEntries([]);
        setStatus("저장된 일기가 없습니다.");
        return;
      }

      const firstDiaryId = diaries[0].id;
      const entriesRes = await fetch(`${API_BASE}/api/diaries/${firstDiaryId}/entries`, { headers: authHeaders });
      if (!entriesRes.ok) {
        setStatus("저장된 일기 조회에 실패했습니다.");
        return;
      }
      const allEntries = await entriesRes.json();
      const savedEntries = allEntries.filter((e) => e.status === "saved");
      setEntries(savedEntries);
      setStatus(savedEntries.length ? "" : "저장된 일기가 없습니다.");
    };
    load();
  }, [authHeaders, username]);

  return (
    <section className="card">
      <h2 className="hero-title" style={{ fontSize: "clamp(30px, 5vw, 44px)" }}>일기 보관함</h2>
      <p className="hero-sub">저장한 일기를 시간순으로 확인할 수 있습니다.</p>
      {status && <div className="status warn" style={{ marginTop: 10 }}>{status}</div>}
      {entries.map((entry) => (
        <article className="card entry-card" key={entry.id}>
          <div className="entry-date">작성일 {entry.created_at.slice(0, 10)}</div>
          <div className="entry-text">{entry.draft}</div>
        </article>
      ))}
    </section>
  );
}

createRoot(document.getElementById("root")).render(<App />);
