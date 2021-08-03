import { currentStocks, getCurrentStocks, removeChildren } from "./helpers.js";

"use strict";

// Open autocomplete box when user types in search bar
const initiateAutocomplete = () => {
  let searchBar = document.querySelector(".search-bar");
  searchBar.addEventListener("input", (e) => {
    let searchBarValue = e.target.value.toLowerCase()
    if (searchBarValue.length === 0) {
      document.querySelector(".auto-complete").style.visibility = "hidden";
    } else {
      document.querySelector(".auto-complete").style.visibility = "visible";
      getAutocompleteOptions(searchBarValue);
      autocompleteSelection();
    }
  });
}

// Insert search results in autocomplete box
const getAutocompleteOptions = (searchBarValue) => {
  // Get list of top five matches
  let matches = [];
  currentStocks.forEach(stock => {
    if (stock["symbol"].toLowerCase().startsWith(searchBarValue) || stock["name"].toLowerCase().startsWith(searchBarValue)) {
      if (matches.length !== 5) {
        matches.push(stock["symbol"] + " - " + stock["name"]);
      }
    }
  });

  // Populate autocomplete area with top 5 matches
  let parent = document.querySelector(".auto-complete");
  removeChildren(parent);
  if (!matches.length) {
    let node = document.createElement("li");
    node.innerHTML = "No results found";
    parent.appendChild(node);
  } else {
    matches.forEach(stock => {
      let node = document.createElement("li");
      node.className = "result"
      node.innerHTML = stock;
      parent.appendChild(node);
    });
  }
}

// Populate search bar with selected autocomplete option
const autocompleteSelection = () => {
  let stocks = document.querySelectorAll(".auto-complete li");
  stocks.forEach((stock) => {
    stock.addEventListener("click", (e) => {
      if (e.target.innerHTML !== "No results found") {
        document.querySelector(".search-bar").value = e.target.innerHTML;
        // Submit form when autocomplete option is selected
        document.querySelector(".search").submit();
      }
    })
  });
}

// Handle invalid searches for when user presses 'enter' key
const handleSubmission = () => {
  let searchForm = document.querySelector(".search");
  searchForm.addEventListener("input", (e) => {
    if (e.keyCode === 13) {
      // Prevent form submission
      let searchInput = document.querySelector(".search-bar").value;
      let autocompleteNode = document.querySelector(".auto-complete").firstChild.innerHTML;
      if (searchInput.length === 0 || autocompleteNode === "No results found") {
        e.preventDefault();
      }
    }
  });
}

// Exit autocomplete box when clicked anywhere else
const exitAutocomplete = () => {
  let body = document.querySelector("main");
  body.addEventListener("click", () => {
    document.querySelector(".auto-complete").style.visibility = "hidden";
  });
}

getCurrentStocks();
initiateAutocomplete();
handleSubmission();
exitAutocomplete();
