export function exportNotes(notes, download) {
  const markdown = notes.map((note) => `## ${note.title}\n\n${note.body}`).join("\n\n");
  download("notes.md", markdown);
}

export function bindExportButton(button, getNotes, download) {
  // Each click starts an export; a double click starts two.
  button.addEventListener("click", () => exportNotes(getNotes(), download));
}
