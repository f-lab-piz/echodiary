import React, { useState } from "react";
import { createRoot } from "react-dom/client";

const API_BASE = "http://localhost:8000";

function App() {
  const [username, setUsername] = useState("demo-user");
  const [password, setPassword] = useState("demo-pass");
  const [token, setToken] = useState("");
  const [role, setRole] = useState("");
  const [accountId, setAccountId] = useState("demo-account");
  const [inputText, setInputText] = useState("");
  const [draft, setDraft] = useState("");
  const [log, setLog] = useState([]);
  const [diaryId, setDiaryId] = useState(null);
  const [personaId, setPersonaId] = useState(null);
  const [entryId, setEntryId] = useState(null);

  const appendLog = (message) => setLog((prev) => [...prev, message]);
  const authHeaders = token ? { Authorization: `Bearer ${token}` } : {};

  const login = async () => {
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) {
      appendLog(`로그인 실패: ${data.detail || "unknown error"}`);
      return;
    }
    setToken(data.access_token);
    setRole(data.role);
    appendLog(`로그인 성공: user=${data.username}, role=${data.role}`);
  };

  const signup = async () => {
    const res = await fetch(`${API_BASE}/api/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) {
      appendLog(`회원가입 실패: ${data.detail || "unknown error"}`);
      return;
    }
    appendLog(`회원가입 성공: user=${data.username}`);
  };

  const setup = async () => {
    if (!token) {
      appendLog("먼저 로그인하세요.");
      return;
    }

    const persona = await fetch(`${API_BASE}/api/personas`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders },
      body: JSON.stringify({
        account_id: accountId,
        name: "따뜻한 친구",
        tone: "다정한",
        description: "공감형 톤",
      }),
    }).then((r) => r.json());

    const diary = await fetch(`${API_BASE}/api/diaries`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders },
      body: JSON.stringify({ account_id: accountId, title: "나의 일기장" }),
    }).then((r) => r.json());

    await fetch(`${API_BASE}/api/diaries/${diary.id}/personas/${persona.id}`, { method: "POST", headers: authHeaders });
    setDiaryId(diary.id);
    setPersonaId(persona.id);
    appendLog(`setup 완료: diary=${diary.id}, persona=${persona.id}`);
  };

  const generate = async () => {
    if (!diaryId || !personaId) {
      appendLog("먼저 setup을 실행하세요.");
      return;
    }

    const data = await fetch(`${API_BASE}/api/entries/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders },
      body: JSON.stringify({ diary_id: diaryId, persona_id: personaId, input_text: inputText }),
    }).then((r) => r.json());

    setEntryId(data.id);
    setDraft(data.draft || "");
    appendLog(`draft 생성: entry=${data.id}`);
  };

  const save = async () => {
    if (!entryId) {
      appendLog("저장할 entry가 없습니다. generate를 먼저 실행하세요.");
      return;
    }

    const data = await fetch(`${API_BASE}/api/entries/${entryId}/save`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders },
      body: JSON.stringify({ draft }),
    }).then((r) => r.json());

    appendLog(`저장 완료: status=${data.status}`);
  };

  return (
    <main style={{ maxWidth: 760, margin: "40px auto", padding: "0 16px", fontFamily: "sans-serif" }}>
      <h1>EchoDiary MVP (React)</h1>
      <h3>로그인</h3>
      <label>Username</label>
      <input value={username} onChange={(e) => setUsername(e.target.value)} style={{ width: "100%", padding: 10, marginTop: 8 }} />
      <label style={{ marginTop: 8, display: "block" }}>Password</label>
      <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} style={{ width: "100%", padding: 10, marginTop: 8 }} />
      <div style={{ marginTop: 12 }}>
        <button onClick={signup} style={{ width: "100%", padding: 10, marginBottom: 8 }}>회원가입</button>
        <button onClick={login} style={{ width: "100%", padding: 10 }}>로그인</button>
      </div>
      <div style={{ marginTop: 8, color: "#444" }}>
        현재 권한: {role || "미로그인"}
      </div>

      {role === "admin" && (
        <section style={{ marginTop: 20, padding: 12, border: "1px solid #ddd", borderRadius: 8 }}>
          <h3 style={{ marginTop: 0 }}>관리자 페이지</h3>
          <p style={{ marginBottom: 0 }}>관리자 전용 기능은 이후 추가될 예정입니다.</p>
        </section>
      )}

      <label>Account ID</label>
      <input value={accountId} onChange={(e) => setAccountId(e.target.value)} style={{ width: "100%", padding: 10, marginTop: 8 }} />
      <div style={{ marginTop: 12 }}>
        <button onClick={setup} style={{ width: "100%", padding: 10 }}>1) 샘플 Persona/Diary 생성</button>
      </div>

      <div style={{ marginTop: 16 }}>
        <label>Input Text</label>
        <textarea value={inputText} onChange={(e) => setInputText(e.target.value)} rows={4} style={{ width: "100%", padding: 10, marginTop: 8 }} />
        <button onClick={generate} style={{ width: "100%", padding: 10, marginTop: 8 }}>2) Draft 생성</button>
      </div>

      <div style={{ marginTop: 16 }}>
        <label>Draft</label>
        <textarea value={draft} onChange={(e) => setDraft(e.target.value)} rows={6} style={{ width: "100%", padding: 10, marginTop: 8 }} />
        <button onClick={save} style={{ width: "100%", padding: 10, marginTop: 8 }}>3) 저장</button>
      </div>

      <h3>로그</h3>
      <pre style={{ background: "#f4f4f4", padding: 12, borderRadius: 8 }}>{log.join("\n")}</pre>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
