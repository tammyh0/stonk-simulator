import { removeChildren } from "./helpers.js";

"use strict";

const buyStock = () => {
  let stockForm = document.querySelector("#buyForm");
  stockForm.addEventListener("submit", (e) => {
    if (document.querySelector('.alert')) {
      document.querySelector('.alert').remove();
    } 

    let inputValue = document.querySelector("#buyUnitsInput").value;
    // Handle when user doesn't type in a number
    if (isNaN(inputValue)) {
      createAlert("Please submit a valid number", "#buyBody", "#cash");
      e.preventDefault();
    } else {
      // Handle when user types in a number but they can't afford it 
      let price = Number(document.querySelector('.stock-overview-title h2').innerHTML.substr(11))
      let totalPrice = inputValue * price;
      totalPrice = totalPrice.toFixed(2);
      let cash = Number(document.querySelector('#cash').innerHTML.substr(20));
      if (totalPrice > cash) {
        createAlert("Not enough cash. Please submit a different value.", "#buyBody", "#cash");
        e.preventDefault();
      } else if (totalPrice == 0) {
        createAlert("Please enter a value greater than 0.", "#buyBody", "#cash");
        e.preventDefault();
      }
    }
  });
}

const sellStock = () => {
  let stockForm = document.querySelector("#sellForm");
  stockForm.addEventListener("submit", (e) => {
    if (document.querySelector('.alert')) {
      document.querySelector('.alert').remove();
    } 

    let inputValue = document.querySelector("#sellUnitsInput").value;
    // Handle when user doesn't type in a number
    if (isNaN(inputValue)) {
      createAlert("Please submit a valid number", "#sellBody", "#shares");
      e.preventDefault();
    } else {
      // Handle when user types a number that's over or less than their holdings
      let holdings = Number(document.querySelector("#shares").innerHTML.substr(34, 1));
      if (inputValue <= 0 || inputValue > holdings) {
        createAlert("Please submit a valid number", "#sellBody", "#shares");
        e.preventDefault();
      }
    }
  });
}


const createAlert = (message, firstElement, secondElement) => {
  let alert = document.createElement('div');
  alert.setAttribute('role', 'alert');
  alert.classList.add('alert');
  alert.classList.add('alert-danger');
  alert.innerHTML = message;
  let parent = document.querySelector(firstElement);
  let title = document.querySelector(secondElement);
  parent.insertBefore(alert, title);
}

buyStock();
sellStock();