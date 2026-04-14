document.querySelectorAll('.has-sub').forEach(menu => {
  menu.addEventListener('click', () => {
    const submenu = menu.nextElementSibling;

    if (!submenu || !submenu.classList.contains('submenu')) return;

    // Fecha todos
    document.querySelectorAll('.submenu').forEach(s => {
      if (s !== submenu) s.classList.remove('open');
    });

    document.querySelectorAll('.has-sub').forEach(m => {
      if (m !== menu) m.classList.remove('open');
    });

    // Abre o atual
    submenu.classList.toggle('open');
    menu.classList.toggle('open');
  });
});