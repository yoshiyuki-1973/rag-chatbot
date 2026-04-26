"use client";

import { useState } from "react";
import { searchDocuments, type SearchResult } from "@/lib/api";
import { SourceBadge } from "@/components/SourceBadge";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    const trimmed = query.trim();
    if (!trimmed || loading) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      setResults(await searchDocuments(trimmed));
    } catch (err) {
      setError(err instanceof Error ? err.message : "エラーが発生しました。");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto min-h-screen max-w-5xl border-x border-line bg-field">
      <header className="flex items-center justify-between border-b border-line bg-white px-4 py-3">
        <h1 className="text-lg font-semibold">ドキュメント検索</h1>
        <a className="text-sm font-medium text-moss" href="/">
          チャット
        </a>
      </header>
      <form
        className="flex gap-2 border-b border-line bg-white p-4"
        onSubmit={(event) => {
          event.preventDefault();
          submit();
        }}
      >
        <label className="sr-only" htmlFor="search-query">
          検索クエリ
        </label>
        <input
          id="search-query"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          className="h-11 flex-1 rounded border border-line px-3 outline-none focus:border-moss"
          placeholder="検索キーワード"
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="h-11 w-20 rounded bg-ink px-4 text-sm font-semibold text-white disabled:bg-ink/30"
        >
          検索
        </button>
      </form>
      {error ? (
        <div className="border-b border-brick bg-white px-4 py-3 text-sm text-brick" role="alert">
          {error}
        </div>
      ) : null}
      <section className="grid gap-3 p-4">
        {loading ? <p className="text-sm" aria-live="polite">ドキュメントを検索しています...</p> : null}
        {results.map((result) => (
          <article key={`${result.document_id}-${result.chunk_index}`} className="rounded border border-line bg-white p-4">
            <SourceBadge source={result} />
            <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-ink/80">{result.content}</p>
          </article>
        ))}
      </section>
    </main>
  );
}

