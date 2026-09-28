export const VIOLATION_LIMIT = 3;

type StreamStore = { __proctorStream?: MediaStream | null };

function store(): StreamStore | null {
  return typeof window === "undefined" ? null : (window as StreamStore);
}

function isLive(stream: MediaStream | null): boolean {
  return !!stream && stream.getVideoTracks().some((t) => t.readyState === "live");
}

export async function acquireCamera(): Promise<MediaStream> {
  const existing = store()?.__proctorStream ?? null;
  if (isLive(existing)) return existing as MediaStream;
  const stream = await navigator.mediaDevices.getUserMedia({
    video: { width: { ideal: 320 }, height: { ideal: 240 } },
    audio: false,
  });
  const s = store();
  if (s) s.__proctorStream = stream;
  return stream;
}

export function getCameraStream(): MediaStream | null {
  const stream = store()?.__proctorStream ?? null;
  return isLive(stream) ? stream : null;
}

export function releaseCamera(): void {
  const s = store();
  const stream = s?.__proctorStream;
  if (!stream) return;
  stream.getTracks().forEach((track) => track.stop());
  if (s) s.__proctorStream = null;
}

export async function requestTestFullscreen(): Promise<void> {
  const doc = document as Document & {
    webkitFullscreenElement?: Element | null;
  };
  if (document.fullscreenElement || doc.webkitFullscreenElement) return;
  const el = document.documentElement as HTMLElement & {
    webkitRequestFullscreen?: () => Promise<void>;
  };
  if (el.requestFullscreen) {
    await el.requestFullscreen();
    return;
  }
  if (el.webkitRequestFullscreen) {
    await el.webkitRequestFullscreen();
    return;
  }
  throw new Error("Fullscreen is not supported in this browser.");
}