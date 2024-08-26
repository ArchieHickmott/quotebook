let colorMode = localStorage.getItem('colorMode');

const themeSwitch = document.getElementById('theme-switch');
const moon = document.getElementById('moon');
const sun = document.getElementById('sun');

if (colorMode === 'darkmode') {
  document.body.classList.remove('lightmode');
  sun.classList.add('invisible');
  moon.classList.remove('invisible');
} else {
  document.body.classList.add('lightmode');
  sun.classList.remove('invisible');
  moon.classList.add('invisible');
}

themeSwitch.addEventListener("click", () => {
  if (colorMode === 'darkmode') {
    document.body.classList.add('lightmode');
    sun.classList.remove('invisible');
    moon.classList.add('invisible');
    localStorage.setItem('colorMode', 'lightmode');
    colorMode = 'lightmode';
  } else {
    document.body.classList.remove('lightmode');
    sun.classList.add('invisible');
    moon.classList.remove('invisible');
    localStorage.setItem('colorMode', 'darkmode');
    colorMode = 'darkmode';
  }
});