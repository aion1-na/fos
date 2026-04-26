"use client";

export type EventLogFrame = {
  offset: number;
  tick: number;
  message: string;
};

export function EventLogTail({ events }: { events: EventLogFrame[] }) {
  return (
    <section className="run-panel event-log-tail">
      <h2>Event Log Tail</h2>
      <ol className="console-log">
        {events.slice(-8).map((event) => (
          <li data-state="complete" key={event.offset}>
            t={event.tick} · {event.message}
          </li>
        ))}
      </ol>
    </section>
  );
}
