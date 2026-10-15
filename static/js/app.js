// Alpine components. Loaded before Alpine itself so `alpine:init` is caught.
document.addEventListener("alpine:init", () => {
  // Light/dark mode, remembered per browser. The <head> script applies the saved
  // choice before first paint; this store starts from whatever it decided.
  Alpine.store("theme", {
    dark: document.documentElement.classList.contains("dark"),
    toggle() {
      this.dark = !this.dark;
      document.documentElement.classList.toggle("dark", this.dark);
      try {
        localStorage.setItem("theme", this.dark ? "dark" : "light");
      } catch (e) {}
    },
  });

  // "Copy link" button on a post.
  Alpine.data("copyLink", () => ({
    copied: false,
    async copy() {
      try {
        await navigator.clipboard.writeText(window.location.href);
        this.copied = true;
        setTimeout(() => (this.copied = false), 2000);
      } catch (e) {}
    },
  }));
});
