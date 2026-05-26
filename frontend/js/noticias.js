// ============================================================
//  js/noticias.js
//  Módulo de notícias — busca, filtra e renderiza as notícias.
// ============================================================

let categoriaAtual = 'Todas';
let paginaAtual = 1;
const POR_PAGINA = 12;

// ── Ícones por categoria ──────────────────────────────────
const ICONES_CAT = {
  Python: '🐍', DevOps: '⚙️', IA: '🤖',
  Segurança: '🔐', Web: '🌐', Geral: '📰', Todas: '🔭',
};

// ── Renderização ──────────────────────────────────────────
function renderizarNoticia(noticia) {
  const { titulo, descricao, url, imagem, fonte, publicado_em, categoria } = noticia;

  const imgHtml = imagem
    ? `<img src="${imagem}" alt="${titulo}" class="noticia-img" loading="lazy" onerror="this.parentElement.innerHTML='<div class=noticia-img-placeholder>${ICONES_CAT[categoria] || '📰'}</div>'">`
    : `<div class="noticia-img-placeholder">${ICONES_CAT[categoria] || '📰'}</div>`;

  return `
    <article class="noticia-card">
      ${imgHtml}
      <div class="noticia-body">
        <div class="noticia-meta">
          <span class="noticia-fonte">${fonte.nome}</span>
          <span class="noticia-data">${publicado_em}</span>
        </div>
        <h3 class="noticia-titulo">${titulo}</h3>
        ${descricao ? `<p class="noticia-desc">${descricao}</p>` : ''}
        <div class="noticia-footer">
          <span class="noticia-cat ${categoria}">${ICONES_CAT[categoria] || ''} ${categoria}</span>
          <a href="${url}" target="_blank" rel="noopener" class="noticia-link">Ler mais →</a>
        </div>
      </div>
    </article>
  `;
}

function renderizarCategorias(categorias) {
  const container = document.getElementById('categoriasBtns');
  container.innerHTML = categorias.map(cat => `
    <button
      class="cat-btn ${cat === categoriaAtual ? 'active' : ''}"
      onclick="filtrarCategoria('${cat}', this)">
      ${ICONES_CAT[cat] || ''} ${cat}
    </button>
  `).join('');
}

function renderizarPaginacao(total) {
  const totalPaginas = Math.ceil(total / POR_PAGINA);
  if (totalPaginas <= 1) {
    document.getElementById('paginacao').innerHTML = '';
    return;
  }

  let html = '';
  if (paginaAtual > 1) {
    html += `<button class="pag-btn" onclick="mudarPagina(${paginaAtual - 1})">← Anterior</button>`;
  }
  for (let i = 1; i <= totalPaginas; i++) {
    html += `<button class="pag-btn ${i === paginaAtual ? 'active' : ''}" onclick="mudarPagina(${i})">${i}</button>`;
  }
  if (paginaAtual < totalPaginas) {
    html += `<button class="pag-btn" onclick="mudarPagina(${paginaAtual + 1})">Próximo →</button>`;
  }

  document.getElementById('paginacao').innerHTML = html;
}

// ── Busca e filtros ───────────────────────────────────────
async function carregarNoticias() {
  const grid = document.getElementById('noticiasGrid');
  grid.innerHTML = '<div class="loading"><div class="spinner"></div> Carregando notícias...</div>';

  try {
    // Busca categorias
    const resCat = await fetch('/api/noticias/categorias');
    const dataCat = await resCat.json();
    renderizarCategorias(dataCat.categorias);

    // Busca notícias
    const params = new URLSearchParams({
      pagina: paginaAtual,
      por_pagina: POR_PAGINA,
    });
    if (categoriaAtual !== 'Todas') params.append('categoria', categoriaAtual);

    const res = await fetch(`/api/noticias/?${params}`);
    if (!res.ok) throw new Error('Erro na API');
    const data = await res.json();

    if (data.noticias.length === 0) {
      grid.innerHTML = '<div class="loading">Nenhuma notícia encontrada nesta categoria.</div>';
      return;
    }

    grid.innerHTML = data.noticias.map(renderizarNoticia).join('');
    renderizarPaginacao(data.total);

    const agora = new Date().toLocaleTimeString('pt-BR');
    document.getElementById('noticiasUpdate').textContent = `Atualizado: ${agora}`;

  } catch (err) {
    console.error('Erro ao carregar notícias:', err);
    grid.innerHTML = '<div class="loading">Erro ao carregar notícias. Tente novamente.</div>';
  }
}

function filtrarCategoria(categoria, btn) {
  categoriaAtual = categoria;
  paginaAtual = 1;

  document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');

  carregarNoticias();
}

function mudarPagina(pagina) {
  paginaAtual = pagina;
  carregarNoticias();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
