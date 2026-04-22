(function () {
  const presets = [
    {
      id: "house-shot",
      name: "Typical House Shot",
      description: "Balanced shape with miss room and a moderate transition move.",
      values: {
        arrowBoard: 12,
        breakpointBoard: 8,
        breakpointDistance: 40,
        laydownDistance: 6,
        driftDistance: 5,
        driftDirection: "left"
      }
    },
    {
      id: "sport-medium",
      name: "Medium Sport Pattern",
      description: "Tighter blend with a cleaner need for breakpoint control.",
      values: {
        arrowBoard: 11,
        breakpointBoard: 7,
        breakpointDistance: 39,
        laydownDistance: 5,
        driftDistance: 4,
        driftDirection: "left"
      }
    },
    {
      id: "long-pattern",
      name: "Long Challenge Pattern",
      description: "More forward control with a smaller angle profile.",
      values: {
        arrowBoard: 14,
        breakpointBoard: 10,
        breakpointDistance: 43,
        laydownDistance: 4,
        driftDistance: 3,
        driftDirection: "left"
      }
    },
    {
      id: "short-pattern",
      name: "Short Sport Pattern",
      description: "Breakpoint farther right with a sharper need for touch.",
      values: {
        arrowBoard: 9,
        breakpointBoard: 5,
        breakpointDistance: 36,
        laydownDistance: 7,
        driftDistance: 5,
        driftDirection: "left"
      }
    }
  ];

  const clampBoard = (value) => Math.max(1, Math.min(39, value));
  const round = (value) => Math.round(value * 10) / 10;
  const floorBoard = (value) => Math.max(1, Math.min(39, Math.floor(value)));
  const ARROW_DISTANCE_FEET = 15;
  const FOCAL_DISTANCE_FEET = 34;
  const BOARD_WIDTH_INCHES = 1.06;

  function calculateLanePlay(inputs) {
    const direction = inputs.handedness === "right" ? 1 : -1;
    const driftDirection = inputs.driftDirection === "left" ? -1 : 1;
    const boardSlope =
      (inputs.breakpointBoard - inputs.arrowBoard) /
      Math.max(1, inputs.breakpointDistance - ARROW_DISTANCE_FEET);

    const laydownBoard = clampBoard(inputs.arrowBoard - boardSlope * ARROW_DISTANCE_FEET);
    const slideBoard = clampBoard(laydownBoard + inputs.laydownDistance * direction);
    const standBoard = clampBoard(slideBoard + inputs.driftDistance * driftDirection);
    const focalBoard = floorBoard(
      inputs.arrowBoard + boardSlope * (FOCAL_DISTANCE_FEET - ARROW_DISTANCE_FEET)
    );

    const launchAngle =
      (Math.atan(
        (Math.abs(inputs.breakpointBoard - laydownBoard) * BOARD_WIDTH_INCHES) /
          (inputs.breakpointDistance * 12)
      ) *
        180) /
      Math.PI;

    const buildMove = (moveCount) => ({
      standBoard: round(clampBoard(standBoard + moveCount * 2 * direction)),
      slideBoard: round(clampBoard(slideBoard + moveCount * 2 * direction)),
      arrowBoard: round(clampBoard(inputs.arrowBoard + moveCount * direction)),
      focalBoard: round(clampBoard(focalBoard + moveCount * direction))
    });

    const fitNotes = [];

    if (inputs.breakpointDistance < 35) {
      fitNotes.push("A shorter breakpoint distance suggests a more forward shape and earlier friction response.");
    }

    if (inputs.breakpointDistance >= 41) {
      fitNotes.push("A deeper breakpoint usually means you can keep the line in front of you while preserving entry angle.");
    }

    if (Math.abs(inputs.arrowBoard - inputs.breakpointBoard) >= 6) {
      fitNotes.push("This line creates a larger side-to-side motion, so ball choice and speed control will matter more.");
    }

    if (Math.abs(inputs.driftDistance) >= 5) {
      fitNotes.push("Higher drift distance can help open the lane, but it also makes timing and projection more important.");
    }

    if (inputs.driftDistance > 0) {
      fitNotes.push(
        `Current drift is set ${inputs.driftDirection}, so the slide board is projected ${inputs.driftDirection} of the stance board.`
      );
    }

    if (Math.abs(inputs.laydownDistance) >= 7) {
      fitNotes.push("A larger laydown distance creates a bigger gap between the ball and your slide board at the line.");
    }

    if (inputs.handedness === "left") {
      fitNotes.push("Left-handed mode mirrors board movement so the same PLAC-style logic works from the opposite side.");
    }

    return {
      standBoard: round(standBoard),
      slideBoard: round(slideBoard),
      laydownBoard: round(laydownBoard),
      focalBoard: round(focalBoard),
      launchAngle: round(direction === 1 ? -launchAngle : launchAngle),
      currentLine: buildMove(0),
      nextMove: buildMove(1),
      twoMoves: buildMove(2),
      fitNotes
    };
  }

  function init() {
    const presetSelect = document.getElementById("patternPreset");
    const resultsWrap = document.getElementById("lanePlayResults");
    const movesWrap = document.getElementById("lanePlayMoves");
    const notesWrap = document.getElementById("lanePlayNotes");
    if (!presetSelect || !resultsWrap || !movesWrap || !notesWrap) return;

    presets.forEach((preset) => {
      const option = document.createElement("option");
      option.value = preset.id;
      option.textContent = preset.name;
      presetSelect.appendChild(option);
    });

    const fieldIds = [
      "arrowBoard",
      "breakpointBoard",
      "breakpointDistance",
      "laydownDistance",
      "driftDistance",
      "driftDirection"
    ];

    function getInputs() {
      const handedness = document.querySelector('input[name="handedness"]:checked')?.value || "right";
      return {
        handedness,
        arrowBoard: Number(document.getElementById("arrowBoard").value || 0),
        breakpointBoard: Number(document.getElementById("breakpointBoard").value || 0),
        breakpointDistance: Number(document.getElementById("breakpointDistance").value || 0),
        laydownDistance: Number(document.getElementById("laydownDistance").value || 0),
        driftDistance: Number(document.getElementById("driftDistance").value || 0),
        driftDirection: document.getElementById("driftDirection").value || "left"
      };
    }

    function renderStats(result) {
      const stats = [
        ["Stand board", result.standBoard],
        ["Slide board", result.slideBoard],
        ["Laydown board", result.laydownBoard],
        ["Focal board", result.focalBoard],
        ["Launch angle", `${result.launchAngle}°`]
      ];
      resultsWrap.innerHTML = stats
        .map(
          ([label, value]) => `
            <div class="tool-stat-card">
              <span>${label}</span>
              <strong>${value}</strong>
            </div>
          `
        )
        .join("");
    }

    function renderMoves(result) {
      const moveCards = [
        ["Current line", result.currentLine],
        ["Next move", result.nextMove],
        ["2 moves", result.twoMoves]
      ];
      movesWrap.innerHTML = moveCards
        .map(
          ([label, line]) => `
            <article class="tool-move-card">
              <h3>${label}</h3>
              <div class="tag-list">
                <span class="tag">Stand ${line.standBoard}</span>
                <span class="tag">Slide ${line.slideBoard}</span>
                <span class="tag">Arrow ${line.arrowBoard}</span>
                <span class="tag">Focal ${line.focalBoard}</span>
              </div>
            </article>
          `
        )
        .join("");
    }

    function renderNotes(result, preset) {
      const notes = [...result.fitNotes];
      if (preset) {
        notes.unshift(preset.description);
      }
      notesWrap.innerHTML = notes.length
        ? `<ul class="list">${notes.map((note) => `<li><strong>${note}</strong></li>`).join("")}</ul>`
        : "";
    }

    function calculateAndRender() {
      const preset = presets.find((item) => item.id === presetSelect.value);
      const result = calculateLanePlay(getInputs());
      renderStats(result);
      renderMoves(result);
      renderNotes(result, preset);
    }

    presetSelect.addEventListener("change", () => {
      const preset = presets.find((item) => item.id === presetSelect.value);
      if (preset) {
        fieldIds.forEach((id) => {
          const field = document.getElementById(id);
          if (!field) return;
          field.value = preset.values[id];
        });
      }
      calculateAndRender();
    });

    document.querySelectorAll('input[name="handedness"]').forEach((input) => {
      input.addEventListener("change", calculateAndRender);
    });
    fieldIds.forEach((id) => {
      const field = document.getElementById(id);
      if (field) {
        field.addEventListener("input", calculateAndRender);
        field.addEventListener("change", calculateAndRender);
      }
    });

    calculateAndRender();
  }

  document.addEventListener("DOMContentLoaded", init);
})();
