// for the index humburger side menu


  const hamburger = document.querySelector('.hamburger');
  const navLinks = document.querySelector('.nav-links');
  const navBtn = document.querySelector('.nav-btn');

  hamburger.addEventListener('click', () => {
    navLinks.classList.toggle('active');
    navBtn.classList.toggle('active');
  });
