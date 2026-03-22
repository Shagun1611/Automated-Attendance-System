import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api';

class ApiService {
  // Students API
  async getStudents(filters = {}) {
    try {
      const params = new URLSearchParams(filters).toString();
      const response = await axios.get(`${API_BASE_URL}/students?${params}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async createStudent(studentData) {
    try {
      const response = await axios.post(`${API_BASE_URL}/students`, studentData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async updateStudent(studentId, studentData) {
    try {
      const response = await axios.put(`${API_BASE_URL}/students/${studentId}`, studentData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async deleteStudent(studentId) {
    try {
      const response = await axios.delete(`${API_BASE_URL}/students/${studentId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async registerStudentFace(studentId, images) {
    try {
      const formData = new FormData();
      images.forEach((image, index) => {
        formData.append('images', image);
      });

      const response = await axios.post(
        `${API_BASE_URL}/students/${studentId}/register-face`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Attendance API
  async recognizeAndMarkAttendance(imageFile) {
    try {
      const formData = new FormData();
      formData.append('image', imageFile);

      const response = await axios.post(
        `${API_BASE_URL}/attendance/recognize`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getAttendanceByDate(date, filters = {}) {
    try {
      const params = new URLSearchParams(filters).toString();
      const response = await axios.get(`${API_BASE_URL}/attendance/date/${date}?${params}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getStudentAttendanceHistory(studentId, startDate, endDate) {
    try {
      const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate,
      }).toString();
      const response = await axios.get(`${API_BASE_URL}/attendance/student/${studentId}?${params}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getAttendanceStatistics(filters = {}) {
    try {
      const params = new URLSearchParams(filters).toString();
      const response = await axios.get(`${API_BASE_URL}/attendance/statistics?${params}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async markManualAttendance(attendanceData) {
    try {
      const response = await axios.post(`${API_BASE_URL}/attendance/manual`, attendanceData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getAttendanceAlerts(daysThreshold = 3) {
    try {
      const response = await axios.get(`${API_BASE_URL}/attendance/alerts?days=${daysThreshold}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Reports API
  async exportAttendanceReport(format, filters = {}) {
    try {
      const params = new URLSearchParams({ ...filters, format }).toString();
      const response = await axios.get(`${API_BASE_URL}/reports/attendance?${params}`, {
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getClassList() {
    try {
      const response = await axios.get(`${API_BASE_URL}/classes`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async createTeacher(teacherData) {
    try {
      const response = await axios.post(`${API_BASE_URL}/admin/teachers`, teacherData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async listTeachers() {
    try {
      const response = await axios.get(`${API_BASE_URL}/admin/teachers`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async updateTeacher(teacherId, data) {
    try {
      const response = await axios.put(`${API_BASE_URL}/admin/teachers/${teacherId}`, data);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async deleteTeacher(teacherId) {
    try {
      const response = await axios.delete(`${API_BASE_URL}/admin/teachers/${teacherId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // System health check
  async healthCheck() {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Error handler
  handleError(error) {
    const errorMessage = error.response?.data?.error || error.message || 'An error occurred';
    const errorCode = error.response?.status || 500;
    
    return {
      message: errorMessage,
      code: errorCode,
      details: error.response?.data
    };
  }

  // Utility methods
  async uploadImage(imageFile) {
    try {
      const formData = new FormData();
      formData.append('image', imageFile);

      const response = await axios.post(`${API_BASE_URL}/upload/image`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Power BI Integration
  async syncToPowerBI() {
    try {
      const response = await axios.post(`${API_BASE_URL}/powerbi/sync`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getPowerBIDashboardUrl() {
    try {
      const response = await axios.get(`${API_BASE_URL}/powerbi/dashboard-url`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }
}

export const apiService = new ApiService();