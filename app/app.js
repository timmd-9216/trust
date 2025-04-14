let articles = [];
let annotations = {};

Promise.all([
  fetch('../data/lavoz_input_04FEB2025.json').then(res => res.json()),
  fetch('../data/lavoz_output_04FEB2025.json').then(res => res.json())
])
.then(([inputData, annotationData]) => {
  // Create lookup table from annotationData by ID
  annotationData.forEach(entry => {
    annotations[entry.id] = entry.metrics?.general?.num_chars?.value || null;
  });

  // Merge num_chars into input data
  articles = inputData.map(article => ({
    ...article,
    num_chars: annotations[article.id] || null
  }));

  renderListView(); // call existing renderer
})
.catch(error => console.error('Failed to load data:', error));

function renderListView() {
  const app = document.getElementById('app');
  app.innerHTML = '';

  const header = document.createElement('header');
  const title = document.createElement('h1');
  title.textContent = 'News Dashboard';
  const desc = document.createElement('p');
  desc.className = 'description';
  desc.textContent = 'A simple viewer for imported news articles including title, date, reviewed status, and length.';
  header.appendChild(title);
  header.appendChild(desc);

  const style = document.createElement('style');
  style.textContent = `
    .clickable {
      cursor: pointer;
      color: #007BFF;
      text-decoration: none;
    }
    .clickable:hover {
      text-decoration: underline;
    }
    .back-button {
      cursor: pointer;
      color: #007BFF;
      font-size: 1rem;
      margin-bottom: 1rem;
      display: inline-block;
    }
    .back-button:hover {
      text-decoration: underline;
    }
  `;
  document.head.appendChild(style);

  const table = document.createElement('table');
  const thead = document.createElement('thead');
  thead.innerHTML = `
    <tr>
      <th>Title</th>
      <th>Date</th>
      <th>Reviewed</th>
      <th>Chars</th>
    </tr>
  `;
  table.appendChild(thead);

  const tbody = document.createElement('tbody');
  articles.forEach((article, index) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td class="clickable">${article.titulo}</td>
      <td>${article.fecha}</td>
      <td class="${article.reviewed ? 'reviewed-true' : 'reviewed-false'}">
        ${article.reviewed ? 'Yes' : 'No'}
      </td>
      <td>${article.num_chars ?? '-'}</td>
    `;
    row.querySelector('.clickable').addEventListener('click', () => renderDetailView(article));
    tbody.appendChild(row);
  });

  table.appendChild(tbody);
  app.appendChild(header);
  app.appendChild(table);
}

function renderDetailView(article) {
  const app = document.getElementById('app');
  app.innerHTML = '';

  const back = document.createElement('div');
  back.className = 'back-button';
  back.innerHTML = '← Back to list';
  back.addEventListener('click', renderListView);

  const container = document.createElement('div');
  container.style.display = 'flex';
  container.style.height = '100vh';

  const left = document.createElement('div');
  left.style.flex = '1';
  left.style.padding = '2rem';
  left.style.overflowY = 'auto';
  left.innerHTML = `
    <h2>${article.titulo}</h2>
    <p>${article.cuerpo?.replace(/\n/g, '<br>') ?? ''}</p>
  `;

  const right = document.createElement('div');
  right.style.flex = '1';
  right.style.padding = '2rem';
  right.style.background = '#f4f4f4';
  right.innerHTML = '<p>(Reserved for future functionality)</p>';

  app.appendChild(back);
  container.appendChild(left);
  container.appendChild(right);
  app.appendChild(container);
}