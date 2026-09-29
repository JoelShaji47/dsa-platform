"use client";

import { useEffect, useRef } from "react";
import { acquireCamera, getCameraStream, releaseCamera } from "./proctoring";

export function CameraFeed() {
  const videoRef = useRef<HTMLVideoElement | null>(null);

  useEffect(() => {
    let disposed = false;

    const bind = () => {
      const video = videoRef.current;
      const stream = getCameraStream();
      if (!video || !stream) return;
      video.srcObject = stream;
      void video.play().catch(() => undefined);
    };

    bind();
    if (!getCameraStream()) {
      void acquireCamera()
        .then(() => {
          if (!disposed) bind();
        })
        .catch(() => undefined);
    }

    return () => {
      disposed = true;
    };
  }, []);

  useEffect(() => {
    return () => {
      releaseCamera();
    };
  }, []);

  return (
    <div className="fixed bottom-4 right-4 z-50 overflow-hidden rounded-xl border-2 border-red-500/70 bg-black shadow-2xl">
      <div className="flex items-center gap-1.5 bg-red-600/90 px-2 py-1">
        <span className="h-2 w-2 animate-pulse rounded-full bg-white" />
        <span className="font-mono text-[10px] font-bold tracking-[0.2em] text-white">
          CAM
        </span>
      </div>
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="-scale-x-100 object-cover"
        style={{ width: 160, height: 120 }}
      />
    </div>
  );
}