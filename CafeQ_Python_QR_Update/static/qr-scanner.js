(() => {
  const video = document.getElementById("camera-preview");
  const message = document.getElementById("scanner-message");
  const startButton = document.getElementById("start-camera");
  const stopButton = document.getElementById("stop-camera");
  if (!video || !message || !startButton || !stopButton) return;

  let stream = null;
  let detector = null;
  let scanning = false;

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
        const results = await detector.detect(video);
        const rawValue = results[0]?.rawValue || null;
        let destination = null;
        try {
          const url = new URL(rawValue);
          if (url.protocol === "http:" || url.protocol === "https:") {
            destination = url;
          }
        } catch {
          destination = null;
        }
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
      if (!("BarcodeDetector" in window)) {
        message.textContent = "This browser does not have a built-in QR scanner. Use your phone's camera app to scan the cafe QR code.";
        startButton.disabled = false;
        return;
      }
      const formats = await BarcodeDetector.getSupportedFormats();
      if (!formats.includes("qr_code")) {
        message.textContent = "This browser cannot scan QR codes. Use your phone's camera app to scan the cafe QR code.";
        startButton.disabled = false;
        return;
      }
      detector = new BarcodeDetector({ formats: ["qr_code"] });
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
