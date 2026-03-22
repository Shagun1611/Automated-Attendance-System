import React, { useEffect, useState } from 'react';
import { apiService } from '../../services/apiService';
import { authService } from '../../services/authService';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Switch,
  FormControlLabel
} from '@mui/material';

export default function AdminAddTeacher() {
  const [classes, setClasses] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    full_name: '',
    class_id: ''
  });
  const [assignOpen, setAssignOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [selectedTeacher, setSelectedTeacher] = useState(null);
  const [editForm, setEditForm] = useState({ email: '', full_name: '', password: '', is_active: true, class_id: '' });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadClasses() {
      try {
        const resp = await apiService.getClassList();
        setClasses(resp.classes || resp);
      } catch (err) {
        console.error('Failed to load classes', err);
      }
    }
    async function loadTeachers() {
      try {
        const resp = await apiService.listTeachers();
        setTeachers(resp.teachers || resp);
      } catch (err) {
        console.error('Failed to load teachers', err);
      }
    }
    loadClasses();
    loadTeachers();
  }, []);

  function onChange(e) {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  }

  async function onSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    setError(null);

    // Prepare payload
    const payload = {
      username: form.username,
      email: form.email,
      password: form.password,
      full_name: form.full_name,
      class_id: form.class_id ? Number(form.class_id) : undefined
    };

    try {
      const resp = await apiService.createTeacher(payload);
      setMessage(resp.message || 'Teacher created');
      setForm({ username: '', email: '', password: '', full_name: '', class_id: '' });
      // Refresh lists
      const t = await apiService.listTeachers();
      setTeachers(t.teachers || t);
      const c = await apiService.getClassList();
      setClasses(c.classes || c);
    } catch (err) {
      setError(err.message || 'Failed to create teacher');
    } finally {
      setLoading(false);
    }
  }

  // Simple role guard in UI
  const currentUser = authService.getCurrentUser();
  if (!currentUser || currentUser.role !== 'admin') {
    return <div>You must be an administrator to access this page.</div>;
  }

  return (
    <div style={{ padding: 20 }}>
      <h2>Add Teacher</h2>
      {message && <div style={{ color: 'green' }}>{message}</div>}
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <form onSubmit={onSubmit} style={{ maxWidth: 480 }}>
        <div>
          <label>Username</label>
          <input name="username" value={form.username} onChange={onChange} required />
        </div>
        <div>
          <label>Email</label>
          <input name="email" value={form.email} onChange={onChange} type="email" required />
        </div>
        <div>
          <label>Password</label>
          <input name="password" value={form.password} onChange={onChange} type="password" required />
        </div>
        <div>
          <label>Full name</label>
          <input name="full_name" value={form.full_name} onChange={onChange} required />
        </div>
        <div>
          <label>Assign to Class (optional)</label>
          <select name="class_id" value={form.class_id} onChange={onChange}>
            <option value="">-- none --</option>
            {classes && classes.map((c) => (
              <option key={c.id} value={c.id}>{`${c.name} ${c.section} (${c.academic_year})`}</option>
            ))}
          </select>
        </div>
        <div style={{ marginTop: 12 }}>
          <button type="submit" disabled={loading}>{loading ? 'Creating...' : 'Create Teacher'}</button>
        </div>
      </form>

      <hr style={{ margin: '24px 0' }} />

      <h3>Classes</h3>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{ textAlign: 'left', padding: 8 }}>Class</th>
            <th style={{ textAlign: 'left', padding: 8 }}>Section</th>
            <th style={{ textAlign: 'left', padding: 8 }}>Academic Year</th>
            <th style={{ textAlign: 'left', padding: 8 }}>Assigned Teacher</th>
          </tr>
        </thead>
        <tbody>
          {classes && classes.map((c) => (
            <tr key={c.id} style={{ borderTop: '1px solid #eee' }}>
              <td style={{ padding: 8 }}>{c.name}</td>
              <td style={{ padding: 8 }}>{c.section}</td>
              <td style={{ padding: 8 }}>{c.academic_year}</td>
              <td style={{ padding: 8 }}>{c.teacher_name || '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <hr style={{ margin: '24px 0' }} />

      <h3>Teachers</h3>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{ textAlign: 'left', padding: 8 }}>Name</th>
            <th style={{ textAlign: 'left', padding: 8 }}>Email</th>
            <th style={{ textAlign: 'left', padding: 8 }}>Role</th>
            <th style={{ textAlign: 'left', padding: 8 }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {teachers && teachers.map((t) => (
            <tr key={t.id} style={{ borderTop: '1px solid #eee' }}>
              <td style={{ padding: 8 }}>{t.full_name}</td>
              <td style={{ padding: 8 }}>{t.email}</td>
              <td style={{ padding: 8 }}>{t.role}</td>
              <td style={{ padding: 8 }}>
                <Button variant="outlined" size="small" onClick={() => {
                  setSelectedTeacher(t);
                  setAssignOpen(true);
                }}>Assign</Button>
                <Button variant="contained" size="small" sx={{ ml: 1 }} onClick={() => {
                  setSelectedTeacher(t);
                  setEditForm({ email: t.email, full_name: t.full_name, password: '', is_active: t.is_active, class_id: '' });
                  setEditOpen(true);
                }}>Edit</Button>
                <Button color="error" size="small" sx={{ ml: 1 }} onClick={async () => {
                  if (!window.confirm('Delete this teacher? This will unassign their classes.')) return;
                  try {
                    await apiService.deleteTeacher(t.id);
                    const tt = await apiService.listTeachers();
                    setTeachers(tt.teachers || tt);
                    const cc = await apiService.getClassList();
                    setClasses(cc.classes || cc);
                    setMessage('Teacher deleted');
                  } catch (err) {
                    setError(err.message || 'Failed to delete teacher');
                  }
                }}>Delete</Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Assign Dialog */}
      <Dialog open={assignOpen} onClose={() => setAssignOpen(false)}>
        <DialogTitle>Assign Teacher to Class</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 1 }}>
            <InputLabel id="assign-class-label">Class</InputLabel>
            <Select
              labelId="assign-class-label"
              value={selectedTeacher?.class_id || ''}
              label="Class"
              onChange={(e) => setSelectedTeacher(s => ({ ...s, class_id: e.target.value }))}
            >
              <MenuItem value="">-- Unassign --</MenuItem>
              {classes.map(c => (
                <MenuItem key={c.id} value={c.id}>{`${c.name} ${c.section} (${c.academic_year})`}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAssignOpen(false)}>Cancel</Button>
          <Button onClick={async () => {
            try {
              await apiService.updateTeacher(selectedTeacher.id, { class_id: selectedTeacher.class_id === '' ? '' : Number(selectedTeacher.class_id) });
              const tt = await apiService.listTeachers();
              setTeachers(tt.teachers || tt);
              const cc = await apiService.getClassList();
              setClasses(cc.classes || cc);
              setMessage('Teacher assignment updated');
              setAssignOpen(false);
            } catch (err) {
              setError(err.message || 'Failed to assign teacher');
            }
          }}>Save</Button>
        </DialogActions>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={editOpen} onClose={() => setEditOpen(false)}>
        <DialogTitle>Edit Teacher</DialogTitle>
        <DialogContent>
          <TextField fullWidth label="Full name" sx={{ mt: 1 }} value={editForm.full_name} onChange={(e) => setEditForm(f => ({ ...f, full_name: e.target.value }))} />
          <TextField fullWidth label="Email" sx={{ mt: 1 }} value={editForm.email} onChange={(e) => setEditForm(f => ({ ...f, email: e.target.value }))} />
          <TextField fullWidth label="Password (leave blank to keep)" sx={{ mt: 1 }} type="password" value={editForm.password} onChange={(e) => setEditForm(f => ({ ...f, password: e.target.value }))} />
          <FormControlLabel control={<Switch checked={editForm.is_active} onChange={(e) => setEditForm(f => ({ ...f, is_active: e.target.checked }))} />} label="Active" sx={{ mt: 1 }} />
          <FormControl fullWidth sx={{ mt: 1 }}>
            <InputLabel id="edit-class-label">Assign Class</InputLabel>
            <Select labelId="edit-class-label" value={editForm.class_id} label="Assign Class" onChange={(e) => setEditForm(f => ({ ...f, class_id: e.target.value }))}>
              <MenuItem value="">-- none --</MenuItem>
              {classes.map(c => (
                <MenuItem key={c.id} value={c.id}>{`${c.name} ${c.section} (${c.academic_year})`}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditOpen(false)}>Cancel</Button>
          <Button onClick={async () => {
            try {
              const payload = {
                full_name: editForm.full_name,
                email: editForm.email,
                password: editForm.password || undefined,
                is_active: editForm.is_active,
                class_id: editForm.class_id === '' ? '' : Number(editForm.class_id)
              };
              await apiService.updateTeacher(selectedTeacher.id, payload);
              const tt = await apiService.listTeachers();
              setTeachers(tt.teachers || tt);
              const cc = await apiService.getClassList();
              setClasses(cc.classes || cc);
              setMessage('Teacher updated');
              setEditOpen(false);
            } catch (err) {
              setError(err.message || 'Failed to update teacher');
            }
          }}>Save</Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}
