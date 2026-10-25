(() => {
  const video = document.getElementById("camera-preview");
  const message = document.getElementById("scanner-message");
  const startButton = document.getElementById("start-camera");
  const stopButton = document.getElementById("stop-camera");
  if (!video || !message || !startButton || !stopButton) return;

  let stream = null;
  let detector = null;
  let canvas = null;
  let canvasContext = null;
  let scanning = false;

  function resolveDestination(rawValue) {
    let destination;
    try {
      destination = new URL(rawValue);
    } catch {
      return null;
    }
    if (destination.protocol !== "http:" && destination.protocol !== "https:") {
      return null;
    }

    const host = destination.hostname.toLowerCase();
    if ((host === "google.com" || host.endsWith(".google.com")) &&
        destination.pathname.startsWith("/maps/search/")) {
      const query = `${destination.searchParams.get("query") || ""} ${destination.searchParams.get("q") || ""}`.toLowerCase();
      if (query.includes("sunrise") && query.includes("cafe")) {
        return new URL("/shop/demo-sunrise-cafe", window.location.origin);
      }
      if (query.includes("moonlight") && query.includes("coffee")) {
        return new URL("/shop/demo-moonlight-coffee", window.location.origin);
      }
    }
    return destination;
  }

  function stopCamera() {
    scanning = false;
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      stream = null;
    }
    video.srcObject = null;
    startButton.disabled = false;
    stopButton.disabled = true;
  }

  async function scanFrame() {
    if (!scanning) return;
    if (video.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA) {
      try {
        let rawValue = null;
        if (detector) {
          const results = await detector.detect(video);
          rawValue = results[0]?.rawValue || null;
        } else {
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          canvasContext.drawImage(video, 0, 0, canvas.width, canvas.height);
          const frame = canvasContext.getImageData(0, 0, canvas.width, canvas.height);
          rawValue = window.jsQR(frame.data, frame.width, frame.height, {
            inversionAttempts: "dontInvert",
          })?.data || null;
        }
        const destination = resolveDestination(rawValue);
        if (destination) {
          scanning = false;
          message.textContent = `QR code found. Opening ${destination.href}`;
          stopCamera();
          window.location.assign(destination.href);
          return;
        }
      } catch (error) {
        if (scanning) {
          message.textContent = `Could not read the camera frame: ${error.message}`;
          stopCamera();
        }
        return;
      }
    }
    if (scanning) window.setTimeout(scanFrame, 150);
  }

  startButton.addEventListener("click", async () => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      message.textContent = "Camera access requires HTTPS or localhost. Open CafeQ using a secure HTTPS address and try again.";
      return;
    }

    startButton.disabled = true;
    try {
      if ("BarcodeDetector" in window) {
        const formats = await BarcodeDetector.getSupportedFormats();
        if (formats.includes("qr_code")) {
          detector = new BarcodeDetector({ formats: ["qr_code"] });
        }
      }
      if (!detector && typeof window.jsQR !== "function") {
        throw new Error("The local QR decoder did not load. Refresh the page and try again.");
      }
      if (!detector) {
        canvas = document.createElement("canvas");
        canvasContext = canvas.getContext("2d", { willReadFrequently: true });
        if (!canvasContext) {
          throw new Error("This browser could not initialize the local QR decoder.");
        }
      }
      stream = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: { facingMode: { ideal: "environment" } },
      });
      video.srcObject = stream;
      await video.play();
      scanning = true;
      stopButton.disabled = false;
      message.textContent = "Camera is on. Point it at a cafe QR code.";
      scanFrame();
    } catch (error) {
      stopCamera();
      if (error.name === "NotAllowedError" || error.name === "PermissionDeniedError") {
        message.textContent = "Camera permission was denied. Allow camera access in your browser settings, then try again.";
      } else if (error.name === "NotFoundError" || error.name === "DevicesNotFoundError") {
        message.textContent = "No camera was found on this device.";
      } else {
        message.textContent = `Could not start the camera: ${error.message}`;
      }
    }
  });

  stopButton.addEventListener("click", () => {
    stopCamera();
    message.textContent = "Camera stopped.";
  });
  window.addEventListener("pagehide", stopCamera);
})();
