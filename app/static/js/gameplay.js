/**
 * Quiz Royale — Real-Time Gameplay Client Controller
 * Controls synchronized countdowns, audio integration, keyboard events, and authoritative submissions.
 */

class GameplayController {
  constructor(sessionId) {
    this.sessionId = sessionId;
    this.currentQuestion = null;
    this.timerInterval = null;
    this.timeRemaining = 15;
    this.timeLimit = 15;
    this.hasAnswered = false;
    this.currentScore = 0;
    this.currentStreak = 0;

    // DOM Elements
    this.dom = {
      progressText: document.getElementById("q-progress-text"),
      scoreCounter: document.getElementById("q-score-counter"),
      streakCounter: document.getElementById("q-streak-counter"),
      livesContainer: document.getElementById("q-lives-container"),
      livesText: document.getElementById("q-lives-text"),
      timerText: document.getElementById("q-timer-text"),
      timerBar: document.getElementById("q-timer-bar"),
      categoryBadge: document.getElementById("q-category-badge"),
      difficultyBadge: document.getElementById("q-difficulty-badge"),
      questionText: document.getElementById("q-question-text"),
      optionsContainer: document.getElementById("q-options-container"),
      feedbackBox: document.getElementById("q-feedback-box"),
      feedbackTitle: document.getElementById("q-feedback-title"),
      feedbackExplanation: document.getElementById("q-feedback-explanation"),
      feedbackPoints: document.getElementById("q-feedback-points"),
      nextBtn: document.getElementById("q-next-btn"),
    };

    this.bindEvents();
    this.loadQuestion();
  }

  bindEvents() {
    this.dom.nextBtn.addEventListener("click", () => {
      this.advanceNextQuestion();
    });

    // Keyboard support: 1-4 or A-D
    window.addEventListener("keydown", (e) => {
      if (this.hasAnswered || !this.currentQuestion) return;
      const key = e.key.toUpperCase();
      let index = -1;
      if (key === "1" || key === "A") index = 0;
      else if (key === "2" || key === "B") index = 1;
      else if (key === "3" || key === "C") index = 2;
      else if (key === "4" || key === "D") index = 3;

      if (index >= 0 && index < this.currentQuestion.options.length) {
        const optionId = this.currentQuestion.options[index].id;
        this.submitAnswer(optionId);
      }
    });
  }

  async loadQuestion() {
    this.hasAnswered = false;
    this.dom.feedbackBox.style.display = "none";
    this.dom.nextBtn.style.display = "none";
    this.dom.optionsContainer.innerHTML = `<div style="text-align: center; padding: 2rem; color: var(--text-muted);">Loading next challenge...</div>`;

    try {
      const res = await fetch(`/play/${this.sessionId}/question`);
      const data = await res.json();

      if (!data.success) {
        if (data.error && data.error.includes("answered")) {
          window.location.href = `/play/${this.sessionId}/results`;
          return;
        }
        alert(data.error || "Unable to load question.");
        return;
      }

      this.renderQuestion(data.data);
    } catch (err) {
      console.error(err);
      this.dom.optionsContainer.innerHTML = `<div style="color: var(--color-danger); text-align: center; padding: 2rem;">Network error loading question. Please refresh.</div>`;
    }
  }

  renderQuestion(data) {
    this.currentQuestion = data.question;
    this.currentScore = data.current_score;
    this.currentStreak = data.current_streak;

    // Update Headings & Indicators
    this.dom.progressText.textContent = `Question ${data.current_index} of ${data.total_questions}`;
    this.dom.scoreCounter.textContent = `${data.current_score} pts`;
    this.dom.streakCounter.textContent = `${data.current_streak}x`;

    if (data.game_mode === "survival") {
      this.dom.livesContainer.style.display = "flex";
      this.dom.livesText.textContent = "❤️".repeat(Math.max(0, data.lives_remaining));
    } else {
      this.dom.livesContainer.style.display = "none";
    }

    this.dom.categoryBadge.textContent = data.question.category_name || "General";
    this.dom.difficultyBadge.textContent = data.question.difficulty.toUpperCase();
    this.dom.difficultyBadge.className = `pill-difficulty pill-${data.question.difficulty.toLowerCase()}`;
    this.dom.questionText.textContent = data.question.question_text;

    // Render 4 Options
    this.dom.optionsContainer.innerHTML = "";
    const letters = ["A", "B", "C", "D"];

    data.question.options.forEach((opt, idx) => {
      const btn = document.createElement("button");
      btn.className = "option-btn";
      btn.setAttribute("data-option-id", opt.id);
      btn.innerHTML = `
        <span class="option-letter">${letters[idx]}</span>
        <span class="option-text">${this.escapeHtml(opt.option_text)}</span>
      `;

      btn.addEventListener("click", () => {
        if (!this.hasAnswered) {
          this.submitAnswer(opt.id);
        }
      });

      this.dom.optionsContainer.appendChild(btn);
    });

    // Start Authoritative Countdown
    this.timeLimit = data.question.time_limit_sec || 15;
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
        this.submitAnswer(null); // Timeout expired
      }
    }, 1000);
  }

  updateTimerUI() {
    this.dom.timerText.textContent = `${Math.max(0, this.timeRemaining)}s`;
    const pct = Math.max(0, (this.timeRemaining / this.timeLimit) * 100);
    this.dom.timerBar.style.width = `${pct}%`;

    if (pct < 30) {
      this.dom.timerBar.style.backgroundColor = "var(--color-danger)";
    } else if (pct < 60) {
      this.dom.timerBar.style.backgroundColor = "var(--color-warning)";
    } else {
      this.dom.timerBar.style.backgroundColor = "var(--accent-purple)";
    }
  }

  async submitAnswer(selectedOptionId) {
    if (this.hasAnswered) return;
    this.hasAnswered = true;
    clearInterval(this.timerInterval);

    // Disable all option buttons immediately
    const optionButtons = this.dom.optionsContainer.querySelectorAll(".option-btn");
    optionButtons.forEach((btn) => (btn.disabled = true));

    // Mark selected button pending
    if (selectedOptionId) {
      const selectedBtn = this.dom.optionsContainer.querySelector(`[data-option-id="${selectedOptionId}"]`);
      if (selectedBtn) selectedBtn.classList.add("selected");
    }

    // Submit to server
    try {
      const res = await fetch(`/play/${this.sessionId}/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question_id: this.currentQuestion.id,
          selected_option_id: selectedOptionId,
          idempotency_key: `${this.sessionId}-${this.currentQuestion.id}`,
        }),
      });

      const json = await res.json();
      if (!json.success) {
        alert(json.error || "Submission failed.");
        return;
      }

      this.handleAnswerResult(json.data, selectedOptionId);
    } catch (e) {
      console.error(e);
      alert("Network error evaluating submission.");
    }
  }

  handleAnswerResult(data, selectedOptionId) {
    const isCorrect = data.is_correct;
    const correctOptId = data.correct_option_id;

    // Audio SFX
    if (window.soundEngine) {
      if (isCorrect) {
        if (data.current_streak >= 3) {
          window.soundEngine.playStreak();
        } else {
          window.soundEngine.playCorrect();
        }
      } else {
        window.soundEngine.playWrong();
      }
    }

    // Visual button highlights
    const buttons = this.dom.optionsContainer.querySelectorAll(".option-btn");
    buttons.forEach((btn) => {
      const optId = parseInt(btn.getAttribute("data-option-id"));
      if (optId === correctOptId) {
        btn.classList.add("correct");
      } else if (optId === selectedOptionId && !isCorrect) {
        btn.classList.add("wrong");
      }
    });

    // Update scoreboard
    this.dom.scoreCounter.textContent = `${data.current_score} pts`;
    this.dom.streakCounter.textContent = `${data.current_streak}x`;
    if (data.lives_remaining !== undefined && this.dom.livesText) {
      this.dom.livesText.textContent = "❤️".repeat(Math.max(0, data.lives_remaining));
    }

    // Feedback Banner
    this.dom.feedbackBox.style.display = "block";
    if (isCorrect) {
      this.dom.feedbackBox.className = "feedback-box feedback-correct";
      this.dom.feedbackTitle.textContent = "✅ Correct Answer!";
      let bonusText = `+${data.points_awarded} Points`;
      if (data.speed_bonus > 0) bonusText += ` (⚡ +${data.speed_bonus} Speed)`;
      if (data.streak_bonus > 0) bonusText += ` (🔥 +${data.streak_bonus} Streak)`;
      this.dom.feedbackPoints.textContent = bonusText;
    } else {
      this.dom.feedbackBox.className = "feedback-box feedback-wrong";
      this.dom.feedbackTitle.textContent = selectedOptionId ? "❌ Incorrect" : "⏰ Time Expired";
      this.dom.feedbackPoints.textContent = "+0 Points";
    }

    this.dom.feedbackExplanation.textContent = data.explanation || "";
    this.dom.nextBtn.style.display = "inline-flex";

    if (data.game_over) {
      this.dom.nextBtn.textContent = "View Final Results (Game Over)";
    } else {
      this.dom.nextBtn.textContent = "Next Question →";
    }
  }

  async advanceNextQuestion() {
    this.dom.nextBtn.disabled = true;
    try {
      const res = await fetch(`/play/${this.sessionId}/next`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      const data = await res.json();
      if (data.success && data.is_finished) {
        window.location.href = `/play/${this.sessionId}/results`;
      } else {
        this.dom.nextBtn.disabled = false;
        this.loadQuestion();
      }
    } catch (e) {
      console.error(e);
      window.location.href = `/play/${this.sessionId}/results`;
    }
  }

  escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }
}
