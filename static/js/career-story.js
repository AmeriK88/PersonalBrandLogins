(() => {
  const initializeStories = () => {
    document.querySelectorAll(".career-story").forEach((story) => {
      const button = story.querySelector("[data-story-toggle]");
      const preview = story.querySelector("[data-story-preview]");
      const fullStory = story.querySelector("[data-story-full]");

      if (!button || !preview || !fullStory) return;

      fullStory.hidden = true;
      preview.hidden = false;
      button.hidden = false;

      button.addEventListener("click", () => {
        const expanded = button.getAttribute("aria-expanded") !== "true";
        button.setAttribute("aria-expanded", String(expanded));
        button.textContent = expanded ? "Show less" : "Read full story";
        preview.hidden = expanded;
        fullStory.hidden = !expanded;
      });
    });
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeStories, { once: true });
  } else {
    initializeStories();
  }
})();
