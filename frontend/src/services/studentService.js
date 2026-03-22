import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api';

class StudentService {
  async getAllStudents(filters = {}) {
    try {
      const params = new URLSearchParams();
      if (filters.class) params.append('class', filters.class);
      if (filters.section) params.append('section', filters.section);
      if (filters.search) params.append('search', filters.search);
      
      const response = await axios.get(`${API_BASE_URL}/students?${params}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to fetch students'
      };
    }
  }

  async createStudent(studentData) {
    try {
      const response = await axios.post(`${API_BASE_URL}/students`, studentData);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to create student'
      };
    }
  }

  async updateStudent(studentId, studentData) {
    try {
      const response = await axios.put(`${API_BASE_URL}/students/${studentId}`, studentData);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to update student'
      };
    }
  }

  async deleteStudent(studentId) {
    try {
      const response = await axios.delete(`${API_BASE_URL}/students/${studentId}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to delete student'
      };
    }
  }

  async uploadStudentPhoto(studentId, photoFile) {
    try {
      const formData = new FormData();
      formData.append('photo', photoFile);

      const response = await axios.post(
        `${API_BASE_URL}/students/${studentId}/upload-photo`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to upload photo'
      };
    }
  }

  async getStudentPhoto(studentId) {
    try {
      const response = await axios.get(`${API_BASE_URL}/students/${studentId}/photo`, {
        responseType: 'blob'
      });
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to get photo'
      };
    }
  }
}

export const studentService = new StudentService();