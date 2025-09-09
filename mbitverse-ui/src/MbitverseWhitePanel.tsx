import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
// @ts-ignore
import remarkGfm from "remark-gfm";

// Mbitverse — White Panel Frontend with Graphics
// Purpose: user pastes news, clicks Run, sees agent cards with icons
//          and a highlighted Meta Reviewer panel, all on a white background.
// Uses TailwindCSS for styling.

// ---- Types ----
type Reaction = { personality: string; reaction: string };

type PanelResponse = {
  news: string;
  results: Reaction[];
  meta_review?: string | null;
  errors?: Record<string, string>;
};

const DEFAULT_NEWS = `NVIDIA unveils an energy‑efficient GPU architecture aimed at hyperscale datacenters.\nVendors expect lower TCO due to reduced power draw.`;

// Assign each MBTI type a color and emoji icon for visual flair
const AGENT_STYLE: Record<string, { color: string; icon: string }> = {
  ISTJ: { color: "bg-blue-50 border-blue-200", icon: "📘" },
  ISFJ: { color: "bg-cyan-50 border-cyan-200", icon: "🛡️" },
  INFJ: { color: "bg-indigo-50 border-indigo-200", icon: "🔮" },
  INTJ: { color: "bg-purple-50 border-purple-200", icon: "♟️" },
  ISTP: { color: "bg-green-50 border-green-200", icon: "🛠️" },
  ISFP: { color: "bg-emerald-50 border-emerald-200", icon: "🎨" },
  INFP: { color: "bg-pink-50 border-pink-200", icon: "💭" },
  INTP: { color: "bg-teal-50 border-teal-200", icon: "🔬" },
  ESTP: { color: "bg-yellow-50 border-yellow-200", icon: "⚡" },
  ESFP: { color: "bg-orange-50 border-orange-200", icon: "🎭" },
  ENFP: { color: "bg-rose-50 border-rose-200", icon: "🌈" },
  ENTP: { color: "bg-red-50 border-red-200", icon: "🌀" },
  ESTJ: { color: "bg-lime-50 border-lime-200", icon: "📊" },
  ESFJ: { color: "bg-amber-50 border-amber-200", icon: "🤝" },
  ENFJ: { color: "bg-fuchsia-50 border-fuchsia-200", icon: "🌟" },
  ENTJ: { color: "bg-sky-50 border-sky-200", icon: "🚀" },
};

function Spinner() {
  return (
    <svg className="h-5 w-5 animate-spin" viewBox="0 0 24 24" fill="none">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
    </svg>
  );
}

export default function MbitverseWhitePanel() {
  const [news, setNews] = useState<string>(DEFAULT_NEWS);
  const [data, setData] = useState<PanelResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onRun = async () => {
    setLoading(true); setError(null); setData(null);
    try {
      const res = await fetch("/full_pipeline", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ news, max_tokens: 512 }),
      });
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
      const json: PanelResponse = await res.json();
      setData(json);
    } catch (e: any) {
      setError(e?.message || String(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-7xl p-6 text-gray-900 font-sans bg-white">
      {/* Header */}
      <header className="mb-6 text-center">
        <h1 className="text-3xl font-extrabold">🌐 MBTIverse Panel</h1>
        <p className="mt-1 text-sm text-gray-600">16 MBTI agents + Meta Reviewer — Visualized</p>
      </header>

      {/* Input */}
      <section className="mb-6 rounded-2xl border bg-white p-5 shadow-sm">
        <label className="mb-2 block text-sm font-medium text-gray-700">News</label>
        <textarea
          value={news}
          onChange={(e) => setNews(e.target.value)}
          rows={6}
          className="w-full resize-y rounded-xl border px-3 py-2 outline-none focus:ring-2 focus:ring-black/30"
          placeholder="Paste or type news here..."
        />
        <div className="mt-3 flex flex-wrap gap-2">
          <button
            onClick={onRun}
            disabled={loading || !news.trim()}
            className="inline-flex items-center gap-2 rounded-xl bg-black px-5 py-2 text-sm font-medium text-white shadow-md transition hover:opacity-90 disabled:opacity-50"
          >
            {loading && <Spinner />}<span>{loading ? "Running" : "Run Panel"}</span>
          </button>
          <button onClick={() => setNews("")} className="rounded-xl border px-4 py-2 text-sm hover:bg-gray-100">Clear</button>
          <button onClick={() => setNews(DEFAULT_NEWS)} className="rounded-xl border px-4 py-2 text-sm hover:bg-gray-100">Example</button>
        </div>
        {error && (
          <div className="mt-3 rounded-xl border border-red-300 bg-red-50 p-3 text-sm text-red-800">
            <strong>Error:</strong> {error}
          </div>
        )}
      </section>

      {/* Results */}
      {data && (
        <div className="space-y-6">
          {/* Meta Review */}
          {data.meta_review && (
            <div className="rounded-2xl border-2 border-black bg-white p-6 shadow-md">
              <h2 className="mb-3 text-xl font-bold flex items-center gap-2">🧭 Meta Review</h2>
              {(() => {
                try {
                  const trimmed = (data.meta_review || "").trim();
                  if (trimmed.startsWith("{") || trimmed.startsWith("[")) {
                    const parsed = JSON.parse(trimmed) as Record<string, any>;
                    const entries = Object.entries(parsed);
                    return (
                      <div className="grid gap-4 md:grid-cols-2">
                        {entries.map(([k, v]) => (
                          <div key={k} className="rounded-xl border p-4">
                            <div className="mb-2 flex items-center justify-between">
                              <h3 className="font-semibold">{k}</h3>
                              <span className="text-xs text-gray-500">{Array.isArray(v) ? `${v.length}` : typeof v}</span>
                            </div>
                            {Array.isArray(v) ? (
                              <ul className="list-disc pl-5 space-y-1">
                                {v.map((item: any, i: number) => (
                                  <li key={i} className="text-sm">
                                    {typeof item === "string" ? item : <pre className="whitespace-pre-wrap text-xs">{JSON.stringify(item, null, 2)}</pre>}
                                  </li>
                                ))}
                              </ul>
                            ) : typeof v === "object" ? (
                              <pre className="whitespace-pre-wrap text-xs">{JSON.stringify(v, null, 2)}</pre>
                            ) : (
                              <p className="text-sm whitespace-pre-wrap">{String(v)}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    );
                  }
                } catch (_) {}
                return (
                  <div className="prose prose-sm sm:prose-base max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {data.meta_review as string}
                    </ReactMarkdown>
                  </div>
                );
              })()}
            </div>
          )}

          {/* Agent Reactions */}
          <section>
            <h2 className="mb-4 text-xl font-bold">Agent Reactions</h2>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {data.results?.map((r) => {
                const style = AGENT_STYLE[r.personality] || { color: "bg-gray-50 border-gray-200", icon: "🤖" };
                return (
                  <div
                    key={r.personality}
                    className={`rounded-2xl border p-5 shadow-sm transition hover:shadow-md ${style.color}`}
                  >
                    <div className="mb-2 flex items-center gap-2">
                      <span className="text-xl">{style.icon}</span>
                      <h3 className="text-lg font-semibold">{r.personality}</h3>
                    </div>
                    <p className="whitespace-pre-wrap leading-relaxed text-gray-800">{r.reaction}</p>
                  </div>
                );
              })}
            </div>
          </section>

          {/* Errors */}
          {data.errors && Object.keys(data.errors).length > 0 && (
            <section>
              <h2 className="mb-2 text-sm font-semibold">Errors</h2>
              <ul className="list-disc pl-5 text-sm text-red-700">
                {Object.entries(data.errors).map(([k, v]) => (
                  <li key={k}><span className="font-mono">{k}</span>: {v}</li>
                ))}
              </ul>
            </section>
          )}
        </div>
      )}

      {!data && !loading && (
        <div className="rounded-2xl border bg-white p-8 text-center text-gray-700">
          <p className="text-sm">Tip: Paste news above and click <span className="font-semibold">Run Panel</span> to see agent responses and a meta review.</p>
        </div>
      )}

      <footer className="mt-10 text-center text-xs text-gray-500">
        <p>© {new Date().getFullYear()} MBTIverse. Clean • White • Professional</p>
      </footer>
    </div>
  );
}
