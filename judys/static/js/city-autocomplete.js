// Town/city autocomplete for contact form boxes marked data-city-autocomplete.
// Uses Google Places Autocomplete (New). Google calls window.jdPlacesReady once
// its script has loaded. The picked place ID goes in a hidden "<name>__place_id"
// box so the server can double-check it with Google.
(function () {
  const inputs = document.querySelectorAll("[data-city-autocomplete]");
  if (!inputs.length) return;

  window.jdPlacesReady = async function () {
    const places = await google.maps.importLibrary("places");
    inputs.forEach((input) => setup(input, places));
  };

  function setup(input, places) {
    const hidden = document.createElement("input");
    hidden.type = "hidden";
    hidden.name = input.name + "__place_id";
    hidden.value = input.dataset.placeId || "";

    const list = document.createElement("ul");
    list.className = "city-suggestions";
    list.id = input.id + "-suggestions";
    list.setAttribute("role", "listbox");
    list.hidden = true;

    input.after(hidden, list);
    input.parentElement.classList.add("has-suggestions");
    input.setAttribute("role", "combobox");
    input.setAttribute("aria-autocomplete", "list");
    input.setAttribute("aria-expanded", "false");
    input.setAttribute("aria-controls", list.id);

    let token = new places.AutocompleteSessionToken();
    let items = [];
    let active = -1;
    let timer;
    let latest = 0;

    input.addEventListener("input", () => {
      hidden.value = ""; // typing again means a new choice is needed
      clearTimeout(timer);
      const text = input.value.trim();
      if (text.length < 2) return close();
      timer = setTimeout(() => lookup(text), 200);
    });

    async function lookup(text) {
      const request = ++latest;
      try {
        const { suggestions } =
          await places.AutocompleteSuggestion.fetchAutocompleteSuggestions({
            input: text,
            includedPrimaryTypes: ["(cities)"],
            includedRegionCodes: ["us"],
            sessionToken: token,
          });
        if (request !== latest) return; // a newer search has started
        items = suggestions.map((s) => s.placePrediction).filter(Boolean).slice(0, 5);
        render();
      } catch (err) {
        close();
      }
    }

    function render() {
      list.replaceChildren();
      active = -1;
      if (!items.length) return close();
      items.forEach((place, i) => {
        const li = document.createElement("li");
        li.id = `${list.id}-${i}`;
        li.setAttribute("role", "option");
        li.textContent = place.text.toString();
        li.addEventListener("mousedown", (e) => {
          e.preventDefault();
          choose(i);
        });
        list.append(li);
      });
      const credit = document.createElement("li");
      credit.className = "city-credit";
      credit.setAttribute("aria-hidden", "true");
      credit.textContent = "Powered by Google";
      list.append(credit);
      list.hidden = false;
      input.setAttribute("aria-expanded", "true");
    }

    function highlight(i) {
      const options = list.querySelectorAll('[role="option"]');
      options.forEach((o, j) => o.setAttribute("aria-selected", String(j === i)));
      active = i;
      if (i >= 0) input.setAttribute("aria-activedescendant", options[i].id);
      else input.removeAttribute("aria-activedescendant");
    }

    function choose(i) {
      const place = items[i];
      if (!place) return;
      input.value = place.text.toString();
      hidden.value = place.placeId;
      close();
      token = new places.AutocompleteSessionToken(); // one session per pick
    }

    function close() {
      list.hidden = true;
      input.setAttribute("aria-expanded", "false");
      input.removeAttribute("aria-activedescendant");
      active = -1;
    }

    input.addEventListener("keydown", (e) => {
      if (list.hidden) return;
      const count = items.length;
      if (e.key === "ArrowDown") {
        e.preventDefault();
        highlight((active + 1) % count);
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        highlight((active - 1 + count) % count);
      } else if (e.key === "Enter" && active >= 0) {
        e.preventDefault();
        choose(active);
      } else if (e.key === "Escape") {
        close();
      }
    });
    input.addEventListener("blur", () => setTimeout(close, 120));
  }
})();
