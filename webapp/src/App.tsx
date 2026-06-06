import { useCallback, useEffect, useState, type CSSProperties } from "react";

type Status = {
  mcp_name?: string;
  mcp_version?: string;
  upstream_configured?: boolean;
  upstream_path?: string | null;
  upstream_python_ready?: boolean;
  stablewm_home?: string | null;
  default_policy_ready?: boolean;
  checkpoint_exists?: boolean;
  device?: string;
  active_job?: { job_id: string; kind: string; status: string; running: boolean } | null;
};

type Job = {
  job_id: string;
  kind: string;
  status: string;
  running: boolean;
  command?: string[];
  log_tail?: string[];
};

type Checkpoint = {
  relative: string;
  kind: string;
  size_bytes: number;
};

export function App() {
  const [status, setStatus] = useState<Status | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [checkpoints, setCheckpoints] = useState<Checkpoint[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [dataEnv, setDataEnv] = useState("pusht");
  const [policy, setPolicy] = useState("pusht/lewm");

  const refresh = useCallback(async () => {
    try {
      const [s, j, c] = await Promise.all([
        fetch("/api/status").then((r) => {
          if (!r.ok) throw new Error(`status HTTP ${r.status}`);
          return r.json() as Promise<Status>;
        }),
        fetch("/api/jobs").then((r) => r.json() as Promise<{ jobs?: Job[] }>),
        fetch("/api/checkpoints").then((r) => r.json() as Promise<{ checkpoints?: Checkpoint[] }>),
      ]);
      setStatus(s);
      setJobs(j.jobs ?? []);
      setCheckpoints(c.checkpoints ?? []);
      setErr(null);
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    }
  }, []);

  useEffect(() => {
    void refresh();
    const id = setInterval(() => void refresh(), 8000);
    return () => clearInterval(id);
  }, [refresh]);

  const runTrain = async () => {
    setBusy(true);
    try {
      const r = await fetch("/api/jobs/train", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ data_env: dataEnv }),
      });
      const body = await r.json();
      if (!r.ok) throw new Error(body.detail ?? `HTTP ${r.status}`);
      await refresh();
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  const runEval = async () => {
    setBusy(true);
    try {
      const r = await fetch("/api/jobs/eval", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ policy }),
      });
      const body = await r.json();
      if (!r.ok) throw new Error(body.detail ?? `HTTP ${r.status}`);
      await refresh();
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  const stopJob = async () => {
    setBusy(true);
    try {
      await fetch("/api/jobs/stop", { method: "POST" });
      await refresh();
    } finally {
      setBusy(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        padding: "2rem 1rem",
      }}
    >
      <div
        style={{
          maxWidth: 820,
          width: "100%",
          padding: "1.75rem",
          borderRadius: 16,
          background: "rgba(15, 23, 42, 0.55)",
          border: "1px solid rgba(148, 163, 184, 0.25)",
          boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.45)",
          backdropFilter: "blur(12px)",
        }}
      >
        <h1 style={{ margin: "0 0 0.5rem", fontWeight: 600, letterSpacing: "-0.02em" }}>
          LeWM-MCP
        </h1>
        <p style={{ margin: "0 0 0.75rem", color: "#94a3b8", fontSize: "0.95rem" }}>
          Real subprocess bridge to <strong>lucas-maes/le-wm</strong> — <code>train.py</code> and{" "}
          <code>eval.py</code> in upstream Python 3.10 venv.
        </p>
        <p style={{ margin: "0 0 1.25rem", color: "#94a3b8", fontSize: "0.85rem" }}>
          Paper:{" "}
          <a href="https://arxiv.org/abs/2603.19312" target="_blank" rel="noreferrer" style={{ color: "#93c5fd" }}>
            arXiv:2603.19312
          </a>{" "}
          (LeWorldModel) · full text in{" "}
          <strong>arxiv-mcp</strong> depot after <code>tools/ingest_lewm_paper.ps1</code>
        </p>

        {err && <p style={{ color: "#f87171" }}>{err}</p>}

        {status && (
          <dl
            style={{
              display: "grid",
              gridTemplateColumns: "160px 1fr",
              gap: "0.5rem 1rem",
              fontSize: "0.9rem",
            }}
          >
            <dt style={{ color: "#94a3b8" }}>Upstream</dt>
            <dd style={{ margin: 0 }}>
              {status.upstream_configured ? status.upstream_path : "not found — run bootstrap_upstream.ps1"}
            </dd>
            <dt style={{ color: "#94a3b8" }}>Upstream venv</dt>
            <dd style={{ margin: 0 }}>{status.upstream_python_ready ? "ready" : "missing"}</dd>
            <dt style={{ color: "#94a3b8" }}>STABLEWM_HOME</dt>
            <dd style={{ margin: 0, fontFamily: "monospace", fontSize: "0.8rem" }}>{status.stablewm_home}</dd>
            <dt style={{ color: "#94a3b8" }}>Policy</dt>
            <dd style={{ margin: 0 }}>{status.default_policy_ready ? "checkpoint ok" : "not ready"}</dd>
            <dt style={{ color: "#94a3b8" }}>Device</dt>
            <dd style={{ margin: 0 }}>{status.device}</dd>
            <dt style={{ color: "#94a3b8" }}>Active job</dt>
            <dd style={{ margin: 0 }}>
              {status.active_job
                ? `${status.active_job.kind} ${status.active_job.job_id} (${status.active_job.status})`
                : "none"}
            </dd>
          </dl>
        )}

        <div style={{ marginTop: "1.25rem", display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
          <select
            value={dataEnv}
            onChange={(e) => setDataEnv(e.target.value)}
            style={{ padding: "0.4rem 0.6rem", borderRadius: 8, background: "#1e293b", color: "#e2e8f0", border: "1px solid #334155" }}
          >
            <option value="pusht">train: pusht</option>
            <option value="tworoom">train: tworoom</option>
            <option value="dmc">train: dmc</option>
            <option value="ogb">train: ogb</option>
          </select>
          <button type="button" onClick={runTrain} disabled={busy} style={btnStyle}>
            Start train job
          </button>
          <input
            value={policy}
            onChange={(e) => setPolicy(e.target.value)}
            placeholder="policy e.g. pusht/lewm"
            style={{ flex: 1, minWidth: 140, padding: "0.4rem 0.6rem", borderRadius: 8, background: "#1e293b", color: "#e2e8f0", border: "1px solid #334155" }}
          />
          <button type="button" onClick={runEval} disabled={busy} style={btnStyle}>
            Start eval job
          </button>
          <button type="button" onClick={stopJob} disabled={busy} style={btnStyle}>
            Stop job
          </button>
          <button type="button" onClick={() => void refresh()} disabled={busy} style={btnStyle}>
            Refresh
          </button>
        </div>

        {jobs.length > 0 && (
          <div style={{ marginTop: "1.25rem" }}>
            <h2 style={{ fontSize: "0.95rem", color: "#cbd5e1" }}>Recent jobs</h2>
            <ul style={{ margin: 0, paddingLeft: "1.2rem", fontSize: "0.85rem", color: "#94a3b8" }}>
              {jobs.slice(0, 5).map((j) => (
                <li key={j.job_id}>
                  {j.kind} · {j.status} · <code>{j.job_id}</code>
                </li>
              ))}
            </ul>
          </div>
        )}

        {checkpoints.length > 0 && (
          <div style={{ marginTop: "1rem", fontSize: "0.8rem", color: "#64748b" }}>
            {checkpoints.length} checkpoint(s) under STABLEWM_HOME
          </div>
        )}

        <footer style={{ marginTop: "1.5rem", fontSize: "0.8rem", color: "#64748b" }}>
          API <strong>10927</strong> · Vite <strong>10928</strong> · MCP <code>/mcp</code>
        </footer>
      </div>
    </div>
  );
}

const btnStyle: CSSProperties = {
  padding: "0.4rem 0.75rem",
  borderRadius: 8,
  border: "1px solid #475569",
  background: "#334155",
  color: "#f1f5f9",
  cursor: "pointer",
};
