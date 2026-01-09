// api.js
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api';

export async function getCurricula() {
  const res = await fetch(`${API_BASE}/curricula`);
  return res.json();
}

export async function getCurriculum(name) {
  const res = await fetch(`${API_BASE}/curricula/${name}`);
  return res.json();
}

export async function submitAdmission(formData) {
  const res = await fetch(`${API_BASE}/admissions`, {
    method: 'POST',
    body: formData
  });
  return res.json();
}

export async function sendContact(data) {
  const res = await fetch(`${API_BASE}/contact`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return res.json();
}

export async function login(credentials) {
  const res = await fetch(`${API_BASE}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials)
  });
  return res.json();
}
