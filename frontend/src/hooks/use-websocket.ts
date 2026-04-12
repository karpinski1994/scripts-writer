"use client";

import { useEffect, useRef, useState } from "react";

type ConnectionStatus = "connecting" | "connected" | "disconnected";

function getWsUrl(projectId: string): string {
  const apiUrl =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const wsBase = apiUrl.replace(/^http/, "ws");
  return `${wsBase}/ws/pipeline/${projectId}`;
}

interface UseWebSocketReturn {
  lastEvent: Record<string, unknown> | null;
  connectionStatus: ConnectionStatus;
}

export function useWebSocket(projectId: string | null): UseWebSocketReturn {
  const [lastEvent, setLastEvent] = useState<Record<string, unknown> | null>(
    null
  );
  const [connectionStatus, setConnectionStatus] =
    useState<ConnectionStatus>("disconnected");
  const retryRef = useRef(0);
  const mountedRef = useRef(true);
  const retryTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    mountedRef.current = true;

    function scheduleReconnect() {
      if (!mountedRef.current || !projectId) return;
      const delay = Math.min(1000 * 2 ** retryRef.current, 30000);
      retryRef.current += 1;
      retryTimerRef.current = setTimeout(doConnect, delay);
    }

    function doConnect() {
      if (!projectId || !mountedRef.current) return;

      const url = getWsUrl(projectId);
      const ws = new WebSocket(url);
      setConnectionStatus("connecting");

      ws.onopen = () => {
        if (!mountedRef.current) return;
        setConnectionStatus("connected");
        retryRef.current = 0;
      };

      ws.onmessage = (event) => {
        if (!mountedRef.current) return;
        try {
          const data = JSON.parse(event.data);
          setLastEvent(data);
        } catch {
          // ignore non-JSON
        }
      };

      ws.onclose = () => {
        if (!mountedRef.current) return;
        setConnectionStatus("disconnected");
        scheduleReconnect();
      };

      ws.onerror = () => {
        ws.close();
      };
    }

    doConnect();

    return () => {
      mountedRef.current = false;
      if (retryTimerRef.current) clearTimeout(retryTimerRef.current);
    };
  }, [projectId]);

  return { lastEvent, connectionStatus };
}
