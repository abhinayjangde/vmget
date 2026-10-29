const copyButtons = document.querySelectorAll("[data-copy]");
const generatedCommand = document.querySelector("#generated-command");
const formatSelect = document.querySelector("#format");
const qualitySelect = document.querySelector("#quality");
const copyBuilder = document.querySelector("#copy-builder");
const copyGenerated = document.querySelector("#copy-generated");

function copyText(text, button) {
  navigator.clipboard.writeText(text).then(() => {
    const original = button.textContent;
    button.textContent = "copied!";
    window.setTimeout(() => { button.textContent = original; }, 1400);
  }).catch(() => {
    button.textContent = "select manually";
    window.setTimeout(() => { button.textContent = "copy"; }, 1800);
  });
}

copyButtons.forEach((button) => {
  button.addEventListener("click", () => copyText(button.dataset.copy, button));
});

function updateCommand() {
  generatedCommand.textContent = `vmget "URL" -F ${formatSelect.value} -q ${qualitySelect.value}`;
}

function copyGeneratedCommand(button) {
  copyText(generatedCommand.textContent, button);
}

formatSelect.addEventListener("change", updateCommand);
qualitySelect.addEventListener("change", updateCommand);
copyBuilder.addEventListener("click", () => copyGeneratedCommand(copyBuilder));
copyGenerated.addEventListener("click", () => copyGeneratedCommand(copyGenerated));

const menuToggle = document.querySelector(".menu-toggle");
const siteNav = document.querySelector(".site-nav");
menuToggle.addEventListener("click", () => {
  const isOpen = siteNav.classList.toggle("open");
  menuToggle.setAttribute("aria-expanded", String(isOpen));
});
siteNav.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => {
    siteNav.classList.remove("open");
    menuToggle.setAttribute("aria-expanded", "false");
  });
});

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add("visible");
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });
document.querySelectorAll(".reveal").forEach((element) => observer.observe(element));

document.querySelector("#year").textContent = new Date().getFullYear();
