import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  Alert,
  CircularProgress,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import { FormControl, InputLabel, MenuItem, Select, Tooltip, Chip, Stack } from '@mui/material';
import {
  CameraAlt,
  Stop,
  Replay,
  CheckCircle,
  Error as ErrorIcon
} from '@mui/icons-material';

const CameraCapture = ({ 
  onPhotoCapture, 
  onClose, 
  isProcessing = false,
  processingMessage = "Processing photo..."
}) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const [capturedPhoto, setCapturedPhoto] = useState(null);
  const [showInstructions, setShowInstructions] = useState(true);

  // Camera devices and permissions
  const [devices, setDevices] = useState([]); // list of {deviceId, label}
  const [selectedDeviceId, setSelectedDeviceId] = useState('');
  const [permissionStatus, setPermissionStatus] = useState('unknown'); // 'unknown' | 'prompt' | 'granted' | 'denied'
  const [isEnumerating, setIsEnumerating] = useState(false);

  const isSecureContext = (() => {
    try {
      const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
      return window.isSecureContext || (window.location.protocol === 'http:' && isLocalhost);
    } catch (_) {
      return true;
    }
  })();

  const mapGetUserMediaError = useCallback((err) => {
    const base = 'Unable to access camera. ';
    switch (err?.name) {
      case 'NotAllowedError':
      case 'SecurityError':
        return base + 'Permission was denied. Please allow camera access in your browser and try again.';
      case 'NotFoundError':
      case 'OverconstrainedError':
        return base + 'No suitable camera device found. If you have multiple cameras, try selecting a different one.';
      case 'NotReadableError':
        return base + 'The camera is already in use by another application (e.g., Teams/Zoom). Close it and try again.';
      case 'AbortError':
        return base + 'The operation was aborted. Please retry.';
      case 'TypeError':
        return base + 'The constraints provided were invalid.';
      default:
        if (!isSecureContext) {
          return base + 'Camera access requires a secure context. Use http://localhost:3000 or https in production.';
        }
        return base + 'Please check your camera settings and permissions.';
    }
  }, [isSecureContext]);

  const updatePermissionStatus = useCallback(async () => {
    try {
      if (navigator.permissions && navigator.permissions.query) {
        // @ts-ignore - camera is not always typed but supported in Chromium
        const res = await navigator.permissions.query({ name: 'camera' });
        setPermissionStatus(res.state); // 'granted' | 'denied' | 'prompt'
        res.onchange = () => setPermissionStatus(res.state);
      } else {
        // Fallback: unknown until we attempt getUserMedia
        setPermissionStatus('unknown');
      }
    } catch (_) {
      setPermissionStatus('unknown');
    }
  }, []);

  const enumerateCameras = useCallback(async () => {
    if (!navigator.mediaDevices?.enumerateDevices) {
      setError('Camera enumeration is not supported in this browser.');
      return;
    }
    try {
      setIsEnumerating(true);
      const list = await navigator.mediaDevices.enumerateDevices();
      const cams = list.filter((d) => d.kind === 'videoinput').map((d) => ({ deviceId: d.deviceId, label: d.label || 'Camera' }));
      setDevices(cams);
      if (cams.length === 0) {
        setError('No camera devices found on your system.');
      }
      // If nothing selected, pick the first
      if (!selectedDeviceId && cams.length > 0) {
        setSelectedDeviceId(cams[0].deviceId);
      }
    } catch (e) {
      console.error('enumerateDevices failed:', e);
    } finally {
      setIsEnumerating(false);
    }
  }, [selectedDeviceId]);

  const requestPermission = useCallback(async () => {
    try {
      setError(null);
      const tmpStream = await navigator.mediaDevices.getUserMedia({ video: true });
      // Immediately stop and release
      tmpStream.getTracks().forEach((t) => t.stop());
      await updatePermissionStatus();
      await enumerateCameras();
    } catch (err) {
      console.error('Permission request error:', err);
      setError(mapGetUserMediaError(err));
      await updatePermissionStatus();
    }
  }, [enumerateCameras, updatePermissionStatus, mapGetUserMediaError]);

  // Start camera stream
  const startCamera = useCallback(async () => {
    try {
      console.log('Starting camera...');
      setError(null);
      // If permission is explicitly denied, surface actionable error
      if (permissionStatus === 'denied') {
        setError('Camera permission is denied. Use the browser address bar to Allow camera access and try again.');
        return;
      }
      
      const constraints = {
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          ...(selectedDeviceId
            ? { deviceId: { exact: selectedDeviceId } }
            : { facingMode: 'user' })
        }
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      
      console.log('Camera stream obtained:', stream);
      
      // Save stream immediately
      streamRef.current = stream;

      // Attach stream to video element when ready
      if (videoRef.current) {
        videoRef.current.srcObject = stream;

        // Wait for metadata then play
        const onLoaded = () => {
          console.log('Video metadata loaded, starting playback');
          const playPromise = videoRef.current.play();
          if (playPromise && typeof playPromise.then === 'function') {
            playPromise
              .then(() => {
                console.log('Video playing successfully');
                setIsStreaming(true);
                setShowInstructions(false);
              })
              .catch((playError) => {
                console.error('Error playing video:', playError);
                setError('Failed to display camera feed. Please try again.');
              });
          } else {
            setIsStreaming(true);
            setShowInstructions(false);
          }
        };
        // If metadata already available, invoke immediately
        if (videoRef.current.readyState >= 1) {
          onLoaded();
        } else {
          videoRef.current.onloadedmetadata = onLoaded;
        }

        videoRef.current.onerror = (videoError) => {
          console.error('Video error:', videoError);
          setError('Error with video display. Please check camera permissions.');
        };
      } else {
        // Video might not be mounted yet on slow renders; toggle streaming to mount it
        console.warn('Video ref not ready; mounting video element and retrying attach');
        setIsStreaming(true);
        setShowInstructions(false);
        // Give the browser a tick to render the video element, then attach
        setTimeout(() => {
          if (videoRef.current) {
            videoRef.current.srcObject = streamRef.current;
            videoRef.current.play().catch((e) => {
              console.error('Play after mount failed:', e);
            });
          }
        }, 0);
      }
    } catch (err) {
      console.error('Error accessing camera:', err);
      setError(mapGetUserMediaError(err));
    }
  }, [mapGetUserMediaError, permissionStatus, selectedDeviceId]);

  // Stop camera stream
  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      // Detach stream to release camera in some browsers
      videoRef.current.srcObject = null;
    }
    setIsStreaming(false);
  }, []);

  // Capture photo from video stream
  const capturePhoto = useCallback(() => {
    console.log('Capturing photo...');
    
    if (!videoRef.current || !canvasRef.current) {
      console.error('Video or canvas ref is null');
      return null;
    }

    const video = videoRef.current;
    const canvas = canvasRef.current;
    
    if (video.videoWidth === 0 || video.videoHeight === 0) {
      console.error('Video dimensions are zero:', { width: video.videoWidth, height: video.videoHeight });
      return null;
    }
    
    const context = canvas.getContext('2d');

    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    console.log('Canvas dimensions set:', { width: canvas.width, height: canvas.height });

    // Draw video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert to base64
    const photoDataUrl = canvas.toDataURL('image/jpeg', 0.8);
    setCapturedPhoto(photoDataUrl);
    
    console.log('Photo captured, data URL length:', photoDataUrl.length);
    
    return photoDataUrl;
  }, []);

  // Handle spacebar press
  const handleKeyPress = useCallback((event) => {
    if (event.code === 'Space' && isStreaming && !isProcessing) {
      event.preventDefault();
      const photo = capturePhoto();
      if (photo && onPhotoCapture) {
        onPhotoCapture(photo);
      }
    }
  }, [isStreaming, isProcessing, capturePhoto, onPhotoCapture]);

  // Set up keyboard event listener
  useEffect(() => {
    document.addEventListener('keydown', handleKeyPress);
    return () => {
      document.removeEventListener('keydown', handleKeyPress);
    };
  }, [handleKeyPress]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, [stopCamera]);

  // On mount: check permission and enumerate devices
  useEffect(() => {
    (async () => {
      await updatePermissionStatus();
      // To get device labels, browsers may require a prior permission; still enumerate
      await enumerateCameras();
    })();

    // React to device changes (e.g., plugging webcam)
    const onDeviceChange = () => {
      enumerateCameras();
    };
    if (navigator.mediaDevices?.addEventListener) {
      navigator.mediaDevices.addEventListener('devicechange', onDeviceChange);
    } else if (navigator.mediaDevices && 'ondevicechange' in navigator.mediaDevices) {
      navigator.mediaDevices.ondevicechange = onDeviceChange;
    }
    return () => {
      if (navigator.mediaDevices?.removeEventListener) {
        navigator.mediaDevices.removeEventListener('devicechange', onDeviceChange);
      } else if (navigator.mediaDevices && 'ondevicechange' in navigator.mediaDevices) {
        navigator.mediaDevices.ondevicechange = null;
      }
    };
  }, [enumerateCameras, updatePermissionStatus]);

  // Handle manual capture button
  const handleManualCapture = () => {
    console.log('Manual capture button clicked');
    if (!isProcessing) {
      const photo = capturePhoto();
      if (photo && onPhotoCapture) {
        console.log('Calling onPhotoCapture with photo');
        onPhotoCapture(photo);
      } else {
        console.log('Photo capture failed or no callback provided');
      }
    } else {
      console.log('Processing in progress, capture ignored');
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
      {/* Instructions Dialog */}
      <Dialog open={showInstructions} onClose={() => setShowInstructions(false)}>
        <DialogTitle>Camera Instructions</DialogTitle>
        <DialogContent>
          <Typography variant="body1" paragraph>
            📸 <strong>How to mark attendance:</strong>
          </Typography>
          <Typography variant="body2" paragraph>
            1. Click "Start Camera" to begin
          </Typography>
          <Typography variant="body2" paragraph>
            2. Position your face clearly in the camera view
          </Typography>
          <Typography variant="body2" paragraph>
            3. Press the <strong>SPACEBAR</strong> to capture your photo
          </Typography>
          <Typography variant="body2" paragraph>
            4. The system will automatically match your face and mark attendance
          </Typography>
          <Alert severity="info" sx={{ mt: 2 }}>
            Make sure you're in a well-lit area for best recognition results
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowInstructions(false)}>Got it!</Button>
        </DialogActions>
      </Dialog>

      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">
          📹 Face Recognition Attendance
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* Permission status chip */}
          <Tooltip title={`Camera permission: ${permissionStatus}`} placement="bottom">
            <Chip size="small" label={`Permission: ${permissionStatus}`} color={permissionStatus === 'granted' ? 'success' : (permissionStatus === 'denied' ? 'error' : 'default')} />
          </Tooltip>
          <IconButton onClick={() => setShowInstructions(true)} title="Show Instructions">
            ❓
          </IconButton>
          <IconButton onClick={onClose} title="Close Camera">
            ✕
          </IconButton>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} icon={<ErrorIcon />}>
          {error}
          <Button size="small" onClick={() => setError(null)} sx={{ ml: 1 }}>
            Dismiss
          </Button>
        </Alert>
      )}

      {isProcessing && (
        <Alert severity="info" sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CircularProgress size={20} />
            <Typography>{processingMessage}</Typography>
          </Box>
        </Alert>
      )}

      <Box sx={{ textAlign: 'center', mb: 2 }}>
        {/* Persistently mounted video element to ensure ref is available */}
        <Box sx={{ position: 'relative', display: 'inline-block' }}>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            controls={false}
            style={{
              width: '100%',
              maxWidth: 640,
              height: isStreaming ? 'auto' : 0,
              border: isStreaming ? '2px solid #2196f3' : 'none',
              borderRadius: 8,
              backgroundColor: '#000',
              overflow: 'hidden',
              transition: 'height 200ms ease'
            }}
          />

          {isStreaming && (
            <Box
              sx={{
                position: 'absolute',
                bottom: 10,
                left: '50%',
                transform: 'translateX(-50%)',
                backgroundColor: 'rgba(0, 0, 0, 0.7)',
                color: 'white',
                padding: '8px 16px',
                borderRadius: 2,
                typography: 'body2'
              }}
            >
              Press SPACEBAR to capture photo
            </Box>
          )}
        </Box>

        {/* Hidden Canvas for photo capture */}
        <canvas ref={canvasRef} style={{ display: 'none' }} />

        {/* Controls and Start UI */}
        {!isStreaming ? (
          <Stack spacing={2} sx={{ mt: 2, alignItems: 'center' }}>
            <CameraAlt sx={{ fontSize: 48, color: 'grey.500' }} />
            <Typography variant="body2" color="textSecondary">
              Camera is ready to start
            </Typography>

            {/* Permission and device controls */}
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ alignItems: 'center' }}>
              <Button variant="outlined" onClick={requestPermission} disabled={permissionStatus === 'granted'}>
                {permissionStatus === 'granted' ? 'Permission Granted' : 'Enable Camera Access'}
              </Button>

              <FormControl size="small" sx={{ minWidth: 220 }} disabled={devices.length === 0}>
                <InputLabel id="camera-select-label">Camera</InputLabel>
                <Select
                  labelId="camera-select-label"
                  label="Camera"
                  value={selectedDeviceId}
                  onChange={(e) => setSelectedDeviceId(e.target.value)}
                >
                  {devices.map((d, idx) => (
                    <MenuItem key={d.deviceId || idx} value={d.deviceId}>
                      {d.label || `Camera ${idx + 1}`}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Button
                variant="contained"
                startIcon={<CameraAlt />}
                onClick={startCamera}
                size="large"
              >
                Start Camera
              </Button>
            </Stack>

            {!isSecureContext && (
              <Alert severity="warning" sx={{ mt: 1 }}>
                This page is not a secure context. Use http://localhost during development or HTTPS in production for camera access.
              </Alert>
            )}
            {isEnumerating && <Typography variant="caption">Enumerating cameras…</Typography>}
          </Stack>
        ) : (
          <Box sx={{ mt: 2, display: 'flex', gap: 2, justifyContent: 'center' }}>
            <Button
              variant="contained"
              startIcon={<CameraAlt />}
              onClick={handleManualCapture}
              disabled={isProcessing}
            >
              Capture Photo
            </Button>
            <Button
              variant="outlined"
              startIcon={<Replay />}
              onClick={() => {
                stopCamera();
                setTimeout(startCamera, 100);
              }}
              disabled={isProcessing}
            >
              Restart Camera
            </Button>
            <Button
              variant="outlined"
              color="error"
              startIcon={<Stop />}
              onClick={stopCamera}
            >
              Stop Camera
            </Button>
          </Box>
        )}

        {isStreaming && (
          <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
            💡 Tip: Make sure your face is clearly visible and well-lit
          </Typography>
        )}
      </Box>

      {capturedPhoto && (
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Typography variant="h6" sx={{ mb: 1 }}>
            <CheckCircle sx={{ color: 'green', mr: 1 }} />
            Photo Captured Successfully!
          </Typography>
          <img
            src={capturedPhoto}
            alt="Captured"
            style={{
              maxWidth: 200,
              height: 'auto',
              border: '2px solid green',
              borderRadius: 8
            }}
          />
        </Box>
      )}
    </Paper>
  );
};

export default CameraCapture;