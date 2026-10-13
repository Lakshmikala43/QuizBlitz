/**
 * Quiz Royale — Real-Time Multiplayer Socket.IO Arena Controller
 * Manages WebSocket room synchronization, synchronized countdowns, and live podium updates.
 */

class MultiplayerArena {
  constructor(roomCode) {
    this.roomCode = roomCode;
    this.socket = null;
    this.isHost = false;
    this.hasAnswered = false;
    this.currentQuestion = null;
    this.timerInterval = null;
    this.timeRemaining = 15;
    this.timeLimit = 15;

    // View containers
    this.views = {
      lobby: document.getElementById("lobby-view"),
      arena: document.getElementById("arena-view"),
      podium: document.getElementById("podium-view"),
    };

    // DOM References
    this.dom = {
      roomCodeDisplay: document.getElementById("room-code-display"),
      playerCount: document.getElementById("player-count"),
      rosterList: document.getElementById("lobby-roster"),
      readyBtn: document.getElementById("ready-btn"),
      startBtn: document.getElementById("start-btn"),
      progressText: document.getElementById("mp-progress-text"),
      timerText: document.getElementById("mp-timer-text"),
      timerBar: document.getElementById("mp-timer-bar"),
      questionText: document.getElementById("mp-question-text"),
      optionsContainer: document.getElementById("mp-options-container"),
      scoreboard: document.getElementById("mp-scoreboard"),
      feedbackBox: document.getElementById("mp-feedback-box"),
      feedbackTitle: document.getElementById("mp-feedback-title"),
      feedbackExp: document.getElementById("mp-feedback-exp"),
      podiumList: document.getElementById("mp-podium-list"),
    };

    this.initSocket();
    this.bindDOMEvents();
  }

  initSocket() {
    this.socket = io();

    this.socket.on("connect", () => {
      console.log("[SocketIO] Connected with SID:", this.socket.id);
      this.socket.emit("join_room", { room_code: this.roomCode });
    });

    this.socket.on("joined_successfully", (data) => {
      this.isHost = data.is_host;
      if (this.isHost) {
        this.dom.startBtn.style.display = "inline-flex";
      }
      this.renderRoster(data.leaderboard);
    });

    this.socket.on("roster_updated", (data) => {
      this.renderRoster(data.leaderboard);
    });

    this.socket.on("battle_started", () => {
      this.views.lobby.style.display = "none";
      this.views.arena.style.display = "block";
    });

    this.socket.on("new_question", (data) => {
      this.renderQuestion(data);
    });

    this.socket.on("answer_feedback", (data) => {
      this.handleAnswerFeedback(data);
    });

    this.socket.on("score_update", (data) => {
      this.renderScoreboard(data.leaderboard);
    });

    this.socket.on("all_players_answered", (data) => {
      this.revealAnswer(data);
      if (this.isHost) {
        setTimeout(() => {
          this.socket.emit("advance_question", { room_code: this.roomCode });
        }, 3000);
      }
    });

    this.socket.on("battle_ended", (data) => {
      this.views.arena.style.display = "none";
      this.views.podium.style.display = "block";
      this.renderPodium(data.podium);
    });

    this.socket.on("error", (err) => {
      alert(err.message || "An error occurred.");
    });
  }

  bindDOMEvents() {
    this.dom.readyBtn.addEventListener("click", () => {
      this.socket.emit("toggle_ready", { room_code: this.roomCode });
    });

    this.dom.startBtn.addEventListener("click", () => {
      this.socket.emit("start_battle", { room_code: this.roomCode });
    });
  }

  renderRoster(leaderboard) {
    this.dom.playerCount.textContent = `${leaderboard.length} Players`;
    this.dom.rosterList.innerHTML = "";

    leaderboard.forEach((player) => {
      const card = document.createElement("div");
      card.className = "card";
      card.style.display = "flex";
      card.style.alignItems = "center";
      card.style.justifyContent = "space-between";
      card.style.padding = "0.85rem 1rem";

      card.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.75rem;">
          <div style="width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, var(--accent-purple), var(--accent-gold)); display: flex; align-items: center; justify-content: center; font-weight: 700; color: #fff;">
            ${this.escape(player.display_name.slice(0, 2).toUpperCase())}
          </div>
          <div>
            <strong style="display: block;">${this.escape(player.display_name)}</strong>
            <span style="font-size: 0.8rem; color: var(--text-muted);">@${this.escape(player.username)}</span>
          </div>
        </div>
        <span style="font-size: 0.8rem; font-weight: 700; padding: 0.2rem 0.6rem; border-radius: var(--radius-full); ${player.ready ? 'background-color: var(--color-success-bg); color: #34d399;' : 'background-color: var(--bg-surface-elevated); color: var(--text-muted);'}">
          ${player.ready ? 'READY' : 'WAITING'}
        </span>
      `;
      this.dom.rosterList.appendChild(card);
    });
  }

  renderQuestion(data) {
    this.hasAnswered = false;
    this.currentQuestion = data;
    this.dom.feedbackBox.style.display = "none";

    this.dom.progressText.textContent = `Question ${data.question_index} of ${data.total_questions}`;
    this.dom.questionText.textContent = data.question_text;
    this.dom.optionsContainer.innerHTML = "";

    const letters = ["A", "B", "C", "D"];
    data.options.forEach((opt, idx) => {
      const btn = document.createElement("button");
      btn.className = "option-btn";
      btn.setAttribute("data-option-id", opt.id);
      btn.innerHTML = `
        <span class="option-letter">${letters[idx]}</span>
        <span class="option-text">${this.escape(opt.option_text)}</span>
      `;

      btn.addEventListener("click", () => {
        if (!this.hasAnswered) {
          this.submitAnswer(opt.id);
        }
      });
      this.dom.optionsContainer.appendChild(btn);
    });

    this.timeLimit = data.time_limit_sec || 15;
    this.startTimer(this.timeLimit);
  }

  startTimer(seconds) {
    clearInterval(this.timerInterval);
    this.timeRemaining = seconds;
    this.updateTimerUI();

    this.timerInterval = setInterval(() => {
      this.timeRemaining -= 1;
      this.updateTimerUI();

      if (this.timeRemaining <= 5 && this.timeRemaining > 0) {
        if (window.soundEngine) window.soundEngine.playTick();
      }

      if (this.timeRemaining <= 0) {
        clearInterval(this.timerInterval);
        if (!this.hasAnswered) {
          this.submitAnswer(null); // Time out
        }
      }
    }, 1000);
  }

  updateTimerUI() {
    this.dom.timerText.textContent = `${Math.max(0, this.timeRemaining)}s`;
    const pct = Math.max(0, (this.timeRemaining / this.timeLimit) * 100);
    this.dom.timerBar.style.width = `${pct}%`;
  }

  submitAnswer(selectedOptionId) {
    this.hasAnswered = true;
    clearInterval(this.timerInterval);

    const buttons = this.dom.optionsContainer.querySelectorAll(".option-btn");
    buttons.forEach((btn) => (btn.disabled = true));

    if (selectedOptionId) {
      const btn = this.dom.optionsContainer.querySelector(`[data-option-id="${selectedOptionId}"]`);
      if (btn) btn.classList.add("selected");
    }

    this.socket.emit("submit_answer", {
      room_code: this.roomCode,
      question_id: this.currentQuestion.question_id,
      selected_option_id: selectedOptionId,
    });
  }

  handleAnswerFeedback(data) {
    if (window.soundEngine) {
      if (data.is_correct) window.soundEngine.playCorrect();
      else window.soundEngine.playWrong();
    }
  }

  revealAnswer(data) {
    const buttons = this.dom.optionsContainer.querySelectorAll(".option-btn");
    buttons.forEach((btn) => {
      const optId = parseInt(btn.getAttribute("data-option-id"));
      if (optId === data.correct_option_id) {
        btn.classList.add("correct");
      }
    });

    this.dom.feedbackBox.style.display = "block";
    this.dom.feedbackTitle.textContent = "Round Ended";
    this.dom.feedbackExp.textContent = data.explanation || "";
  }

  renderScoreboard(leaderboard) {
    this.dom.scoreboard.innerHTML = "";
    leaderboard.forEach((player, idx) => {
      const row = document.createElement("div");
      row.style.display = "flex";
      row.style.justifyContent = "space-between";
      row.style.padding = "0.5rem 0";
      row.style.borderBottom = "1px solid var(--color-border)";
      row.style.fontSize = "0.9rem";

      row.innerHTML = `
        <span style="font-weight: 600;">#${idx + 1} ${this.escape(player.display_name)}</span>
        <strong style="color: var(--accent-gold);">${player.score} pts</strong>
      `;
      this.dom.scoreboard.appendChild(row);
    });
  }

  renderPodium(podium) {
    if (window.soundEngine) window.soundEngine.playStreak();
    this.dom.podiumList.innerHTML = "";

    podium.forEach((p, idx) => {
      const card = document.createElement("div");
      card.className = "card";
      card.style.display = "flex";
      card.style.alignItems = "center";
      card.style.justifyContent = "space-between";
      card.style.marginBottom = "0.75rem";
      card.style.borderLeft = idx === 0 ? "4px solid var(--accent-gold)" : "1px solid var(--color-border)";

      card.innerHTML = `
        <div style="display: flex; align-items: center; gap: 1rem;">
          <span style="font-size: 1.5rem;">${idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : '#' + (idx + 1)}</span>
          <div>
            <strong style="display: block; font-size: 1.1rem;">${this.escape(p.display_name)}</strong>
            <span style="color: var(--text-muted); font-size: 0.85rem;">@${this.escape(p.username)}</span>
          </div>
        </div>
        <span style="font-size: 1.3rem; font-weight: 800; color: var(--accent-gold);">${p.score} pts</span>
      `;
      this.dom.podiumList.appendChild(card);
    });
  }

  escape(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }
}
