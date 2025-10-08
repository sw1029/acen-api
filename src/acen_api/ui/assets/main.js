const state = {
  apiKey: '',
  userId: '',
};

function buildHeaders({ requireUser = true, requireApiKey = true, json = true } = {}) {
  const headers = {};
  if (json) headers['Content-Type'] = 'application/json';
  headers['Accept'] = 'application/json';

  if (state.apiKey) headers['X-API-Key'] = state.apiKey;
  else if (requireApiKey) throw new Error('API Key가 필요합니다. 상단에서 입력하세요.');

  if (state.userId) headers['X-User-Id'] = state.userId;
  else if (requireUser) throw new Error('User ID가 필요합니다. 사용자 생성 후 설정하세요.');

  return headers;
}

async function postJSON(url, data, options = {}) {
  const { requireUser = true, requireApiKey = true } = options;
  const res = await fetch(url, {
    method: 'POST',
    headers: buildHeaders({ requireUser, requireApiKey, json: true }),
    body: JSON.stringify(data),
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw body;
  return body;
}

async function getJSON(url, { requireUser = false, requireApiKey = false } = {}) {
  const headers = {};
  try {
    Object.assign(headers, buildHeaders({ requireUser, requireApiKey, json: false }));
  } catch (err) {
    // 키가 필요하지만 없는 경우 호출하지 않음
    throw err;
  }
  const res = await fetch(url, { headers });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw body;
  return body;
}

function renderError(err) {
  if (!err) return '알 수 없는 오류';
  if (err.field_errors && Array.isArray(err.field_errors)) {
    return err.field_errors.map(e => `${e.loc.join('.')}: ${e.message}`).join(' | ');
  }
  if (err.message) return err.message;
  return JSON.stringify(err);
}

function qs(sel) { return document.querySelector(sel); }

// Template form
const schedulesDiv = document.createElement('div');

function scheduleRow() {
  const wrap = document.createElement('div');
  wrap.className = 'row';
  wrap.innerHTML = `
    <label>title <input name="title" required /></label>
    <label>order_index <input name="order_index" type="number" min="0" value="0" /></label>
    <label>tags <input name="tags" /></label>
    <label>extra_info <input name="extra_info" /></label>
  `;
  return wrap;
}

window.addEventListener('DOMContentLoaded', () => {
  const apiKeyInput = qs('#api-key');
  const userIdInput = qs('#user-id');
  apiKeyInput?.addEventListener('input', () => { state.apiKey = apiKeyInput.value.trim(); });
  userIdInput?.addEventListener('input', () => { state.userId = userIdInput.value.trim(); });

  const apiKeyTableBody = qs('#apikey-table tbody');
  async function refreshApiKeys() {
    try {
      const keys = await getJSON('/api-keys', { requireApiKey: !!state.apiKey, requireUser: false });
      apiKeyTableBody.innerHTML = '';
      keys.forEach((item) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${item.id}</td>
          <td>${item.description ?? ''}</td>
          <td>${item.created_at ?? ''}</td>
          <td>${item.revoked_at ?? ''}</td>
          <td>
            ${item.revoked_at ? '' : `<button data-id="${item.id}" class="revoke-key">회수</button>`}
          </td>
        `;
        apiKeyTableBody.appendChild(tr);
      });
    } catch (err) {
      if (String(err).includes('API Key가 필요')) {
        apiKeyTableBody.innerHTML = '<tr><td colspan="5">API Key 입력 후 새로고칠 수 있습니다.</td></tr>';
      }
    }
  }

  // schedules container
  const schedContainer = qs('#schedules');
  const addBtn = qs('#add-schedule');
  addBtn?.addEventListener('click', () => schedContainer.appendChild(scheduleRow()));

  // user submit
  const userForm = qs('#user-form');
  userForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(userForm);
    const payload = {
      username: fd.get('username') || null,
      display_name: fd.get('display_name') || null,
      email: fd.get('email') || null,
    };
    const out = qs('#user-result');
    try {
      const res = await postJSON('/users', payload, { requireUser: false, requireApiKey: true });
      out.textContent = `생성됨: id=${res.id}`;
      state.userId = String(res.id);
      if (userIdInput) userIdInput.value = state.userId;
    } catch (err) {
      out.textContent = `오류: ${renderError(err)}`;
    }
  });

  const apiKeyForm = qs('#apikey-form');
  apiKeyForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(apiKeyForm);
    const payload = { description: fd.get('description') || null };
    const out = qs('#apikey-result');
    try {
      const res = await postJSON('/api-keys', payload, { requireApiKey: !!state.apiKey, requireUser: false });
      out.textContent = `새 키: ${res.key}`;
      state.apiKey = res.key;
      if (apiKeyInput) apiKeyInput.value = state.apiKey;
      await refreshApiKeys();
    } catch (err) {
      out.textContent = `오류: ${renderError(err)}`;
    }
  });

  apiKeyTableBody?.addEventListener('click', async (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    if (target.classList.contains('revoke-key')) {
      const id = target.dataset.id;
      if (!id) return;
      try {
        const headers = buildHeaders({ requireApiKey: true, requireUser: false, json: false });
        const res = await fetch(`/api-keys/${id}`, { method: 'DELETE', headers });
        if (!res.ok) {
          const body = await res.json().catch(() => ({}));
          throw body;
        }
        await refreshApiKeys();
      } catch (err) {
        alert(`회수 실패: ${renderError(err)}`);
      }
    }
  });

  // template submit
  const tplForm = qs('#template-form');
  tplForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(tplForm);
    const schedules = Array.from(qs('#schedules').querySelectorAll('.row')).map(row => {
      const o = {};
      row.querySelectorAll('input').forEach(inp => { o[inp.name] = inp.value; });
      o.order_index = Number(o.order_index || 0);
      return o;
    });
    const payload = {
      name: fd.get('name'),
      description: fd.get('description') || null,
      theme: fd.get('theme') || null,
      schedules: schedules.length ? schedules : undefined,
    };
    const out = qs('#template-result');
    try {
      const res = await postJSON('/templates', payload, { requireUser: false, requireApiKey: true });
      out.textContent = `생성됨: id=${res.id}`;
    } catch (err) {
      out.textContent = `오류: ${renderError(err)}`;
    }
  });

  // product submit
  const prodForm = qs('#product-form');
  prodForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(prodForm);
    const payload = {
      name: fd.get('name'), brand: fd.get('brand') || null,
      tags: fd.get('tags') || null, description: fd.get('description') || null,
    };
    const out = qs('#product-result');
    try {
      const res = await postJSON('/products', payload, { requireApiKey: true, requireUser: false });
      out.textContent = `생성됨: id=${res.id}`;
    } catch (err) {
      out.textContent = `오류: ${renderError(err)}`;
    }
  });

  // calendar submit
  const calForm = qs('#calendar-form');
  calForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(calForm);
    const payload = { name: fd.get('name'), description: fd.get('description') || null };
    const out = qs('#calendar-result');
    try {
      const res = await postJSON('/calendars', payload, { requireApiKey: true, requireUser: true });
      out.textContent = `생성됨: id=${res.id}`;
    } catch (err) {
      out.textContent = `오류: ${renderError(err)}`;
    }
  });

  // date submit
  const dateForm = qs('#date-form');
  dateForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(dateForm);
    const payload = {
      calendar_id: Number(fd.get('calendar_id')),
      scheduled_date: fd.get('scheduled_date'),
      schedule_done: Number(fd.get('schedule_done') || 0),
      schedule_total: Number(fd.get('schedule_total') || 0),
      notes: fd.get('notes') || null,
      image_path: fd.get('image_path') || null,
    };
    const out = qs('#date-result');
    try {
      const res = await postJSON('/dates', payload, { requireApiKey: true, requireUser: true });
      out.textContent = `생성됨: id=${res.id}`;
    } catch (err) {
      out.textContent = `오류: ${renderError(err)}`;
    }
  });

  // schedule submit
  const schForm = qs('#schedule-form');
  schForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(schForm);
    const templateId = Number(fd.get('template_id'));
    const payload = {
      title: fd.get('title'),
      order_index: Number(fd.get('order_index') || 0),
      tags: fd.get('tags') || null,
      extra_info: fd.get('extra_info') || null,
    };
    const out = qs('#schedule-result');
    try {
      const res = await postJSON(`/templates/${templateId}/schedules`, payload, { requireApiKey: true, requireUser: false });
      out.textContent = `생성됨: id=${res.id}`;
    } catch (err) {
      out.textContent = `오류: ${renderError(err)}`;
    }
  });

  refreshApiKeys();
});
