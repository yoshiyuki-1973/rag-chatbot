"use client";

type Props = {
  value: string;
  disabled?: boolean;
  onChange: (value: string) => void;
  onSubmit: () => void;
};

export function InputArea({ value, disabled, onChange, onSubmit }: Props) {
  return (
    <form
      className="flex gap-2 border-t border-line bg-white p-4"
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit();
      }}
    >
      <label className="sr-only" htmlFor="chat-query">
        質問
      </label>
      <textarea
        id="chat-query"
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
        className="min-h-12 flex-1 resize-none rounded border border-line px-3 py-2 outline-none focus:border-moss"
        rows={2}
        maxLength={500}
        placeholder="スポーツに関する質問を入力"
      />
      <button
        type="submit"
        disabled={disabled || !value.trim()}
        className="h-12 w-20 rounded bg-ink px-4 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-ink/30"
      >
        送信
      </button>
    </form>
  );
}

