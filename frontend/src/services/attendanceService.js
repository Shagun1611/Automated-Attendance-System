import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api';

class AttendanceService {
  async markManualAttendance(attendanceData) {
    try {
      const response = await axios.post(`${API_BASE_URL}/attendance/manual`, attendanceData);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to mark attendance'
      };
    }
  }

  async getAttendanceByDate(date, filters = {}) {
    try {
      const params = new URLSearchParams();
      if (filters.class) params.append('class', filters.class);
      if (filters.section) params.append('section', filters.section);
      
      const response = await axios.get(`${API_BASE_URL}/attendance/date/${date}?${params}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to fetch attendance'
      };
    }
  }

  async getStudentAttendanceHistory(studentId, startDate = null, endDate = null) {
    try {
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      
      const response = await axios.get(`${API_BASE_URL}/attendance/student/${studentId}?${params}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to fetch student attendance'
      };
    }
  }

  async recognizeAndMarkAttendance(photoFile) {
    try {
      const formData = new FormData();
      formData.append('photo', photoFile);

      const response = await axios.post(`${API_BASE_URL}/attendance/recognize`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to recognize faces'
      };
    }
  }

  async recognizeFromCamera(imageDataUrl) {
    try {
      const formData = new FormData();
      formData.append('image_data', imageDataUrl);

      const response = await axios.post(`${API_BASE_URL}/attendance/recognize`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to recognize faces'
      };
    }
  }

  async getAttendanceStatistics(filters = {}) {
    try {
      const params = new URLSearchParams();
      if (filters.class) params.append('class', filters.class);
      if (filters.section) params.append('section', filters.section);
      if (filters.startDate) params.append('start_date', filters.startDate);
      if (filters.endDate) params.append('end_date', filters.endDate);
      
      const response = await axios.get(`${API_BASE_URL}/attendance/statistics?${params}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to fetch statistics'
      };
    }
  }

  async getAttendanceAlerts(daysThreshold = 3) {
    try {
      const response = await axios.get(`${API_BASE_URL}/attendance/alerts?days=${daysThreshold}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to fetch alerts'
      };
    }
  }
}

export const attendanceService = new AttendanceService();