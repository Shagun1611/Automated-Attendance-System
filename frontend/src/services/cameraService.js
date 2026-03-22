class CameraService {
  constructor() {
    this.stream = null;
    this.videoElement = null;
    this.isStreaming = false;
    this.constraints = {
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        facingMode: 'user'
      },
      audio: false
    };
  }

  async initialize(videoElement) {
    try {
      this.videoElement = videoElement;
      
      // Check if camera is available
      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoDevices = devices.filter(device => device.kind === 'videoinput');
      
      if (videoDevices.length === 0) {
        throw new Error('No camera devices found');
      }

      return true;
    } catch (error) {
      console.error('Camera initialization error:', error);
      throw error;
    }
  }

  async startStream() {
    try {
      if (this.isStreaming) {
        return true;
      }

      this.stream = await navigator.mediaDevices.getUserMedia(this.constraints);
      
      if (this.videoElement) {
        this.videoElement.srcObject = this.stream;
        this.videoElement.play();
        this.isStreaming = true;
      }

      return true;
    } catch (error) {
      console.error('Error starting camera stream:', error);
      throw new Error(`Camera access denied: ${error.message}`);
    }
  }

  stopStream() {
    try {
      if (this.stream) {
        this.stream.getTracks().forEach(track => {
          track.stop();
        });
        this.stream = null;
      }

      if (this.videoElement) {
        this.videoElement.srcObject = null;
      }

      this.isStreaming = false;
      return true;
    } catch (error) {
      console.error('Error stopping camera stream:', error);
      return false;
    }
  }

  captureFrame() {
    try {
      if (!this.videoElement || !this.isStreaming) {
        throw new Error('Camera not initialized or not streaming');
      }

      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      
      canvas.width = this.videoElement.videoWidth;
      canvas.height = this.videoElement.videoHeight;
      
      context.drawImage(this.videoElement, 0, 0, canvas.width, canvas.height);
      
      return canvas.toDataURL('image/jpeg', 0.8);
    } catch (error) {
      console.error('Error capturing frame:', error);
      throw error;
    }
  }

  captureFrameAsBlob() {
    return new Promise((resolve, reject) => {
      try {
        if (!this.videoElement || !this.isStreaming) {
          reject(new Error('Camera not initialized or not streaming'));
          return;
        }

        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        
        canvas.width = this.videoElement.videoWidth;
        canvas.height = this.videoElement.videoHeight;
        
        context.drawImage(this.videoElement, 0, 0, canvas.width, canvas.height);
        
        canvas.toBlob((blob) => {
          if (blob) {
            resolve(blob);
          } else {
            reject(new Error('Failed to capture image blob'));
          }
        }, 'image/jpeg', 0.8);
      } catch (error) {
        reject(error);
      }
    });
  }

  async switchCamera() {
    try {
      // Get available video devices
      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoDevices = devices.filter(device => device.kind === 'videoinput');
      
      if (videoDevices.length < 2) {
        throw new Error('Only one camera available');
      }

      // Toggle between front and back camera
      const currentFacingMode = this.constraints.video.facingMode;
      this.constraints.video.facingMode = currentFacingMode === 'user' ? 'environment' : 'user';
      
      // Restart stream with new constraints
      this.stopStream();
      await this.startStream();
      
      return true;
    } catch (error) {
      console.error('Error switching camera:', error);
      throw error;
    }
  }

  getStreamSettings() {
    if (!this.stream) {
      return null;
    }

    const videoTrack = this.stream.getVideoTracks()[0];
    return videoTrack ? videoTrack.getSettings() : null;
  }

  async setResolution(width, height) {
    try {
      this.constraints.video.width = { ideal: width };
      this.constraints.video.height = { ideal: height };
      
      if (this.isStreaming) {
        this.stopStream();
        await this.startStream();
      }
      
      return true;
    } catch (error) {
      console.error('Error setting resolution:', error);
      throw error;
    }
  }

  isSupported() {
    return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
  }

  async getAvailableCameras() {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      return devices.filter(device => device.kind === 'videoinput');
    } catch (error) {
      console.error('Error getting available cameras:', error);
      return [];
    }
  }
}

// Face Detection Utilities
class FaceDetectionOverlay {
  constructor(canvasElement) {
    this.canvas = canvasElement;
    this.ctx = canvasElement.getContext('2d');
  }

  drawFaceBox(face, label = '', confidence = 0) {
    const { x, y, width, height } = face;
    
    // Draw rectangle around face
    this.ctx.strokeStyle = confidence > 0.7 ? '#4caf50' : '#ff9800';
    this.ctx.lineWidth = 2;
    this.ctx.strokeRect(x, y, width, height);
    
    // Draw label background
    if (label) {
      const labelHeight = 20;
      this.ctx.fillStyle = confidence > 0.7 ? '#4caf50' : '#ff9800';
      this.ctx.fillRect(x, y - labelHeight, width, labelHeight);
      
      // Draw label text
      this.ctx.fillStyle = 'white';
      this.ctx.font = '12px Arial';
      this.ctx.textAlign = 'center';
      this.ctx.fillText(
        `${label} (${Math.round(confidence * 100)}%)`,
        x + width / 2,
        y - 6
      );
    }
  }

  clearOverlay() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
  }

  updateCanvasSize(width, height) {
    this.canvas.width = width;
    this.canvas.height = height;
  }
}

// Real-time Attendance Processing
class AttendanceProcessor {
  constructor(apiService, cameraService) {
    this.apiService = apiService;
    this.cameraService = cameraService;
    this.isProcessing = false;
    this.processingInterval = null;
    this.lastProcessTime = 0;
    this.processingDelay = 2000; // 2 seconds between processing
  }

  startRealTimeProcessing(onResult, onError) {
    if (this.isProcessing) {
      return;
    }

    this.isProcessing = true;
    this.processingInterval = setInterval(async () => {
      try {
        const now = Date.now();
        if (now - this.lastProcessTime < this.processingDelay) {
          return;
        }

        const imageBlob = await this.cameraService.captureFrameAsBlob();
        const result = await this.apiService.recognizeAndMarkAttendance(imageBlob);
        
        this.lastProcessTime = now;
        
        if (onResult) {
          onResult(result);
        }
      } catch (error) {
        console.error('Real-time processing error:', error);
        if (onError) {
          onError(error);
        }
      }
    }, 500); // Check every 500ms, but process every 2 seconds
  }

  stopRealTimeProcessing() {
    this.isProcessing = false;
    if (this.processingInterval) {
      clearInterval(this.processingInterval);
      this.processingInterval = null;
    }
  }

  async processSingleFrame() {
    try {
      const imageBlob = await this.cameraService.captureFrameAsBlob();
      const result = await this.apiService.recognizeAndMarkAttendance(imageBlob);
      return result;
    } catch (error) {
      console.error('Single frame processing error:', error);
      throw error;
    }
  }
}

// Offline Storage for Attendance Data
class OfflineStorageService {
  constructor() {
    this.dbName = 'AttendanceDB';
    this.version = 1;
    this.db = null;
  }

  async initialize() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.version);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        
        // Create object stores
        if (!db.objectStoreNames.contains('attendance')) {
          const attendanceStore = db.createObjectStore('attendance', { keyPath: 'id', autoIncrement: true });
          attendanceStore.createIndex('date', 'date', { unique: false });
          attendanceStore.createIndex('studentId', 'studentId', { unique: false });
        }

        if (!db.objectStoreNames.contains('students')) {
          const studentStore = db.createObjectStore('students', { keyPath: 'id' });
          studentStore.createIndex('rollNumber', 'rollNumber', { unique: true });
        }
      };
    });
  }

  async storeAttendanceRecord(record) {
    const transaction = this.db.transaction(['attendance'], 'readwrite');
    const store = transaction.objectStore('attendance');
    
    return new Promise((resolve, reject) => {
      const request = store.add({
        ...record,
        timestamp: new Date().toISOString(),
        synced: false
      });
      
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async getUnsyncedRecords() {
    const transaction = this.db.transaction(['attendance'], 'readonly');
    const store = transaction.objectStore('attendance');
    
    return new Promise((resolve, reject) => {
      const request = store.getAll();
      
      request.onsuccess = () => {
        const allRecords = request.result;
        const unsyncedRecords = allRecords.filter(record => !record.synced);
        resolve(unsyncedRecords);
      };
      
      request.onerror = () => reject(request.error);
    });
  }

  async markRecordAsSynced(recordId) {
    const transaction = this.db.transaction(['attendance'], 'readwrite');
    const store = transaction.objectStore('attendance');
    
    return new Promise((resolve, reject) => {
      const getRequest = store.get(recordId);
      
      getRequest.onsuccess = () => {
        const record = getRequest.result;
        if (record) {
          record.synced = true;
          const putRequest = store.put(record);
          
          putRequest.onsuccess = () => resolve();
          putRequest.onerror = () => reject(putRequest.error);
        } else {
          reject(new Error('Record not found'));
        }
      };
      
      getRequest.onerror = () => reject(getRequest.error);
    });
  }
}

export { 
  CameraService, 
  FaceDetectionOverlay, 
  AttendanceProcessor, 
  OfflineStorageService 
};