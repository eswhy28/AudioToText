import React, { useState, useEffect, useRef } from "react";
import Lottie from 'lottie-react';
import { Mic, StopCircle, Upload, Loader2, Clock, ChevronDown, ChevronUp, Trash2,Info } from "lucide-react";
import voiceRecordingAnimation from '../voice-recording-animation.json';
import "../Recorder.css";

const Recorder = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [audioChunks, setAudioChunks] = useState([]);
  const [transcription, setTranscription] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [previousTranscriptions, setPreviousTranscriptions] = useState([]);
  
  // Enhanced state for duration and waveform
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [audioContext, setAudioContext] = useState(null);
  const [analyser, setAnalyser] = useState(null);
  const [audioStream, setAudioStream] = useState(null);
  const [waveformData, setWaveformData] = useState([]);
  const [isPreviousCollapsed, setIsPreviousCollapsed] = useState(true);
  const [showExplanation, setShowExplanation] = useState(true);


  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const durationIntervalRef = useRef(null);

  // Constants
  const MAX_RECORDING_TIME = 300; // 5 minutes in seconds
  const WAVEFORM_SAMPLES = 100; // Number of data points for waveform

  // Load previous transcriptions from local storage on component mount
  useEffect(() => {
    const savedTranscriptions = JSON.parse(
      localStorage.getItem("transcriptions") || "[]"
    );
    setPreviousTranscriptions(savedTranscriptions);
  }, []);

  // Cleanup function to stop animations and intervals
  const cleanupRecording = () => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
    if (durationIntervalRef.current) {
      clearInterval(durationIntervalRef.current);
    }
    if (audioStream) {
      audioStream.getTracks().forEach(track => track.stop());
    }
  };

  // Enhanced audio visualization
  const visualizeAudio = () => {
    if (!analyser || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const canvasCtx = canvas.getContext('2d');
    const WIDTH = canvas.width;
    const HEIGHT = canvas.height;

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const drawWave = () => {
      animationRef.current = requestAnimationFrame(drawWave);

      // Get time domain data
      analyser.getByteTimeDomainData(dataArray);

      // Downsample data for smoother visualization
      const downsampledData = [];
      for (let i = 0; i < WAVEFORM_SAMPLES; i++) {
        const index = Math.floor(i * (bufferLength / WAVEFORM_SAMPLES));
        downsampledData.push((dataArray[index] - 128) / 128.0);
      }
      setWaveformData(downsampledData);

      // Clear canvas
      canvasCtx.fillStyle = 'rgba(255, 255, 255, 0.1)';
      canvasCtx.fillRect(0, 0, WIDTH, HEIGHT);

      // Draw waveform
      canvasCtx.lineWidth = 2;
      canvasCtx.strokeStyle = 'rgb(0, 123, 255)';
      canvasCtx.beginPath();

      const sliceWidth = WIDTH / (WAVEFORM_SAMPLES - 1);
      let x = 0;

      for (let i = 0; i < downsampledData.length; i++) {
        const v = downsampledData[i];
        const y = (v + 1) * HEIGHT / 2;

        if (i === 0) {
          canvasCtx.moveTo(x, y);
        } else {
          canvasCtx.lineTo(x, y);
        }

        x += sliceWidth;
      }

      canvasCtx.stroke();
    };

    drawWave();
  };

  const startRecording = async () => {
    if (isLoading) return; // Prevent recording while processing

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      
      // Setup audio context for visualization
      const context = new (window.AudioContext || window.webkitAudioContext)();
      const analyser = context.createAnalyser();
      const source = context.createMediaStreamSource(stream);
      source.connect(analyser);
      
      recorder.ondataavailable = (event) => {
        setAudioChunks((prev) => [...prev, event.data]);
      };
      
      recorder.onstop = () => {
        setIsRecording(false);
        cleanupRecording();
      };
      
      setMediaRecorder(recorder);
      setAudioContext(context);
      setAnalyser(analyser);
      setAudioStream(stream);

      // Reset duration
      setRecordingDuration(0);

      // Start duration tracking
      durationIntervalRef.current = setInterval(() => {
        setRecordingDuration((prev) => {
          if (prev >= MAX_RECORDING_TIME) {
            recorder.stop();
            return MAX_RECORDING_TIME;
          }
          return prev + 1;
        });
      }, 1000);

      recorder.start();
      setIsRecording(true);
      setAudioChunks([]);

      // Start visualization
      visualizeAudio();
    } catch (err) {
      console.error("Error accessing microphone:", err);
      alert("Could not access microphone. Please check permissions.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop();
      cleanupRecording();
    }
  };

  const uploadAudio = async () => {
    if (audioChunks.length === 0 || isLoading) return;

    const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
    const formData = new FormData();
    formData.append("file", audioBlob, "recording.wav");

    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:5000/api/transcribe", {
        method: "POST",
        body: formData,
      });
      
      const result = await response.json();

      if (response.ok) {
        const newTranscription = result.transcription || "No transcription available";
        setTranscription(newTranscription);

        // Save transcription to local storage
        const updatedTranscriptions = [
          { 
            text: newTranscription, 
            timestamp: new Date().toLocaleString(),
            duration: recordingDuration
          },
          ...previousTranscriptions.slice(0, 9) // Keep last 10 transcriptions
        ];
        setPreviousTranscriptions(updatedTranscriptions);
        localStorage.setItem("transcriptions", JSON.stringify(updatedTranscriptions));
      } else {
        setTranscription("Error: " + (result.error || "Failed to transcribe"));
      }
    } catch (err) {
      console.error("Error uploading audio:", err);
      setTranscription("Error: Could not reach the server");
    } finally {
      setIsLoading(false);
    }
  };

  const clearTranscription = () => {
    setTranscription("");
    setAudioChunks([]);
  };

  // Format duration to MM:SS
  const formatDuration = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  };
  const deleteTranscription = (indexToRemove) => {
    const updatedTranscriptions = previousTranscriptions.filter((_, index) => index !== indexToRemove);
    setPreviousTranscriptions(updatedTranscriptions);
    localStorage.setItem("transcriptions", JSON.stringify(updatedTranscriptions));
  };

  const renderStaticWaveform = () => {
    return (
      <div className="static-waveform">
        {waveformData.map((value, index) => (
          <div 
            key={index} 
            className="waveform-bar" 
            style={{ 
              height: `${Math.abs(value * 50) + 10}px`,
              backgroundColor: value > 0 ? '#007bff' : '#dc3545'
            }}
          />
        ))}
      </div>
    );
  };

  const renderExplanationOverlay = () => {
    return (
      <div className="explanation-overlay">
        <div className="explanation-content">
          <Lottie 
            animationData={voiceRecordingAnimation} 
            loop={true} 
            className="explanation-animation"
          />
          <div className="explanation-text">
            <h2>How Voice Transcription Works</h2>
            <ol>
              <li>
                <strong>Record</strong>
                <p>Click the microphone to start recording your voice</p>
              </li>
              <li>
                <strong>Transcribe</strong>
                <p>Upload the recording to convert speech to text</p>
              </li>
              <li>
                <strong>Save</strong>
                <p>View and manage your transcriptions easily</p>
              </li>
            </ol>
            <button 
              className="got-it-btn" 
              onClick={() => setShowExplanation(false)}
            >
              Got It!
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="recorder-container">
      {showExplanation && renderExplanationOverlay()}
      
      <h1>Voice Recorder & Transcription</h1>
      
      <div className="recording-duration">
        <Clock className="duration-icon" />
        <span>{formatDuration(recordingDuration)} / {formatDuration(MAX_RECORDING_TIME)}</span>
      </div>

      <div className="waveform-container">
        {isRecording ? (
          <canvas 
            ref={canvasRef} 
            width="500" 
            height="100" 
            style={{ 
              width: '100%', 
              height: '100px', 
              background: '#f8f9fa', 
              borderRadius: '8px'
            }}
          />
        ) : waveformData.length > 0 ? (
          renderStaticWaveform()
        ) : (
          <div className="empty-waveform" />
        )}
      </div>
      
      <div className="controls">
        <button
          className={`record-btn ${isRecording ? "stop" : "start"}`}
          onClick={isRecording ? stopRecording : startRecording}
          disabled={isLoading || (isRecording && recordingDuration >= MAX_RECORDING_TIME)}
        >
          {isRecording ? (
            <>
              <StopCircle className="button-icon" /> Stop Recording
            </>
          ) : (
            <>
              <Mic className="button-icon" /> Start Recording
            </>
          )}
        </button>
        
        {!isRecording && audioChunks.length > 0 && (
          <button 
            className="upload-btn" 
            onClick={uploadAudio} 
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 className="button-icon spin" /> Processing...
              </>
            ) : (
              <>
                <Upload className="button-icon" /> Upload & Transcribe
              </>
            )}
          </button>
        )}
      </div>

      <div className="transcription-section">
        {isLoading ? (
          <div className="loading-indicator">
            <Loader2 className="spin" />
            <p>Processing your audio...</p>
          </div>
        ) : (
          <>
            {transcription && (
              <div className="current-transcription">
                <h2>Current Transcription</h2>
                <p>{transcription}</p>
                <button onClick={clearTranscription} className="clear-btn">
                  Clear
                </button>
              </div>
            )}
          </>
        )}
      </div>

      <div className="previous-transcriptions">
        <div 
          className="transcriptions-header" 
          onClick={() => setIsPreviousCollapsed(!isPreviousCollapsed)}
        >
          <h2>Previous Transcriptions</h2>
          {isPreviousCollapsed ? <ChevronDown /> : <ChevronUp />}
        </div>

        {!isPreviousCollapsed && (
          previousTranscriptions.length === 0 ? (
            <p>No previous transcriptions</p>
          ) : (
            <ul>
              {previousTranscriptions.map((item, index) => (
                <li key={index} className="transcription-item">
                  <div className="transcription-content">
                    <span className="transcription-text">{item.text}</span>
                    <div className="transcription-details">
                      <span className="transcription-duration">
                        {formatDuration(item.duration)}
                      </span>
                      <span className="transcription-timestamp">{item.timestamp}</span>
                    </div>
                  </div>
                  <button 
                    className="delete-transcription-btn" 
                    onClick={() => deleteTranscription(index)}
                  >
                    <Trash2 size={16} />
                  </button>
                </li>
              ))}
            </ul>
          )
        )}
      </div>

      <button 
        className="show-explanation-btn" 
        onClick={() => setShowExplanation(true)}
      >
        <Info size={16} /> How it works
      </button>
    </div>
  );
};

export default Recorder;