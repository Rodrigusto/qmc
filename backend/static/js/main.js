function renderMenu(menu) {
  const container = document.getElementById('sidebar-menu')
  container.innerHTML = ''

  menu.forEach(group => {
    if (group.section) {
      const section = document.createElement('div')
      section.className = 'sidebar-section'
      section.innerText = group.section
      container.appendChild(section)
    }

    group.items.forEach(item => {

      // Grupo (com submenu)
      if (item.type === 'group') {
        const header = document.createElement('div')
        header.className = 'has-sub'
        header.innerHTML = `
          <span><span class="icon">${item.icon}</span> ${item.label}</span>
          <span class="arrow">▸</span>
        `

        const submenu = document.createElement('div')
        submenu.className = 'submenu'

        item.children.forEach(child => {
          const link = document.createElement('a')
          link.href = child.url
          link.innerText = child.label
          submenu.appendChild(link)
        })

        header.onclick = () => {
          submenu.classList.toggle('open')
          header.classList.toggle('open')
        }

        container.appendChild(header)
        container.appendChild(submenu)

      } else {
        // Link simples
        const link = document.createElement('a')
        link.href = item.url
        link.innerHTML = `<span class="icon">${item.icon}</span> ${item.label}`
        container.appendChild(link)
      }

    })
  })
}