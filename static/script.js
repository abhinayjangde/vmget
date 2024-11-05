// document.getElementById("mobile-menu-button").addEventListener("click", function () {
//   const mobileMenu = document.getElementById("mobile-menu");
//   mobileMenu.classList.toggle("hidden");
// });

document.addEventListener("DOMContentLoaded", function() {
  document.getElementById("mobile-menu-button").addEventListener("click", function () {
    const mobileMenu = document.getElementById("mobile-menu");
    mobileMenu.classList.toggle("hidden");
  });
});




// WebSocket connection for real-time progress updates
document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    socket.on('download_progress', (data) => {
        const app = Alpine.data('downloaderApp');
        if (app) {
            app.progress = data.progress;
        }
    });
});
