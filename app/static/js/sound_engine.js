/**
 * Quiz Royale — Client-Side Web Audio Synthesizer Sound Engine
 * Zero external audio files or dependencies. Generates dynamic audio in-browser.
 */

class SoundEngine {
  constructor() {
    this.audioCtx = null;
    this.muted = localStorage.getItem("quiz_royale_muted") === "true";
  }

  initContext() {
    if (!this.audioCtx) {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (AudioContextClass) {
        this.audioCtx = new AudioContextClass();
      }
    }
    if (this.audioCtx && this.audioCtx.state === "suspended") {
      this.audioCtx.resume();
    }
  }

  toggleMute() {
    this.muted = !this.muted;
    localStorage.setItem("quiz_royale_muted", this.muted ? "true" : "false");
    this.updateSoundButtonUI();
    if (!this.muted) {
      this.playClick();
    }
    return this.muted;
  }

  isMuted() {
    return this.muted;
  }

  updateSoundButtonUI() {
    const btn = document.getElementById("sound-toggle-btn");
    if (!btn) return;
    if (this.muted) {
      btn.classList.add("muted");
      btn.setAttribute("title", "Sound Muted (Click to Unmute)");
      btn.innerHTML = `<svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2"/></svg>`;
    } else {
      btn.classList.remove("muted");
      btn.setAttribute("title", "Sound On (Click to Mute)");
      btn.innerHTML = `<svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"/></svg>`;
    }
  }

  playClick() {
    if (this.muted) return;
    try {
      this.initContext();
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(600, this.audioCtx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(300, this.audioCtx.currentTime + 0.05);

      gain.gain.setValueAtTime(0.15, this.audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, this.audioCtx.currentTime + 0.05);

      osc.connect(gain);
      gain.connect(this.audioCtx.destination);
      osc.start();
      osc.stop(this.audioCtx.currentTime + 0.05);
    } catch (e) {}
  }

  playTick() {
    if (this.muted) return;
    try {
      this.initContext();
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc.type = "triangle";
      osc.frequency.setValueAtTime(800, this.audioCtx.currentTime);

      gain.gain.setValueAtTime(0.08, this.audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.audioCtx.currentTime + 0.04);

      osc.connect(gain);
      gain.connect(this.audioCtx.destination);
      osc.start();
      osc.stop(this.audioCtx.currentTime + 0.04);
    } catch (e) {}
  }

  playCorrect() {
    if (this.muted) return;
    try {
      this.initContext();
      const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6
      notes.forEach((freq, idx) => {
        const osc = this.audioCtx.createOscillator();
        const gain = this.audioCtx.createGain();
        osc.type = "sine";
        osc.frequency.setValueAtTime(freq, this.audioCtx.currentTime + idx * 0.06);

        gain.gain.setValueAtTime(0.2, this.audioCtx.currentTime + idx * 0.06);
        gain.gain.exponentialRampToValueAtTime(0.01, this.audioCtx.currentTime + idx * 0.06 + 0.25);

        osc.connect(gain);
        gain.connect(this.audioCtx.destination);
        osc.start(this.audioCtx.currentTime + idx * 0.06);
        osc.stop(this.audioCtx.currentTime + idx * 0.06 + 0.25);
      });
    } catch (e) {}
  }

  playWrong() {
    if (this.muted) return;
    try {
      this.initContext();
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc.type = "sawtooth";
      osc.frequency.setValueAtTime(220, this.audioCtx.currentTime);
      osc.frequency.linearRampToValueAtTime(140, this.audioCtx.currentTime + 0.25);

      gain.gain.setValueAtTime(0.25, this.audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, this.audioCtx.currentTime + 0.25);

      osc.connect(gain);
      gain.connect(this.audioCtx.destination);
      osc.start();
      osc.stop(this.audioCtx.currentTime + 0.25);
    } catch (e) {}
  }

  playStreak() {
    if (this.muted) return;
    try {
      this.initContext();
      const freqs = [440, 554.37, 659.25, 880, 1108.73];
      freqs.forEach((f, i) => {
        const osc = this.audioCtx.createOscillator();
        const gain = this.audioCtx.createGain();
        osc.type = "triangle";
        osc.frequency.setValueAtTime(f, this.audioCtx.currentTime + i * 0.05);

        gain.gain.setValueAtTime(0.25, this.audioCtx.currentTime + i * 0.05);
        gain.gain.exponentialRampToValueAtTime(0.01, this.audioCtx.currentTime + i * 0.05 + 0.3);

        osc.connect(gain);
        gain.connect(this.audioCtx.destination);
        osc.start(this.audioCtx.currentTime + i * 0.05);
        osc.stop(this.audioCtx.currentTime + i * 0.05 + 0.3);
      });
    } catch (e) {}
  }
}

// Global sound engine instance
window.soundEngine = new SoundEngine();

document.addEventListener("DOMContentLoaded", () => {
  window.soundEngine.updateSoundButtonUI();

  // Attach button click sounds to interactive primary buttons
  document.querySelectorAll(".btn, .nav-link").forEach((el) => {
    el.addEventListener("click", () => {
      window.soundEngine.playClick();
    });
  });
});
