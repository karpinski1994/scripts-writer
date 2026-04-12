import { Mark, markInputRule, markPasteRule } from "@tiptap/core";

export const StructuralCueBroll = Mark.create({
  name: "structuralCueBroll",

  parseHTML() {
    return [{ tag: "span.cue-broll" }];
  },

  renderHTML() {
    return ["span", { class: "cue-broll" }, 0];
  },

  addInputRules() {
    return [
      markInputRule({
        find: /\[B-ROLL\]$/,
        type: this.type,
      }),
    ];
  },

  addPasteRules() {
    return [
      markPasteRule({
        find: /\[B-ROLL\]/g,
        type: this.type,
      }),
    ];
  },
});

export const StructuralCueTextOverlay = Mark.create({
  name: "structuralCueTextOverlay",

  parseHTML() {
    return [{ tag: "span.cue-text-overlay" }];
  },

  renderHTML() {
    return ["span", { class: "cue-text-overlay" }, 0];
  },

  addInputRules() {
    return [
      markInputRule({
        find: /\[TEXT OVERLAY\]$/,
        type: this.type,
      }),
    ];
  },

  addPasteRules() {
    return [
      markPasteRule({
        find: /\[TEXT OVERLAY\]/g,
        type: this.type,
      }),
    ];
  },
});

export const StructuralCuePause = Mark.create({
  name: "structuralCuePause",

  parseHTML() {
    return [{ tag: "span.cue-pause" }];
  },

  renderHTML() {
    return ["span", { class: "cue-pause" }, 0];
  },

  addInputRules() {
    return [
      markInputRule({
        find: /\[PAUSE\]$/,
        type: this.type,
      }),
    ];
  },

  addPasteRules() {
    return [
      markPasteRule({
        find: /\[PAUSE\]/g,
        type: this.type,
      }),
    ];
  },
});
