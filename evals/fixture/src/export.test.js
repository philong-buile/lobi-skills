import { describe, expect, it, vi } from "vitest";
import { exportNotes } from "./export.js";

describe("exportNotes", () => {
  it("writes one Markdown section per note", () => {
    const download = vi.fn();
    exportNotes([{ title: "A", body: "x" }], download);
    expect(download).toHaveBeenCalledWith("notes.md", "## A\n\nx");
  });
});
