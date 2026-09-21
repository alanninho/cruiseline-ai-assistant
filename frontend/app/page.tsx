"use client";

import { useState } from "react";

type Source = {
  source_type: string;
  source_file: string;
  distance: number;
};

type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function sendMessage() {
    console.log("sendMessage called, input is:", input);
    if (!input.trim()) return;

    const question = input;
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setInput("");
    setLoading(true);

    const response = await fetch("http://localhost:8000/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await response.json();

    setMessages((prev) => [
      ...prev,
      { role: "assistant", content: data.answer, sources: data.sources },
    ]);
    setLoading(false);
  }

  return (
    <div className="flex flex-col h-screen bg-slate-50">
      <div className="bg-[#0a2540] text-white px-6 py-4 shadow-md">
        <h1 className="text-2xl font-bold">Cruise Assistant</h1>
      </div>

      <div className="flex-1 overflow-y-auto p-4 max-w-2xl mx-auto w-full space-y-4">
        {messages.length === 0 && (
          <p className="text-slate-400 text-center mt-8">
            Ask me anything about your cruise - cabins, excursions, policies, and more.
          </p>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={msg.role === "user" ? "text-right" : "text-left"}>
            <div
              className={
                "inline-block p-3 rounded-lg max-w-lg shadow-sm " +
                (msg.role === "user"
                  ? "bg-[#0a2540] text-white"
                  : "bg-white text-slate-800 border border-slate-200")
              }
            >
              {msg.content}
            </div>
            {msg.sources && msg.sources.length > 0 && (
              <div className="text-xs text-[#c9a227] mt-1 font-medium">
                Sources: {msg.sources.map((s) => s.source_file).join(", ")}
              </div>
            )}
          </div>
        ))}
        {loading && <div className="text-slate-400 italic">Thinking...</div>}
      </div>

      <div className="border-t border-slate-200 bg-white p-4">
        <div className="flex gap-2 max-w-2xl mx-auto">
          <input
            className="flex-1 border border-slate-300 rounded-lg px-3 py-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#c9a227]"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Ask about your cruise..."
          />
          <button
            className="bg-[#c9a227] text-[#0a2540] font-semibold px-4 py-2 rounded-lg hover:brightness-95"
            onClick={sendMessage}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}