"use client";

import { useEditor, EditorContent } from "@tiptap/react";
import { BubbleMenu } from "@tiptap/react/menus";
import StarterKit from "@tiptap/starter-kit";
import Highlight from "@tiptap/extension-highlight";
import { useState, useEffect } from "react";
import { useEditorStore } from "@/stores/editor-store";
import { Toolbar } from "./toolbar";
import {
  StructuralCueBroll,
  StructuralCueTextOverlay,
  StructuralCuePause,
} from "./structural-cue-extension";
import { PersistentSelection } from "./persistent-selection";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { api } from "@/lib/api";

interface ScriptEditorProps {
  projectId: string;
  className?: string;
}

export function ScriptEditor({ projectId, className }: ScriptEditorProps) {
  const content = useEditorStore((s) => s.content);
  console.log('EDITOR CONTENT: ', content)
  const isSaving = useEditorStore((s) => s.isSaving);
  const isDirty = useEditorStore((s) => s.isDirty);
  const startAutoSave = useEditorStore((s) => s.startAutoSave);
  const stopAutoSave = useEditorStore((s) => s.stopAutoSave);
  const currentVersionId = useEditorStore((s) => s.currentVersionId);
  void currentVersionId; // used in future for version locking

  const [isRewriting, setIsRewriting] = useState(false);
  const [instruction, setInstruction] = useState("");
  const [storedSelection, setStoredSelection] = useState("");
  const [storedSelectionPos, setStoredSelectionPos] = useState<{ from: number; to: number } | null>(null);

  const editor = useEditor({
    extensions: [
      StarterKit,
      Highlight,
      StructuralCueBroll,
      StructuralCueTextOverlay,
      StructuralCuePause,
      PersistentSelection,
    ],
    content,
    editable: !isSaving && !isRewriting,
    immediatelyRender: false,
    onUpdate: ({ editor: ed }) => {
      const text = ed.getText();
      useEditorStore.getState().setContent(text);
    },
  });

  useEffect(() => {
    if (!editor) return;
    
    const updateSelection = () => {
      const selection = editor.state.selection;
      if (selection.empty) {
        setStoredSelection("");
        setStoredSelectionPos(null);
        return;
      }
      const selectedText = editor.state.doc.textBetween(selection.from, selection.to, " ");
      if (selectedText.trim()) {
        setStoredSelection(selectedText);
        setStoredSelectionPos({ from: selection.from, to: selection.to });
      }
    };
    
    updateSelection();
    
    editor.on("selectionUpdate", updateSelection);
    return () => {
      editor.off("selectionUpdate", updateSelection);
    };
  }, [editor]);

  useEffect(() => {
    if (!editor || !storedSelectionPos) return;
    
    editor.commands.setPersistedSelection(storedSelectionPos.from, storedSelectionPos.to);
  }, [editor, storedSelectionPos]);

  // Clear persisted selection when selection is cleared
  useEffect(() => {
    if (!editor) return;
    
    const clearSelection = () => {
      if (editor.state.selection.empty) {
        editor.commands.clearPersistedSelection();
      }
    };
    
    editor.on("selectionUpdate", clearSelection);
    return () => {
      editor.off("selectionUpdate", clearSelection);
    };
  }, [editor]);

  const handleBubbleMenuFocus = () => {
    if (editor && storedSelectionPos) {
      editor.commands.setTextSelection(storedSelectionPos);
    }
  };

  useEffect(() => {
    if (!editor) return;
    const storeContent = useEditorStore.getState().content;
    if (storeContent !== editor.getText()) {
      editor.commands.setContent(storeContent);
    }
  }, [editor, content]);

  useEffect(() => {
    if (!editor) return;
    editor.setEditable(!isSaving && !isRewriting);
  }, [editor, isSaving, isRewriting]);

  useEffect(() => {
    startAutoSave();
    return () => stopAutoSave();
  }, [startAutoSave, stopAutoSave]);

  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      const store = useEditorStore.getState();
      if (store.isDirty && store.currentVersionId) {
        store.save();
        e.preventDefault();
      }
    };
    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, []);

  const handleRewrite = async () => {
    if (!editor || !instruction.trim() || !storedSelection.trim()) return;

    const fullContent = editor.getText();

    setIsRewriting(true);

    try {
      const response = await api.post<{ rewritten_text: string }>(
        `/api/v1/projects/${projectId}/scripts/rewrite-selection`,
        {
          full_content: fullContent,
          selected_text: storedSelection,
          instruction: instruction,
        }
      );

      const { from, to } = editor.state.selection;
      editor
        .chain()
        .focus()
        .insertContentAt({ from, to }, response.rewritten_text)
        .run();

      setInstruction("");
      setStoredSelection("");
    } catch (error) {
      console.error("Rewrite failed:", error);
    } finally {
      setIsRewriting(false);
    }
  };

  const wordCount = editor ? editor.getText().split(/\s+/).filter(Boolean).length : 0;

  return (
    <div className={`flex flex-col rounded-md border ${className ?? ""}`}>
      <Toolbar editor={editor} />
      {editor && (
        <BubbleMenu
          editor={editor}
          className="flex items-center gap-2 p-2 bg-background border rounded-lg shadow-lg"
        >
          {storedSelection && (
            <span className="text-xs text-muted-foreground max-w-[120px] truncate" title={storedSelection}>
              "{storedSelection.length > 30 ? storedSelection.slice(0, 30) + "..." : storedSelection}"
            </span>
          )}
          <Input
            placeholder="e.g. Make this punchier..."
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            disabled={isRewriting}
            className="h-8 w-48 text-sm"
            onFocus={handleBubbleMenuFocus}
            onKeyDown={(e) => {
              if (e.key === "Enter" && instruction.trim() && !isRewriting) {
                handleRewrite();
              }
            }}
          />
          <Button
            onClick={handleRewrite}
            onFocus={handleBubbleMenuFocus}
            disabled={isRewriting || !instruction.trim() || !storedSelection.trim()}
            size="sm"
            className="h-8"
          >
            {isRewriting ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              "Rewrite"
            )}
          </Button>
        </BubbleMenu>
      )}
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