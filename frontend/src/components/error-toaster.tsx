"use client";

import { useEffect } from "react";
import { setErrorHandler, useToast } from "@/context/toast-context";

/**
 * Mounts once and registers a callback with the API client so that any
 * failed request (that isn't a 401 redirect) is surfaced as a toast.
 * Previously errors were swallowed silently (e.g. `.catch(() => {})`).
 */
export function ErrorToaster() {
  const { toast } = useToast();
  useEffect(() => {
    setErrorHandler((message) => {
      toast({ title: "Request failed", description: message, variant: "destructive" });
    });
  }, [toast]);
  return null;
}
