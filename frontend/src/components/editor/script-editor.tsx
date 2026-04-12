"use client";

import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Highlight from "@tiptap/extension-highlight";
import { useEffect } from "react";
import { useEditorStore } from "@/stores/editor-store";
import { Toolbar } from "./toolbar";
import {
  StructuralCueBroll,
  StructuralCueTextOverlay,
  StructuralCuePause,
} from "./structural-cue-extension";

interface ScriptEditorProps {
  className?: string;
}

export function ScriptEditor({ className }: ScriptEditorProps) {
  const content = useEditorStore((s) => s.content);
  const isSaving = useEditorStore((s) => s.isSaving);
  const isDirty = useEditorStore((s) => s.isDirty);

  const editor = useEditor({
    extensions: [
      StarterKit,
      Highlight,
      StructuralCueBroll,
      StructuralCueTextOverlay,
      StructuralCuePause,
    ],
    content,
    editable: !isSaving,
    onUpdate: ({ editor: ed }) => {
      const text = ed.getText();
      useEditorStore.getState().setContent(text);
    },
  });

  useEffect(() => {
    if (!editor) return;
    const storeContent = useEditorStore.getState().content;
    if (storeContent !== editor.getText()) {
      editor.commands.setContent(storeContent);
    }
  }, [editor, content]);

  useEffect(() => {
    if (!editor) return;
    editor.setEditable(!isSaving);
  }, [editor, isSaving]);

  const wordCount = editor ? editor.getText().split(/\s+/).filter(Boolean).length : 0;

  return (
    <div className={`flex flex-col rounded-md border ${className ?? ""}`}>
      <Toolbar editor={editor} />
      <EditorContent
        editor={editor}
        className="prose prose-sm max-w-none flex-1 p-4 min-h-[400px] focus:outline-none"
      />
      <div className="flex items-center justify-between border-t px-4 py-2 text-xs text-muted-foreground">
        <span>{wordCount} {wordCount === 1 ? "word" : "words"}</span>
        <span>
          {isSaving ? (
            <span className="text-blue-500">Saving...</span>
          ) : isDirty ? (
            <span className="text-amber-500">Unsaved</span>
          ) : (
            <span className="text-green-600">Saved</span>
          )}
        </span>
      </div>
    </div>
  );
}
