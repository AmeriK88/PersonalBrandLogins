document.addEventListener("DOMContentLoaded", () => {
  const archive = document.querySelector(".highlights-archive");
  const viewer = archive?.querySelector(".archive-viewer");
  const viewerContent = archive?.querySelector(".archive-viewer-content");

  if (!archive || !viewer || !viewerContent || typeof viewer.showModal !== "function") {
    return;
  }

  let returnFocusTo = null;
  let previousOverflow = "";

  const closeViewer = () => {
    if (viewer.open) viewer.close();
  };

  archive.addEventListener("click", (event) => {
    const photoLink = event.target.closest("[data-photo-viewer]");
    const videoButton = event.target.closest("[data-video-viewer]");
    const closeButton = event.target.closest("[data-viewer-close]");

    if (closeButton) {
      closeViewer();
      return;
    }

    if (event.target === viewer) {
      closeViewer();
      return;
    }

    if (!photoLink && !videoButton) return;

    if (photoLink) {
      event.preventDefault();
      returnFocusTo = photoLink;
      const image = document.createElement("img");
      image.src = photoLink.href;
      image.alt = photoLink.dataset.photoTitle || "";
      viewerContent.replaceChildren(image);

      const title = document.createElement("h2");
      title.textContent = photoLink.dataset.photoTitle || "";
      viewerContent.append(title);

      if (photoLink.dataset.photoDescription) {
        const description = document.createElement("p");
        description.textContent = photoLink.dataset.photoDescription;
        viewerContent.append(description);
      }
    } else {
      const embedUrl = videoButton.dataset.videoEmbed;
      if (!embedUrl) return;

      event.preventDefault();
      returnFocusTo = videoButton;
      const iframe = document.createElement("iframe");
      iframe.src = embedUrl;
      iframe.title = videoButton.dataset.videoTitle || "Video player";
      iframe.loading = "eager";
      iframe.referrerPolicy = "strict-origin-when-cross-origin";
      iframe.allow = "fullscreen; picture-in-picture";
      iframe.allowFullscreen = true;
      iframe.sandbox = "allow-scripts allow-same-origin allow-presentation";
      viewerContent.replaceChildren(iframe);
    }

    previousOverflow = document.documentElement.style.overflow;
    document.documentElement.style.overflow = "hidden";
    viewer.showModal();
    viewer.querySelector("[data-viewer-close]").focus();
  });

  viewer.addEventListener("close", () => {
    viewerContent.replaceChildren();
    document.documentElement.style.overflow = previousOverflow;
    if (returnFocusTo?.isConnected) returnFocusTo.focus();
    returnFocusTo = null;
  });
});
