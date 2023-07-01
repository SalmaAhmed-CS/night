let favRecipes = document.querySelectorAll(".edit-profile .item");
favRecipes.forEach((item) => {
  item.addEventListener("click", () => {
    item.classList.toggle("fav-item");
  });
});
// Glass Effect
let loginBtn = document.querySelectorAll(".loginBtn");
let blurEffectElement = document.getElementById("blurEffectElement");
let close = document.querySelectorAll(".btn-close");
let closeModal = document.querySelector(".close-signup");
let createNewAccountBtn = document.querySelector(".new-acount");
let completeSignUpModel = document.getElementById("completeSignUpModel");
let completeSignUpBtn = document.getElementById("complete-signup-btn");
signUpModel = document.querySelector(".sign-up-form");
signInModel = document.getElementById("loginModal");
console.log(loginBtn);

loginBtn.forEach((btn) => {
  btn.addEventListener("click", () => {
    blurEffectElement.classList.remove("d-none");
    signInModel.classList.add("show");
    signInModel.style.display = "block";
  });
});

close.forEach((closeBtn) => {
  closeBtn.addEventListener("click", () => {
    blurEffectElement.classList.add("d-none");
    document.querySelectorAll(".btn-close").forEach((btn) => {
      btn.click();
    });
  });
});

createNewAccountBtn.addEventListener("click", () => {
  signInModel.classList.remove("show");
  signInModel.style.display = "none";
  document.querySelectorAll(".btn-close").forEach((btn) => {
    btn.click();
  });
  blurEffectElement.classList.remove("d-none");
});
completeSignUpBtn.addEventListener("click", () => {
  blurEffectElement.classList.remove("d-none");
  completeSignUpModel.classList.remove("show");

  document.querySelectorAll(".btn-close").forEach((btn) => {
    btn.click();
  });
});
