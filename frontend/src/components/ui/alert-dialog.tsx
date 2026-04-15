"use client"

import * as React from "react"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"

interface AlertDialogProps {
  open?: boolean
  onOpenChange?: (open: boolean) => void
  children?: React.ReactNode
}

function AlertDialog({ open, onOpenChange, children }: AlertDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {children}
    </Dialog>
  )
}

interface AlertDialogContentProps {
  children?: React.ReactNode
}

function AlertDialogContent({ children }: AlertDialogContentProps) {
  return (
    <DialogContent className="sm:max-w-[425px]">
      {children}
    </DialogContent>
  )
}

interface AlertDialogHeaderProps {
  children?: React.ReactNode
}

function AlertDialogHeader({ children }: AlertDialogHeaderProps) {
  return <DialogHeader>{children}</DialogHeader>
}

interface AlertDialogTitleProps {
  children?: React.ReactNode
}

function AlertDialogTitle({ children }: AlertDialogTitleProps) {
  return <DialogTitle>{children}</DialogTitle>
}

interface AlertDialogDescriptionProps {
  children?: React.ReactNode
}

function AlertDialogDescription({ children }: AlertDialogDescriptionProps) {
  return <DialogDescription>{children}</DialogDescription>
}

interface AlertDialogFooterProps {
  children?: React.ReactNode
}

function AlertDialogFooter({ children }: AlertDialogFooterProps) {
  return <DialogFooter>{children}</DialogFooter>
}

interface AlertDialogActionProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children?: React.ReactNode
}

function AlertDialogAction({ children, className, ...props }: AlertDialogActionProps) {
  return (
    <Button className={className} {...props}>
      {children}
    </Button>
  )
}

interface AlertDialogCancelProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children?: React.ReactNode
}

function AlertDialogCancel({ children, className, ...props }: AlertDialogCancelProps) {
  return (
    <Button variant="outline" className={className} {...props}>
      {children}
    </Button>
  )
}

export {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
}