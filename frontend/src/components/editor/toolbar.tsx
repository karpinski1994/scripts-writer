"use client";

import type { Editor } from "@tiptap/react";
import { Button } from "@/components/ui/button";
import {
  Bold,
  Italic,
  Heading1,
  Heading2,
  List,
  ListOrdered,
  Undo,
  Redo,
} from "lucide-react";

interface ToolbarProps {
  editor: Editor | null;
}

export function Toolbar({ editor }: ToolbarProps) {
  if (!editor) return null;

  return (
    <div className="flex items-center gap-0.5 border-b px-2 py-1">
      <ToolbarButton
        onClick={() => editor.chain().focus().toggleBold().run()}
        isActive={editor.isActive("bold")}
        icon={<Bold className="size-4" />}
        tooltip="Bold"
      />
      <ToolbarButton
        onClick={() => editor.chain().focus().toggleItalic().run()}
        isActive={editor.isActive("italic")}
        icon={<Italic className="size-4" />}
        tooltip="Italic"
      />
      <div className="mx-1 h-4 w-px bg-border" />
      <ToolbarButton
        onClick={() =>
          editor.chain().focus().toggleHeading({ level: 1 }).run()
        }
        isActive={editor.isActive("heading", { level: 1 })}
        icon={<Heading1 className="size-4" />}
        tooltip="Heading 1"
      />
      <ToolbarButton
        onClick={() =>
          editor.chain().focus().toggleHeading({ level: 2 }).run()
        }
        isActive={editor.isActive("heading", { level: 2 })}
        icon={<Heading2 className="size-4" />}
        tooltip="Heading 2"
      />
      <div className="mx-1 h-4 w-px bg-border" />
      <ToolbarButton
        onClick={() => editor.chain().focus().toggleBulletList().run()}
        isActive={editor.isActive("bulletList")}
        icon={<List className="size-4" />}
        tooltip="Bullet List"
      />
      <ToolbarButton
        onClick={() => editor.chain().focus().toggleOrderedList().run()}
        isActive={editor.isActive("orderedList")}
        icon={<ListOrdered className="size-4" />}
        tooltip="Ordered List"
      />
      <div className="mx-1 h-4 w-px bg-border" />
      <ToolbarButton
        onClick={() => editor.chain().focus().undo().run()}
        disabled={!editor.can().undo()}
        icon={<Undo className="size-4" />}
        tooltip="Undo"
      />
      <ToolbarButton
        onClick={() => editor.chain().focus().redo().run()}
        disabled={!editor.can().redo()}
        icon={<Redo className="size-4" />}
        tooltip="Redo"
      />
    </div>
  );
}

function ToolbarButton({
  onClick,
  isActive = false,
  disabled = false,
  icon,
  tooltip,
}: {
  onClick: () => void;
  isActive?: boolean;
  disabled?: boolean;
  icon: React.ReactNode;
  tooltip: string;
}) {
  return (
    <Button
      variant="ghost"
      size="icon"
      className={`size-8 ${isActive ? "bg-accent" : ""}`}
      onClick={onClick}
      disabled={disabled}
      title={tooltip}
    >
      {icon}
    </Button>
  );
}
