import { bindExportButton } from "./export.js";

const notes = [{ title: "First note", body: "Hello" }];
const download = (name, text) => {
  const link = document.createElement("a");
  link.href = URL.createObjectURL(new Blob([text], { type: "text/markdown" }));
  link.download = name;
  link.click();
};
bindExportButton(document.getElementById("export"), () => notes, download);
