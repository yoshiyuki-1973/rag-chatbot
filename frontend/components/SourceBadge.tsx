import type { Source } from "@/lib/api";

type Props = {
  source: Source;
};

export function SourceBadge({ source }: Props) {
  const label = source.authority_score >= 0.8 ? "高信頼" : source.authority_score >= 0.5 ? "中信頼" : "要確認";
  const tone =
    source.authority_score >= 0.8
      ? "border-moss bg-white text-moss"
      : source.authority_score >= 0.5
        ? "border-blue-600 bg-white text-blue-600"
        : "border-line bg-white text-ink";
  // ブラックリスト方式で XSS を防止（より拡張性が高い）
  const isUnsafeUrl = source.source_url.toLowerCase().startsWith("javascript:");
  const safeUrl = isUnsafeUrl ? "#" : source.source_url;

  return (
    <a
      href={safeUrl}
      target="_blank"
      rel="noopener noreferrer"
      className={`block rounded border p-3 text-sm ${tone}`}
    >
      <div className="flex items-center justify-between gap-3">
        <span className="font-semibold">{source.title}</span>
        <span className="shrink-0 text-xs">{label}</span>
      </div>
      <div className="mt-1 text-xs text-ink/70">
        {source.organization ?? "不明"} / chunk {source.chunk_index} / similarity{" "}
        {source.similarity.toFixed(2)}
      </div>
    </a>
  );
}
