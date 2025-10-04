CREATE TABLE IF NOT EXISTS task (
    -- A unique identifier that represents the current task.
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- A brief summary explaining the task.
    title TEXT NOT NULL,
    -- Priority: 0=Low, 1=Medium, 2=High
    priority INTEGER CHECK (priority >= 0 AND priority <= 2) DEFAULT 1,
    -- Status: 0=Pending, 1=Active, 2=Completed
    status INTEGER CHECK (priority >= 0 AND priority <= 2) DEFAULT 0,
    -- A timestamp indicating when the task was created.
    created_at NUMERIC NOT NULL DEFAULT (unixepoch('now')),
    -- A timestamp indicating the last time the entry was updated.
    updated_at NUMERIC NOT NULL DEFAULT (unixepoch('now'))
);
