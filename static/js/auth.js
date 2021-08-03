"use strict"

// Handle empty forms
const emptyFormError = () => {
  let form = document.querySelector('form');
  form.addEventListener("submit", (e) => {
    let usernameInput = document.querySelector('#usernameInput');
    let passwordInput = document.querySelector('#passwordInput');
    if (usernameInput.value.length == 0) {
      e.preventDefault();
      // Show alert for empty username
      emptyFormAlert('username')
    } else if (passwordInput.value.length == 0) {
      e.preventDefault();
      // Show alert for empty password
      emptyFormAlert('password')
    }
  });
}


// Show an alert
const emptyFormAlert = (inputType) => {
  let alert = document.createElement('div');
  alert.setAttribute('role', 'alert');
  alert.classList.add('alert');
  alert.classList.add('alert-danger');
  alert.innerHTML = 'Please submit a ' + inputType;
  let parent = document.querySelector('.register-container');
  let title = document.querySelector('.auth-title');
  parent.insertBefore(alert, title);
}

emptyFormError()