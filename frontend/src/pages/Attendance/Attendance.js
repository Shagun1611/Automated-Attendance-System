import React, { useState, useEffect, useCallback } from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
  Alert
} from '@mui/material';
import CameraCapture from '../../components/CameraCapture/CameraCapture';
import {
  Add as AddIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Schedule as ScheduleIcon,
  CalendarToday as CalendarIcon,
  Person as PersonIcon,
  CameraAlt as CameraAltIcon
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import { attendanceService } from '../../services/attendanceService';
import { studentService } from '../../services/studentService';

function TabPanel({ children, value, index }) {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

function Attendance() {
  const [tabValue, setTabValue] = useState(0);
  const [students, setStudents] = useState([]);
  const [attendanceRecords, setAttendanceRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [classFilter, setClassFilter] = useState('');
  const [sectionFilter, setSectionFilter] = useState('');
  const [formData, setFormData] = useState({
    student_id: '',
    date: new Date().toISOString().split('T')[0],
    status: 'present',
    time_in: new Date().toLocaleTimeString('en-GB', { hour12: false, hour: '2-digit', minute: '2-digit' }),
    notes: ''
  });
  const [recognizing, setRecognizing] = useState(false);
  const [recognitionResults, setRecognitionResults] = useState(null);
  const [showCamera, setShowCamera] = useState(false);

  useEffect(() => {
    fetchStudents();
  }, []);

  const fetchAttendanceByDate = useCallback(async () => {
    setLoading(true);
    try {
      const filters = {};
      if (classFilter) filters.class = classFilter;
      if (sectionFilter) filters.section = sectionFilter;

      const result = await attendanceService.getAttendanceByDate(selectedDate, filters);
      if (result.success) {
        setAttendanceRecords(result.data.attendance || []);
      } else {
        toast.error(result.error);
        setAttendanceRecords([]);
      }
    } catch (error) {
      toast.error('Failed to fetch attendance records');
      setAttendanceRecords([]);
    } finally {
      setLoading(false);
    }
  }, [selectedDate, classFilter, sectionFilter]);

  useEffect(() => {
    if (tabValue === 1) {
      fetchAttendanceByDate();
    }
  }, [tabValue, fetchAttendanceByDate]);

  const fetchStudents = async () => {
    try {
      const result = await studentService.getAllStudents();
      if (result.success) {
        setStudents(result.data.students || []);
      } else {
        toast.error(result.error);
      }
    } catch (error) {
      toast.error('Failed to fetch students');
    }
  };

  

  const handleOpenDialog = () => {
    setFormData({
      student_id: '',
      date: new Date().toISOString().split('T')[0],
      status: 'present',
      time_in: new Date().toLocaleTimeString('en-GB', { hour12: false, hour: '2-digit', minute: '2-digit' }),
      notes: ''
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmitAttendance = async () => {
    try {
      if (!formData.student_id || !formData.date) {
        toast.error('Please select a student and date');
        return;
      }

      const result = await attendanceService.markManualAttendance(formData);
      
      if (result.success) {
        toast.success('Attendance marked successfully!');
        handleCloseDialog();
        if (tabValue === 1) {
          fetchAttendanceByDate();
        }
      } else {
        toast.error(result.error);
      }
    } catch (error) {
      toast.error('Failed to mark attendance');
    }
  };

  const handleFaceRecognitionUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file
    if (!file.type.startsWith('image/')) {
      toast.error('Please select a valid image file');
      return;
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      toast.error('Image size must be less than 10MB');
      return;
    }

    setRecognizing(true);
    setRecognitionResults(null);

    try {
      const result = await attendanceService.recognizeAndMarkAttendance(file);
      
      if (result.success) {
        setRecognitionResults(result.data);
        
        if (result.data.students_recognized > 0) {
          const newAttendees = result.data.recognized_students.filter(s => !s.already_marked);
          if (newAttendees.length > 0) {
            toast.success(`Successfully recognized and marked ${newAttendees.length} student(s)!`);
          } else {
            toast.info('All recognized students already have attendance marked today.');
          }
          
          // Refresh attendance data if viewing attendance tab
          if (tabValue === 1) {
            fetchAttendanceByDate();
          }
        } else {
          toast.warning('No students were recognized. Try manual attendance or ensure students have registered photos.');
        }
      } else {
        toast.error(result.error);
        setRecognitionResults({ recognized_students: [], faces_detected: 0, students_recognized: 0 });
      }
    } catch (error) {
      toast.error('Face recognition failed. Please try again or use manual attendance.');
      setRecognitionResults({ recognized_students: [], faces_detected: 0, students_recognized: 0 });
    } finally {
      setRecognizing(false);
      // Clear the file input
      event.target.value = '';
    }
  };

  // Handle camera photo capture
  const handleCameraCapture = async (imageDataUrl) => {
    setRecognizing(true);
    setRecognitionResults(null);

    try {
      const result = await attendanceService.recognizeFromCamera(imageDataUrl);
      
      if (result.success) {
        setRecognitionResults(result.data);
        
        if (result.data.students_recognized > 0) {
          const newAttendees = result.data.recognized_students.filter(s => !s.already_marked);
          if (newAttendees.length > 0) {
            toast.success(`Successfully recognized and marked ${newAttendees.length} student(s)!`);
          } else {
            toast.info('All recognized students already have attendance marked today.');
          }
          
          // Refresh attendance data if viewing attendance tab
          if (tabValue === 1) {
            fetchAttendanceByDate();
          }
        } else {
          toast.warning('No students were recognized. Try manual attendance or ensure students have registered photos.');
        }
      } else {
        toast.error(result.error);
        setRecognitionResults({ recognized_students: [], faces_detected: 0, students_recognized: 0 });
      }
    } catch (error) {
      toast.error('Face recognition failed. Please try again or use manual attendance.');
      setRecognitionResults({ recognized_students: [], faces_detected: 0, students_recognized: 0 });
    } finally {
      setRecognizing(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'present':
        return 'success';
      case 'absent':
        return 'error';
      case 'late':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'present':
        return <CheckCircleIcon />;
      case 'absent':
        return <CancelIcon />;
      case 'late':
        return <ScheduleIcon />;
      default:
        return <PersonIcon />;
    }
  };

  const getUniqueClasses = () => {
    const classes = [...new Set(students.map(student => student.class_name))];
    return classes.filter(cls => cls);
  };

  const getUniqueSections = () => {
    const sections = [...new Set(students.map(student => student.section))];
    return sections.filter(section => section);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <div className="page-header">
        <Typography variant="h4" className="page-title" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CheckCircleIcon /> Attendance Management
        </Typography>
        <Typography variant="body1" className="page-subtitle">
          Mark and track student attendance
        </Typography>
      </div>

      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
            <Tab label="Mark Attendance" />
            <Tab label="View Attendance" />
          </Tabs>
        </Box>

        {/* Mark Attendance Tab */}
        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={4}>
            {/* Face Recognition Section */}
            <Grid item xs={12} md={6}>
              <Card sx={{ height: '100%' }}>
                <CardContent sx={{ textAlign: 'center', p: 4 }}>
                  <CameraAltIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Camera Face Recognition
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    Open camera and press SPACEBAR to capture and recognize faces
                  </Typography>
                  
                  <Button
                    variant="contained"
                    size="large"
                    startIcon={<CameraAltIcon />}
                    onClick={() => {
                      console.log('Camera button clicked, opening dialog...');
                      setShowCamera(true);
                    }}
                    disabled={recognizing}
                    sx={{ mb: 2 }}
                  >
                    Open Camera for Attendance
                  </Button>

                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    OR
                  </Typography>
                  
                  <input
                    accept="image/*"
                    style={{ display: 'none' }}
                    id="face-recognition-upload"
                    type="file"
                    onChange={handleFaceRecognitionUpload}
                  />
                  <label htmlFor="face-recognition-upload">
                    <Button
                      variant="outlined"
                      component="span"
                      size="large"
                      startIcon={<CameraAltIcon />}
                      disabled={recognizing}
                    >
                      Upload Photo
                    </Button>
                  </label>
                  
                  {recognizing && (
                    <Box sx={{ mt: 2 }}>
                      <CircularProgress size={24} />
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        Processing facial recognition...
                      </Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Manual Attendance Section */}
            <Grid item xs={12} md={6}>
              <Card sx={{ height: '100%' }}>
                <CardContent sx={{ textAlign: 'center', p: 4 }}>
                  <AddIcon sx={{ fontSize: 60, color: 'secondary.main', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Manual Attendance
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    Manually mark attendance if face recognition fails
                  </Typography>
                  <Button
                    variant="outlined"
                    size="large"
                    startIcon={<AddIcon />}
                    onClick={handleOpenDialog}
                  >
                    Mark Manually
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Recognition Results */}
          {recognitionResults && (
            <Card sx={{ mt: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recognition Results
                </Typography>
                {recognitionResults.recognized_students.length > 0 ? (
                  <Grid container spacing={2}>
                    {recognitionResults.recognized_students.map((student, index) => (
                      <Grid item xs={12} md={6} key={index}>
                        <Alert 
                          severity={student.already_marked ? "info" : "success"}
                          sx={{ mb: 1 }}
                        >
                          <Box>
                            <Typography variant="subtitle2">
                              {student.student_name} ({student.roll_number})
                            </Typography>
                            <Typography variant="body2">
                              Confidence: {student.confidence}%
                            </Typography>
                            {student.already_marked ? (
                              <Typography variant="body2">
                                Already marked {student.existing_status} at {student.existing_time}
                              </Typography>
                            ) : (
                              <Typography variant="body2">
                                Marked present at {student.time_marked}
                              </Typography>
                            )}
                          </Box>
                        </Alert>
                      </Grid>
                    ))}
                  </Grid>
                ) : (
                  <Alert severity="warning">
                    No students recognized. Try manual attendance or ensure students have registered photos.
                  </Alert>
                )}
              </CardContent>
            </Card>
          )}

          {/* Quick Stats */}
          <Grid container spacing={3} sx={{ mt: 2 }}>
            <Grid item xs={12} md={4}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="success.main">
                    {students.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Students
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="primary.main">
                    {attendanceRecords.filter(r => r.status === 'present').length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Present Today
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="error.main">
                    {attendanceRecords.filter(r => r.status === 'absent').length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Absent Today
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* View Attendance Tab */}
        <TabPanel value={tabValue} index={1}>
          {/* Filters */}
          <Grid container spacing={3} alignItems="center" sx={{ mb: 3 }}>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="Date"
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Class</InputLabel>
                <Select
                  value={classFilter}
                  onChange={(e) => setClassFilter(e.target.value)}
                  label="Class"
                >
                  <MenuItem value="">All Classes</MenuItem>
                  {getUniqueClasses().map((cls) => (
                    <MenuItem key={cls} value={cls}>{cls}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Section</InputLabel>
                <Select
                  value={sectionFilter}
                  onChange={(e) => setSectionFilter(e.target.value)}
                  label="Section"
                >
                  <MenuItem value="">All Sections</MenuItem>
                  {getUniqueSections().map((section) => (
                    <MenuItem key={section} value={section}>{section}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <Button
                fullWidth
                variant="outlined"
                onClick={fetchAttendanceByDate}
                startIcon={<CalendarIcon />}
              >
                Refresh
              </Button>
            </Grid>
          </Grid>

          {/* Attendance Records */}
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : attendanceRecords.length === 0 ? (
            <Alert severity="info" sx={{ mt: 2 }}>
              No attendance records found for the selected date and filters.
            </Alert>
          ) : (
            <TableContainer component={Paper} elevation={0}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Student Name</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell>Time In</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Marked By</TableCell>
                    <TableCell>Notes</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {attendanceRecords.map((record) => (
                    <TableRow key={record.id} hover>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {record.student_name}
                        </Typography>
                      </TableCell>
                      <TableCell>{record.date}</TableCell>
                      <TableCell>{record.time_in}</TableCell>
                      <TableCell>
                        <Chip
                          icon={getStatusIcon(record.status)}
                          label={record.status.charAt(0).toUpperCase() + record.status.slice(1)}
                          color={getStatusColor(record.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={record.marked_by}
                          variant="outlined"
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {record.notes || '-'}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </TabPanel>
      </Card>

      {/* Mark Attendance Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Mark Student Attendance</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <FormControl fullWidth required>
                  <InputLabel>Student</InputLabel>
                  <Select
                    name="student_id"
                    value={formData.student_id}
                    onChange={handleInputChange}
                    label="Student"
                  >
                    {students.map((student) => (
                      <MenuItem key={student.id} value={student.id}>
                        {student.full_name} ({student.roll_number}) - {student.class_name} {student.section}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Date"
                  name="date"
                  type="date"
                  value={formData.date}
                  onChange={handleInputChange}
                  InputLabelProps={{ shrink: true }}
                  required
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Time In"
                  name="time_in"
                  type="time"
                  value={formData.time_in}
                  onChange={handleInputChange}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Status</InputLabel>
                  <Select
                    name="status"
                    value={formData.status}
                    onChange={handleInputChange}
                    label="Status"
                  >
                    <MenuItem value="present">Present</MenuItem>
                    <MenuItem value="absent">Absent</MenuItem>
                    <MenuItem value="late">Late</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Notes"
                  name="notes"
                  multiline
                  rows={2}
                  value={formData.notes}
                  onChange={handleInputChange}
                  placeholder="Optional notes about this attendance record"
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmitAttendance} variant="contained">
            Mark Attendance
          </Button>
        </DialogActions>
      </Dialog>

      {/* Camera Capture Dialog */}
      <Dialog 
        open={showCamera} 
        onClose={() => {
          console.log('Closing camera dialog...');
          setShowCamera(false);
        }}
        maxWidth="md"
        fullWidth
      >
        <DialogContent sx={{ p: 0 }}>
          <CameraCapture
            onPhotoCapture={handleCameraCapture}
            onClose={() => setShowCamera(false)}
            isProcessing={recognizing}
            processingMessage="Recognizing faces and marking attendance..."
          />
        </DialogContent>
      </Dialog>
    </Container>
  );
}

export default Attendance;