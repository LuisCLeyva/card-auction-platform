import { act, render, screen } from "@testing-library/react";

import { CountdownTimer } from "./CountdownTimer";

describe("CountdownTimer", () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it("shows the remaining time and ticks down", () => {
    const now = new Date("2024-01-01T00:00:00Z");
    jest.setSystemTime(now);
    const endTime = new Date(now.getTime() + 90 * 1000).toISOString(); // 1m30s away

    render(<CountdownTimer endTime={endTime} />);
    act(() => {
      jest.advanceTimersByTime(0);
    });
    expect(screen.getByText("1m 30s")).toBeInTheDocument();

    act(() => {
      // Advance the same fake clock that drives both Date.now() and the
      // interval — mixing this with jest.setSystemTime() makes the interval's
      // next scheduled tick land at a confusing offset.
      jest.advanceTimersByTime(31 * 1000);
    });
    expect(screen.getByText("0m 59s")).toBeInTheDocument();
  });

  it("shows Ended once the time has passed", () => {
    const now = new Date("2024-01-01T00:00:00Z");
    jest.setSystemTime(now);
    const endTime = new Date(now.getTime() - 1000).toISOString();

    render(<CountdownTimer endTime={endTime} />);
    act(() => {
      jest.advanceTimersByTime(0);
    });
    expect(screen.getByText("Ended")).toBeInTheDocument();
  });
});
