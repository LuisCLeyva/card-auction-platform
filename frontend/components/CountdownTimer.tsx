"use client";

import { useEffect, useState } from "react";

function formatRemaining(ms: number): string {
  if (ms <= 0) return "Ended";
  const totalSeconds = Math.floor(ms / 1000);
  const days = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  if (days > 0) return `${days}d ${hours}h ${minutes}m`;
  if (hours > 0) return `${hours}h ${minutes}m ${seconds}s`;
  return `${minutes}m ${seconds}s`;
}

export function CountdownTimer({ endTime }: { endTime: string }) {
  // Starts null (rather than computing immediately) so the server-rendered
  // markup and the client's first paint match exactly — Date.now() differs
  // between the two and would otherwise trigger a hydration mismatch.
  const [remaining, setRemaining] = useState<number | null>(null);

  useEffect(() => {
    const target = new Date(endTime).getTime();
    const tick = () => setRemaining(target - Date.now());
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [endTime]);

  if (remaining === null) {
    return <span className="text-parchment/50">…</span>;
  }

  const ended = remaining <= 0;
  const urgent = !ended && remaining < 5 * 60 * 1000;

  return (
    <span className={ended ? "text-parchment/50" : urgent ? "text-red-400" : "text-gold"}>
      {formatRemaining(remaining)}
    </span>
  );
}
